-- SV4 - Thêm điểm quét SP03, SP04 vào MySQL để thử tải 4 điểm quét (dữ liệu giả).
-- Bản MySQL tương đương seed_mo_rong_4_diem.sql của SV1 (bản đó viết cho SQLite nên không chạy được trên MySQL).
-- Chạy trong MySQL Workbench (tài khoản root). Chạy lại nhiều lần vẫn an toàn.
USE smart_warehouse;

INSERT INTO ScanPoints (scan_point_id, scan_point_name) VALUES
('SP03', 'Diem quet kho 03 (thu tai)'),
('SP04', 'Diem quet kho 04 (thu tai)')
ON DUPLICATE KEY UPDATE scan_point_name = VALUES(scan_point_name);

SELECT scan_point_id, scan_point_name FROM ScanPoints ORDER BY scan_point_id;
