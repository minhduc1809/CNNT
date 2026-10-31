"""Điểm quét giả lập - khung ban đầu (CV01).

Chạy:
    python scanner.py config_scan01.json
    python scanner.py config_scan02.json     (mở ở cửa sổ terminal thứ hai)

Khung này đã làm:
    - đọc file cấu hình của điểm quét
    - nhập mã hàng, loại giao dịch, số lượng, người thực hiện
    - kiểm tra đầu vào, báo lỗi bằng tiếng Việt (bước C)
    - sinh txn_id và seq_no cho giao dịch hợp lệ
    - in giao dịch ra màn hình dưới dạng JSON

Chưa làm (các bước sau trong kế hoạch):
    - gửi lên máy chủ, hiện trạng thái      (bước D)
    - hàng đợi và gửi lại khi mất mạng      (bước E)
"""
import json
import sys
import uuid
from datetime import datetime

CAC_LOAI = ("NHAP", "XUAT")


def load_config(path):
    """Đọc file cấu hình; thoát với thông báo rõ ràng nếu file lỗi."""
    try:
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
    except FileNotFoundError:
        sys.exit(f"Không tìm thấy file cấu hình: {path}")
    except json.JSONDecodeError as e:
        sys.exit(f"File cấu hình {path} không phải JSON hợp lệ: {e}")
    if not cfg.get("scan_point_id"):
        sys.exit(f"File cấu hình {path} thiếu trường scan_point_id")
    return cfg


def new_txn_id():
    """Mã giao dịch duy nhất, do máy khách sinh.
    Tạm dùng UUID; đổi nếu nhóm chốt định dạng khác ở Cổng 1."""
    return str(uuid.uuid4())


def read_input():
    """Hỏi người dùng 4 thông tin. Trả về None nếu người dùng muốn thoát."""
    product_id = input("Mã hàng (q để thoát): ").strip()
    if product_id.lower() == "q":
        return None
    txn_type = input(f"Loại giao dịch ({'/'.join(CAC_LOAI)}): ").strip().upper()
    quantity = input("Số lượng: ").strip()
    user = input("Người thực hiện: ").strip()
    return {
        "product_id": product_id,
        "txn_type": txn_type,
        "quantity": quantity,   # chuỗi thô; validate() kiểm tra và đổi sang số nguyên
        "user": user,
    }


def validate(raw):
    """Kiểm tra đầu vào ở máy khách. Trả về (danh sách lỗi, số lượng đã đổi sang int).
    Máy chủ vẫn kiểm tra lại: máy khách không phải lớp bảo vệ duy nhất."""
    errors = []
    if not raw["product_id"]:
        errors.append("Mã hàng không được để trống.")
    if raw["txn_type"] not in CAC_LOAI:
        errors.append(f"Loại giao dịch phải là {' hoặc '.join(CAC_LOAI)}.")
    qty_text = raw["quantity"]
    qty = None
    if not (qty_text.isascii() and qty_text.isdigit()):
        errors.append("Số lượng phải là số nguyên dương (không chữ, không dấu, không số thập phân).")
    else:
        qty = int(qty_text)
        if qty <= 0:
            errors.append("Số lượng phải lớn hơn 0.")
            qty = None
    if not raw["user"]:
        errors.append("Người thực hiện không được để trống.")
    return errors, qty


def build_txn(cfg, seq_no, raw):
    """Ghép thông tin nhập vào thành một giao dịch.
    Tên trường theo sơ đồ dữ liệu; đổi lại nếu giao ước API của SV1 khác."""
    return {
        "txn_id": new_txn_id(),
        "product_id": raw["product_id"],
        "txn_type": raw["txn_type"],
        "quantity": raw["quantity"],   # đã là số nguyên sau bước kiểm tra
        "user": raw["user"],
        "scan_point_id": cfg["scan_point_id"],
        "seq_no": seq_no,
        "client_time": datetime.now().isoformat(timespec="seconds"),
    }


def main():
    if len(sys.argv) != 2:
        sys.exit("Cách dùng: python scanner.py config_scan01.json")
    cfg = load_config(sys.argv[1])
    seq_no = 0   # tạm: chạy lại sẽ về 0. Bước E sẽ lưu số này vào file.
    print(f"=== {cfg.get('name', cfg['scan_point_id'])} ({cfg['scan_point_id']}) ===")
    try:
        while True:
            raw = read_input()
            if raw is None:
                break
            errors, qty = validate(raw)
            if errors:
                print("Dữ liệu không hợp lệ, giao dịch KHÔNG được tạo:")
                for e in errors:
                    print(f"  - {e}")
                print()
                continue
            raw["quantity"] = qty
            seq_no += 1   # chỉ tăng khi giao dịch hợp lệ
            txn = build_txn(cfg, seq_no, raw)
            # TODO bước D: gửi lên máy chủ và hiển thị trạng thái
            print(json.dumps(txn, ensure_ascii=False, indent=2))
            print()
    except (EOFError, KeyboardInterrupt):
        print()
    print("Đã thoát.")


if __name__ == "__main__":
    main()