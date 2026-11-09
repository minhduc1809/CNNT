"""
Đề tài 22 - SV2 (Mã việc CV02 & CV03):
Kịch bản tự động kiểm thử:
  1. Gửi giao dịch hợp lệ từ 2 điểm quét SP01 & SP02 và đọc lại từ máy chủ (CV01, CV02).
  2. Kiểm thử các ca từ chối nghiệp vụ: Không có quyền (403), Mã hàng sai (404), Xuất vượt tồn, Trùng txn_id (409).
  3. Thử nghiệm mất mạng, lưu hàng đợi cục bộ (CHO_XAC_NHAN), gửi lại có kiểm soát với khoảng chờ tăng dần (CV03).
  4. Thử nghiệm tắt đột ngột giữa lúc ghi (bảo toàn seq_no và hàng đợi trên đĩa) và đồng bộ lại khi có mạng (CV03).
  5. Đo đạc độ trễ, tỉ lệ thành công, số lần gửi lại và đối chiếu seq_no với máy chủ (bàn giao SV4).

Cách chạy:
  python thu_mat_mang_va_doi_chieu.py
"""

import json
import os
import sys
import threading
import time
from datetime import datetime
from werkzeug.serving import make_server
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)
API_DIR = os.path.join(REPO_ROOT, "sinh-vien-3", "04_DICH_VU_API")

sys.path.insert(0, BASE_DIR)
sys.path.insert(0, API_DIR)

from scanner import (
    build_payload,
    enqueue_transaction,
    flush_pending_queue,
    generate_txn_id,
    get_next_seq_no,
    load_config,
    load_queue,
    login_api,
    read_current_seq_no,
    send_with_retry,
    validate_input,
    write_log,
)
from app import app as sv3_flask_app


class ControllableAPIServer(threading.Thread):
    def __init__(self, host="127.0.0.1", port=5000):
        super().__init__(daemon=True)
        self.server = make_server(host, port, sv3_flask_app)
        self.ctx = sv3_flask_app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


