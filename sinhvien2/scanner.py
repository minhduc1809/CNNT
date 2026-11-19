import json
import os
import socket
import sys
import time
import getpass
from urllib.parse import urlsplit
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
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            test_sock.bind((client_ip, 0))
        except OSError as exc:
            raise RuntimeError(
                f"Không thể gắn IP nguồn {client_ip}. Hãy cấu hình IP này trên máy điểm quét "
                "hoặc dùng API_BASE_URL/--url loopback cho chạy thử cùng máy."
            ) from exc
        finally:
            test_sock.close()
        adapter = SourceIPAdapter(client_ip)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
    return session


def get_api_session(base_url: str, client_ip: str = "") -> requests.Session:
    """Bind the configured source IP for remote calls; loopback is local development only."""
    parsed_url = urlsplit(base_url)
    loopback_hosts = {"127.0.0.1", "localhost", "::1"}
    source_ip = "" if parsed_url.hostname in loopback_hosts else client_ip
    return get_http_session(source_ip)


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
                raise ValueError(f"Tệp seq_no rỗng: {seq_file}")
        except ValueError as exc:
            raise ValueError(f"Tệp seq_no không hợp lệ: {seq_file}") from exc
    return 0


def get_next_seq_no(seq_file: str) -> int:
    """Đọc và tăng seq_no bằng thao tác thay tệp nguyên tử, sau đó fsync xuống đĩa."""
    seq = read_current_seq_no(seq_file) + 1
    parent = os.path.dirname(seq_file)
    if parent:
        os.makedirs(parent, exist_ok=True)
    temp_path = f"{seq_file}.tmp-{os.getpid()}"
    try:
        with open(temp_path, "w", encoding="utf-8", newline="") as f:
            f.write(str(seq))
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, seq_file)
        _fsync_directory(parent or ".")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    return seq


def _fsync_directory(directory: str):
    """Lưu metadata thư mục trên hệ thống hỗ trợ mở và fsync thư mục."""
    if os.name == "nt":
        return
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    try:
        fd = os.open(directory, flags)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except OSError:
        # Một số hệ thống tệp không cho fsync thư mục; dữ liệu tệp vẫn đã fsync.
        pass


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
    items_by_id = {}
    ordered_ids = []
    with open(queue_file, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if line:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Hàng đợi bị lỗi JSON tại dòng {line_no}: {queue_file}. "
                        "Không tiếp tục để tránh âm thầm bỏ giao dịch."
                    ) from exc

                # Tương thích các hàng đợi cũ lưu một bản ghi hoàn chỉnh trên mỗi dòng.
                if event.get("event") == "enqueue":
                    record = event["record"]
                    txn_id = record["payload"]["txn_id"]
                    items_by_id[txn_id] = record
                    if txn_id not in ordered_ids:
                        ordered_ids.append(txn_id)
                elif event.get("event") == "status":
                    txn_id = event["txn_id"]
                    if txn_id in items_by_id:
                        record = items_by_id[txn_id]
                        record["status"] = event["status"]
                        record["updated_at"] = event["updated_at"]
                        if event.get("note"):
                            record["note"] = event["note"]
                        if event.get("latency_ms", 0) > 0:
                            record["latency_ms"] = event["latency_ms"]
                        record["retries"] = record.get("retries", 0) + event.get("retries_delta", 0)
                else:
                    txn_id = event.get("payload", {}).get("txn_id")
                    if not txn_id:
                        raise ValueError(f"Bản ghi hàng đợi thiếu txn_id tại dòng {line_no}: {queue_file}")
                    items_by_id[txn_id] = event
                    if txn_id not in ordered_ids:
                        ordered_ids.append(txn_id)
    return [items_by_id[txn_id] for txn_id in ordered_ids]


