

CREATE USER IF NOT EXISTS 'wh_dump'@'localhost' IDENTIFIED BY '123456';

-- Quyen doc du lieu va cau truc de mysqldump --single-transaction --routines --triggers
GRANT SELECT, SHOW VIEW, TRIGGER, EVENT, LOCK TABLES ON smart_warehouse.* TO 'wh_dump'@'localhost';

-- Can de dump duoc stored procedure (MySQL 8.0.20 tro len).
-- Neu MySQL cu hon 8.0.20 thi lenh nay bao loi: bo qua dong nay va xem HuongDan_KhoiPhuc.md muc "Xu ly loi".
GRANT SHOW_ROUTINE ON *.* TO 'wh_dump'@'localhost';

FLUSH PRIVILEGES;

-- Kiem tra:
-- SHOW GRANTS FOR 'wh_dump'@'localhost';
