"""
Kiểm tra toàn diện app.py bằng Flask Test Client (Không cần mở cổng mạng hoặc bật MySQL)
"""
import os
import sys
from datetime import datetime
import pymysql

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app as app_module
from app import app

# ----------------------------------------------------------------------
# Mock kết nối MySQL phục vụ chạy Unit Test độc lập không cần MySQL Server
# ----------------------------------------------------------------------
MOCK_USERS = {
    "AD01": {"user_id": "AD01", "username": "admin_demo", "full_name": "Quản trị viên mẫu", "role": "admin"},
    "admin_demo": {"user_id": "AD01", "username": "admin_demo", "full_name": "Quản trị viên mẫu", "role": "admin"},
    "TK01": {"user_id": "TK01", "username": "thukho_demo", "full_name": "Thủ kho mẫu", "role": "warehouse"},
    "thukho_demo": {"user_id": "TK01", "username": "thukho_demo", "full_name": "Thủ kho mẫu", "role": "warehouse"},
    "NV01": {"user_id": "NV01", "username": "nhanvien_demo", "full_name": "Nhân viên mẫu", "role": "employee"},
    "nhanvien_demo": {"user_id": "NV01", "username": "nhanvien_demo", "full_name": "Nhân viên mẫu", "role": "employee"},
    "nv01": {"user_id": "NV01", "username": "nv01", "full_name": "Nhân viên 01", "role": "employee"},
    "VIEW01": {"user_id": "VIEW01", "username": "viewer_demo", "full_name": "Tài khoản chỉ xem", "role": "viewer"},
    "viewer_demo": {"user_id": "VIEW01", "username": "viewer_demo", "full_name": "Tài khoản chỉ xem", "role": "viewer"},
}
MOCK_SCAN_POINTS = {"SCAN01", "SCAN02", "SP01", "SP02"}
MOCK_INVENTORY = {f"SP{i:03d}": 10 + (i % 20) for i in range(1, 101)}
MOCK_TXNS = {}


class MockCursor:
    def __init__(self):
        self._one = None
        self._all = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def execute(self, sql: str, params=()):
        q = sql.strip().lower()
        if "from users where" in q:
            key = params[0]
            self._one = MOCK_USERS.get(key)
        elif "from users" in q:
            seen = set()
            rows = []
            for u in MOCK_USERS.values():
                if u["user_id"] not in seen:
                    seen.add(u["user_id"])
                    rows.append(u)
            self._all = rows
        elif "select quantity from inventory where product_id" in q:
            pid = params[0]
            self._one = {"quantity": MOCK_INVENTORY[pid]} if pid in MOCK_INVENTORY else None
        elif "from inventory i" in q and "where i.product_id" in q:
            pid = params[0]
            if pid in MOCK_INVENTORY:
                self._one = {
                    "product_id": pid,
                    "product_name": f"San pham mau {pid[-3:]}",
                    "unit": "cai",
                    "quantity": MOCK_INVENTORY[pid],
                    "updated_at": datetime.now(),
                }
            else:
                self._one = None
        elif "from inventory i" in q:
            self._all = [
                {
                    "product_id": pid,
                    "product_name": f"San pham mau {pid[-3:]}",
                    "unit": "cai",
                    "quantity": qty,
                    "updated_at": datetime.now(),
                }
                for pid, qty in sorted(MOCK_INVENTORY.items())
            ]
        elif "from warehouse_transactions where transaction_id" in q:
            tid = params[0]
            self._one = MOCK_TXNS.get(tid)
        elif "from warehouse_transactions" in q:
            self._all = list(MOCK_TXNS.values())[:10]

    def callproc(self, proc_name: str, args=()):
        txn_id, product_id, db_type, qty, user_id, scan_point_id = args
        if txn_id in MOCK_TXNS:
            raise pymysql.MySQLError(1644, "Ma giao dich da ton tai")
        if product_id not in MOCK_INVENTORY:
            raise pymysql.MySQLError(1644, "Khong tim thay san pham trong Inventory")
        if scan_point_id not in MOCK_SCAN_POINTS:
            raise pymysql.MySQLError(1644, "Khong tim thay diem quet")
        if db_type == "EXPORT" and MOCK_INVENTORY[product_id] < qty:
            raise pymysql.MySQLError(1644, "Ton kho khong du de xuat")

        if db_type == "IMPORT":
            MOCK_INVENTORY[product_id] += qty
        else:
            MOCK_INVENTORY[product_id] -= qty

        MOCK_TXNS[txn_id] = {
            "transaction_id": txn_id,
            "product_id": product_id,
            "transaction_type": db_type,
            "quantity": qty,
            "transaction_time": datetime.now(),
            "user_id": user_id,
            "scan_point_id": scan_point_id,
        }

    def fetchone(self):
        return self._one

    def fetchall(self):
        return self._all


class MockConnection:
    def cursor(self):
        return MockCursor()

    def close(self):
        pass


app_module.get_connection = lambda: MockConnection()
client = app.test_client()