def _append_queue_event(queue_file: str, event: dict):
    """Nối một sự kiện JSONL và fsync; không viết lại các giao dịch cũ."""
    parent = os.path.dirname(queue_file)
    if parent:
        os.makedirs(parent, exist_ok=True)
    payload = (json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    fd = os.open(queue_file, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise OSError(f"Không ghi thêm được dữ liệu vào hàng đợi {queue_file}")
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)
    _fsync_directory(parent or ".")


def save_queue(queue_file: str, items: list):
    """Tương thích API cũ bằng cách ghi sự kiện, không thay thế nhật ký."""
    current_items = load_queue(queue_file)
    current = {item.get("payload", {}).get("txn_id"): item for item in current_items}
    for item in items:
        txn_id = item.get("payload", {}).get("txn_id")
        if not txn_id:
            raise ValueError("Không thể lưu bản ghi hàng đợi không có txn_id")
        if txn_id not in current:
            _append_queue_event(queue_file, {"event": "enqueue", "record": item})
            current[txn_id] = item
            continue

        old = current[txn_id]
        if any(old.get(key) != item.get(key) for key in ("status", "note", "latency_ms", "retries")):
            event = {
                "event": "status",
                "txn_id": txn_id,
                "status": item.get("status", old.get("status", "CHO_XAC_NHAN")),
                "updated_at": item.get("updated_at", datetime.now().isoformat()),
                "retries_delta": max(0, item.get("retries", 0) - old.get("retries", 0)),
            }
            if item.get("note"):
                event["note"] = item["note"]
            if item.get("latency_ms", 0) > 0:
                event["latency_ms"] = item["latency_ms"]
            _append_queue_event(queue_file, event)


def enqueue_transaction(queue_file: str, record: dict):
    """Ghi giao dịch vào file hàng đợi cục bộ trước khi gửi qua mạng (CV03)."""
    txn_id = record.get("payload", {}).get("txn_id")
    if not txn_id:
        raise ValueError("Không thể lưu giao dịch không có txn_id")
    if any(item.get("payload", {}).get("txn_id") == txn_id for item in load_queue(queue_file)):
        raise ValueError(f"txn_id đã có trong hàng đợi cục bộ: {txn_id}")
    _append_queue_event(queue_file, {"event": "enqueue", "record": record})


def update_queue_status(
    queue_file: str,
    txn_id: str,
    new_status: str,
    note: str = "",
    latency_ms: float = 0.0,
    retries: int = 0,
):
    event = {
        "event": "status",
        "txn_id": txn_id,
        "status": new_status,
        "updated_at": datetime.now().isoformat(),
        "retries_delta": retries,
    }
    if note:
        event["note"] = note
    if latency_ms > 0:
        event["latency_ms"] = latency_ms
    _append_queue_event(queue_file, event)


def login_api(base_url: str, username: str, password: str, timeout: int, client_ip: str = "") -> str:
    """Đăng nhập lấy Bearer Token; lỗi xác thực/kết nối luôn dừng luồng gửi."""
    try:
        with get_api_session(base_url, client_ip) as session:
            resp = session.post(
                f"{base_url}/api/login",
                json={"username": username, "password": password},
                timeout=timeout,
            )
        if resp.status_code != 200:
            raise RuntimeError(f"Đăng nhập thất bại: HTTP {resp.status_code}: {resp.text.strip()}")
        data = resp.json()
        token = data.get("token")
        if not isinstance(token, str) or not token.strip():
            raise RuntimeError("API đăng nhập trả HTTP 200 nhưng không có Bearer token hợp lệ")
        return token.strip()
    except requests.RequestException as exc:
        raise RuntimeError(f"Không kết nối được API đăng nhập tại {base_url}/api/login: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("API đăng nhập trả về JSON không hợp lệ") from exc


def verify_saved_on_server(base_url: str, txn_id: str, headers: dict, timeout: int, log_file: str, client_ip: str = "") -> bool:
    """Đọc lại giao dịch từ máy chủ theo txn_id để chứng minh đã lưu vào CSDL (CV02)."""
    try:
        with get_api_session(base_url, client_ip) as session:
            resp = session.get(
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
    if not token or not token.strip():
        raise ValueError("Thiếu Bearer token; giao dịch chưa được gửi")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    session = get_api_session(base_url, config.get("client_ip", ""))

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
                verify_saved_on_server(base_url, txn_id, headers, timeout, log_file, config.get("client_ip", ""))
                session.close()
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
                session.close()
                return True

            # 3. Các lỗi nghiệp vụ rõ ràng theo yêu cầu CV02 (không gửi lại)
            if resp.status_code == 403 or error_code == "FORBIDDEN":
                update_queue_status(queue_file, txn_id, "TU_CHOI", "403 FORBIDDEN", latency_ms, attempt - 1)
                write_log(
                    log_file,
                    f"[KHÔNG CÓ QUYỀN - 403 FORBIDDEN] txn_id={txn_id} | error_code={error_code or 'FORBIDDEN'} | thông_báo={msg_server} | độ_trễ={latency_ms}ms | chi_tiết={resp_text}",
                )
                session.close()
                return False

            if resp.status_code == 404 or error_code == "PRODUCT_NOT_FOUND" or "PRODUCT_NOT_FOUND" in resp_text:
                update_queue_status(queue_file, txn_id, "TU_CHOI", "404 NOT_FOUND", latency_ms, attempt - 1)
                write_log(
                    log_file,
                    f"[MÃ HÀNG / ĐIỂM QUÉT KHÔNG TỒN TẠI - 404] txn_id={txn_id} | error_code={error_code or 'NOT_FOUND'} | độ_trễ={latency_ms}ms | chi_tiết={resp_text}",
                )
                session.close()
                return False

            if error_code == "INSUFFICIENT_STOCK" or "INSUFFICIENT_STOCK" in resp_text or resp.status_code == 422:
                update_queue_status(queue_file, txn_id, "TU_CHOI", "INSUFFICIENT_STOCK", latency_ms, attempt - 1)
                write_log(
                    log_file,
                    f"[KHÔNG ĐỦ HÀNG TRONG KHO - INSUFFICIENT_STOCK] txn_id={txn_id} | error_code={error_code or 'INSUFFICIENT_STOCK'} | độ_trễ={latency_ms}ms | chi_tiết={resp_text}",
                )
                session.close()
                return False

            if resp.status_code in (400, 401):
                update_queue_status(queue_file, txn_id, "TU_CHOI", f"HTTP {resp.status_code}", latency_ms, attempt - 1)
                write_log(
                    log_file,
                    f"[BỊ TỪ CHỐI NGHIỆP VỤ] txn_id={txn_id} | HTTP={resp.status_code} | độ_trễ={latency_ms}ms | chi_tiết={resp_text}",
                )
                session.close()
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
    session.close()
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
        with get_api_session(base_url, config.get("client_ip", "")) as session:
            resp = session.get(f"{base_url}/api/inventory/{p_code}", headers=headers, timeout=timeout)
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
                with get_api_session(base_url, config.get("client_ip", "")) as session:
                    r = session.get(f"{base_url}/api/transactions/{tid}", headers=headers, timeout=timeout)
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
        print("Cách chạy: python scanner.py <đường_dẫn_file_config.json> [--url http://IP_MAY_CHU:8080]")
        print("Ví dụ:     python scanner.py config_sp01.json --url http://172.23.155.222:8080")
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
    password = getpass.getpass("Đăng nhập - Mật khẩu: ")
    try:
        token = login_api(config["api_base_url"], username, password, config.get("timeout_seconds", 5), config.get("client_ip", ""))
    except RuntimeError as exc:
        print(f"[LỖI] {exc}. Không gửi giao dịch.")
        sys.exit(2)
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
                new_password = getpass.getpass(f"Mật khẩu của {new_user}: ")
                try:
                    new_token = login_api(config["api_base_url"], new_user, new_password, config.get("timeout_seconds", 5), config.get("client_ip", ""))
                except RuntimeError as exc:
                    write_log(log_file, f"[ĐỔI TÀI KHOẢN THẤT BẠI] {exc}")
                else:
                    username, password, token = new_user, new_password, new_token
                    write_log(log_file, f"Đã xác thực người dùng '{username}' tại {scan_point_id}.")
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
                "seq_no": seq_no,
                "username": username,
                "retries": 0,
                "payload": payload,
            }
            enqueue_transaction(queue_file, record)

            # Gửi qua mạng tới máy chủ
            send_with_retry(config, payload, token)


if __name__ == "__main__":
    main()
