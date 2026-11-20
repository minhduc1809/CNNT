"""
SV4 - KT3a bổ sung: tài khoản CHỈ XEM (viewer_demo) đọc được, nhưng thêm/sửa/xóa bị từ chối.

Kiểm tra 2 tầng:
  - Tầng dịch vụ (API, cổng 8080): đăng nhập viewer_demo, đọc tồn và lịch sử, thử ghi giao dịch,
    thử sửa/xóa qua API.
  - Tầng CSDL: nối MySQL bằng tài khoản wh_viewer (chỉ có quyền SELECT), thử INSERT/UPDATE/DELETE.

Script KHÔNG làm thay đổi dữ liệu: các lệnh ghi dùng mã giả, nếu lỡ được phép thì ROLLBACK.
Điều kiện: API đang chạy (python SV3_MayChu_CSDL_API/04_DICH_VU_API/app.py), MySQL đang chạy.
Cách chạy:  python kt3a_viewer.py
Kết quả in ra màn hình và ghi vào MC-KT3a-03.txt (cùng thư mục với script), mỗi dòng có giờ.
"""
import os
import sys
import time
from datetime import datetime

import pymysql
import requests

API = os.getenv("API_URL", "http://127.0.0.1:8080")
VIEWER_USER = "viewer_demo"          # tài khoản chỉ xem trong bảng Users
DB = dict(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    user="wh_viewer",                # tài khoản MySQL chỉ có quyền SELECT
    password=os.getenv("VIEWER_DB_PASS", "ViewerUser@2026"),  # theo README của SV3
    database="smart_warehouse",
    connect_timeout=5,
)
OUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MC-KT3a-03.txt")

lines = []
results = []  # (tên ca, True/False)


def log(msg=""):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}" if msg else ""
    print(line)
    lines.append(line)


def check(name, ok, detail):
    results.append((name, ok))
    log(f"{'ĐÚNG KỲ VỌNG' if ok else 'SAI KỲ VỌNG '} | {name} | {detail}")


