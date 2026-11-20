# GIAO ƯỚC API CHO DỊCH VỤ MÁY CHỦ (SV3)
**Hệ thống Quản lý Kho Hàng Thông Minh – Đề tài 22**
*Tài liệu bàn giao từ SV2 (Điểm quét) gửi SV3 (Máy chủ CSDL MySQL)*

---

## 1. Nguyên tắc chung
* **Chuẩn giao thức:** HTTP RESTful, định dạng dữ liệu gửi và nhận là `JSON` (UTF-8).
* **Quy ước tên biến:** Toàn bộ hệ thống giữ nguyên 100% theo **Giao ước API v1.0 của SV1**:
  - `txn_id`, `product_code`, `txn_type`, `quantity`, `scan_point_id`, `client_time`.
* **Cơ chế xác thực:**
  - `POST /api/login` trả về Bearer Token.
  - Các request nghiệp vụ sau đó đính kèm Header: `Authorization: Bearer <token>`.
* **Toàn vẹn dữ liệu:**
  - Máy chủ chỉ trả về `201 Created` sau khi đã **COMMIT** giao dịch vào MySQL thành công.

---

## 2. Danh sách 4 Endpoint SV3 cần dựng

### 2.1. Đăng nhập – `POST /api/login`
Dùng để xác thực nhân viên điểm quét và cấp token.

* **Request Body:**
  ```json
  {
    "username": "nv01",
    "password": "Kho@2026"
  }
  ```
* **Response `200 OK`:**
  ```json
  {
    "status": "OK",
    "token": "token-nv01-abc123xyz",
    "username": "nv01",
    "role": "NHANVIEN",
    "message": "Đăng nhập thành công"
  }
  ```
* **Response `401 Unauthorized`:** (nếu sai mật khẩu hoặc tài khoản bị khóa)
  ```json
  {
    "status": "REJECTED",
    "error_code": "LOGIN_FAILED",
    "message": "Sai tài khoản hoặc mật khẩu"
  }
  ```

---

### 2.2. Ghi nhận giao dịch – `POST /api/transactions`
Điểm quét gửi thông tin nhập hoặc xuất kho lên máy chủ.

* **Headers:**
  - `Content-Type: application/json`
  - `Authorization: Bearer <token>`
* **Request Body (Chuẩn SV1):**
  ```json
  {
    "txn_id": "SP01-20261103-0001",
    "product_code": "SP001",
    "txn_type": "NHAP",
    "quantity": 10,
    "scan_point_id": "SP01",
    "client_time": "2026-11-03T09:40:00"
  }
  ```
  *(Lưu ý: `txn_type` chỉ nhận `"NHAP"` hoặc `"XUAT"`; `quantity` là số nguyên > 0).*

* **Response `201 Created` (Ghi thành công):**
  ```json
  {
    "status": "OK",
    "txn_id": "SP01-20261103-0001",
    "product_code": "SP001",
    "stock_after": 110,
    "server_time": "2026-11-03T09:40:02"
  }
  ```

* **Response `409 Conflict` (Chống trùng giao dịch - Ca KT2):**
  *(Nếu `txn_id` này đã có trong CSDL, không được cộng/trừ tồn kho lần 2, trả về 409)*
  ```json
  {
    "status": "REJECTED",
    "error_code": "DUPLICATE_TXN",
    "message": "Mã giao dịch đã được ghi trước đó",
    "original": {
      "stock_after": 110,
      "server_time": "2026-11-03T09:40:02"
    }
  }
  ```

* **Response `422 Unprocessable Entity` (Xuất vượt quá tồn kho):**
  ```json
  {
    "status": "REJECTED",
    "error_code": "INSUFFICIENT_STOCK",
    "message": "Tồn kho không đủ để xuất"
  }
  ```

* **Response `404 Not Found` (Mã hàng không có trong danh mục):**
  ```json
  {
    "status": "REJECTED",
    "error_code": "PRODUCT_NOT_FOUND",
    "message": "Không tìm thấy mã hàng trong hệ thống"
  }
  ```

---

### 2.3. Đọc lại chi tiết 1 giao dịch – `GET /api/transactions/{txn_id}`
Phục vụ máy khách điểm quét xác minh dữ liệu đã thực sự lưu vào CSDL (Mã việc `CV02`).

