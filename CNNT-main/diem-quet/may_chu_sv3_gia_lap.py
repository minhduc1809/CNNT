"""
Đề tài 22 - DỊCH VỤ API GIẢ LẬP THEO CSDL MYSQL CỦA SV3
Mục đích: Giúp SV2 tự chạy kiểm thử độc lập toàn bộ các ca CV01, CV02, CV03
trong khi chờ SV3 hoàn thiện dịch vụ API chính thức trên máy chủ Linux/MySQL.

Hỗ trợ các endpoint:
  - POST /api/login                   : Đăng nhập lấy Bearer token
  - POST /api/transactions            : Ghi giao dịch, trừ/cộng tồn kho, chống trùng
  - GET  /api/transactions/{txn_id}   : Đọc lại chi tiết giao dịch (CV02)
  - GET  /api/inventory/{product_id}  : Tra cứu tồn kho hiện tại

Chạy:
  python may_chu_sv3_gia_lap.py [--port 8080]
"""

import argparse
import json
import os
import sys
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

# Dữ liệu mô phỏng CSDL MySQL `smart_warehouse` của SV3
# Khởi tạo 100 sản phẩm với số lượng mẫu giống 02_insert_sample_data.sql
LOCK = threading.Lock()
INVENTORY = {f"SP{i:03d}": 10 + (i % 20) for i in range(1, 101)}
TRANSACTIONS = {}
USERS = {
    "admin_demo": {"role": "admin", "full_name": "Quản trị viên mẫu"},
    "nhanvien_demo": {"role": "employee", "full_name": "Nhân viên mẫu"},
    "nv01": {"role": "employee", "full_name": "Nhân viên 01"},
    "thukho_demo": {"role": "warehouse", "full_name": "Thủ kho mẫu"},
}


