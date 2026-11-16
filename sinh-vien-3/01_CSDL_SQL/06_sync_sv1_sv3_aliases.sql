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
-- Mat khau SHA-256:
-- admin    : Admin@2026
-- thukho01 : Kho@2026
-- nv01,nv02: Kho@2026
-- quanly01 : View@2026
INSERT INTO Users (user_id, username, full_name, role, password_hash) VALUES
('admin',    'admin',    'Quan tri he thong', 'admin',     'a36aef5a11c4073fbe60314fc9df530a9d5f986533594d1f5190742ff9e0e408'),
('thukho01', 'thukho01', 'Thu kho chinh',    'warehouse', 'ee16ffb887af634aac40042af9bd9eeef0692617e531987d43df6cb55279b7a5'),
('nv01',     'nv01',     'Nhan vien quet 01', 'employee',  'ee16ffb887af634aac40042af9bd9eeef0692617e531987d43df6cb55279b7a5'),
('nv02',     'nv02',     'Nhan vien quet 02', 'employee',  'ee16ffb887af634aac40042af9bd9eeef0692617e531987d43df6cb55279b7a5'),
('quanly01', 'quanly01', 'Quan ly xem kho',  'viewer',    '9f9f20ec6958d3c176c17ea3eb9731b053b6fc753367e3c25e3fb2578ec0f4e6')
ON DUPLICATE KEY UPDATE
  full_name     = VALUES(full_name),
  role          = VALUES(role),
  password_hash = VALUES(password_hash);

-- 3. Kiem tra lai so luong du lieu
SELECT 'ScanPoints' AS bang, COUNT(*) AS so_luong FROM ScanPoints
UNION ALL
SELECT 'Users' AS bang, COUNT(*) AS so_luong FROM Users;
