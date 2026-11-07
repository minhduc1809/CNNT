"""
SV3 – MÁY CHỦ XỬ LÝ GIAO DỊCH KHO HÀNG THÔNG MINH (ĐỀ TÀI 22)
Phân quyền 3 tầng:
  1. Tầng dịch vụ API (RBAC theo vai trò người dùng trong MySQL):
     - admin: Toàn quyền (nhập, xuất, xem tồn, xem user)
     - warehouse: Thủ kho (nhập, xuất, xem tồn)
     - employee: Nhân viên (chỉ được nhập kho, xem tồn - cấm xuất kho)
     - viewer: Chỉ xem (cấm mọi thao tác ghi - 403 Forbidden)
  2. Tầng CSDL MySQL:
     - Dịch vụ kết nối bằng tài khoản đặc quyền tối thiểu 'wh_store'
     - Thực thi cập nhật kho qua Stored Procedure sp_warehouse_transaction (ACID, chống âm kho, chống trùng)
  3. Tầng hệ thống:
     - Kiểm soát lỗi, xác thực tham số đầu vào và mã lỗi đồng bộ
"""

import os
from datetime import datetime
from flask import Flask, request, jsonify
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

# ----------------------------------------------------------------------
# 1. Cấu hình kết nối MySQL (Dùng tài khoản tối thiểu wh_store)
# ----------------------------------------------------------------------
load_dotenv()
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "wh_store")
DB_PASS = os.getenv("DB_PASS", "StoreUser@2026")
DB_NAME = os.getenv("DB_NAME", "smart_warehouse")


def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=True,
    )


app = Flask(__name__)


# ----------------------------------------------------------------------
# 2. Ma trận phân quyền tầng ứng dụng (RBAC)
# ----------------------------------------------------------------------
ROLE_PERMISSIONS = {
    "admin": {
        "can_import": True,
        "can_export": True,
        "can_view": True,
        "can_manage_users": True,
    },
    "warehouse": {
        "can_import": True,
        "can_export": True,
        "can_view": True,
        "can_manage_users": False,
    },
    "employee": {
        "can_import": True,
        "can_export": False,  # Nhân viên quét chỉ được nhập, không được xuất
        "can_view": True,
        "can_manage_users": False,
    },
    "viewer": {
        "can_import": False,  # Chỉ xem, cấm ghi
        "can_export": False,
        "can_view": True,
        "can_manage_users": False,
    },
}


