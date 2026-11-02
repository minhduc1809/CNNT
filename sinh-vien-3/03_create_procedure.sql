-- 03_create_procedure.sql
-- Thu tuc nhap/xuat kho co transaction, khoa dong ton kho va chan ma giao dich trung.
-- Quy uoc transaction_type: IMPORT hoac EXPORT.
-- Luu y: neu ung dung hien tai goi thu tuc voi bo tham so khac,
-- can dong bo lai API/ung dung theo chu ky ben duoi.

USE smart_warehouse;

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