print("[1] Test /api/login (viewer_demo, nhanvien_demo, thukho_demo, admin_demo)...")
res_v = client.post("/api/login", json={"username": "viewer_demo"})
assert res_v.status_code == 200 and res_v.get_json()["role"] == "viewer"
token_viewer = res_v.get_json()["token"]

res_e = client.post("/api/login", json={"username": "nhanvien_demo"})
assert res_e.status_code == 200 and res_e.get_json()["role"] == "employee"
token_emp = res_e.get_json()["token"]

res_w = client.post("/api/login", json={"username": "thukho_demo"})
assert res_w.status_code == 200 and res_w.get_json()["role"] == "warehouse"
token_wh = res_w.get_json()["token"]

res_a = client.post("/api/login", json={"username": "admin_demo"})
assert res_a.status_code == 200 and res_a.get_json()["role"] == "admin"
token_adm = res_a.get_json()["token"]
print("   Đăng nhập 4 vai trò thành công!")

print("[2] Test /api/login tài khoản không tồn tại (401)...")
res_bad = client.post("/api/login", json={"username": "hacker_xyz"})
assert res_bad.status_code == 401
print("   401 error_code:", res_bad.get_json().get("error_code"))

print("[3] Test RBAC: viewer_demo bị chặn ghi giao dịch (403 FORBIDDEN)...")
res = client.post(
    "/api/transactions",
    json={"scan_point_id": "SCAN01", "txn_id": "TXN-FORBIDDEN-01", "product_code": "SP001", "txn_type": "NHAP", "quantity": 10},
    headers={"Authorization": f"Bearer {token_viewer}"},
)
assert res.status_code == 403
print("   Viewer bị chặn chuẩn:", res.get_json()["message"])

print("[4] Test RBAC: nhanvien_demo được NHẬP kho (201), bị chặn XUẤT kho (403)...")
res_in = client.post(
    "/api/transactions",
    json={"scan_point_id": "SCAN01", "txn_id": "TXN-EMP-IN-01", "product_code": "SP001", "txn_type": "NHAP", "quantity": 10},
    headers={"Authorization": f"Bearer {token_emp}"},
)
assert res_in.status_code == 201
res_out = client.post(
    "/api/transactions",
    json={"scan_point_id": "SCAN01", "txn_id": "TXN-EMP-OUT-01", "product_code": "SP001", "txn_type": "XUAT", "quantity": 5},
    headers={"Authorization": f"Bearer {token_emp}"},
)
assert res_out.status_code == 403
print("   Nhân viên NHẬP 201, XUẤT bị chặn 403 chuẩn!")

print("[5] Test thukho_demo NHẬP và XUẤT kho hợp lệ (KT1)...")
stock_before = client.get("/api/inventory/SP002").get_json()["quantity"]
res = client.post(
    "/api/transactions",
    json={"scan_point_id": "SCAN01", "txn_id": "SP01-20261109-0001", "product_code": "SP002", "txn_type": "NHAP", "quantity": 20},
    headers={"Authorization": f"Bearer {token_wh}"},
)
assert res.status_code == 201 and res.get_json()["stock_after"] == stock_before + 20
print(f"   NHẬP SP002 thành công: Tồn {stock_before} -> {res.get_json()['stock_after']}")

print("[6] Test đọc lại giao dịch GET /api/transactions/<txn_id>...")
res = client.get("/api/transactions/SP01-20261109-0001")
assert res.status_code == 200 and res.get_json()["product_id"] == "SP002"
print("   Đọc lại thành công:", res.get_json()["transaction_id"])

print("[7] Test chống trùng txn_id (409 DUPLICATE_TXN - KT2)...")
res = client.post(
    "/api/transactions",
    json={"scan_point_id": "SCAN01", "txn_id": "SP01-20261109-0001", "product_code": "SP002", "txn_type": "NHAP", "quantity": 20},
    headers={"Authorization": f"Bearer {token_wh}"},
)
assert res.status_code == 409 and res.get_json()["error_code"] == "DUPLICATE_TXN"
print("   Chống trùng 409 thành công:", res.get_json())

print("[8] Test chống âm tồn kho khi xuất vượt tồn (INSUFFICIENT_STOCK - KT3)...")
res = client.post(
    "/api/transactions",
    json={"scan_point_id": "SCAN02", "txn_id": "SP02-OVERSTOCK-01", "product_code": "SP002", "txn_type": "XUAT", "quantity": 500},
    headers={"Authorization": f"Bearer {token_wh}"},
)
assert res.status_code in (400, 422) and res.get_json()["error_code"] == "INSUFFICIENT_STOCK"
print("   Chống âm tồn kho thành công:", res.get_json())

print("[9] Test bảo vệ endpoint GET /api/users (chỉ Admin)...")
assert client.get("/api/users", headers={"Authorization": f"Bearer {token_wh}"}).status_code == 403
assert client.get("/api/users", headers={"Authorization": f"Bearer {token_adm}"}).status_code == 200
print("   Bảo vệ /api/users thành công!")

print("\n>>> TẤT CẢ CA KIỂM THỬ UNIT TEST CHO APP.PY MỚI ĐÃ ĐẠT 100%! <<<")