def get_user_info(user_id_or_username: str):
    """Truy vấn vai trò người dùng trực tiếp từ bảng users trong MySQL"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, username, full_name, role FROM users WHERE user_id = %s OR username = %s",
                (user_id_or_username, user_id_or_username),
            )
            return cur.fetchone()
    finally:
        conn.close()


def extract_current_user():
    """Lấy thông tin người dùng từ Header Authorization (Bearer) hoặc payload JSON"""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        # Hỗ trợ token định dạng: token-{user_id}-{role}
        parts = token.split("-")
        if len(parts) >= 2:
            user_id = parts[1]
            user = get_user_info(user_id)
            if user:
                return user

    # Fallback kiểm tra trong body JSON
    if request.is_json:
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id") or data.get("username")
        if user_id:
            user = get_user_info(user_id)
            if user:
                return user

    return None


# ======================================================================
# 3. Endpoint Xác thực / Đăng nhập (POST /api/login)
# ======================================================================
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error_code": "INVALID_REQUEST", "message": "Yêu cầu phải có dữ liệu JSON"}), 400

    username = data.get("username", "").strip()
    user = get_user_info(username)

    if not user:
        return jsonify({"error_code": "LOGIN_FAILED", "message": f"Không tìm thấy tài khoản '{username}'"}), 401

    token = f"token-{user['user_id']}-{user['role']}"
    return jsonify({
        "status": "OK",
        "token": token,
        "user_id": user["user_id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
        "permissions": ROLE_PERMISSIONS.get(user["role"], {}),
    }), 200


# ======================================================================
# 4. Endpoint Ghi Giao dịch Kho (POST /api/transactions)
#    Có kiểm tra phân quyền chặt chẽ trước khi gọi Stored Procedure
# ======================================================================
@app.route("/api/transactions", methods=["POST"])
def receive_transaction():
    payload = request.get_json()
    if not payload:
        return jsonify({"error_code": "NO_PAYLOAD", "message": "Không có JSON payload"}), 400

    # 1. Kiểm tra các trường bắt buộc
    required = ["scan_point_id", "txn_id", "product_code", "txn_type", "quantity"]
    missing = [k for k in required if k not in payload]
    if missing:
        return jsonify({"error_code": "MISSING_FIELDS", "message": f"Thiếu trường: {', '.join(missing)}"}), 400

    # 2. Chuẩn hóa loại giao dịch
    txn_type_map = {"NHAP": "IMPORT", "XUAT": "EXPORT", "IMPORT": "IMPORT", "EXPORT": "EXPORT"}
    raw_type = payload["txn_type"].strip().upper()
    db_type = txn_type_map.get(raw_type)
    if not db_type:
        return jsonify({"error_code": "INVALID_TXN_TYPE", "message": "Loại giao dịch phải là 'NHAP' hoặc 'XUAT'"}), 400

    # 3. Kiểm tra số lượng
    try:
        qty = int(payload["quantity"])
        if qty <= 0 or qty > 10000:
            return jsonify({"error_code": "INVALID_QUANTITY", "message": "Số lượng phải là số nguyên dương từ 1 đến 10000"}), 400
    except (ValueError, TypeError):
        return jsonify({"error_code": "INVALID_QUANTITY", "message": "Số lượng phải là số nguyên"}), 400

    # 4. Xác định người dùng & KIỂM TRA PHÂN QUYỀN
    user = extract_current_user()
    if not user:
        default_user_id = payload.get("user_id", "TK01")
        user = get_user_info(default_user_id)
        if not user:
            return jsonify({"error_code": "UNAUTHORIZED", "message": "Không xác định được người dùng thực hiện"}), 401

    role = user["role"]
    perms = ROLE_PERMISSIONS.get(role, {})

    # Quyền kiểm tra: viewer bị cấm hoàn toàn
    if not perms.get("can_import") and not perms.get("can_export"):
        return jsonify({
            "error_code": "FORBIDDEN",
            "message": f"Tài khoản '{user['username']}' thuộc vai trò '{role}' chỉ có quyền xem, bị cấm ghi giao dịch kho!"
        }), 403

    # Quyền kiểm tra: nhân viên cố tình xuất kho
    if db_type == "EXPORT" and not perms.get("can_export"):
        return jsonify({
            "error_code": "FORBIDDEN",
            "message": f"Tài khoản '{user['username']}' thuộc vai trò '{role}' không có quyền xuất kho (EXPORT)!"
        }), 403

    # 5. Gọi Stored Procedure thông qua tài khoản wh_store
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.callproc("sp_warehouse_transaction", (
                payload["txn_id"],
                payload["product_code"],
                db_type,
                qty,
                user["user_id"],
                payload["scan_point_id"],
            ))

            # Lấy tồn kho sau khi giao dịch thành công
            cur.execute("SELECT quantity FROM inventory WHERE product_id = %s", (payload["product_code"],))
            inv = cur.fetchone()
            stock_after = inv["quantity"] if inv else 0

        return jsonify({
            "status": "OK",
            "message": "Giao dịch đã lưu thành công",
            "txn_id": payload["txn_id"],
            "stock_after": stock_after,
            "operator": {
                "user_id": user["user_id"],
                "role": user["role"],
            }
        }), 201

    except pymysql.MySQLError as e:
        err_msg = str(e)
        # Bắt các thông điệp SIGNAL từ Stored Procedure
        if "Ma giao dich da ton tai" in err_msg:
            return jsonify({"error_code": "DUPLICATE_TXN", "message": f"Mã giao dịch '{payload['txn_id']}' đã tồn tại"}), 409
        elif "Ton kho khong du de xuat" in err_msg:
            return jsonify({"error_code": "INSUFFICIENT_STOCK", "message": "Tồn kho không đủ để xuất"}), 400
        elif "Khong tim thay san pham" in err_msg:
            return jsonify({"error_code": "PRODUCT_NOT_FOUND", "message": f"Không tìm thấy sản phẩm '{payload['product_code']}'"}), 404
        elif "Khong tim thay diem quet" in err_msg:
            return jsonify({"error_code": "SCAN_POINT_NOT_FOUND", "message": f"Không tìm thấy điểm quét '{payload['scan_point_id']}'"}), 404
        elif "Khong tim thay nguoi dung" in err_msg:
            return jsonify({"error_code": "USER_NOT_FOUND", "message": f"Không tìm thấy người dùng '{user['user_id']}'"}), 404
        else:
            return jsonify({"error_code": "DB_ERROR", "message": err_msg}), 500
    finally:
        conn.close()


# ======================================================================
# 5. Các Endpoint Đọc Dữ Liệu (GET)
# ======================================================================
@app.route("/api/transactions/<txn_id>", methods=["GET"])
def get_transaction(txn_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM warehouse_transactions WHERE transaction_id = %s", (txn_id,))
            row = cur.fetchone()
    finally:
        conn.close()

    if row:
        if row.get("transaction_time"):
            row["transaction_time"] = row["transaction_time"].isoformat()
        return jsonify(row), 200
    return jsonify({"error_code": "NOT_FOUND", "message": "Không tìm thấy giao dịch"}), 404


@app.route("/api/transactions/recent", methods=["GET"])
def recent():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT transaction_id, product_id, transaction_type, quantity, transaction_time, user_id, scan_point_id
                FROM warehouse_transactions
                ORDER BY transaction_time DESC LIMIT 10
            """)
            rows = cur.fetchall()
            for r in rows:
                if r.get("transaction_time"):
                    r["transaction_time"] = r["transaction_time"].isoformat()
    finally:
        conn.close()
    return jsonify(rows), 200


