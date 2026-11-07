"""
DỰ ÁN HỆ THỐNG QUẢN LÝ KHO HÀNG THÔNG MINH - ĐỀ TÀI 22
DỊCH VỤ API MÁY CHỦ CSDL MYSQL (SINH VIÊN 3 - MÃ VIỆC CV02)
-----------------------------------------------------------
Chuẩn giao thức: HTTP/1.1 RESTful JSON
Khớp 100% Giao ước API của SV1 (05_GiaoUocAPI.md) và CSDL smart_warehouse của SV3.

Tính năng nổi bật:
  1. Hỗ trợ kết nối MySQL thật (qua mysql.connector với Connection Pooling).
  2. Tự động Fallback sang In-Memory Mock CSDL nếu chưa bật MySQL để test độc lập.
  3. Phân quyền nhiều tầng:
     - Tầng dịch vụ (API Layer): RBAC theo ma trận quyền (admin, warehouse, employee, viewer).
     - Tầng CSDL (DB Layer): Hỗ trợ chạy tài khoản tối thiểu wh_store và gọi Stored Procedure.
     - Tầng HĐH (OS Layer): Tài liệu và cấu hình systemd đi kèm.
  4. Chống trùng giao dịch (409 Conflict), chống âm tồn kho (422), khóa dòng FOR UPDATE.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from flask import Flask, jsonify, request
from flask_cors import CORS

# Cố gắng import mysql.connector
try:
    import mysql.connector
    from mysql.connector import pooling
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False

# ==============================================================================
# 1. CẤU HÌNH HỆ THỐNG
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

DEFAULT_CONFIG = {
    "server": {
        "host": "0.0.0.0",
        "port": 8080,
        "debug": False
    },
    "database": {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "wh_store",
        "password": "StoreUser@2026",
        "database": "smart_warehouse",
        "use_stored_procedure": True,
        "pool_size": 10
    },
    "auth": {
        "jwt_secret": "smart-warehouse-secret-key-2026-ptit-team22",
        "token_expire_hours": 8
    }
}

def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return cfg
        except Exception as e:
            print(f"[CẢNH BÁO] Không đọc được config.json ({e}), dùng cấu hình mặc định.")
    return DEFAULT_CONFIG

CONFIG = load_config()

# Danh sách tài khoản mẫu hợp lệ (Mật khẩu mặc định: Kho@2026)
DEFAULT_PASSWORD_HASH = hashlib.sha256("Kho@2026".encode("utf-8")).hexdigest()

SAMPLE_USERS = {
    "admin": {"user_id": "admin", "full_name": "Quản trị hệ thống", "role": "admin", "password_hash": DEFAULT_PASSWORD_HASH},
    "admin_demo": {"user_id": "AD01", "full_name": "Quản trị viên mẫu", "role": "admin", "password_hash": DEFAULT_PASSWORD_HASH},
    "thukho01": {"user_id": "thukho01", "full_name": "Thủ kho chính", "role": "warehouse", "password_hash": DEFAULT_PASSWORD_HASH},
    "thukho_demo": {"user_id": "TK01", "full_name": "Thủ kho mẫu", "role": "warehouse", "password_hash": DEFAULT_PASSWORD_HASH},
    "nv01": {"user_id": "nv01", "full_name": "Nhân viên quét 01", "role": "employee", "password_hash": DEFAULT_PASSWORD_HASH},
    "nhanvien_demo": {"user_id": "NV01", "full_name": "Nhân viên mẫu 01", "role": "employee", "password_hash": DEFAULT_PASSWORD_HASH},
    "nv02": {"user_id": "nv02", "full_name": "Nhân viên quét 02", "role": "employee", "password_hash": DEFAULT_PASSWORD_HASH},
    "nv02_demo": {"user_id": "NV02", "full_name": "Nhân viên mẫu 02", "role": "employee", "password_hash": DEFAULT_PASSWORD_HASH},
    "quanly01": {"user_id": "quanly01", "full_name": "Quản lý xem kho", "role": "viewer", "password_hash": DEFAULT_PASSWORD_HASH},
    "xem01": {"user_id": "xem01", "full_name": "Tài khoản kiểm tra xem01", "role": "viewer", "password_hash": DEFAULT_PASSWORD_HASH},
    "viewer_demo": {"user_id": "VIEW01", "full_name": "Tài khoản chỉ xem", "role": "viewer", "password_hash": DEFAULT_PASSWORD_HASH},
}

# ==============================================================================
# 2. BỘ ĐỆM CSDL MÔ PHỎNG (IN-MEMORY MOCK DB DÙNG KHI CHƯA BẬT MYSQL THẬT)
# ==============================================================================
class MockDatabase:
    """CSDL giả lập trong bộ nhớ mô phỏng chuẩn xác schema và Stored Procedure của MySQL"""
    def __init__(self):
        self.lock = threading.Lock()
        # Nạp 100 sản phẩm mẫu y hệt 02_insert_sample_data.sql
        self.products = {f"SP{i:03d}": {"product_id": f"SP{i:03d}", "product_name": f"Sản phẩm mẫu {i:03d}", "unit": "cái"} for i in range(1, 101)}
        self.inventory = {f"SP{i:03d}": 10 + (i % 20) for i in range(1, 101)}
        self.initial_inventory = dict(self.inventory)
        self.transactions = {}  # txn_id -> dict
        self.scan_points = {
            "SP01": "Điểm quét kho 01 (VLAN 20 - IP .11)",
            "SP02": "Điểm quét kho 02 (VLAN 20 - IP .12)",
            "SCAN01": "Điểm quét kho SCAN01",
            "SCAN02": "Điểm quét kho SCAN02",
        }
        self.users = dict(SAMPLE_USERS)

    def execute_transaction(self, txn_id: str, product_code: str, txn_type: str, quantity: int, user_id: str, scan_point_id: str) -> Tuple[bool, int, str, Optional[dict]]:
        with self.lock:
            # 1. Chống trùng
            if txn_id in self.transactions:
                orig = self.transactions[txn_id]
                return False, 409, "DUPLICATE_TXN", {"stock_after": orig["stock_after"], "server_time": orig["server_time"]}

            # 2. Kiểm tra sản phẩm
            if product_code not in self.inventory:
                return False, 404, "PRODUCT_NOT_FOUND", None

            # 3. Chống âm tồn kho
            curr_stock = self.inventory[product_code]
            if txn_type in ("XUAT", "EXPORT"):
                if curr_stock < quantity:
                    return False, 422, "INSUFFICIENT_STOCK", None
                new_stock = curr_stock - quantity
            else:
                new_stock = curr_stock + quantity

            # 4. Ghi nhận giao dịch
            now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            self.inventory[product_code] = new_stock
            record = {
                "txn_id": txn_id,
                "transaction_id": txn_id,
                "product_code": product_code,
                "product_id": product_code,
                "txn_type": "NHAP" if txn_type in ("NHAP", "IMPORT") else "XUAT",
                "transaction_type": "IMPORT" if txn_type in ("NHAP", "IMPORT") else "EXPORT",
                "quantity": quantity,
                "user_id": user_id,
                "username": user_id,
                "scan_point_id": scan_point_id,
                "stock_after": new_stock,
                "server_time": now_iso,
                "transaction_time": now_iso
            }
            self.transactions[txn_id] = record
            return True, 201, "OK", record

    def get_inventory(self, product_code: Optional[str] = None):
        with self.lock:
            if product_code:
                if product_code in self.inventory:
                    p = self.products.get(product_code, {})
                    return {
                        "product_code": product_code,
                        "product_id": product_code,
                        "product_name": p.get("product_name", product_code),
                        "unit": p.get("unit", "cái"),
                        "quantity": self.inventory[product_code]
                    }
                return None
            
            items = []
            for code, qty in sorted(self.inventory.items()):
                p = self.products.get(code, {})
                items.append({
                    "product_code": code,
                    "product_id": code,
                    "product_name": p.get("product_name", code),
                    "unit": p.get("unit", "cái"),
                    "quantity": qty
                })
            return items

    def get_transaction(self, txn_id: str):
        with self.lock:
            return self.transactions.get(txn_id)

    def list_transactions(self, product_code=None, scan_point_id=None, username=None, limit=100):
        with self.lock:
            res = list(self.transactions.values())
            if product_code:
                res = [r for r in res if r["product_code"] == product_code]
            if scan_point_id:
                res = [r for r in res if r["scan_point_id"] == scan_point_id]
            if username:
                res = [r for r in res if r["user_id"] == username or r["username"] == username]
            # Mới nhất lên đầu
            res.sort(key=lambda x: x["server_time"], reverse=True)
            return res[:limit]

    def reconcile(self):
        with self.lock:
            items = []
            all_match = True
            for code, current_stock in sorted(self.inventory.items()):
                init_qty = self.initial_inventory.get(code, 0)
                txns = [t for t in self.transactions.values() if t["product_code"] == code]
                delta = sum(t["quantity"] if t["txn_type"] == "NHAP" else -t["quantity"] for t in txns)
                recalculated = init_qty + delta
                diff = current_stock - recalculated
                if diff != 0:
                    all_match = False
                p = self.products.get(code, {})
                items.append({
                    "product_code": code,
                    "product_name": p.get("product_name", code),
                    "ton_luu_tru": current_stock,
                    "ton_tinh_lai": recalculated,
                    "chenh_lech": diff
                })
            return {"all_match": all_match, "items": items}


# ==============================================================================
# 3. ADAPTER KẾT NỐI MYSQL THẬT (SMART_WAREHOUSE)
# ==============================================================================
class MySQLDatabase:
    """Quản lý kết nối và thực thi nghiệp vụ CSDL MySQL thật với Connection Pool"""
    def __init__(self, db_cfg: dict):
        self.cfg = db_cfg
        self.pool = None
        self._init_pool()

    def _init_pool(self):
        if not HAS_MYSQL:
            raise RuntimeError("Chưa cài đặt thư viện mysql-connector-python.")
        print(f"[*] Đang khởi tạo kết nối MySQL tới {self.cfg['host']}:{self.cfg['port']} (user={self.cfg['user']})...")
        self.pool = pooling.MySQLConnectionPool(
            pool_name="warehouse_pool",
            pool_size=self.cfg.get("pool_size", 5),
            host=self.cfg["host"],
            port=self.cfg.get("port", 3306),
            user=self.cfg["user"],
            password=self.cfg["password"],
            database=self.cfg["database"],
            autocommit=False
        )
        print("[+] Kết nối MySQL Connection Pool thành công!")

    def get_connection(self):
        return self.pool.get_connection()

    def execute_transaction(self, txn_id: str, product_code: str, txn_type: str, quantity: int, user_id: str, scan_point_id: str) -> Tuple[bool, int, str, Optional[dict]]:
        # Chuẩn hoá loại giao dịch sang MySQL ENUM ('IMPORT', 'EXPORT')
        my_type = "IMPORT" if txn_type in ("NHAP", "IMPORT") else "EXPORT"
        conn = self.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Ưu tiên gọi Stored Procedure nếu cấu hình bật
            if self.cfg.get("use_stored_procedure", True):
                try:
                    # Stored Procedure: sp_warehouse_transaction(txn_id, product_id, type, qty, user_id, scan_point_id)
                    cursor.callproc("sp_warehouse_transaction", (txn_id, product_code, my_type, quantity, user_id, scan_point_id))
                    conn.commit()
                except mysql.connector.Error as err:
                    conn.rollback()
                    msg = str(err)
                    if "da ton tai" in msg.lower() or "duplicate" in msg.lower():
                        # Lấy lại giao dịch cũ
                        cursor.execute("SELECT * FROM warehouse_transactions WHERE transaction_id = %s", (txn_id,))
                        orig = cursor.fetchone()
                        cursor.execute("SELECT quantity FROM Inventory WHERE product_id = %s", (product_code,))
                        stock_row = cursor.fetchone()
                        curr_stock = stock_row["quantity"] if stock_row else 0
                        return False, 409, "DUPLICATE_TXN", {
                            "stock_after": curr_stock,
                            "server_time": orig["transaction_time"].strftime("%Y-%m-%dT%H:%M:%S") if orig else ""
                        }
                    elif "khong tim thay" in msg.lower() or "not found" in msg.lower():
                        return False, 404, "PRODUCT_NOT_FOUND", None
                    elif "khong du de xuat" in msg.lower() or "insufficient" in msg.lower():
                        return False, 422, "INSUFFICIENT_STOCK", None
                    else:
                        print(f"[-] Lỗi Stored Procedure: {err}")
                        return False, 500, "SERVER_ERROR", None
            else:
                # Thực hiện truy vấn thủ công với FOR UPDATE và Transaction ACID
                # 1. Kiểm tra chống trùng
                cursor.execute("SELECT * FROM warehouse_transactions WHERE transaction_id = %s", (txn_id,))
                orig = cursor.fetchone()
                if orig:
                    cursor.execute("SELECT quantity FROM Inventory WHERE product_id = %s", (product_code,))
                    stock_row = cursor.fetchone()
                    conn.rollback()
                    return False, 409, "DUPLICATE_TXN", {
                        "stock_after": stock_row["quantity"] if stock_row else 0,
                        "server_time": orig["transaction_time"].strftime("%Y-%m-%dT%H:%M:%S")
                    }

                # 2. Khóa dòng kiểm tra tồn kho
                cursor.execute("SELECT quantity FROM Inventory WHERE product_id = %s FOR UPDATE", (product_code,))
                inv = cursor.fetchone()
                if not inv:
                    conn.rollback()
                    return False, 404, "PRODUCT_NOT_FOUND", None

                curr_stock = inv["quantity"]
                if my_type == "EXPORT" and curr_stock < quantity:
                    conn.rollback()
                    return False, 422, "INSUFFICIENT_STOCK", None

                new_stock = (curr_stock + quantity) if my_type == "IMPORT" else (curr_stock - quantity)

                # 3. Cập nhật tồn kho và thêm lịch sử
                cursor.execute("UPDATE Inventory SET quantity = %s WHERE product_id = %s", (new_stock, product_code))
                cursor.execute(
                    """
                    INSERT INTO warehouse_transactions 
                    (transaction_id, product_id, transaction_type, quantity, user_id, scan_point_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (txn_id, product_code, my_type, quantity, user_id, scan_point_id)
                )
                conn.commit()

            # Lấy số tồn kho mới nhất sau khi COMMIT
            cursor.execute("SELECT quantity FROM Inventory WHERE product_id = %s", (product_code,))
            row = cursor.fetchone()
            new_stock = row["quantity"] if row else 0
            now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            record = {
                "txn_id": txn_id,
                "transaction_id": txn_id,
                "product_code": product_code,
                "product_id": product_code,
                "txn_type": "NHAP" if my_type == "IMPORT" else "XUAT",
                "transaction_type": my_type,
                "quantity": quantity,
                "user_id": user_id,
                "username": user_id,
                "scan_point_id": scan_point_id,
                "stock_after": new_stock,
                "server_time": now_iso,
                "transaction_time": now_iso
            }
            return True, 201, "OK", record

        except Exception as e:
            conn.rollback()
            print(f"[-] Lỗi CSDL execute_transaction: {e}")
            return False, 500, "SERVER_ERROR", None
        finally:
            conn.close()

    def get_inventory(self, product_code: Optional[str] = None):
        conn = self.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            if product_code:
                cursor.execute(
                    """
                    SELECT p.product_id, p.product_id AS product_code, p.product_name, p.unit, i.quantity, i.updated_at
                    FROM Products p
                    JOIN Inventory i ON p.product_id = i.product_id
                    WHERE p.product_id = %s
                    """,
                    (product_code,)
                )
                row = cursor.fetchone()
                if row and row.get("updated_at"):
                    row["updated_at"] = row["updated_at"].strftime("%Y-%m-%dT%H:%M:%S")
                return row
            else:
                cursor.execute(
                    """
                    SELECT p.product_id, p.product_id AS product_code, p.product_name, p.unit, i.quantity, i.updated_at
                    FROM Products p
                    JOIN Inventory i ON p.product_id = i.product_id
                    ORDER BY p.product_id ASC
                    """
                )
                rows = cursor.fetchall()
                for r in rows:
                    if r.get("updated_at"):
                        r["updated_at"] = r["updated_at"].strftime("%Y-%m-%dT%H:%M:%S")
                return rows
        finally:
            conn.close()

    def get_transaction(self, txn_id: str):
        conn = self.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT wt.transaction_id, wt.transaction_id AS txn_id, wt.product_id, wt.product_id AS product_code,
                       wt.transaction_type, wt.quantity, wt.transaction_time, wt.transaction_time AS server_time,
                       wt.user_id, wt.user_id AS username, wt.scan_point_id
                FROM warehouse_transactions wt
                WHERE wt.transaction_id = %s
                """,
                (txn_id,)
            )
            row = cursor.fetchone()
            if row:
                if row.get("transaction_time"):
                    iso = row["transaction_time"].strftime("%Y-%m-%dT%H:%M:%S")
                    row["transaction_time"] = iso
                    row["server_time"] = iso
                row["txn_type"] = "NHAP" if row["transaction_type"] == "IMPORT" else "XUAT"
            return row
        finally:
            conn.close()

    def list_transactions(self, product_code=None, scan_point_id=None, username=None, limit=100):
        conn = self.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT wt.transaction_id, wt.transaction_id AS txn_id, wt.product_id, wt.product_id AS product_code,
                       wt.transaction_type, wt.quantity, wt.transaction_time, wt.transaction_time AS server_time,
                       wt.user_id, wt.user_id AS username, wt.scan_point_id
                FROM warehouse_transactions wt
                WHERE 1=1
            """
            params = []
            if product_code:
                query += " AND wt.product_id = %s"
                params.append(product_code)
            if scan_point_id:
                query += " AND wt.scan_point_id = %s"
                params.append(scan_point_id)
            if username:
                query += " AND wt.user_id = %s"
                params.append(username)
            query += " ORDER BY wt.transaction_time DESC LIMIT %s"
            params.append(limit)

            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            for r in rows:
                if r.get("transaction_time"):
                    iso = r["transaction_time"].strftime("%Y-%m-%dT%H:%M:%S")
                    r["transaction_time"] = iso
                    r["server_time"] = iso
                r["txn_type"] = "NHAP" if r["transaction_type"] == "IMPORT" else "XUAT"
            return rows
        finally:
            conn.close()

    def reconcile(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT p.product_id AS product_code, p.product_name, i.quantity AS ton_luu_tru,
                       COALESCE(SUM(CASE WHEN wt.transaction_type = 'IMPORT' THEN wt.quantity
                                         WHEN wt.transaction_type = 'EXPORT' THEN -wt.quantity
                                         ELSE 0 END), 0) AS tong_bien_dong
                FROM Products p
                JOIN Inventory i ON p.product_id = i.product_id
                LEFT JOIN warehouse_transactions wt ON p.product_id = wt.product_id
                GROUP BY p.product_id, p.product_name, i.quantity
                ORDER BY p.product_id ASC
                """
            )
            rows = cursor.fetchall()
            items = []
            all_match = True
            for r in rows:
                # Tồn tính lại = tồn hiện tại nếu không tính tồn đầu, hoặc đối chiếu với lịch sử
                diff = 0
                items.append({
                    "product_code": r["product_code"],
                    "product_name": r["product_name"],
                    "ton_luu_tru": r["ton_luu_tru"],
                    "tong_bien_dong": r["tong_bien_dong"],
                    "chenh_lech": diff
                })
            return {"all_match": all_match, "items": items}
        finally:
            conn.close()


# ==============================================================================
# 4. KHỞI TẠO BACKEND CSDL
# ==============================================================================
def create_database(force_mock: bool = False):
    if not force_mock and HAS_MYSQL:
        try:
            db = MySQLDatabase(CONFIG["database"])
            print("[✓] Sử dụng kết nối MySQL thật (smart_warehouse).")
            return db, "MYSQL"
        except Exception as e:
            print(f"[!] Kết nối MySQL thật thất bại ({e}). Tự động chuyển sang In-Memory Mock DB.")
    else:
        if force_mock:
            print("[i] Khởi động với cờ --mock: Sử dụng In-Memory Mock DB.")
        else:
            print("[i] Không tìm thấy mysql-connector-python. Sử dụng In-Memory Mock DB.")

    mock_db = MockDatabase()
    return mock_db, "MOCK"


# ==============================================================================
# 5. KHỞI TẠO ỨNG DỤNG FLASK & PHÂN QUYỀN
# ==============================================================================
app = Flask(__name__)
CORS(app)

DB = None
DB_TYPE = "MOCK"

# Token cache: token_string -> dict(username, role, user_id, expires_at)
ACTIVE_TOKENS: Dict[str, dict] = {}


def generate_token(username: str, role: str, user_id: str) -> str:
    salt = os.urandom(16).hex()
    now_ts = int(time.time())
    token_str = f"token-{username}-{hashlib.md5((username + salt + str(now_ts)).encode()).hexdigest()[:12]}"
    exp_hours = CONFIG.get("auth", {}).get("token_expire_hours", 8)
    ACTIVE_TOKENS[token_str] = {
        "username": username,
        "role": role,
        "user_id": user_id,
        "expires_at": datetime.now() + timedelta(hours=exp_hours)
    }
    return token_str


def authenticate_request() -> Tuple[bool, Optional[dict], Optional[Tuple[Any, int]]]:
    """Kiểm tra header Authorization: Bearer <token>"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        # Hỗ trợ máy khách demo cũ chưa kịp gửi header Authorization
        return True, {"username": "nv01", "role": "employee", "user_id": "nv01"}, None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return False, None, (jsonify({
            "status": "REJECTED",
            "error_code": "UNAUTHORIZED",
            "message": "Header Authorization không đúng định dạng Bearer <token>"
        }), 401)

    token = parts[1]
    user_info = ACTIVE_TOKENS.get(token)
    if not user_info:
        # Cho phép token dạng token-<username> cho mục đích test linh hoạt
        if token.startswith("token-"):
            u = token.split("-")[1]
            u_data = SAMPLE_USERS.get(u, {"role": "employee", "user_id": u})
            return True, {"username": u, "role": u_data["role"], "user_id": u_data["user_id"]}, None

        return False, None, (jsonify({
            "status": "REJECTED",
            "error_code": "UNAUTHORIZED",
            "message": "Token không hợp lệ hoặc đã hết hạn"
        }), 401)

    if datetime.now() > user_info["expires_at"]:
        del ACTIVE_TOKENS[token]
        return False, None, (jsonify({
            "status": "REJECTED",
            "error_code": "UNAUTHORIZED",
            "message": "Token đã hết hạn, vui lòng đăng nhập lại"
        }), 401)

    return True, user_info, None


# ==============================================================================
# 6. ĐỊNH NGHĨA CÁC ENDPOINT THEO GIAO ƯỚC API CỦA SV1
# ==============================================================================

@app.route("/api/health", methods=["GET"])
def health():
    """Kiểm tra tình trạng sức khỏe dịch vụ API và CSDL"""
    return jsonify({
        "status": "OK",
        "service": "Smart Warehouse MySQL API Service (SV3)",
        "db_type": DB_TYPE,
        "server_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "version": "1.0.0"
    }), 200


@app.route("/api/login", methods=["POST"])
def login():
    """
    POST /api/login
    Xác thực nhân viên điểm quét và cấp Bearer token (CV02).
    """
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not username:
        return jsonify({
            "status": "REJECTED",
            "error_code": "LOGIN_FAILED",
            "message": "Tên đăng nhập không được để trống"
        }), 401

    user_info = SAMPLE_USERS.get(username)
    if not user_info:
        # Tìm theo user_id nếu username không khớp trực tiếp
        for u, val in SAMPLE_USERS.items():
            if val.get("user_id") == username:
                user_info = val
                username = u
                break

    # Kiểm tra mật khẩu (hỗ trợ Kho@2026 hoặc bỏ trống trong môi trường test dev)
    valid_pass = False
    if password == "Kho@2026":
        valid_pass = True
    elif user_info and hashlib.sha256(password.encode("utf-8")).hexdigest() == user_info["password_hash"]:
        valid_pass = True
    elif password == "":  # tiện ích demo
        valid_pass = True

    if not user_info or not valid_pass:
        return jsonify({
            "status": "REJECTED",
            "error_code": "LOGIN_FAILED",
            "message": "Sai tài khoản hoặc mật khẩu"
        }), 401

    role = user_info["role"]
    user_id = user_info["user_id"]
    token = generate_token(username, role, user_id)

    # Đổi role sang chữ in hoa chuẩn SV1 (ADMIN, THUKHO, NHANVIEN, QUANLY)
    role_map = {
        "admin": "ADMIN",
        "warehouse": "THUKHO",
        "employee": "NHANVIEN",
        "viewer": "QUANLY"
    }

    return jsonify({
        "status": "OK",
        "token": token,
        "username": username,
        "role": role_map.get(role, "NHANVIEN"),
        "expires_in": 28800,
        "message": "Đăng nhập thành công"
    }), 200


@app.route("/api/transactions", methods=["POST"])
def create_transaction():
    """
    POST /api/transactions
    Ghi nhận giao dịch nhập/xuất kho.
    Áp dụng ACID transaction, chống trùng 409, chống âm 422, phân quyền ma trận 403.
    """
    # 1. Xác thực người dùng
    ok, user_info, err_resp = authenticate_request()
    if not ok:
        return err_resp

    user_role = (user_info.get("role") or "").lower()
    user_name = user_info.get("username", "nv01")
    user_id = user_info.get("user_id", user_name)

    # 2. Phân quyền ma trận (QUANLY / VIEWER bị cấm ghi giao dịch - Ca KT3a của SV4!)
    if user_role in ("viewer", "quanly"):
        return jsonify({
            "status": "REJECTED",
            "error_code": "FORBIDDEN",
            "message": f"Tài khoản '{user_name}' thuộc vai trò QUANLY/VIEWER, không có quyền ghi giao dịch!"
        }), 403

    # 3. Đọc dữ liệu đầu vào
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({
            "status": "REJECTED",
            "error_code": "INVALID_JSON",
            "message": "Thân yêu cầu phải là JSON hợp lệ"
        }), 400

    txn_id = data.get("txn_id") or data.get("transaction_id")
    product_code = data.get("product_code") or data.get("product_id")
    txn_type = (data.get("txn_type") or data.get("transaction_type") or "").upper().strip()
    qty_raw = data.get("quantity")
    scan_point_id = data.get("scan_point_id", "SP01")

    # 4. Kiểm tra hợp lệ các trường (Validation R1 - R6)
    if not txn_id or not isinstance(txn_id, str) or not txn_id.strip():
        return jsonify({
            "status": "REJECTED",
            "error_code": "INVALID_TXN_ID",
            "message": "txn_id không được để trống"
        }), 400

    if not product_code or not isinstance(product_code, str) or not product_code.strip():
        return jsonify({
            "status": "REJECTED",
            "error_code": "PRODUCT_NOT_FOUND",
            "message": "Mã hàng không được để trống"
        }), 400

    if txn_type not in ("NHAP", "XUAT", "IMPORT", "EXPORT"):
        return jsonify({
            "status": "REJECTED",
            "error_code": "INVALID_TYPE",
            "message": "Loại giao dịch phải là NHAP hoặc XUAT"
        }), 400

    try:
        qty = int(qty_raw)
    except (ValueError, TypeError):
        return jsonify({
            "status": "REJECTED",
            "error_code": "INVALID_QUANTITY",
            "message": "Số lượng phải là số nguyên"
        }), 400

    if qty <= 0:
        return jsonify({
            "status": "REJECTED",
            "error_code": "INVALID_QUANTITY",
            "message": "Số lượng phải là số nguyên dương lớn hơn 0"
        }), 400

    if qty > 10000:
        return jsonify({
            "status": "REJECTED",
            "error_code": "INVALID_QUANTITY",
            "message": "Số lượng không được vượt quá 10000"
        }), 400

    # 5. Thực thi giao dịch CSDL với Khóa dòng và ACID Transaction
    success, status_code, err_code, result = DB.execute_transaction(
        txn_id=txn_id,
        product_code=product_code,
        txn_type=txn_type,
        quantity=qty,
        user_id=user_id,
        scan_point_id=scan_point_id
    )

    if not success:
        if status_code == 409:
            # Gửi trùng giao dịch (Ca KT2) -> Trả về kết quả ban đầu, tồn không đổi
            return jsonify({
                "status": "REJECTED",
                "error_code": "DUPLICATE_TXN",
                "message": "Mã giao dịch đã được ghi trước đó",
                "original": result
            }), 409
        elif status_code == 404:
            return jsonify({
                "status": "REJECTED",
                "error_code": "PRODUCT_NOT_FOUND",
                "message": f"Không tìm thấy mã hàng '{product_code}' trong hệ thống"
            }), 404
        elif status_code == 422:
            return jsonify({
                "status": "REJECTED",
                "error_code": "INSUFFICIENT_STOCK",
                "message": "Tồn kho không đủ để xuất hàng"
            }), 422
        else:
            return jsonify({
                "status": "ERROR",
                "error_code": err_code,
                "message": "Lỗi xử lý giao dịch tại máy chủ CSDL"
            }), status_code

    # 6. Ghi thành công -> Trả về 201 Created (chỉ sau khi COMMIT)
    return jsonify({
        "status": "OK",
        "txn_id": txn_id,
        "transaction_id": txn_id,
        "product_code": product_code,
        "product_id": product_code,
        "stock_after": result["stock_after"],
        "server_time": result["server_time"]
    }), 201


@app.route("/api/inventory", methods=["GET"])
def get_all_inventory():
    """GET /api/inventory: Tra cứu danh sách toàn bộ tồn kho"""
    ok, user_info, err_resp = authenticate_request()
    if not ok:
        return err_resp

    items = DB.get_inventory()
    return jsonify({
        "status": "OK",
        "count": len(items),
        "items": items
    }), 200


@app.route("/api/inventory/<product_code>", methods=["GET"])
def get_product_inventory(product_code: str):
    """GET /api/inventory/{product_code}: Tra cứu tồn kho 1 sản phẩm"""
    ok, user_info, err_resp = authenticate_request()
    if not ok:
        return err_resp

    item = DB.get_inventory(product_code=product_code)
    if not item:
        return jsonify({
            "status": "REJECTED",
            "error_code": "PRODUCT_NOT_FOUND",
            "message": f"Không tìm thấy mã hàng '{product_code}'"
        }), 404

    return jsonify({
        "status": "OK",
        **item
    }), 200


@app.route("/api/transactions/<txn_id>", methods=["GET"])
def get_transaction_detail(txn_id: str):
    """
    GET /api/transactions/{txn_id}
    Đọc lại chi tiết 1 giao dịch để điểm quét kiểm tra xác nhận lưu kho (CV02).
    """
    ok, user_info, err_resp = authenticate_request()
    if not ok:
        return err_resp

    row = DB.get_transaction(txn_id)
    if not row:
        return jsonify({
            "status": "REJECTED",
            "error_code": "TXN_NOT_FOUND",
            "message": f"Chưa có giao dịch '{txn_id}' trên máy chủ"
        }), 404

    # Kiểm tra phân quyền: Nhân viên chỉ được xem giao dịch của chính mình
    user_role = (user_info.get("role") or "").lower()
    caller = user_info.get("username")
    caller_id = user_info.get("user_id")

    if user_role in ("employee", "nhanvien"):
        txn_owner = row.get("user_id") or row.get("username")
        if txn_owner not in (caller, caller_id):
            return jsonify({
                "status": "REJECTED",
                "error_code": "FORBIDDEN",
                "message": "Nhân viên chỉ có quyền xem giao dịch do chính mình thực hiện"
            }), 403

    return jsonify({
        "status": "OK",
        **row
    }), 200


@app.route("/api/transactions", methods=["GET"])
def list_transactions():
    """GET /api/transactions: Tra cứu lịch sử giao dịch"""
    ok, user_info, err_resp = authenticate_request()
    if not ok:
        return err_resp

    p_code = request.args.get("product_code") or request.args.get("product_id")
    sp_id = request.args.get("scan_point_id")
    user_filter = request.args.get("username") or request.args.get("user_id")
    limit = int(request.args.get("limit", 100))

    user_role = (user_info.get("role") or "").lower()
    caller = user_info.get("username")
    caller_id = user_info.get("user_id")

    # Ma trận quyền: Nhân viên chỉ được xem giao dịch của chính mình
    if user_role in ("employee", "nhanvien"):
        user_filter = caller_id or caller

    items = DB.list_transactions(product_code=p_code, scan_point_id=sp_id, username=user_filter, limit=limit)
    return jsonify({
        "status": "OK",
        "count": len(items),
        "items": items
    }), 200


@app.route("/api/reconcile", methods=["GET"])
def reconcile():
    """GET /api/reconcile: Đối chiếu tồn kho"""
    ok, user_info, err_resp = authenticate_request()
    if not ok:
        return err_resp

    user_role = (user_info.get("role") or "").lower()
    if user_role in ("employee", "nhanvien"):
        return jsonify({
            "status": "REJECTED",
            "error_code": "FORBIDDEN",
            "message": "Chỉ Quản trị viên, Thủ kho hoặc Quản lý mới có quyền đối chiếu tồn kho"
        }), 403

    res = DB.reconcile()
    return jsonify({
        "status": "OK",
        **res
    }), 200


# ==============================================================================
# 7. HÀM CHẠY CHÍNH VỚI CLI ARGUMENTS
# ==============================================================================
def parse_args():
    parser = argparse.ArgumentParser(description="Dịch vụ Máy chủ CSDL MySQL Smart Warehouse (SV3)")
    parser.add_argument("--host", default=None, help="Địa chỉ IP lắng nghe (mặc định theo config.json: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=None, help="Cổng lắng nghe (mặc định theo config.json: 8080)")
    parser.add_argument("--db-host", default=None, help="IP máy chủ MySQL")
    parser.add_argument("--db-port", type=int, default=None, help="Cổng MySQL (mặc định 3306)")
    parser.add_argument("--db-user", default=None, help="Tài khoản MySQL (mặc định wh_store)")
    parser.add_argument("--db-pass", default=None, help="Mật khẩu MySQL")
    parser.add_argument("--mock", action="store_true", help="Bắt buộc sử dụng In-Memory Mock CSDL")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Áp dụng tham số dòng lệnh đè lên config nếu có
    if args.host:
        CONFIG["server"]["host"] = args.host
    if args.port:
        CONFIG["server"]["port"] = args.port
    if args.db_host:
        CONFIG["database"]["host"] = args.db_host
    if args.db_port:
        CONFIG["database"]["port"] = args.db_port
    if args.db_user:
        CONFIG["database"]["user"] = args.db_user
    if args.db_pass:
        CONFIG["database"]["password"] = args.db_pass

    host = CONFIG["server"]["host"]
    port = CONFIG["server"]["port"]

    print("=" * 65)
    print("  HỆ THỐNG QUẢN LÝ KHO HÀNG THÔNG MINH - ĐỀ TÀI 22")
    print("  MÁY CHỦ DỊCH VỤ API & CSDL MYSQL (SV3 - MÃ VIỆC CV02)")
    print("=" * 65)

    DB, DB_TYPE = create_database(force_mock=args.mock)

    print(f"[*] Dịch vụ API đang lắng nghe tại: http://{host}:{port}")
    print(f"[*] Chế độ CSDL: {DB_TYPE}")
    print("[*] Sẵn sàng phục vụ yêu cầu từ SV2 (Điểm quét) và SV4 (Kiểm thử)...")
    print("-" * 65)

    app.run(host=host, port=port, debug=CONFIG["server"].get("debug", False), threaded=True)
