"""
Kiểm tra toàn diện app.py bằng Flask Test Client (Không cần mở cổng mạng)
"""
import sys
import os
import json

sys.path.insert(0, r"E:\CNNT\sinh-vien-3\04_DICH_VU_API")
from app import app, create_database
import app as app_module

# Khởi tạo Mock DB
db, db_type = create_database(force_mock=True)
app_module.DB = db
app_module.DB_TYPE = db_type

client = app.test_client()

print("[1] Test /api/health...")
res = client.get("/api/health")
assert res.status_code == 200, f"Health check failed: {res.status_code}"
data = res.get_json()
print("   Health:", data)

print("[2] Test /api/login nv01...")
res = client.post("/api/login", json={"username": "nv01", "password": "Kho@2026"})
assert res.status_code == 200, f"Login failed: {res.status_code}"
data = res.get_json()
nv01_token = data["token"]
print("   Token:", nv01_token)

print("[3] Test /api/login quanly01...")
res = client.post("/api/login", json={"username": "quanly01", "password": "Kho@2026"})
assert res.status_code == 200
ql_token = res.get_json()["token"]

print("[4] Test /api/login wrong password (401)...")
res = client.post("/api/login", json={"username": "nv01", "password": "WrongPassword"})
assert res.status_code == 401
print("   401 error_code:", res.get_json().get("error_code"))

print("[5] Test RBAC: quanly01 write transaction (403 FORBIDDEN)...")
headers_ql = {"Authorization": f"Bearer {ql_token}"}
res = client.post("/api/transactions", json={
    "txn_id": "SP01-FORBIDDEN-001",
    "product_code": "SP001",
    "txn_type": "NHAP",
    "quantity": 10
}, headers=headers_ql)
assert res.status_code == 403, f"Expected 403 but got {res.status_code}"
print("   RBAC blocked correctly:", res.get_json())

print("[6] Test valid transaction NHAP (201 Created)...")
headers_nv = {"Authorization": f"Bearer {nv01_token}"}
res = client.get("/api/inventory/SP001", headers=headers_nv)
stock_before = res.get_json()["quantity"]

test_txn_id = "SP01-20261105-0001"
res = client.post("/api/transactions", json={
    "txn_id": test_txn_id,
    "product_code": "SP001",
    "txn_type": "NHAP",
    "quantity": 20,
    "scan_point_id": "SP01"
}, headers=headers_nv)
assert res.status_code == 201, f"Expected 201 but got {res.status_code}: {res.data}"
stock_after = res.get_json()["stock_after"]
assert stock_after == stock_before + 20, f"Stock mismatch: {stock_before} -> {stock_after}"
print(f"   NHAP thành công: Tồn {stock_before} -> {stock_after}")

print("[7] Test read transaction by txn_id...")
res = client.get(f"/api/transactions/{test_txn_id}", headers=headers_nv)
assert res.status_code == 200
assert res.get_json()["product_code"] == "SP001"
print("   Đọc lại giao dịch:", res.get_json()["txn_id"])

print("[8] Test duplicate txn_id (409 Conflict)...")
res = client.post("/api/transactions", json={
    "txn_id": test_txn_id,
    "product_code": "SP001",
    "txn_type": "NHAP",
    "quantity": 20,
    "scan_point_id": "SP01"
}, headers=headers_nv)
assert res.status_code == 409, f"Expected 409 but got {res.status_code}"
print("   Chống trùng 409 thành công:", res.get_json())

print("[9] Test insufficient stock XUAT (422)...")
res = client.post("/api/transactions", json={
    "txn_id": "SP01-OVERSTOCK-001",
    "product_code": "SP001",
    "txn_type": "XUAT",
    "quantity": 500,
    "scan_point_id": "SP01"
}, headers=headers_nv)
assert res.status_code == 422, f"Expected 422 but got {res.status_code}: {res.get_json()}"
print("   Chống âm tồn 422 thành công:", res.get_json())

print("[10] Test reconcile /api/reconcile...")
headers_adm = {"Authorization": "Bearer token-admin"}
res = client.get("/api/reconcile", headers=headers_adm)
assert res.status_code == 200
print(f"   Đối chiếu tồn kho: {len(res.get_json()['items'])} mặt hàng, all_match={res.get_json()['all_match']}")

print("\n>>> TẤT CẢ 10/10 CA KIỂM THỬ ĐÃ ĐẠT CHUẨN 100%! <<<")