@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT i.product_id, p.product_name, p.unit, i.quantity, i.updated_at
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                ORDER BY i.product_id
            """)
            rows = cur.fetchall()
            for r in rows:
                if r.get("updated_at"):
                    r["updated_at"] = r["updated_at"].isoformat()
    finally:
        conn.close()
    return jsonify(rows), 200


@app.route("/api/inventory/<product_id>", methods=["GET"])
def get_product_inventory(product_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT i.product_id, p.product_name, p.unit, i.quantity, i.updated_at
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                WHERE i.product_id = %s
            """, (product_id,))
            row = cur.fetchone()
    finally:
        conn.close()

    if row:
        if row.get("updated_at"):
            row["updated_at"] = row["updated_at"].isoformat()
        return jsonify(row), 200
    return jsonify({"error_code": "NOT_FOUND", "message": "Không tìm thấy sản phẩm"}), 404


@app.route("/api/users", methods=["GET"])
def list_users():
    """Chỉ tài khoản admin mới có quyền xem danh sách người dùng"""
    user = extract_current_user()
    if not user or user["role"] != "admin":
        return jsonify({"error_code": "FORBIDDEN", "message": "Chỉ quản trị viên mới có quyền xem danh sách người dùng!"}), 403

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, username, full_name, role FROM users")
            rows = cur.fetchall()
    finally:
        conn.close()
    return jsonify(rows), 200


# ======================================================================
if __name__ == "__main__":
    print("=" * 65)
    print("  SV3 Server - Smart Warehouse API (Phiên bản Phân Quyền 3 Tầng)")
    print(f"  DB User (Tối thiểu): {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    print("  Listening at http://0.0.0.0:5000")
    print("=" * 65)
    app.run(host="0.0.0.0", port=5000, debug=False)
