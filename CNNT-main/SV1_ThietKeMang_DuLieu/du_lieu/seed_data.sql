-- =====================================================================
-- Đề tài 22 - Dữ liệu mẫu (dữ liệu GIẢ, chỉ dùng cho mô phỏng/kiểm thử)
-- Chạy sau schema.sql
-- Mật khẩu demo của mọi tài khoản: Kho@2026
-- password_hash = 'sha256$' || salt || '$' || SHA-256(salt || ':' || mật_khẩu), salt = 's_' || username
-- =====================================================================

PRAGMA foreign_keys = ON;

INSERT INTO Users (username, full_name, role, password_hash) VALUES
 ('admin',    'Quản trị hệ thống',     'ADMIN',    'sha256$s_admin$effe9d4b00950755cf593820432c65d535d0a35e78254a63411de2cfe3346990'),
 ('thukho01', 'Nguyễn Văn Thủ Kho',    'THUKHO',   'sha256$s_thukho01$4d860d07ffed9612100c1ce069ba58e068de9507d8a6d5378b9d1a5d31556c63'),
 ('nv01',     'Trần Thị Nhân Viên 1',  'NHANVIEN', 'sha256$s_nv01$325765f49b9b28cf669cb5ddfd80795a8681ccee8fb8436fedff31d500e9efee'),
 ('nv02',     'Lê Văn Nhân Viên 2',    'NHANVIEN', 'sha256$s_nv02$d1f5520b50d409d7949275d736574bf961618ea8a8df1646930c634494056602'),
 ('quanly01', 'Phạm Thị Quản Lý',      'QUANLY',   'sha256$s_quanly01$f5d618669d1e5ad2ad18f2f26205dc95606891572a5aef47f756d72cc480b752');

INSERT INTO ScanPoints (scan_point_id, name, location, ip_address) VALUES
 ('SP01', 'Điểm quét 1 - Cổng nhập', 'Khu A - cửa nhận hàng', '192.168.30.11'),
 ('SP02', 'Điểm quét 2 - Cổng xuất', 'Khu B - cửa giao hàng', '192.168.30.12');

INSERT INTO Products (product_code, product_name, unit) VALUES
 ('SP001', 'Nước suối 500ml',       'thùng'),
 ('SP002', 'Mì ăn liền gói',        'thùng'),
 ('SP003', 'Giấy A4 70gsm',         'ram'),
 ('SP004', 'Băng keo trong 5cm',    'cuộn'),
 ('SP005', 'Thùng carton 40x30x30', 'cái');

-- Tồn đầu kỳ được tạo bằng giao dịch NHAP (không ghi thẳng vào Inventory)
-- để luôn giữ bất biến: Inventory.quantity = Σ NHAP - Σ XUAT
INSERT INTO Inventory (product_code, quantity, last_txn_id) VALUES
 ('SP001', 100, 'INIT-SP001'),
 ('SP002',  50, 'INIT-SP002'),
 ('SP003', 200, 'INIT-SP003'),
 ('SP004',  80, 'INIT-SP004'),
 ('SP005',   0, NULL);

INSERT INTO Transactions (txn_id, product_code, txn_type, quantity, username, scan_point_id, client_time, stock_after, note) VALUES
 ('INIT-SP001', 'SP001', 'NHAP', 100, 'thukho01', 'SP01', '2026-10-26T08:00:00', 100, 'Tồn đầu kỳ'),
 ('INIT-SP002', 'SP002', 'NHAP',  50, 'thukho01', 'SP01', '2026-10-26T08:00:00',  50, 'Tồn đầu kỳ'),
 ('INIT-SP003', 'SP003', 'NHAP', 200, 'thukho01', 'SP01', '2026-10-26T08:00:00', 200, 'Tồn đầu kỳ'),
 ('INIT-SP004', 'SP004', 'NHAP',  80, 'thukho01', 'SP01', '2026-10-26T08:00:00',  80, 'Tồn đầu kỳ');
