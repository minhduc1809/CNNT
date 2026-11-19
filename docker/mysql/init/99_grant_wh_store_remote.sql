GRANT SELECT ON smart_warehouse.* TO 'wh_store'@'%';
GRANT EXECUTE ON PROCEDURE smart_warehouse.sp_warehouse_transaction TO 'wh_store'@'%';
FLUSH PRIVILEGES;
