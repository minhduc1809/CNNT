-- 06_sync_sv1_sv3_aliases.sql
-- Bo sung cac ma diem quet va tai khoan de dong bo 100% giua SV1, SV2 va SV3.
-- Tranh loi khoa ngoai (Foreign Key Constraint) khi diem quet SP01, SP02 gui giao dich.

USE smart_warehouse;

-- 1. Bo sung ma diem quet SP01, SP02 (theo chuan diem quet cua SV1 va SV2)
INSERT INTO ScanPoints (scan_point_id, scan_point_name) VALUES
('SP01', 'Diem quet kho 01 (VLAN 20 - IP .11)'),
('SP02', 'Diem quet kho 02 (VLAN 20 - IP .12)')
ON DUPLICATE KEY UPDATE
  scan_point_name = VALUES(scan_point_name);

-- 2. Bo sung cac tai khoan nguoi dung dong bo theo Giao uoc API cua SV1
INSERT INTO Users (user_id, username, full_name, role) VALUES
('admin',    'admin',    'Quan tri he thong', 'admin'),
('thukho01', 'thukho01', 'Thu kho chinh',    'warehouse'),
('nv01',     'nv01',     'Nhan vien quet 01', 'employee'),
('nv02',     'nv02',     'Nhan vien quet 02', 'employee'),
('quanly01', 'quanly01', 'Quan ly xem kho',  'viewer')
ON DUPLICATE KEY UPDATE
  full_name = VALUES(full_name),
  role = VALUES(role);

-- 3. Kiem tra lai so luong du lieu
SELECT 'ScanPoints' AS bang, COUNT(*) AS so_luong FROM ScanPoints
UNION ALL
SELECT 'Users' AS bang, COUNT(*) AS so_luong FROM Users;
