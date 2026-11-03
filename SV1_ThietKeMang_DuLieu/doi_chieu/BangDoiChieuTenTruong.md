# Bảng đối chiếu tên trường – Đề tài 22

- Thời điểm chạy: **2026-10-26 21:18:39**
- Chuẩn: `du_lieu/TuDienDuLieu.csv` (28 tên trường khác nhau, 38 trường trong 6 bảng) + 14 khóa JSON của giao ước API
- Mã SV2: `(chưa cung cấp)` · Mã SV3: `(chưa cung cấp)` · CSDL SV3: `(không đọc)`
- Kết quả: **chưa đối chiếu** – chưa có mã SV2/SV3 (bảng chuẩn sẵn sàng)

| Tên chuẩn | Bảng | SV2 (điểm quét) | SV3 (máy chủ, CSDL) | Kết luận |
|---|---|---|---|---|
| `product_code` | Products, Inventory, Transactions | — | — | Chờ mã SV2/SV3 |
| `product_name` | Products | — | — | Chờ mã SV2/SV3 |
| `unit` | Products | — | — | Chờ mã SV2/SV3 |
| `is_active` | Products, Users, ScanPoints | — | — | Chờ mã SV2/SV3 |
| `quantity` | Inventory, Transactions | — | — | Chờ mã SV2/SV3 |
| `last_txn_id` | Inventory | — | — | Chờ mã SV2/SV3 |
| `updated_at` | Inventory | — | — | Chờ mã SV2/SV3 |
| `txn_id` | Transactions, AuditLog | — | — | Chờ mã SV2/SV3 |
| `txn_type` | Transactions | — | — | Chờ mã SV2/SV3 |
| `username` | Transactions, Users, AuditLog | — | — | Chờ mã SV2/SV3 |
| `scan_point_id` | Transactions, ScanPoints, AuditLog | — | — | Chờ mã SV2/SV3 |
| `client_time` | Transactions | — | — | Chờ mã SV2/SV3 |
| `server_time` | Transactions | — | — | Chờ mã SV2/SV3 |
| `stock_after` | Transactions | — | — | Chờ mã SV2/SV3 |
| `note` | Transactions | — | — | Chờ mã SV2/SV3 |
| `full_name` | Users | — | — | Chờ mã SV2/SV3 |
| `role` | Users | — | — | Chờ mã SV2/SV3 |
| `password_hash` | Users | — | — | Chờ mã SV2/SV3 |
| `created_at` | Users | — | — | Chờ mã SV2/SV3 |
| `name` | ScanPoints | — | — | Chờ mã SV2/SV3 |
| `location` | ScanPoints | — | — | Chờ mã SV2/SV3 |
| `ip_address` | ScanPoints | — | — | Chờ mã SV2/SV3 |
| `log_id` | AuditLog | — | — | Chờ mã SV2/SV3 |
| `log_time` | AuditLog | — | — | Chờ mã SV2/SV3 |
| `action` | AuditLog | — | — | Chờ mã SV2/SV3 |
| `result` | AuditLog | — | — | Chờ mã SV2/SV3 |
| `error_code` | AuditLog | — | — | Chờ mã SV2/SV3 |
| `detail` | AuditLog | — | — | Chờ mã SV2/SV3 |
| `status` | (khóa API) | — | — | Chờ mã SV2/SV3 |
| `error_code` | AuditLog | — | — | Chờ mã SV2/SV3 |
| `message` | (khóa API) | — | — | Chờ mã SV2/SV3 |
| `token` | (khóa API) | — | — | Chờ mã SV2/SV3 |
| `role` | Users | — | — | Chờ mã SV2/SV3 |
| `expires_in` | (khóa API) | — | — | Chờ mã SV2/SV3 |
| `items` | (khóa API) | — | — | Chờ mã SV2/SV3 |
| `count` | (khóa API) | — | — | Chờ mã SV2/SV3 |
| `original` | (khóa API) | — | — | Chờ mã SV2/SV3 |
| `all_match` | (khóa API) | — | — | Chờ mã SV2/SV3 |
| `ton_luu_tru` | (khóa API) | — | — | Chờ mã SV2/SV3 |
| `ton_tinh_lai` | (khóa API) | — | — | Chờ mã SV2/SV3 |
| `chenh_lech` | (khóa API) | — | — | Chờ mã SV2/SV3 |
| `password` | (khóa API) | — | — | Chờ mã SV2/SV3 |

Cách xử lý khi có LỆCH/THIẾU: (1) bên viết mã sửa về tên chuẩn; hoặc (2) nếu nhóm thống nhất đổi chuẩn thì
SV1 sửa `TuDienDuLieu.csv`, `schema.sql`, `05_GiaoUocAPI.md`, tăng phiên bản và ghi `NhatKyThayDoi.md`.
Chạy lại script này đến khi không còn LỆCH.
