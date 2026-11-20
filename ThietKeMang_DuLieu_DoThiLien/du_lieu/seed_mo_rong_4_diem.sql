-- =====================================================================
-- Đề tài 22 - Mở rộng từ 2 lên 4 điểm quét (dữ liệu GIẢ)
-- Chạy SAU schema.sql + seed_data.sql. Dùng cho thử tải 4 tiến trình (SV1-11, SV4).
-- Đây cũng là quy trình thật khi thêm điểm quét: khai báo ScanPoints + tài khoản,
-- cắm máy vào cổng dự phòng Fa0/12-13 (VLAN 30) hoặc nối Wi-Fi KHO-QUETMA.
-- Mật khẩu demo: Kho@2026
-- =====================================================================

PRAGMA foreign_keys = ON;

INSERT INTO ScanPoints (scan_point_id, name, location, ip_address) VALUES
 ('SP03', 'Điểm quét 3 - Cổng nhập phụ', 'Khu A - cửa nhận hàng 2', '192.168.30.13'),
 ('SP04', 'Điểm quét 4 - Cổng xuất phụ', 'Khu B - cửa giao hàng 2', '192.168.30.14');

INSERT INTO Users (username, full_name, role, password_hash) VALUES
 ('nv03', 'Đỗ Văn Nhân Viên 3',  'NHANVIEN', 'sha256$s_nv03$6c98ff860a8b1acb103f9d2bb9c02b4ae4d2cd3afeea299f578ca81f8e8fcf77'),
 ('nv04', 'Vũ Thị Nhân Viên 4',  'NHANVIEN', 'sha256$s_nv04$b02e187376e5eb312021dce274e2814f2509e1b82ce65a2eeb27130cc3ea8b09');
