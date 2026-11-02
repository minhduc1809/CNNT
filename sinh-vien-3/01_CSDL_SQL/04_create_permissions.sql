-- 04_create_permissions.sql
-- Phan quyen theo dung cac GRANT da xac nhan trong MySQL Workbench.
-- Yeu cau: cac tai khoan MySQL wh_admin, wh_store, wh_employee, wh_viewer da ton tai.
-- Chay bang root/admin.

USE smart_warehouse;

GRANT ALL PRIVILEGES ON smart_warehouse.*
TO 'wh_admin'@'localhost';

GRANT SELECT ON smart_warehouse.*
TO 'wh_viewer'@'localhost';

GRANT SELECT ON smart_warehouse.Inventory
TO 'wh_employee'@'localhost';
GRANT SELECT ON smart_warehouse.Products
TO 'wh_employee'@'localhost';
GRANT SELECT ON smart_warehouse.warehouse_transactions
TO 'wh_employee'@'localhost';

GRANT SELECT ON smart_warehouse.Inventory
TO 'wh_store'@'localhost';
GRANT SELECT ON smart_warehouse.Products
TO 'wh_store'@'localhost';
GRANT SELECT ON smart_warehouse.ScanPoints
TO 'wh_store'@'localhost';
GRANT SELECT ON smart_warehouse.Users
TO 'wh_store'@'localhost';
GRANT SELECT ON smart_warehouse.warehouse_transactions
TO 'wh_store'@'localhost';
GRANT EXECUTE ON PROCEDURE smart_warehouse.sp_warehouse_transaction
TO 'wh_store'@'localhost';

FLUSH PRIVILEGES;

-- Kiem tra:
-- SHOW GRANTS FOR 'wh_admin'@'localhost';
-- SHOW GRANTS FOR 'wh_store'@'localhost';
-- SHOW GRANTS FOR 'wh_employee'@'localhost';
-- SHOW GRANTS FOR 'wh_viewer'@'localhost';