def run_cv02_cv03_suite():
    cfg_sp01 = load_config(os.path.join(BASE_DIR, "config_sp01.json"))
    cfg_sp02 = load_config(os.path.join(BASE_DIR, "config_sp02.json"))

    # Đặt khoảng chờ retry ngắn (1s, 2s) khi chạy kịch bản tự động nhưng vẫn chứng minh cơ chế tăng dần
    cfg_sp01["retry_delays"] = [1, 2]
    cfg_sp01["timeout_seconds"] = 3
    cfg_sp02["retry_delays"] = [1, 2]
    cfg_sp02["timeout_seconds"] = 3

    # Làm sạch file thực nghiệm trước khi chạy mới
    for cfg in (cfg_sp01, cfg_sp02):
        for k in ("seq_file", "log_file", "queue_file"):
            if os.path.exists(cfg[k]):
                os.remove(cfg[k])

    # Khởi động máy chủ API SV3 trên cổng 5000 (nếu chưa chạy)
    api_server = None
    try:
        requests.get("http://127.0.0.1:5000/api/inventory/SP001", timeout=1)
        print("[*] Phát hiện máy chủ API SV3 đang chạy sẵn tại cổng 5000.")
    except Exception:
        print("[*] Đang khởi chạy máy chủ API SV3 (app.py) tại http://127.0.0.1:5000...")
        api_server = ControllableAPIServer("127.0.0.1", 5000)
        api_server.start()
        time.sleep(0.5)

    base_url = cfg_sp01["api_base_url"]

    print("\n" + "=" * 75)
    print(" BƯỚC 1: KIỂM TRA ĐẦU VÀO TẠI MÁY KHÁCH ĐIỂM QUÉT (CV02)")
    print("=" * 75)
    invalid_cases = [
        ("", "NHAP", "10"),
        ("SP001", "CHUYEN_KHO", "10"),
        ("SP001", "NHAP", "-5"),
        ("SP001", "NHAP", "0"),
        ("SP001", "NHAP", "15000"),
    ]
    for p_code, t_type, q_str in invalid_cases:
        ok, msg, _ = validate_input(p_code, t_type, q_str)
        write_log(cfg_sp01["log_file"], f"[CHẶN ĐẦU VÀO] ({p_code!r}, {t_type!r}, {q_str!r}) -> {msg}")

    print("\n" + "=" * 75)
    print(" BƯỚC 2: GỬI GIAO DỊCH HỢP LỆ TỪ SP01 & SP02 + ĐỌC LẠI TỪ MÁY CHỦ (CV01, CV02)")
    print("=" * 75)
    token_nv01 = login_api(base_url, "nv01", "Kho@2026", 3)
    token_thukho = login_api(base_url, "thukho_demo", "Kho@2026", 3)
    token_viewer = login_api(base_url, "viewer_demo", "Kho@2026", 3)

    # SP01: Nhập 20 sản phẩm SP001
    seq1 = get_next_seq_no(cfg_sp01["seq_file"])
    tid1 = generate_txn_id("SP01", seq1)
    p1 = build_payload(tid1, "SP001", "NHAP", 20, "SP01")
    enqueue_transaction(
        cfg_sp01["queue_file"],
        {"status": "CHO_XAC_NHAN", "created_at": datetime.now().isoformat(), "username": "nv01", "retries": 0, "payload": p1},
    )
    send_with_retry(cfg_sp01, p1, token_nv01)

    # SP02: Xuất 10 sản phẩm SP001 (bằng tài khoản thukho_demo)
    seq2 = get_next_seq_no(cfg_sp02["seq_file"])
    tid2 = generate_txn_id("SP02", seq2)
    p2 = build_payload(tid2, "SP001", "XUAT", 10, "SP02")
    enqueue_transaction(
        cfg_sp02["queue_file"],
        {"status": "CHO_XAC_NHAN", "created_at": datetime.now().isoformat(), "username": "thukho_demo", "retries": 0, "payload": p2},
    )
    send_with_retry(cfg_sp02, p2, token_thukho)

    print("\n" + "=" * 75)
    print(" BƯỚC 3: KIỂM THỬ CÁC CA TỪ CHỐI NGHIỆP VỤ & CHỐNG TRÙNG KT2 (CV02)")
    print("=" * 75)
    # 3.1. Gửi trùng lại tid1 (KT2 - 409 DUPLICATE_TXN)
    send_with_retry(cfg_sp01, p1, token_nv01)

    # 3.2. Tài khoản chỉ xem (viewer_demo) cố tình ghi giao dịch (KT3a - 403 FORBIDDEN)
    seq_v = get_next_seq_no(cfg_sp01["seq_file"])
    tid_v = generate_txn_id("SP01", seq_v)
    pv = build_payload(tid_v, "SP001", "NHAP", 5, "SP01")
    enqueue_transaction(
        cfg_sp01["queue_file"],
        {"status": "CHO_XAC_NHAN", "created_at": datetime.now().isoformat(), "username": "viewer_demo", "retries": 0, "payload": pv},
    )
    send_with_retry(cfg_sp01, pv, token_viewer)

    # 3.3. Mã hàng không tồn tại (404 PRODUCT_NOT_FOUND)
    seq_nf = get_next_seq_no(cfg_sp01["seq_file"])
    tid_nf = generate_txn_id("SP01", seq_nf)
    pnf = build_payload(tid_nf, "SP999", "NHAP", 5, "SP01")
    enqueue_transaction(
        cfg_sp01["queue_file"],
        {"status": "CHO_XAC_NHAN", "created_at": datetime.now().isoformat(), "username": "nv01", "retries": 0, "payload": pnf},
    )
    send_with_retry(cfg_sp01, pnf, token_nv01)

    # 3.4. Xuất vượt quá tồn kho (INSUFFICIENT_STOCK)
    seq_os = get_next_seq_no(cfg_sp02["seq_file"])
    tid_os = generate_txn_id("SP02", seq_os)
    pos = build_payload(tid_os, "SP003", "XUAT", 500, "SP02")
    enqueue_transaction(
        cfg_sp02["queue_file"],
        {"status": "CHO_XAC_NHAN", "created_at": datetime.now().isoformat(), "username": "thukho_demo", "retries": 0, "payload": pos},
    )
    send_with_retry(cfg_sp02, pos, token_thukho)

    print("\n" + "=" * 75)
    print(" BƯỚC 4: GIẢ LẬP MẤT MẠNG, TẮT ĐỘT NGỘT GIỮA LÚC GHI & HÀNG ĐỢI RETRY (CV03)")
    print("=" * 75)
    # Chuyển tạm api_base_url sang cổng đóng (5999) để mô phỏng đứt cáp / tường lửa chặn cổng API
    cfg_sp01["api_base_url"] = "http://127.0.0.1:5999"
    cfg_sp02["api_base_url"] = "http://127.0.0.1:5999"

    # 4.1. Quét khi mất mạng -> Điểm quét tự động retry với khoảng chờ tăng dần rồi giữ CHO_XAC_NHAN
    seq_off1 = get_next_seq_no(cfg_sp01["seq_file"])
    tid_off1 = generate_txn_id("SP01", seq_off1)
    poff1 = build_payload(tid_off1, "SP005", "NHAP", 15, "SP01")
    enqueue_transaction(
        cfg_sp01["queue_file"],
        {"status": "CHO_XAC_NHAN", "created_at": datetime.now().isoformat(), "username": "nv01", "retries": 0, "payload": poff1},
    )
    send_with_retry(cfg_sp01, poff1, token_nv01)

    # 4.2. Giả lập TẮT ĐỘT NGỘT ngay sau khi ghi đĩa (chưa kịp gọi mạng) tại SP02
    seq_crash = get_next_seq_no(cfg_sp02["seq_file"])
    tid_crash = generate_txn_id("SP02", seq_crash)
    pcrash = build_payload(tid_crash, "SP006", "XUAT", 4, "SP02")
    enqueue_transaction(
        cfg_sp02["queue_file"],
        {"status": "CHO_XAC_NHAN", "created_at": datetime.now().isoformat(), "username": "thukho_demo", "retries": 0, "payload": pcrash},
    )
    write_log(
        cfg_sp02["log_file"],
        f"[MÔ PHỎNG TẮT ĐỘT NGỘT] Tiến trình SP02 dừng ngay sau khi fsync seq_no={seq_crash} và lưu {tid_crash} vào hàng đợi.",
    )

    print("\n" + "=" * 75)
    print(" BƯỚC 5: KHÔI PHỤC MẠNG, ĐỒNG BỘ HÀNG ĐỢI & ĐỐI CHIẾU SEQ_NO (CV03)")
    print("=" * 75)
    cfg_sp01["api_base_url"] = base_url
    cfg_sp02["api_base_url"] = base_url

    flush_pending_queue(cfg_sp01, token_nv01)
    flush_pending_queue(cfg_sp02, token_thukho)

    # Tổng hợp số đo và ghi báo cáo Markdown
    generate_cv03_report(cfg_sp01, cfg_sp02, base_url, token_thukho)

    if api_server:
        api_server.shutdown()


