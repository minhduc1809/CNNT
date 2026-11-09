import json
import os
import socket
import sys
import time
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter


class SourceIPAdapter(HTTPAdapter):
    """Gắn cứng IP nguồn (192.168.20.11 / 192.168.20.12) cho kết nối HTTP của điểm quét."""

    def __init__(self, source_ip: str, **kwargs):
        self.source_ip = source_ip
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        pool_kwargs["source_address"] = (self.source_ip, 0)
        return super().init_poolmanager(connections, maxsize, block=block, **pool_kwargs)


def get_http_session(client_ip: str = "") -> requests.Session:
    session = requests.Session()
    if client_ip:
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.bind((client_ip, 0))
            test_sock.close()
            adapter = SourceIPAdapter(client_ip)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
        except OSError:
            pass
    return session


def resolve_path(config_path: str, file_path: str) -> str:
    if os.path.isabs(file_path):
        return file_path
    base_dir = os.path.dirname(os.path.abspath(config_path))
    return os.path.join(base_dir, file_path)


def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        print(f"[LỖI] Không tìm thấy file cấu hình: {config_path}")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    scan_point_id = cfg.get("scan_point_id", "SP01")
    cfg["seq_file"] = resolve_path(config_path, cfg.get("seq_file", f"queue/seq_{scan_point_id}.txt"))
    cfg["log_file"] = resolve_path(config_path, cfg.get("log_file", f"logs/log_{scan_point_id}.log"))
    cfg["queue_file"] = resolve_path(config_path, cfg.get("queue_file", f"queue/queue_{scan_point_id}.jsonl"))
    return cfg


def write_log(log_file: str, message: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {message}"
    print(line)
    parent = os.path.dirname(log_file)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())


