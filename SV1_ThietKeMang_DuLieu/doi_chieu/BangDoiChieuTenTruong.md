# Bảng đối chiếu tên trường – Đề tài 22

- Thời điểm chạy: **2026-11-09 11:35:06**
- Chuẩn: `du_lieu/TuDienDuLieu.csv` (28 tên trường khác nhau, 38 trường trong 6 bảng) + 14 khóa JSON của giao ước API
- Mã SV2: `E:\CNNT\diem-quet` · Mã SV3: `E:\CNNT\sinh-vien-3` · CSDL SV3: `(không đọc)`
- Kết quả: **38/42 khớp**, 4 cần xử lý

| Tên chuẩn | Bảng | SV2 (điểm quét) | SV3 (máy chủ, CSDL) | Kết luận |
|---|---|---|---|---|
| `product_code` | Products, Inventory, Transactions | ✔ dùng đúng | ✔ dùng đúng · ✘ `product_id` (01_CSDL_SQL\01_create_database.sql:12; 01_CSDL_SQL\01_create_database.sql:20; 01_CSDL_SQL\01_create_database.sql:47) | LỆCH |
| `product_name` | Products | không thấy | ✔ dùng đúng | Khớp |
| `unit` | Products | không thấy | ✔ dùng đúng | Khớp |
| `is_active` | Products, Users, ScanPoints | không thấy | không thấy | Khớp |
| `quantity` | Inventory, Transactions | ✔ dùng đúng | ✔ dùng đúng | Khớp |
| `last_txn_id` | Inventory | không thấy | không thấy | Khớp |
| `updated_at` | Inventory | ✔ dùng đúng | ✔ dùng đúng | Khớp |
| `txn_id` | Transactions, AuditLog | ✔ dùng đúng | ✔ dùng đúng · ✘ `transaction_id` (01_CSDL_SQL\01_create_database.sql:46; 04_DICH_VU_API\app.py:133; 04_DICH_VU_API\test_all_features.py:193) | LỆCH |
| `txn_type` | Transactions | ✔ dùng đúng | ✔ dùng đúng · ✘ `transaction_type` (04_DICH_VU_API\app.py:137; 04_DICH_VU_API\test_all_features.py:193; 04_DICH_VU_API\test_unit.py:107) | LỆCH |
| `username` | Transactions, Users, AuditLog | ✔ dùng đúng | ✔ dùng đúng · ✘ `user_id` (01_CSDL_SQL\01_create_database.sql:31; 01_CSDL_SQL\01_create_database.sql:51; 04_DICH_VU_API\app.py:37), `user` (04_DICH_VU_API\config.json:10) | LỆCH |
| `scan_point_id` | Transactions, ScanPoints, AuditLog | ✔ dùng đúng | ✔ dùng đúng | Khớp |
| `client_time` | Transactions | ✔ dùng đúng | ✔ dùng đúng | Khớp |
| `server_time` | Transactions | không thấy | không thấy | Khớp |
| `stock_after` | Transactions | ✔ dùng đúng | ✔ dùng đúng | Khớp |
| `note` | Transactions | ✔ dùng đúng | không thấy | Khớp |
| `full_name` | Users | không thấy | ✔ dùng đúng | Khớp |
| `role` | Users | không thấy | ✔ dùng đúng | Khớp |
| `password_hash` | Users | không thấy | không thấy | Khớp |
| `created_at` | Users | ✔ dùng đúng | không thấy | Khớp |
| `name` | ScanPoints | ✔ dùng đúng | không thấy | Khớp |
| `location` | ScanPoints | không thấy | không thấy | Khớp |
| `ip_address` | ScanPoints | không thấy | không thấy | Khớp |
| `log_id` | AuditLog | không thấy | không thấy | Khớp |
| `log_time` | AuditLog | không thấy | không thấy | Khớp |
| `action` | AuditLog | không thấy | không thấy | Khớp |
| `result` | AuditLog | không thấy | không thấy | Khớp |
| `error_code` | AuditLog | ✔ dùng đúng | ✔ dùng đúng | Khớp |
| `detail` | AuditLog | không thấy | không thấy | Khớp |
| `status` | (khóa API) | ✔ dùng đúng | ✔ dùng đúng | Khớp |
| `error_code` | AuditLog | ✔ dùng đúng | ✔ dùng đúng | Khớp |
| `message` | (khóa API) | ✔ dùng đúng | ✔ dùng đúng | Khớp |
| `token` | (khóa API) | ✔ dùng đúng | ✔ dùng đúng | Khớp |
| `role` | Users | không thấy | ✔ dùng đúng | Khớp |
| `expires_in` | (khóa API) | không thấy | không thấy | Khớp |
| `items` | (khóa API) | ✔ dùng đúng | ✔ dùng đúng | Khớp |
| `count` | (khóa API) | không thấy | không thấy | Khớp |
| `original` | (khóa API) | không thấy | không thấy | Khớp |
| `all_match` | (khóa API) | không thấy | không thấy | Khớp |
| `ton_luu_tru` | (khóa API) | không thấy | không thấy | Khớp |
| `ton_tinh_lai` | (khóa API) | không thấy | không thấy | Khớp |
| `chenh_lech` | (khóa API) | không thấy | không thấy | Khớp |
| `password` | (khóa API) | ✔ dùng đúng | ✔ dùng đúng | Khớp |

Cách xử lý khi có LỆCH/THIẾU: (1) bên viết mã sửa về tên chuẩn; hoặc (2) nếu nhóm thống nhất đổi chuẩn thì
SV1 sửa `TuDienDuLieu.csv`, `schema.sql`, `05_GiaoUocAPI.md`, tăng phiên bản và ghi `NhatKyThayDoi.md`.
Chạy lại script này đến khi không còn LỆCH.
