-- smart_warehouse_v2_all.sql: tao boi tao_v2_sql.py (SV4). CSDL thu rieng, khong phai CSDL chinh.
DROP DATABASE IF EXISTS smart_warehouse_v2;

-- ===== 01_create_database.sql =====
-- 01_create_database.sql
-- Tao CSDL va 5 bang cho he thong quan ly kho.
-- Chay bang tai khoan co quyen CREATE DATABASE/TABLE.

CREATE DATABASE IF NOT EXISTS smart_warehouse_v2
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE smart_warehouse_v2;

CREATE TABLE IF NOT EXISTS Products (
    product_id   VARCHAR(30)  NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    unit         VARCHAR(30)  NOT NULL,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Inventory (
    product_id VARCHAR(30) NOT NULL,
    quantity   INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                         ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id),
    CONSTRAINT fk_inventory_product
      FOREIGN KEY (product_id) REFERENCES Products(product_id),
    CONSTRAINT chk_inventory_nonnegative CHECK (quantity >= 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Users (
    user_id       VARCHAR(30)  NOT NULL,
    username      VARCHAR(60)  NOT NULL,
    full_name     VARCHAR(100) NOT NULL,
    role          ENUM('admin','warehouse','employee','viewer') NOT NULL,
    password_hash VARCHAR(64)  NOT NULL COMMENT 'SHA-256 cua mat khau; khong luu mat khau ro',
    PRIMARY KEY (user_id),
    UNIQUE KEY uq_users_username (username)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ScanPoints (
    scan_point_id   VARCHAR(30)  NOT NULL,
    scan_point_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (scan_point_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS warehouse_transactions (
    transaction_id   VARCHAR(50) NOT NULL,
    product_id       VARCHAR(30) NOT NULL,
    transaction_type ENUM('IMPORT','EXPORT') NOT NULL,
    quantity         INT NOT NULL,
    transaction_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id           VARCHAR(30) NOT NULL,
    scan_point_id     VARCHAR(30) NOT NULL,
    PRIMARY KEY (transaction_id),
    CONSTRAINT chk_transaction_quantity CHECK (quantity > 0),
    CONSTRAINT fk_transaction_product
      FOREIGN KEY (product_id) REFERENCES Products(product_id),
    CONSTRAINT fk_transaction_user
      FOREIGN KEY (user_id) REFERENCES Users(user_id),
    CONSTRAINT fk_transaction_scanpoint
      FOREIGN KEY (scan_point_id) REFERENCES ScanPoints(scan_point_id),
    KEY idx_transaction_product_time (product_id, transaction_time),
    KEY idx_transaction_scanpoint (scan_point_id)
) ENGINE=InnoDB;


-- ===== 02_insert_sample_data.sql =====
-- 02_insert_sample_data.sql
-- Du lieu mau: 100 san pham, ton kho ban dau, 5 tai khoan nghiep vu, 2 diem quet.
-- Neu da co ma trung, du lieu cu duoc giu nguyen.

USE smart_warehouse_v2;

INSERT INTO Products (product_id, product_name, unit) VALUES
('SP001', 'San pham mau 001', 'cai'),
('SP002', 'San pham mau 002', 'cai'),
('SP003', 'San pham mau 003', 'cai'),
('SP004', 'San pham mau 004', 'cai'),
('SP005', 'San pham mau 005', 'cai'),
('SP006', 'San pham mau 006', 'cai'),
('SP007', 'San pham mau 007', 'cai'),
('SP008', 'San pham mau 008', 'cai'),
('SP009', 'San pham mau 009', 'cai'),
('SP010', 'San pham mau 010', 'cai'),
('SP011', 'San pham mau 011', 'cai'),
('SP012', 'San pham mau 012', 'cai'),
('SP013', 'San pham mau 013', 'cai'),
('SP014', 'San pham mau 014', 'cai'),
('SP015', 'San pham mau 015', 'cai'),
('SP016', 'San pham mau 016', 'cai'),
('SP017', 'San pham mau 017', 'cai'),
('SP018', 'San pham mau 018', 'cai'),
('SP019', 'San pham mau 019', 'cai'),
('SP020', 'San pham mau 020', 'cai'),
('SP021', 'San pham mau 021', 'cai'),
('SP022', 'San pham mau 022', 'cai'),
('SP023', 'San pham mau 023', 'cai'),
('SP024', 'San pham mau 024', 'cai'),
('SP025', 'San pham mau 025', 'cai'),
('SP026', 'San pham mau 026', 'cai'),
('SP027', 'San pham mau 027', 'cai'),
('SP028', 'San pham mau 028', 'cai'),
('SP029', 'San pham mau 029', 'cai'),
('SP030', 'San pham mau 030', 'cai'),
('SP031', 'San pham mau 031', 'cai'),
('SP032', 'San pham mau 032', 'cai'),
('SP033', 'San pham mau 033', 'cai'),
('SP034', 'San pham mau 034', 'cai'),
('SP035', 'San pham mau 035', 'cai'),
('SP036', 'San pham mau 036', 'cai'),
('SP037', 'San pham mau 037', 'cai'),
('SP038', 'San pham mau 038', 'cai'),
('SP039', 'San pham mau 039', 'cai'),
('SP040', 'San pham mau 040', 'cai'),
('SP041', 'San pham mau 041', 'cai'),
('SP042', 'San pham mau 042', 'cai'),
('SP043', 'San pham mau 043', 'cai'),
('SP044', 'San pham mau 044', 'cai'),
('SP045', 'San pham mau 045', 'cai'),
('SP046', 'San pham mau 046', 'cai'),
('SP047', 'San pham mau 047', 'cai'),
('SP048', 'San pham mau 048', 'cai'),
('SP049', 'San pham mau 049', 'cai'),
('SP050', 'San pham mau 050', 'cai'),
('SP051', 'San pham mau 051', 'cai'),
('SP052', 'San pham mau 052', 'cai'),
('SP053', 'San pham mau 053', 'cai'),
('SP054', 'San pham mau 054', 'cai'),
('SP055', 'San pham mau 055', 'cai'),
('SP056', 'San pham mau 056', 'cai'),
('SP057', 'San pham mau 057', 'cai'),
('SP058', 'San pham mau 058', 'cai'),
('SP059', 'San pham mau 059', 'cai'),
('SP060', 'San pham mau 060', 'cai'),
('SP061', 'San pham mau 061', 'cai'),
('SP062', 'San pham mau 062', 'cai'),
('SP063', 'San pham mau 063', 'cai'),
('SP064', 'San pham mau 064', 'cai'),
('SP065', 'San pham mau 065', 'cai'),
('SP066', 'San pham mau 066', 'cai'),
('SP067', 'San pham mau 067', 'cai'),
('SP068', 'San pham mau 068', 'cai'),
('SP069', 'San pham mau 069', 'cai'),
('SP070', 'San pham mau 070', 'cai'),
('SP071', 'San pham mau 071', 'cai'),
('SP072', 'San pham mau 072', 'cai'),
('SP073', 'San pham mau 073', 'cai'),
('SP074', 'San pham mau 074', 'cai'),
('SP075', 'San pham mau 075', 'cai'),
('SP076', 'San pham mau 076', 'cai'),
('SP077', 'San pham mau 077', 'cai'),
('SP078', 'San pham mau 078', 'cai'),
('SP079', 'San pham mau 079', 'cai'),
('SP080', 'San pham mau 080', 'cai'),
('SP081', 'San pham mau 081', 'cai'),
('SP082', 'San pham mau 082', 'cai'),
('SP083', 'San pham mau 083', 'cai'),
('SP084', 'San pham mau 084', 'cai'),
('SP085', 'San pham mau 085', 'cai'),
('SP086', 'San pham mau 086', 'cai'),
('SP087', 'San pham mau 087', 'cai'),
('SP088', 'San pham mau 088', 'cai'),
('SP089', 'San pham mau 089', 'cai'),
('SP090', 'San pham mau 090', 'cai'),
('SP091', 'San pham mau 091', 'cai'),
('SP092', 'San pham mau 092', 'cai'),
('SP093', 'San pham mau 093', 'cai'),
('SP094', 'San pham mau 094', 'cai'),
('SP095', 'San pham mau 095', 'cai'),
('SP096', 'San pham mau 096', 'cai'),
('SP097', 'San pham mau 097', 'cai'),
('SP098', 'San pham mau 098', 'cai'),
('SP099', 'San pham mau 099', 'cai'),
('SP100', 'San pham mau 100', 'cai')
ON DUPLICATE KEY UPDATE
  product_name = VALUES(product_name),
  unit = VALUES(unit);

INSERT INTO Inventory (product_id, quantity) VALUES
('SP001', 11),
('SP002', 12),
('SP003', 13),
('SP004', 14),
('SP005', 15),
('SP006', 16),
('SP007', 17),
('SP008', 18),
('SP009', 19),
('SP010', 20),
('SP011', 21),
('SP012', 22),
('SP013', 23),
('SP014', 24),
('SP015', 25),
('SP016', 26),
('SP017', 27),
('SP018', 28),
('SP019', 29),
('SP020', 10),
('SP021', 11),
('SP022', 12),
('SP023', 13),
('SP024', 14),
('SP025', 15),
('SP026', 16),
('SP027', 17),
('SP028', 18),
('SP029', 19),
('SP030', 20),
('SP031', 21),
('SP032', 22),
('SP033', 23),
('SP034', 24),
('SP035', 25),
('SP036', 26),
('SP037', 27),
('SP038', 28),
('SP039', 29),
('SP040', 10),
('SP041', 11),
('SP042', 12),
('SP043', 13),
('SP044', 14),
('SP045', 15),
('SP046', 16),
('SP047', 17),
('SP048', 18),
('SP049', 19),
('SP050', 20),
('SP051', 21),
('SP052', 22),
('SP053', 23),
('SP054', 24),
('SP055', 25),
('SP056', 26),
('SP057', 27),
('SP058', 28),
('SP059', 29),
('SP060', 10),
('SP061', 11),
('SP062', 12),
('SP063', 13),
('SP064', 14),
('SP065', 15),
('SP066', 16),
('SP067', 17),
('SP068', 18),
('SP069', 19),
('SP070', 20),
('SP071', 21),
('SP072', 22),
('SP073', 23),
('SP074', 24),
('SP075', 25),
('SP076', 26),
('SP077', 27),
('SP078', 28),
('SP079', 29),
('SP080', 10),
('SP081', 11),
('SP082', 12),
('SP083', 13),
('SP084', 14),
('SP085', 15),
('SP086', 16),
('SP087', 17),
('SP088', 18),
('SP089', 19),
('SP090', 20),
('SP091', 21),
('SP092', 22),
('SP093', 23),
('SP094', 24),
('SP095', 25),
('SP096', 26),
('SP097', 27),
('SP098', 28),
('SP099', 29),
('SP100', 10)
ON DUPLICATE KEY UPDATE
  quantity = Inventory.quantity;

-- Mat khau: SHA-256 khong muoi.
-- AD01/admin_demo   : Admin@2026
-- NV01/nhanvien_demo: Kho@2026
-- NV02/nv02_demo    : Kho@2026
-- TK01/thukho_demo  : Kho@2026
-- VIEW01/viewer_demo: View@2026
INSERT INTO Users (user_id, username, full_name, role, password_hash) VALUES
('AD01',   'admin_demo',    'Quan tri vien mau', 'admin',     'a36aef5a11c4073fbe60314fc9df530a9d5f986533594d1f5190742ff9e0e408'),
('NV01',   'nhanvien_demo', 'Nhan vien mau',     'employee',  'ee16ffb887af634aac40042af9bd9eeef0692617e531987d43df6cb55279b7a5'),
('NV02',   'nv02_demo',     'Nhan vien mau 2',   'employee',  'ee16ffb887af634aac40042af9bd9eeef0692617e531987d43df6cb55279b7a5'),
('TK01',   'thukho_demo',   'Thu kho mau',       'warehouse', 'ee16ffb887af634aac40042af9bd9eeef0692617e531987d43df6cb55279b7a5'),
('VIEW01', 'viewer_demo',   'Tai khoan chi xem', 'viewer',    '9f9f20ec6958d3c176c17ea3eb9731b053b6fc753367e3c25e3fb2578ec0f4e6')
ON DUPLICATE KEY UPDATE
  username      = VALUES(username),
  full_name     = VALUES(full_name),
  role          = VALUES(role),
  password_hash = VALUES(password_hash);

INSERT INTO ScanPoints (scan_point_id, scan_point_name) VALUES
('SCAN01', 'Diem quet kho 01'),
('SCAN02', 'Diem quet kho 02')
ON DUPLICATE KEY UPDATE
  scan_point_name = VALUES(scan_point_name);

-- Kiem tra so luong du lieu
SELECT 'Products' AS table_name, COUNT(*) AS total FROM Products
UNION ALL
SELECT 'Inventory', COUNT(*) FROM Inventory
UNION ALL
SELECT 'Users', COUNT(*) FROM Users
UNION ALL
SELECT 'ScanPoints', COUNT(*) FROM ScanPoints;


-- ===== 03_create_procedure.sql =====
-- 03_create_procedure.sql
-- Thu tuc nhap/xuat kho co transaction, khoa dong ton kho va chan ma giao dich trung.
-- Quy uoc transaction_type: IMPORT hoac EXPORT.
-- Luu y: neu ung dung hien tai goi thu tuc voi bo tham so khac,
-- can dong bo lai API/ung dung theo chu ky ben duoi.

USE smart_warehouse_v2;

DROP PROCEDURE IF EXISTS sp_warehouse_transaction;

DELIMITER $$

CREATE PROCEDURE sp_warehouse_transaction(
    IN p_transaction_id VARCHAR(50),
    IN p_product_id VARCHAR(30),
    IN p_transaction_type VARCHAR(10),
    IN p_quantity INT,
    IN p_user_id VARCHAR(30),
    IN p_scan_point_id VARCHAR(30)
)
BEGIN
    DECLARE v_exists INT DEFAULT 0;
    DECLARE v_stock INT DEFAULT 0;
    DECLARE v_type VARCHAR(10);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    SET v_type = UPPER(TRIM(p_transaction_type));

    IF p_transaction_id IS NULL OR TRIM(p_transaction_id) = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'transaction_id khong duoc de trong';
    END IF;

    IF p_quantity IS NULL OR p_quantity <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'So luong phai lon hon 0';
    END IF;

    IF v_type NOT IN ('IMPORT', 'EXPORT') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Loai giao dich phai la IMPORT hoac EXPORT';
    END IF;

    START TRANSACTION;

    SELECT COUNT(*) INTO v_exists
    FROM warehouse_transactions
    WHERE transaction_id = p_transaction_id;

    IF v_exists > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ma giao dich da ton tai';
    END IF;

    SELECT quantity INTO v_stock
    FROM Inventory
    WHERE product_id = p_product_id
    FOR UPDATE;

    IF v_stock IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Khong tim thay san pham trong Inventory';
    END IF;

    IF v_type = 'EXPORT' AND v_stock < p_quantity THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ton kho khong du de xuat';
    END IF;

    INSERT INTO warehouse_transactions
      (transaction_id, product_id, transaction_type, quantity,
       transaction_time, user_id, scan_point_id)
    VALUES
      (p_transaction_id, p_product_id, v_type, p_quantity,
       CURRENT_TIMESTAMP, p_user_id, p_scan_point_id);

    IF v_type = 'IMPORT' THEN
        UPDATE Inventory
        SET quantity = quantity + p_quantity
        WHERE product_id = p_product_id;
    ELSE
        UPDATE Inventory
        SET quantity = quantity - p_quantity
        WHERE product_id = p_product_id;
    END IF;

    COMMIT;
END$$

DELIMITER ;


-- ===== 04_create_permissions.sql =====
-- 04_create_permissions.sql
-- Phan quyen theo dung cac GRANT da xac nhan trong MySQL Workbench.
-- Yeu cau: cac tai khoan MySQL wh_admin, wh_store, wh_employee, wh_viewer da ton tai.
-- Chay bang root/admin.

USE smart_warehouse_v2;

GRANT ALL PRIVILEGES ON smart_warehouse_v2.*
TO 'wh_admin'@'localhost';

GRANT SELECT ON smart_warehouse_v2.*
TO 'wh_viewer'@'localhost';

GRANT SELECT ON smart_warehouse_v2.Inventory
TO 'wh_employee'@'localhost';
GRANT SELECT ON smart_warehouse_v2.Products
TO 'wh_employee'@'localhost';
GRANT SELECT ON smart_warehouse_v2.warehouse_transactions
TO 'wh_employee'@'localhost';

GRANT SELECT ON smart_warehouse_v2.Inventory
TO 'wh_store'@'localhost';
GRANT SELECT ON smart_warehouse_v2.Products
TO 'wh_store'@'localhost';
GRANT SELECT ON smart_warehouse_v2.ScanPoints
TO 'wh_store'@'localhost';
GRANT SELECT ON smart_warehouse_v2.Users
TO 'wh_store'@'localhost';
GRANT SELECT ON smart_warehouse_v2.warehouse_transactions
TO 'wh_store'@'localhost';
GRANT EXECUTE ON PROCEDURE smart_warehouse_v2.sp_warehouse_transaction
TO 'wh_store'@'localhost';

FLUSH PRIVILEGES;

-- Kiem tra:
-- SHOW GRANTS FOR 'wh_admin'@'localhost';
-- SHOW GRANTS FOR 'wh_store'@'localhost';
-- SHOW GRANTS FOR 'wh_employee'@'localhost';
-- SHOW GRANTS FOR 'wh_viewer'@'localhost';


-- ===== 06_sync_sv1_sv3_aliases.sql =====
-- 06_sync_sv1_sv3_aliases.sql
-- Bo sung cac ma diem quet va tai khoan de dong bo 100% giua SV1, SV2 va SV3.
-- Tranh loi khoa ngoai (Foreign Key Constraint) khi diem quet SP01, SP02 gui giao dich.

USE smart_warehouse_v2;

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