def read_current_seq_no(seq_file: str) -> int:
    if os.path.exists(seq_file):
        try:
            with open(seq_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return int(content)
        except ValueError:
            return 0
    return 0


def get_next_seq_no(seq_file: str) -> int:
    """Đọc và tăng số thứ tự seq_no lưu xuống đĩa an toàn (fsync chống tắt đột ngột)."""
    seq = read_current_seq_no(seq_file) + 1
    parent = os.path.dirname(seq_file)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(seq_file, "w", encoding="utf-8") as f:
        f.write(str(seq))
        f.flush()
        os.fsync(f.fileno())
    return seq


def generate_txn_id(scan_point_id: str, seq_no: int) -> str:
    """Sinh mã giao dịch theo chuẩn SV1: SPxx-yyyymmdd-nnnn"""
    today = datetime.now().strftime("%Y%m%d")
    return f"{scan_point_id}-{today}-{seq_no:04d}"


def validate_input(product_code: str, txn_type: str, quantity_str: str):
    """Kiểm tra đầu vào tại điểm quét theo chuẩn SV1 (CV02)."""
    product_code = product_code.strip().upper()
    if not product_code:
        return False, "INVALID_INPUT: Mã hàng (product_code) không được để trống!", None

    txn_type = txn_type.strip().upper()
    if txn_type not in ("NHAP", "XUAT"):
        return False, "INVALID_INPUT: Loại giao dịch chỉ nhận 'NHAP' hoặc 'XUAT'!", None

    try:
        quantity = int(quantity_str)
    except ValueError:
        return False, "INVALID_INPUT: Số lượng phải là số nguyên!", None

    if quantity <= 0:
        return False, "INVALID_INPUT: Số lượng phải là số nguyên dương lớn hơn 0!", None

    if quantity > 10000:
        return False, "INVALID_INPUT: Số lượng không được vượt quá 10000!", None

    return True, "OK", (product_code, txn_type, quantity)


def load_queue(queue_file: str) -> list:
    if not os.path.exists(queue_file):
        return []
    items = []
    with open(queue_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return items


def save_queue(queue_file: str, items: list):
    parent = os.path.dirname(queue_file)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(queue_file, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def enqueue_transaction(queue_file: str, record: dict):
    """Ghi giao dịch vào file hàng đợi cục bộ trước khi gửi qua mạng (CV03)."""
    items = load_queue(queue_file)
    items.append(record)
    save_queue(queue_file, items)


def update_queue_status(
    queue_file: str,
    txn_id: str,
    new_status: str,
    note: str = "",
    latency_ms: float = 0.0,
    retries: int = 0,
):
    items = load_queue(queue_file)
    for item in items:
        p = item.get("payload", {})
        if p.get("txn_id") == txn_id:
            item["status"] = new_status
            item["updated_at"] = datetime.now().isoformat()
            if note:
                item["note"] = note
            if latency_ms > 0:
                item["latency_ms"] = latency_ms
            item["retries"] = item.get("retries", 0) + retries
    save_queue(queue_file, items)


def login_api(base_url: str, username: str, password: str, timeout: int) -> str:
    """Đăng nhập lấy Bearer Token theo giao ước SV1."""
    try:
        resp = requests.post(
            f"{base_url}/api/login",
            json={"username": username, "password": password},
            timeout=timeout,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("token") or username
    except Exception:
        pass
    return f"token-{username}"


def verify_saved_on_server(base_url: str, txn_id: str, headers: dict, timeout: int, log_file: str) -> bool:
    """Đọc lại giao dịch từ máy chủ theo txn_id để chứng minh đã lưu vào CSDL (CV02)."""
    try:
        resp = requests.get(
            f"{base_url}/api/transactions/{txn_id}",
            headers=headers,
            timeout=timeout,
        )
        if resp.status_code == 200:
            write_log(log_file, f"[ĐỌC LẠI THÀNH CÔNG] Bản ghi trên máy chủ: {resp.text.strip()}")
            return True
        else:
            write_log(log_file, f"[ĐỌC LẠI KHÔNG THẤY] HTTP {resp.status_code}: {resp.text.strip()}")
    except Exception as e:
        write_log(log_file, f"[CẢNH BÁO] Không đọc lại được chi tiết {txn_id}: {e}")
    return False


def send_with_retry(config: dict, payload: dict, token: str) -> bool:
    """Gửi giao dịch với cơ chế chờ tăng dần (5 -> 10 -> 20 -> 60s) và giữ nguyên txn_id (CV03)."""
    base_url = config["api_base_url"]
    timeout = config.get("timeout_seconds", 5)
    delays = config.get("retry_delays", [5, 10, 20, 60])
    log_file = config["log_file"]
    queue_file = config["queue_file"]
    txn_id = payload["txn_id"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    session = get_http_session(config.get("client_ip", ""))

    max_attempts = len(delays) + 1
    for attempt in range(1, max_attempts + 1):
        start_time = time.time()
        try:
            write_log(log_file, f"[GỬI LẦN {attempt}/{max_attempts}] txn_id={txn_id} | trạng thái=CHO_XAC_NHAN")
            resp = session.post(
                f"{base_url}/api/transactions",
                json=payload,
                headers=headers,
                timeout=timeout,
            )
            latency_ms = round((time.time() - start_time) * 1000, 2)
            resp_text = resp.text.strip()
            try:
                resp_json = resp.json() if resp_text else {}
            except ValueError:
                resp_json = {}
            error_code = resp_json.get("error_code", "")
            stock_after = resp_json.get("stock_after")
            msg_server = resp_json.get("message", "")

            # 1. Thành công (200 hoặc 201 Created)
            if resp.status_code in (200, 201):
                update_queue_status(
                    queue_file, txn_id, "DA_XAC_NHAN", f"HTTP {resp.status_code}", latency_ms, attempt - 1
                )
                write_log(
                    log_file,
                    f"[THÀNH CÔNG] txn_id={txn_id} | trạng thái=DA_XAC_NHAN | stock_after={stock_after} | độ_trễ={latency_ms}ms | số_lần_gửi_lại={attempt - 1} | phản_hồi={resp_text}",
                )
                verify_saved_on_server(base_url, txn_id, headers, timeout, log_file)
                return True

            # 2. Giao dịch trùng (409 DUPLICATE_TXN)
            if resp.status_code == 409 or error_code == "DUPLICATE_TXN" or "DUPLICATE_TXN" in resp_text:
                update_queue_status(
                    queue_file, txn_id, "DA_XAC_NHAN", "409 DUPLICATE_TXN", latency_ms, attempt - 1
                )
                write_log(
                    log_file,
                    f"[CHỐNG TRÙNG - ĐÃ LƯU TRƯỚC ĐÓ] txn_id={txn_id} | trạng thái=DA_XAC_NHAN | error_code={error_code or 'DUPLICATE_TXN'} | độ_trễ={latency_ms}ms | phản_hồi={resp_text}",
                )
                return True

            # 3. Các lỗi nghiệp vụ rõ ràng theo yêu cầu CV02 (không gửi lại)
            if resp.status_code == 403 or error_code == "FORBIDDEN":
                update_queue_status(queue_file, txn_id, "TU_CHOI", "403 FORBIDDEN", latency_ms, attempt - 1)
                write_log(
                    log_file,
                    f"[KHÔNG CÓ QUYỀN - 403 FORBIDDEN] txn_id={txn_id} | error_code={error_code or 'FORBIDDEN'} | thông_báo={msg_server} | độ_trễ={latency_ms}ms | chi_tiết={resp_text}",
                )
                return False

            if resp.status_code == 404 or error_code == "PRODUCT_NOT_FOUND" or "PRODUCT_NOT_FOUND" in resp_text:
                update_queue_status(queue_file, txn_id, "TU_CHOI", "404 NOT_FOUND", latency_ms, attempt - 1)
                write_log(
                    log_file,
                    f"[MÃ HÀNG / ĐIỂM QUÉT KHÔNG TỒN TẠI - 404] txn_id={txn_id} | error_code={error_code or 'NOT_FOUND'} | độ_trễ={latency_ms}ms | chi_tiết={resp_text}",
                )
                return False

            if error_code == "INSUFFICIENT_STOCK" or "INSUFFICIENT_STOCK" in resp_text or resp.status_code == 422:
                update_queue_status(queue_file, txn_id, "TU_CHOI", "INSUFFICIENT_STOCK", latency_ms, attempt - 1)
                write_log(
                    log_file,
                    f"[KHÔNG ĐỦ HÀNG TRONG KHO - INSUFFICIENT_STOCK] txn_id={txn_id} | error_code={error_code or 'INSUFFICIENT_STOCK'} | độ_trễ={latency_ms}ms | chi_tiết={resp_text}",
                )
                return False

            if resp.status_code in (400, 401):
                update_queue_status(queue_file, txn_id, "TU_CHOI", f"HTTP {resp.status_code}", latency_ms, attempt - 1)
                write_log(
                    log_file,
                    f"[BỊ TỪ CHỐI NGHIỆP VỤ] txn_id={txn_id} | HTTP={resp.status_code} | độ_trễ={latency_ms}ms | chi_tiết={resp_text}",
                )
                return False

            write_log(log_file, f"[LỖI MÁY CHỦ {resp.status_code}] độ_trễ={latency_ms}ms | nội_dung={resp_text}")

        except requests.RequestException as err:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            write_log(log_file, f"[LỖI KẾT NỐI MẠNG] txn_id={txn_id} | độ_trễ={latency_ms}ms | lỗi={err}")

        # Chờ tăng dần trước khi gửi lại (CV03)
        if attempt <= len(delays):
            wait_sec = delays[attempt - 1]
            write_log(log_file, f"[HÀNG ĐỢI] Giữ nguyên txn_id={txn_id}, chờ {wait_sec} giây trước khi gửi lại...")
            time.sleep(wait_sec)

    update_queue_status(queue_file, txn_id, "CHO_XAC_NHAN", "Mất kết nối mạng", 0.0, len(delays))
    write_log(
        log_file,
        f"[GIỮ TRONG HÀNG ĐỢI CỤC BỘ] Đã hết số lần thử. Giao dịch {txn_id} giữ trạng thái CHO_XAC_NHAN trong {queue_file}.",
    )
    return False


def flush_pending_queue(config: dict, token: str):
    """Đồng bộ lại các giao dịch đang CHO_XAC_NHAN trong file hàng đợi khi có mạng lại (CV03)."""
    queue_file = config["queue_file"]
    log_file = config["log_file"]
    items = load_queue(queue_file)
    pending = [i for i in items if i.get("status") == "CHO_XAC_NHAN"]

    if not pending:
        print("Không có giao dịch nào đang chờ trong hàng đợi cục bộ.")
        return

    write_log(log_file, f"[ĐỒNG BỘ HÀNG ĐỢI] Phát hiện {len(pending)} giao dịch CHO_XAC_NHAN, bắt đầu gửi lại...")
    for item in pending:
        send_with_retry(config, item["payload"], token)


def check_server_and_inventory(config: dict, token: str):
    """Kiểm tra kết nối đến máy chủ và tra cứu tồn kho mặt hàng (CV01 & CV02)."""
    base_url = config["api_base_url"]
    timeout = config.get("timeout_seconds", 5)
    log_file = config["log_file"]
    headers = {"Authorization": f"Bearer {token}"}

    p_code = input("Nhập mã hàng cần kiểm tra tồn kho (mặc định SP001): ").strip().upper() or "SP001"
    start = time.time()
    try:
        resp = requests.get(f"{base_url}/api/inventory/{p_code}", headers=headers, timeout=timeout)
        latency_ms = round((time.time() - start) * 1000, 2)
        if resp.status_code == 200:
            data = resp.json()
            write_log(
                log_file,
                f"[KIỂM TRA KẾT NỐI & TỒN KHO] Máy chủ {base_url} phản hồi 200 OK ({latency_ms}ms) -> Mặt hàng {p_code}: Tồn hiện tại = {data.get('quantity')}",
            )
        else:
            write_log(log_file, f"[TRA CỨU TỒN KHO] HTTP {resp.status_code} ({latency_ms}ms): {resp.text.strip()}")
    except requests.RequestException as err:
        write_log(log_file, f"[MẤT KẾT NỐI MÁY CHỦ] Không thể kết nối tới {base_url}: {err}")


def show_metrics_and_reconcile_seq(config: dict, token: str):
    """Hiển thị bảng số đo độ trễ, tỉ lệ thành công, số lần gửi lại và đối chiếu seq_no với máy chủ (CV03)."""
    queue_file = config["queue_file"]
    seq_file = config["seq_file"]
    base_url = config["api_base_url"]
    timeout = config.get("timeout_seconds", 5)
    scan_point_id = config.get("scan_point_id", "SP01")

    items = load_queue(queue_file)
    current_seq = read_current_seq_no(seq_file)
    total = len(items)
    confirmed = [i for i in items if i.get("status") == "DA_XAC_NHAN"]
    pending = [i for i in items if i.get("status") == "CHO_XAC_NHAN"]
    rejected = [i for i in items if i.get("status") == "TU_CHOI"]

    latencies = [float(i["latency_ms"]) for i in items if i.get("latency_ms", 0) > 0]
    avg_lat = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
    min_lat = round(min(latencies), 2) if latencies else 0.0
    max_lat = round(max(latencies), 2) if latencies else 0.0
    total_retries = sum(int(i.get("retries", 0)) for i in items)
    success_rate = round((len(confirmed) / total) * 100, 2) if total > 0 else 0.0

    print("\n" + "=" * 68)
    print(f" BẢNG SỐ ĐO THỰC NGHIỆM & ĐỐI CHIẾU HÀNG ĐỢI - ĐIỂM QUÉT {scan_point_id} (CV03)")
    print("=" * 68)
    print(f" - Số thứ tự seq_no hiện tại trên đĩa : {current_seq}")
    print(f" - Tổng số giao dịch trong hàng đợi    : {total}")
    print(f"   + Đã xác nhận (DA_XAC_NHAN)         : {len(confirmed)}")
    print(f"   + Chờ xác nhận (CHO_XAC_NHAN)       : {len(pending)}")
    print(f"   + Bị từ chối nghiệp vụ (TU_CHOI)    : {len(rejected)}")
    print(f" - Tỉ lệ gửi thành công                : {success_rate}%")
    print(f" - Tổng số lần gửi lại (Retry)         : {total_retries} lần")
    print(f" - Độ trễ phản hồi (Min / Avg / Max)   : {min_lat}ms / {avg_lat}ms / {max_lat}ms")
    print("-" * 68)

    if confirmed:
        print(" Đang đối chiếu các giao dịch DA_XAC_NHAN với CSDL máy chủ...")
        headers = {"Authorization": f"Bearer {token}"}
        matched = 0
        missing_on_server = []
        for item in confirmed:
            tid = item["payload"]["txn_id"]
            try:
                r = requests.get(f"{base_url}/api/transactions/{tid}", headers=headers, timeout=timeout)
                if r.status_code == 200:
                    matched += 1
                else:
                    missing_on_server.append(tid)
            except requests.RequestException:
                missing_on_server.append(tid)
        print(f" -> Kết quả đối chiếu: Khớp {matched}/{len(confirmed)} giao dịch trên máy chủ | Thiếu: {len(missing_on_server)}")
    print("=" * 68)


def build_payload(txn_id: str, product_code: str, txn_type: str, quantity: int, scan_point_id: str) -> dict:
    """Tạo payload chuẩn 100% theo Giao ước API của SV1."""
    return {
        "txn_id": txn_id,
        "product_code": product_code,
        "txn_type": txn_type,
        "quantity": quantity,
        "scan_point_id": scan_point_id,
        "client_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }


def main():
    if len(sys.argv) < 2:
        print("Cách chạy: python scanner.py <đường_dẫn_file_config.json> [--url http://IP_MAY_CHU:5000]")
        print("Ví dụ:     python scanner.py config_sp01.json --url http://172.23.155.222:5000")
        sys.exit(1)

    config = load_config(sys.argv[1])
    if len(sys.argv) >= 4 and sys.argv[2] == "--url":
        config["api_base_url"] = sys.argv[3].rstrip("/")
    elif os.getenv("API_BASE_URL"):
        config["api_base_url"] = os.getenv("API_BASE_URL").rstrip("/")
    scan_point_id = config.get("scan_point_id", "SP01")
    log_file = config["log_file"]
    queue_file = config["queue_file"]

    print("=" * 64)
    print(f" ĐIỂM QUÉT GIẢ LẬP: {scan_point_id} (IP: {config.get('client_ip')})")
    print(f" Máy chủ đích     : {config['api_base_url']}")
    print("=" * 64)

    default_user = config.get("default_username", "nv01")
    username = input(f"Đăng nhập - Tài khoản (mặc định {default_user}): ").strip() or default_user
    password = input("Đăng nhập - Mật khẩu (mặc định Kho@2026): ").strip() or "Kho@2026"
    token = login_api(config["api_base_url"], username, password, config.get("timeout_seconds", 5))
    write_log(log_file, f"Khởi động {scan_point_id} với người dùng '{username}'.")

    # Tự động kiểm tra hàng đợi tồn đọng từ lần tắt đột ngột trước
    flush_pending_queue(config, token)

    while True:
        print(f"\n--- MENU ĐIỂM QUÉT {scan_point_id} (Người dùng: {username}) ---")
        print("1. Quét và gửi giao dịch mới (NHAP / XUAT)")
        print("2. Đồng bộ lại hàng đợi chưa xác nhận (sau khi có mạng lại)")
        print("3. Gửi lặp lại một txn_id cũ (Test ca KT2 - Chống trùng)")
        print("4. Kiểm tra kết nối máy chủ & Tra cứu tồn kho mặt hàng")
        print("5. Xem bảng số đo độ trễ, tỉ lệ thành công & Đối chiếu seq_no (CV03)")
        print("6. Đổi tài khoản đăng nhập (Test phân quyền viewer / nhân viên / thủ kho)")
        print("0. Thoát")
        choice = input("Chọn chức năng (0-6): ").strip()

        if choice == "0":
            break
        elif choice == "2":
            flush_pending_queue(config, token)
        elif choice == "3":
            dup_txn = input("Nhập mã txn_id muốn gửi lặp lại: ").strip()
            p_code = input("Nhập mã hàng (product_code, VD: SP001): ").strip().upper()
            t_type = input("Loại giao dịch (NHAP/XUAT): ").strip().upper()
            qty_str = input("Số lượng: ").strip()
            ok, msg, cleaned = validate_input(p_code, t_type, qty_str)
            if not ok:
                write_log(log_file, f"[CHẶN ĐẦU VÀO] {msg}")
                continue
            product_code, txn_type, quantity = cleaned
            payload = build_payload(dup_txn, product_code, txn_type, quantity, scan_point_id)
            print("\n[JSON GỬI LẶP KT2]:", json.dumps(payload, ensure_ascii=False, indent=2))
            send_with_retry(config, payload, token)
        elif choice == "4":
            check_server_and_inventory(config, token)
        elif choice == "5":
            show_metrics_and_reconcile_seq(config, token)
        elif choice == "6":
            new_user = input("Nhập tài khoản mới (VD: viewer_demo, nhanvien_demo, thukho_demo): ").strip()
            if new_user:
                username = new_user
                token = login_api(config["api_base_url"], username, password, config.get("timeout_seconds", 5))
                write_log(log_file, f"Đã chuyển người thực hiện tại {scan_point_id} sang '{username}' (token={token}).")
        elif choice == "1":
            p_code = input("Nhập mã hàng (product_code, VD: SP001): ")
            t_type = input("Nhập loại giao dịch (NHAP / XUAT): ")
            qty_str = input("Nhập số lượng (1 - 10000): ")

            ok, msg, cleaned = validate_input(p_code, t_type, qty_str)
            if not ok:
                write_log(log_file, f"[CHẶN ĐẦU VÀO] {msg}")
                continue

            product_code, txn_type, quantity = cleaned
            seq_no = get_next_seq_no(config["seq_file"])
            txn_id = generate_txn_id(scan_point_id, seq_no)

            payload = build_payload(txn_id, product_code, txn_type, quantity, scan_point_id)

            print("\n[GIAO DỊCH JSON ĐÃ SINH]:")
            print(json.dumps(payload, indent=2, ensure_ascii=False))

            # Ghi vào file hàng đợi cục bộ với trạng thái CHO_XAC_NHAN trước khi gửi
            record = {
                "status": "CHO_XAC_NHAN",
                "created_at": datetime.now().isoformat(),
                "username": username,
                "retries": 0,
                "payload": payload,
            }
            enqueue_transaction(queue_file, record)

            # Gửi qua mạng tới máy chủ
            send_with_retry(config, payload, token)


if __name__ == "__main__":
    main()