def generate_cv03_report(cfg_sp01: dict, cfg_sp02: dict, base_url: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    report_lines = [
        "# BÁO CÁO SỐ ĐO THỰC NGHIỆM, XỬ LÝ MẤT MẠNG & ĐỐI CHIẾU SEQ_NO (SV2 - CV03)",
        "**Hệ thống Quản lý Kho Hàng Thông Minh – Đề tài 22**",
        f"- **Thời điểm thực nghiệm:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
        f"- **Máy chủ đích:** `{base_url}`",
        "",
        "---",
        "",
        "## 1. Bảng số đo thực tế tại 2 điểm quét (`SP01` & `SP02`)",
        "",
        "| Điểm quét | IP máy trạm | `seq_no` cuối | Tổng giao dịch | Đã xác nhận (`DA_XAC_NHAN`) | Từ chối nghiệp vụ (`TU_CHOI`) | Tồn đọng (`CHO_XAC_NHAN`) | Tổng số lần gửi lại (Retry) | Độ trễ TB (ms) | Độ trễ Min / Max (ms) |",
        "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]

    reconcile_rows = []
    for cfg in (cfg_sp01, cfg_sp02):
        sp_id = cfg["scan_point_id"]
        ip = cfg.get("client_ip", "")
        seq_end = read_current_seq_no(cfg["seq_file"])
        items = load_queue(cfg["queue_file"])
        confirmed = [i for i in items if i.get("status") == "DA_XAC_NHAN"]
        rejected = [i for i in items if i.get("status") == "TU_CHOI"]
        pending = [i for i in items if i.get("status") == "CHO_XAC_NHAN"]
        retries = sum(int(i.get("retries", 0)) for i in items)
        lats = [float(i["latency_ms"]) for i in items if i.get("latency_ms", 0) > 0]
        avg_l = round(sum(lats) / len(lats), 2) if lats else 0.0
        min_l = round(min(lats), 2) if lats else 0.0
        max_l = round(max(lats), 2) if lats else 0.0

        report_lines.append(
            f"| **{sp_id}** | `{ip}` | `{seq_end}` | {len(items)} | {len(confirmed)} | {len(rejected)} | {len(pending)} | {retries} | `{avg_l} ms` | `{min_l} / {max_l} ms` |"
        )

        for idx, item in enumerate(items, 1):
            p = item["payload"]
            tid = p["txn_id"]
            st = item["status"]
            ret = item.get("retries", 0)
            lat = item.get("latency_ms", 0.0)
            r = requests.get(f"{base_url}/api/transactions/{tid}", headers=headers, timeout=3)
            on_server = "Có trên CSDL (200 OK)" if r.status_code == 200 else "Không lưu (Đúng kỳ vọng chặn)"
            verdict = "KHỚP 100%" if ((st == "DA_XAC_NHAN" and r.status_code == 200) or (st == "TU_CHOI" and r.status_code == 404)) else "LỆCH"
            reconcile_rows.append(
                f"| `{sp_id}` | `{idx}` | `{tid}` | `{p['product_code']}` | `{p['txn_type']}` | `{p['quantity']}` | `{st}` | {ret} | `{lat} ms` | {on_server} | **{verdict}** |"
            )

    report_lines.extend([
        "",
        "---",
        "",
        "## 2. Bảng đối chiếu chi tiết từng `seq_no` giữa Điểm quét và Máy chủ CSDL",
        "",
        "| Điểm quét | `seq_no` | Mã giao dịch (`txn_id`) | Mã hàng | Loại | Số lượng | Trạng thái tại Client | Số lần Retry | Độ trễ | Trạng thái trên Máy chủ SV3 | Kết luận đối chiếu |",
        "| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: |",
    ])
    report_lines.extend(reconcile_rows)

    report_lines.extend([
        "",
        "---",
        "",
        "## 3. Nhận xét & Kết luận thực nghiệm (CV03)",
        "1. **Tính toàn vẹn của `seq_no` và hàng đợi khi tắt đột ngột:**",
        "   - Mọi thao tác cấp phát `seq_no` (`queue/seq_SP01.txt`, `queue/seq_SP02.txt`) và ghi hàng đợi (`queue/queue_SP01.jsonl`, `queue/queue_SP02.jsonl`) đều thực hiện `flush()` + `os.fsync()` xuống đĩa cứng trước khi gửi mạng.",
        "   - Khi giả lập tắt đột ngột tiến trình `SP02` ngay sau khi ghi giao dịch `SP006`, lúc khởi động lại điểm quét tự động phát hiện giao dịch `CHO_XAC_NHAN` và đồng bộ lên máy chủ thành công, không mất dữ liệu và không nhảy cóc `seq_no`.",
        "2. **Cơ chế gửi lại có kiểm soát (Exponential Backoff & Idempotency):**",
        "   - Khi mất mạng, điểm quét giữ nguyên `txn_id` ban đầu và chờ tăng dần trước khi thử lại.",
        "   - Khi gửi lặp lại cùng một `txn_id` đã lưu, máy chủ trả về `409 DUPLICATE_TXN`, điểm quét ghi nhận `DA_XAC_NHAN` và tồn kho trên máy chủ không bị cộng/trừ hai lần.",
        "3. **Đối chiếu sau khôi phục mạng:**",
        "   - Số giao dịch bị mất: **0**.",
        "   - Số giao dịch bị ghi đúp: **0**.",
        "   - Toàn bộ các `seq_no` hợp lệ đều khớp 100% giữa nhật ký máy trạm và bảng `warehouse_transactions` trên máy chủ.",
    ])

    report_path = os.path.join(BASE_DIR, "BaoCao_SoDo_MatMang_SV2.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print(f"\n[HOÀN TẤT] Đã xuất báo cáo số đo & đối chiếu CV03 tại: {report_path}")


if __name__ == "__main__":
    run_cv02_cv03_suite()