* **Headers:** `Authorization: Bearer <token>`
* **Response `200 OK`:**
  ```json
  {
    "status": "OK",
    "txn_id": "SP01-20261103-0001",
    "product_code": "SP001",
    "txn_type": "NHAP",
    "quantity": 10,
    "scan_point_id": "SP01",
    "username": "nv01",
    "stock_after": 110,
    "client_time": "2026-11-03T09:40:00",
    "server_time": "2026-11-03T09:40:02"
  }
  ```
* **Response `404 Not Found`:** (nếu giao dịch chưa được lưu)
  ```json
  {
    "status": "REJECTED",
    "error_code": "TXN_NOT_FOUND",
    "message": "Chưa có giao dịch này trên máy chủ"
  }
  ```

---

### 2.4. Tra cứu tồn kho – `GET /api/inventory/{product_code}`
Dùng để kiểm tra nhanh số lượng tồn kho trước và sau khi quét.

* **Headers:** `Authorization: Bearer <token>`
* **Response `200 OK`:**
  ```json
  {
    "status": "OK",
    "product_code": "SP001",
    "quantity": 110
  }
  ```

---

## 3. Hướng dẫn SV3 ánh xạ vào CSDL MySQL `smart_warehouse`

Khi SV3 gọi Stored Procedure hoặc câu lệnh SQL vào MySQL:
1. `txn_id` $\rightarrow$ lưu vào cột `txn_id` (hoặc `transaction_id`).
2. `product_code` $\rightarrow$ lưu vào cột `product_code` (hoặc `product_id`).
3. `txn_type`: Nếu là `"NHAP"` $\rightarrow$ cộng tồn kho; nếu là `"XUAT"` $\rightarrow$ trừ tồn kho.
4. `quantity` $\rightarrow$ lưu vào cột `quantity`.
5. `scan_point_id` $\rightarrow$ lưu vào cột `scan_point_id`.
6. `username` $\rightarrow$ trích xuất từ Bearer token (ví dụ: `nv01`).

---

## 4. Gợi ý code API Server mẫu cho SV3 (Python Flask + PyMySQL)
*SV3 có thể tạo file `app.py` và chạy ngay bằng `python app.py` trên máy chủ:*

```python
from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

def get_db():
    return pymysql.connect(
        host="localhost", user="root", password="your_password",
        database="smart_warehouse", cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json or {}
    u = data.get("username", "nv01")
    return jsonify({"status": "OK", "token": f"token-{u}", "username": u, "role": "NHANVIEN"}), 200

@app.route("/api/transactions", methods=["POST"])
def post_txn():
    data = request.json or {}
    txn_id = data.get("txn_id")
    p_code = data.get("product_code")
    t_type = data.get("txn_type")
    qty = int(data.get("quantity", 0))
    sp_id = data.get("scan_point_id")

    conn = get_db()
    try:
        with conn.cursor() as cur:
            # 1. Chống trùng
            cur.execute("SELECT * FROM Transactions WHERE txn_id = %s", (txn_id,))
            if cur.fetchone():
                return jsonify({"status": "REJECTED", "error_code": "DUPLICATE_TXN", "message": "Trùng txn_id"}), 409
            
            # 2. Khóa dòng kiểm tra tồn kho
            cur.execute("SELECT quantity FROM Inventory WHERE product_code = %s FOR UPDATE", (p_code,))
            row = cur.fetchone()
            if not row:
                return jsonify({"status": "REJECTED", "error_code": "PRODUCT_NOT_FOUND"}), 404
            
            curr_stock = row["quantity"]
            if t_type == "XUAT" and curr_stock < qty:
                return jsonify({"status": "REJECTED", "error_code": "INSUFFICIENT_STOCK"}), 422
            
            new_stock = curr_stock + qty if t_type == "NHAP" else curr_stock - qty
            cur.execute("UPDATE Inventory SET quantity = %s WHERE product_code = %s", (new_stock, p_code))
            cur.execute(
                "INSERT INTO Transactions (txn_id, product_code, txn_type, quantity, scan_point_id) "
                "VALUES (%s, %s, %s, %s, %s)", (txn_id, p_code, t_type, qty, sp_id)
            )
            conn.commit()
            return jsonify({"status": "OK", "txn_id": txn_id, "stock_after": new_stock}), 201
    finally:
        conn.close()

@app.route("/api/transactions/<txn_id>", methods=["GET"])
def get_txn(txn_id):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Transactions WHERE txn_id = %s", (txn_id,))
            row = cur.fetchone()
            if row:
                return jsonify({"status": "OK", **row}), 200
            return jsonify({"status": "REJECTED", "error_code": "TXN_NOT_FOUND"}), 404
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```