class SV3MockHandler(BaseHTTPRequestHandler):
    server_version = "SV3-MySQL-APIServer/1.0"

    def log_message(self, format, *args):
        # In log ngắn gọn
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] [SV3-API] {args[0]} -> {args[1]}")

    def send_json(self, status_code: int, data: dict):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json_body(self) -> dict:
        content_len = int(self.headers.get("Content-Length") or 0)
        if not content_len:
            return {}
        try:
            return json.loads(self.rfile.read(content_len).decode("utf-8"))
        except Exception:
            return {}

    def get_auth_user(self):
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:].strip()
            # Giả lập token hợp lệ nếu có dạng token-<username> hoặc chuỗi bất kỳ
            return token.replace("token-", "") if token else "nhanvien_demo"
        return "nhanvien_demo"

    # ---------------- POST ----------------
    def do_POST(self):
        path = urlparse(self.path).path

        # 1. Endpoint Đăng nhập
        if path == "/api/login":
            body = self.read_json_body()
            username = body.get("username", "nhanvien_demo")
            self.send_json(200, {
                "status": "OK",
                "token": f"token-{username}",
                "username": username,
                "role": USERS.get(username, {}).get("role", "employee"),
                "message": "Đăng nhập thành công vào dịch vụ kho SV3"
            })
            return

        # 2. Endpoint Ghi giao dịch (gọi thủ tục sp_warehouse_transaction)
        if path == "/api/transactions":
            body = self.read_json_body()
            # Hỗ trợ cả tên trường của SV1 và SV3
            txn_id = body.get("transaction_id") or body.get("txn_id")
            product_id = body.get("product_id") or body.get("product_code")
            t_type = (body.get("transaction_type") or body.get("txn_type") or "").upper()
            qty = body.get("quantity")
            scan_point_id = body.get("scan_point_id", "SP01")
            user_id = self.get_auth_user()

            # Chuẩn hoá loại giao dịch
            if t_type in ("NHAP", "IMPORT"):
                action = "IMPORT"
            elif t_type in ("XUAT", "EXPORT"):
                action = "EXPORT"
            else:
                self.send_json(400, {
                    "status": "REJECTED",
                    "error_code": "INVALID_TYPE",
                    "message": "Loại giao dịch phải là NHAP/IMPORT hoặc XUAT/EXPORT"
                })
                return

            if not txn_id or not product_id or qty is None or int(qty) <= 0:
                self.send_json(400, {
                    "status": "REJECTED",
                    "error_code": "INVALID_INPUT",
                    "message": "Dữ liệu không hợp lệ hoặc thiếu tham số bắt buộc"
                })
                return

            qty = int(qty)

            with LOCK:
                # 1. Kiểm tra chống trùng transaction_id
                if txn_id in TRANSACTIONS:
                    old = TRANSACTIONS[txn_id]
                    self.send_json(409, {
                        "status": "REJECTED",
                        "error_code": "DUPLICATE_TXN",
                        "message": f"Mã giao dịch {txn_id} đã tồn tại trong CSDL smart_warehouse!",
                        "original": old
                    })
                    return

                # 2. Kiểm tra sản phẩm tồn tại
                if product_id not in INVENTORY:
                    self.send_json(404, {
                        "status": "REJECTED",
                        "error_code": "PRODUCT_NOT_FOUND",
                        "message": f"Không tìm thấy sản phẩm {product_id} trong Inventory"
                    })
                    return

                current_stock = INVENTORY[product_id]

                # 3. Kiểm tra đủ tồn kho khi xuất
                if action == "EXPORT" and current_stock < qty:
                    self.send_json(422, {
                        "status": "REJECTED",
                        "error_code": "INSUFFICIENT_STOCK",
                        "message": f"Tồn kho không đủ để xuất ({current_stock} < {qty})"
                    })
                    return

                # 4. Cập nhật tồn kho và lưu giao dịch (tương đương commit transaction)
                if action == "IMPORT":
                    new_stock = current_stock + qty
                else:
                    new_stock = current_stock - qty

                INVENTORY[product_id] = new_stock
                server_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                record = {
                    "transaction_id": txn_id,
                    "txn_id": txn_id,
                    "product_id": product_id,
                    "product_code": product_id,
                    "transaction_type": action,
                    "txn_type": "NHAP" if action == "IMPORT" else "XUAT",
                    "quantity": qty,
                    "user_id": user_id,
                    "username": user_id,
                    "scan_point_id": scan_point_id,
                    "stock_after": new_stock,
                    "server_time": server_time,
                    "transaction_time": server_time,
                }
                TRANSACTIONS[txn_id] = record

            # Trả về 201 Created
            self.send_json(201, {
                "status": "OK",
                "message": "Ghi giao dịch thành công vào MySQL smart_warehouse",
                "transaction_id": txn_id,
                "txn_id": txn_id,
                "product_id": product_id,
                "stock_after": new_stock,
                "server_time": server_time
            })
            return

        self.send_json(404, {"status": "ERROR", "message": "Không tìm thấy endpoint POST"})

    # ---------------- GET ----------------
    def do_GET(self):
        path = urlparse(self.path).path

        # 1. Đọc lại giao dịch theo ID (CV02)
        if path.startswith("/api/transactions/"):
            txn_id = path.split("/api/transactions/")[-1].strip()
            with LOCK:
                if txn_id in TRANSACTIONS:
                    self.send_json(200, {
                        "status": "OK",
                        "data": TRANSACTIONS[txn_id],
                        **TRANSACTIONS[txn_id]
                    })
                    return
            self.send_json(404, {
                "status": "REJECTED",
                "error_code": "TXN_NOT_FOUND",
                "message": f"Chưa có giao dịch {txn_id} trên máy chủ"
            })
            return

        # 2. Đọc tồn kho theo product_id
        if path.startswith("/api/inventory/"):
            prod_id = path.split("/api/inventory/")[-1].strip().upper()
            with LOCK:
                if prod_id in INVENTORY:
                    self.send_json(200, {
                        "status": "OK",
                        "product_id": prod_id,
                        "product_code": prod_id,
                        "quantity": INVENTORY[prod_id]
                    })
                    return
            self.send_json(404, {
                "status": "REJECTED",
                "error_code": "PRODUCT_NOT_FOUND",
                "message": f"Không tìm thấy sản phẩm {prod_id}"
            })
            return

        self.send_json(404, {"status": "ERROR", "message": "Không tìm thấy endpoint GET"})


def main():
    parser = argparse.ArgumentParser(description="Máy chủ giả lập dịch vụ API MySQL của SV3")
    parser.add_argument("--host", default="0.0.0.0", help="Địa chỉ lắng nghe")
    parser.add_argument("--port", type=int, default=8080, help="Cổng lắng nghe (mặc định 8080)")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), SV3MockHandler)
    print("=" * 65)
    print(f" MÁY CHỦ API GIẢ LẬP SV3 (CSDL MYSQL smart_warehouse) ĐÃ KHỞI CHẠY")
    print(f" Địa chỉ: http://127.0.0.1:{args.port}")
    print(" Nhấn Ctrl+C để dừng")
    print("=" * 65)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng máy chủ.")


if __name__ == "__main__":
    main()
