# 01 - CƠ SỞ DỮ LIỆU SQL

## 1. Giới thiệu
Thư mục này chứa các file SQL phục vụ xây dựng và quản lý cơ sở dữ liệu cho hệ thống quản lý kho hàng thông minh (`smart_warehouse`).

Cơ sở dữ liệu được xây dựng trên MySQL, sử dụng MySQL Workbench để thiết kế, quản lý và kiểm thử.

## 2. Danh sách file

| STT | Tên file | Chức năng |
|---|---|---|
| 1 | `01_create_database.sql` | Tạo cơ sở dữ liệu và các bảng |
| 2 | `02_insert_sample_data.sql` | Thêm dữ liệu mẫu |
| 3 | `03_create_procedure.sql` | Tạo thủ tục nhập kho, xuất kho |
| 4 | `04_create_permissions.sql` | Tạo tài khoản và phân quyền |
| 5 | `05_test_transactions.sql` | Kiểm thử các giao dịch kho |

## 3. Các bảng dữ liệu chính

- `Products`: Lưu thông tin sản phẩm.
- `Inventory`: Quản lý số lượng hàng tồn kho.
- `Users`: Lưu thông tin tài khoản người dùng.
- `ScanPoints`: Quản lý các điểm quét hàng hóa.
- `warehouse_transactions`: Lưu lịch sử giao dịch nhập, xuất kho.

## 4. Chức năng chính

- Quản lý thông tin sản phẩm và tồn kho.
- Ghi nhận giao dịch nhập kho, xuất kho.
- Cập nhật số lượng tồn kho sau mỗi giao dịch.
- Kiểm tra giao dịch trùng lặp.
- Ngăn chặn giao dịch xuất kho vượt quá số lượng tồn.
- Phân quyền truy cập theo vai trò người dùng.

## 5. Thứ tự triển khai

Thực hiện các file SQL theo thứ tự từ 01 đến 05 để tạo cấu trúc, thêm dữ liệu, thiết lập thủ tục, phân quyền và kiểm thử hệ thống.

## 6. Công cụ sử dụng

- MySQL Server
- MySQL Workbench
- SQL