def call(method, path, token=None, body=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        r = requests.request(method, API + path, json=body, headers=headers, timeout=5)
        try:
            data = r.json()
        except ValueError:
            data = r.text[:120]
        return r.status_code, data
    except Exception as e:  # noqa: BLE001
        return 0, str(e)


def db_read(conn, sql):
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchone()[0]


def main():
    log("=== KT3a bổ sung: tài khoản chỉ xem ===")
    log(f"API: {API} | tài khoản API: {VIEWER_USER} | tài khoản CSDL: {DB['user']}")

    # ---- Mốc trước (đọc bằng wh_viewer) ----
    try:
        conn = pymysql.connect(**DB)
    except Exception as e:  # noqa: BLE001
        log(f"[LỖI] Không nối được MySQL bằng {DB['user']}: {e}")
        log("      Kiểm tra tài khoản/mật khẩu wh_viewer (README của SV3) rồi chạy lại.")
        sys.exit(1)
    ton_truoc = db_read(conn, "SELECT quantity FROM Inventory WHERE product_id='SP002'")
    dem_truoc = db_read(conn, "SELECT COUNT(*) FROM warehouse_transactions")
    log(f"MỐC TRƯỚC (MySQL): tồn SP002 = {ton_truoc}; số bản ghi warehouse_transactions = {dem_truoc}")

    # ---- Tầng dịch vụ (API) ----
    log("--- Tầng dịch vụ (API) ---")
    code, data = call("POST", "/api/login", body={"username": VIEWER_USER, "password": "Kho@2026"})
    check("API-1 đăng nhập viewer_demo", code == 200, f"HTTP {code}, role={data.get('role') if isinstance(data, dict) else data}")
    token = data.get("token") if isinstance(data, dict) else None
    if not token:
        log("[LỖI] Không lấy được token, dừng. Kiểm tra API đang chạy và tài khoản viewer_demo có trong bảng Users.")
        sys.exit(1)

    code, data = call("GET", "/api/inventory/SP002", token)
    check("API-2 viewer ĐỌC tồn SP002", code == 200, f"HTTP {code}, quantity={data.get('quantity') if isinstance(data, dict) else data}")

    code, data = call("GET", "/api/transactions/recent", token)
    check("API-3 viewer ĐỌC lịch sử giao dịch", code == 200, f"HTTP {code}, số dòng={len(data) if isinstance(data, list) else data}")

    txn = f"KT3A-{int(time.time())}"
    body = {"txn_id": txn, "product_code": "SP002", "txn_type": "NHAP", "quantity": 1,
            "scan_point_id": "SP01", "client_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
    code, data = call("POST", "/api/transactions", token, body)
    check("API-4 viewer THÊM giao dịch bị từ chối", code == 403,
          f"HTTP {code}, error_code={data.get('error_code') if isinstance(data, dict) else data}")

    code, data = call("DELETE", "/api/transactions/KT3A-KHONG-TON-TAI", token)
    check("API-5 viewer XÓA giao dịch: API không có chức năng xóa", code in (404, 405), f"HTTP {code}")

    code, data = call("PUT", "/api/inventory/SP002", token, {"quantity": 999})
    check("API-6 viewer SỬA tồn: API không có chức năng sửa", code in (404, 405), f"HTTP {code}")

    code, _ = call("GET", "/api/inventory/SP002")  # không gửi token
    log(f"THÔNG TIN | API-7 đọc tồn SP002 KHÔNG đăng nhập (không gửi token) | HTTP {code} "
        f"({'đọc được' if code == 200 else 'bị chặn'})")

    # ---- Tầng CSDL (wh_viewer) ----
    log("--- Tầng CSDL (tài khoản wh_viewer, chỉ có quyền SELECT) ---")
    check("DB-1 wh_viewer ĐỌC được tồn kho", ton_truoc is not None, f"quantity={ton_truoc}")

    tests = [
        ("DB-2 wh_viewer THÊM (INSERT) bị từ chối",
         "INSERT INTO Products (product_id, product_name, unit) VALUES ('KT3A-TEST', 'test', 'cai')"),
        ("DB-3 wh_viewer SỬA (UPDATE) bị từ chối",
         "UPDATE Inventory SET quantity = quantity + 1 WHERE product_id = 'SP002'"),
        ("DB-4 wh_viewer XÓA (DELETE) bị từ chối",
         "DELETE FROM warehouse_transactions WHERE transaction_id = 'KT3A-KHONG-TON-TAI'"),
    ]
    for name, sql in tests:
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
            check(name, False, "KHÔNG bị từ chối (lệnh chạy được!) -> sẽ ROLLBACK")
        except pymysql.MySQLError as e:
            ma = e.args[0] if e.args else "?"
            check(name, ma == 1142, f"MySQL lỗi {ma}: {e.args[1] if len(e.args) > 1 else e}")
    conn.rollback()

    # ---- Mốc sau ----
    ton_sau = db_read(conn, "SELECT quantity FROM Inventory WHERE product_id='SP002'")
    dem_sau = db_read(conn, "SELECT COUNT(*) FROM warehouse_transactions")
    conn.close()
    log(f"MỐC SAU (MySQL): tồn SP002 = {ton_sau}; số bản ghi warehouse_transactions = {dem_sau}")
    check("DATA dữ liệu không đổi sau khi thử", ton_sau == ton_truoc and dem_sau == dem_truoc,
          f"tồn {ton_truoc} -> {ton_sau}; số bản ghi {dem_truoc} -> {dem_sau}")

    dung = sum(1 for _, ok in results if ok)
    log(f"=== TỔNG KẾT: {dung}/{len(results)} đúng kỳ vọng ===")
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    log(f"Đã ghi kết quả vào: {OUT_FILE}")


if __name__ == "__main__":
    main()