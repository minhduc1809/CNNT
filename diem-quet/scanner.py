import json
import os
import sys
import time
from datetime import datetime
import requests


def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        print(f"[LỖI] Không tìm thấy file cấu hình: {config_path}")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_log(log_file: str, message: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {message}"
    print(line)
    parent = os.path.dirname(log_file)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_next_seq_no(seq_file: str) -> int:
    """Đọc và tăng số thứ tự seq_no lưu trên đĩa."""
    seq = 0
    if os.path.exists(seq_file):
        try:
            with open(seq_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    seq = int(content)
        except ValueError:
            seq = 0
    seq += 1
    parent = os.path.dirname(seq_file)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(seq_file, "w", encoding="utf-8") as f:
        f.write(str(seq))
    return seq


def generate_txn_id(scan_point_id: str, seq_no: int) -> str:
    """Sinh mã giao dịch theo chuẩn SV1: SPxx-yyyymmdd-nnnn"""
    today = datetime.now().strftime("%Y%m%d")
    return f"{scan_point_id}-{today}-{seq_no:04d}"


def validate_input(product_code: str, txn_type: str, quantity_str: str):
    """Kiểm tra đầu vào tại điểm quét theo chuẩn SV1."""
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


def enqueue_transaction(queue_file: str, record: dict):
    """Ghi giao dịch vào file hàng đợi cục bộ trước khi gửi qua mạng (CV03)."""
    items = load_queue(queue_file)
    items.append(record)
    save_queue(queue_file, items)


def update_queue_status(queue_file: str, txn_id: str, new_status: str, note: str = ""):
    items = load_queue(queue_file)
    for item in items:
        p = item.get("payload", {})
        if p.get("txn_id") == txn_id:
            item["status"] = new_status
            item["updated_at"] = datetime.now().isoformat()
            if note:
                item["note"] = note
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
            return data.get("token") or data.get("access_token") or username
    except Exception:
        pass
    # Nếu máy chủ chưa bật /api/login hoặc đang ngắt mạng, dùng token tạm
    return f"token-{username}"


def verify_saved_on_server(base_url: str, txn_id: str, headers: dict, timeout: int, log_file: str) -> bool:
    """Đọc lại giao dịch từ máy chủ theo txn_id để chứng minh đã lưu (CV02)."""
    try:
        resp = requests.get(
            f"{base_url}/api/transactions/{txn_id}",
            headers=headers,
            timeout=timeout,
        )
        if resp.status_code == 200:
            write_log(log_file, f"[ĐỌC LẠI THÀNH CÔNG] Bản ghi trên máy chủ: {resp.text}")
            return True
        else:
            write_log(log_file, f"[ĐỌC LẠI KHÔNG THẤY] HTTP {resp.status_code}: {resp.text}")
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

    max_attempts = len(delays) + 1
    for attempt in range(1, max_attempts + 1):
        start_time = time.time()
        try:
            write_log(log_file, f"[GỬI LẦN {attempt}/{max_attempts}] txn_id={txn_id} | trạng thái=CHO_XAC_NHAN")
            resp = requests.post(
                f"{base_url}/api/transactions",
                json=payload,
                headers=headers,
                timeout=timeout,
            )
            latency_ms = round((time.time() - start_time) * 1000, 2)

            # 1. Thành công (200 hoặc 201 Created)
            if resp.status_code in (200, 201):
                update_queue_status(queue_file, txn_id, "DA_XAC_NHAN", f"HTTP {resp.status_code}")
                write_log(
                    log_file,
                    f"[THÀNH CÔNG] txn_id={txn_id} | trạng thái=DA_XAC_NHAN | độ_trễ={latency_ms}ms | số_lần_gửi_lại={attempt - 1} | phản_hồi={resp.text}",
                )
                verify_saved_on_server(base_url, txn_id, headers, timeout, log_file)
                return True

            # 2. Giao dịch trùng (409 DUPLICATE_TXN)
            if resp.status_code == 409 or (resp.status_code == 400 and "da ton tai" in resp.text.lower()):
                update_queue_status(queue_file, txn_id, "DA_XAC_NHAN", "409 DUPLICATE_TXN")
                write_log(
                    log_file,
                    f"[CHỐNG TRÙNG - ĐÃ LƯU TRƯỚC ĐÓ] txn_id={txn_id} | trạng thái=DA_XAC_NHAN | độ_trễ={latency_ms}ms | phản_hồi={resp.text}",
                )
                return True

            # 3. Các lỗi nghiệp vụ không cần gửi lại (400, 401, 403, 404, 422)
            if resp.status_code in (400, 401, 403, 404, 422):
                update_queue_status(queue_file, txn_id, "TU_CHOI", f"HTTP {resp.status_code}")
                write_log(
                    log_file,
                    f"[BỊ TỪ CHỐI NGHIỆP VỤ] txn_id={txn_id} | HTTP={resp.status_code} | độ_trễ={latency_ms}ms | chi_tiết={resp.text}",
                )
                return False

            write_log(log_file, f"[LỖI MÁY CHỦ {resp.status_code}] độ_trễ={latency_ms}ms | nội_dung={resp.text}")

        except requests.RequestException as err:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            write_log(log_file, f"[LỖI KẾT NỐI MẠNG] txn_id={txn_id} | độ_trễ={latency_ms}ms | lỗi={err}")

        # Chờ tăng dần trước khi gửi lại
        if attempt <= len(delays):
            wait_sec = delays[attempt - 1]
            write_log(log_file, f"[HÀNG ĐỢI] Giữ nguyên txn_id={txn_id}, chờ {wait_sec} giây trước khi gửi lại...")
            time.sleep(wait_sec)

    write_log(
        log_file,
        f"[GIỮ TRONG HÀNG ĐỢI CỤC BỘ] Đã hết số lần thử. Giao dịch {txn_id} giữ trạng thái CHO_XAC_NHAN trong {queue_file}.",
    )
    return False


def flush_pending_queue(config: dict, token: str):
    """Đồng bộ lại các giao dịch đang CHO_XAC_NHAN trong file hàng đợi khi có mạng lại."""
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
        print("Cách chạy: python scanner.py <đường_dẫn_file_config.json>")
        print("Ví dụ:     python scanner.py config_sp01.json")
        sys.exit(1)

    config = load_config(sys.argv[1])
    scan_point_id = config.get("scan_point_id", "SP01")
    log_file = config["log_file"]
    queue_file = config["queue_file"]

    print("=" * 60)
    print(f" ĐIỂM QUÉT GIẢ LẬP: {scan_point_id} (IP: {config.get('client_ip')})")
    print(f" Máy chủ đích     : {config['api_base_url']}")
    print("=" * 60)

    default_user = config.get("default_username", "nv01")
    username = input(f"Đăng nhập - Tài khoản (mặc định {default_user}): ").strip() or default_user
    password = input("Đăng nhập - Mật khẩu (mặc định Kho@2026): ").strip() or "Kho@2026"
    token = login_api(config["api_base_url"], username, password, config.get("timeout_seconds", 5))
    write_log(log_file, f"Khởi động {scan_point_id} với người dùng '{username}'.")

    # Tự động kiểm tra hàng đợi tồn đọng từ lần tắt đột ngột trước
    flush_pending_queue(config, token)

    while True:
        print(f"\n--- MENU ĐIỂM QUÉT {scan_point_id} ---")
        print("1. Quét và gửi giao dịch mới (NHAP / XUAT)")
        print("2. Đồng bộ lại hàng đợi chưa xác nhận (sau khi có mạng lại)")
        print("3. Gửi lặp lại một txn_id cũ (Để test ca KT2 - Chống trùng)")
        print("0. Thoát")
        choice = input("Chọn chức năng (0-3): ").strip()

        if choice == "0":
            break
        elif choice == "2":
            flush_pending_queue(config, token)
        elif choice == "3":
            dup_txn = input("Nhập mã txn_id muốn gửi lặp lại: ").strip()
            p_code = input("Nhập mã hàng (product_code, VD: SP001): ").strip().upper()
            t_type = input("Loại giao dịch (NHAP/XUAT): ").strip().upper()
            qty = int(input("Số lượng: ").strip())
            payload = build_payload(dup_txn, p_code, t_type, qty, scan_point_id)
            print("\n[JSON GỬI LẶP KT2]:", json.dumps(payload, ensure_ascii=False, indent=2))
            send_with_retry(config, payload, token)
        elif choice == "1":
            p_code = input("Nhập mã hàng (product_code, VD: SP001): ")
            t_type = input("Nhập loại giao dịch (NHAP / XUAT): ")
            qty_str = input("Nhập số lượng (1 - 10000): ")

            ok, msg, cleaned = validate_input(p_code, t_type, qty_str)
            if not ok:
                write_log(log_file, f"[CHẶN ĐẦU VÀO] {msg}")
                continue

            product_code, txn_type, quantity = cleaned
            seq_file = config.get("seq_file", f"seq_{scan_point_id}.txt")
            seq_no = get_next_seq_no(seq_file)
            txn_id = generate_txn_id(scan_point_id, seq_no)

            payload = build_payload(txn_id, product_code, txn_type, quantity, scan_point_id)

            print("\n[GIAO DỊCH JSON ĐÃ SINH]:")
            print(json.dumps(payload, indent=2, ensure_ascii=False))

            # Ghi vào file hàng đợi cục bộ với trạng thái CHO_XAC_NHAN trước khi gửi
            record = {
                "status": "CHO_XAC_NHAN",
                "created_at": datetime.now().isoformat(),
                "username": username,
                "payload": payload,
            }
            enqueue_transaction(queue_file, record)

            # Gửi qua mạng tới máy chủ
            send_with_retry(config, payload, token)


if __name__ == "__main__":
    main()
