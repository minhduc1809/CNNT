# 02 - SAO LƯU VÀ KHÔI PHỤC CƠ SỞ DỮ LIỆU

## 1. Giới thiệu

Thư mục này lưu trữ file sao lưu cơ sở dữ liệu `smart_warehouse` và phục vụ quá trình kiểm tra khả năng khôi phục dữ liệu khi xảy ra sự cố.

## 2. File lưu trữ

- `smart_warehouse_backup_2026-11-02.sql`: File sao lưu cơ sở dữ liệu tại thời điểm thực hiện Backup.

## 3. Công cụ sử dụng

- MySQL Server
- MySQL Workbench
- Chức năng Data Export và Data Import

## 4. Quy trình sao lưu

1. Kết nối MySQL bằng tài khoản có quyền quản trị phù hợp.
2. Chọn cơ sở dữ liệu `smart_warehouse`.
3. Sử dụng chức năng Data Export.
4. Xuất toàn bộ các bảng và đối tượng cần thiết thành file SQL.
5. Lưu file backup vào thư mục quy định.

## 5. Quy trình khôi phục

1. Mở MySQL Workbench.
2. Tạo cơ sở dữ liệu kiểm tra riêng, ví dụ `smart_warehouse_restore_test`.
3. Sử dụng chức năng Data Import để nhập file backup.
4. Kiểm tra dữ liệu sau khi khôi phục.
5. Đối chiếu số lượng bản ghi và tổng số lượng tồn kho giữa cơ sở dữ liệu gốc và cơ sở dữ liệu khôi phục.

## 6. Kết quả kiểm thử

Đã thực hiện quá trình sao lưu và khôi phục cơ sở dữ liệu. Kết quả đối chiếu dữ liệu giữa bản gốc và bản khôi phục cho thấy các dữ liệu kiểm tra trùng khớp.

## 7. Mục đích

Đảm bảo dữ liệu kho hàng có thể được khôi phục khi xảy ra sự cố, hạn chế nguy cơ mất dữ liệu và hỗ trợ duy trì hoạt động của hệ thống.
