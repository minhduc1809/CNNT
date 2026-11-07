-- 05_test_transactions.sql
-- Chay sau 01, 02, 03. Su dung san pham mau SP001.
-- Cac lenh CALL lam thay doi ton kho that; dung ma TEST duy nhat.
-- Neu chay lai, doi ma TEST... moi de tranh trung transaction_id.

USE smart_warehouse;

-- Xem ton kho truoc khi test
SELECT product_id, quantity
FROM Inventory
WHERE product_id = 'SP001';

-- KT1: Nhap 5 san pham. Ton kho tang 5.
CALL sp_warehouse_transaction(
  'TEST_IMPORT_001', 'SP001', 'IMPORT', 5, 'TK01', 'SCAN01'
);

-- KT1: Xuat 2 san pham. Ton kho giam 2.
CALL sp_warehouse_transaction(
  'TEST_EXPORT_001', 'SP001', 'EXPORT', 2, 'NV01', 'SCAN02'
);

-- Kiem tra lich su va ton kho sau KT1
SELECT * FROM warehouse_transactions
WHERE transaction_id IN ('TEST_IMPORT_001', 'TEST_EXPORT_001');

SELECT product_id, quantity
FROM Inventory
WHERE product_id = 'SP001';

-- KT2: Goi lai ma giao dich da dung.
-- Ky vong: thu tuc bao loi "Ma giao dich da ton tai";
-- ton kho KHONG duoc thay doi them.
-- Chay rieng lenh CALL nay de quan sat loi:
-- CALL sp_warehouse_transaction(
--   'TEST_IMPORT_001', 'SP001', 'IMPORT', 5, 'TK01', 'SCAN01'
-- );

-- KT3: Thu xuat vuot ton kho.
-- Ky vong: thu tuc bao loi "Ton kho khong du de xuat";
-- ton kho khong bi am va khong ghi giao dich.
-- Chay rieng lenh CALL nay de quan sat loi:
-- CALL sp_warehouse_transaction(
--   'TEST_EXPORT_FAIL_001', 'SP001', 'EXPORT', 999999, 'NV01', 'SCAN02'
-- );

-- Bao cao doi chieu sau kiem thu
SELECT p.product_id, p.product_name, i.quantity
FROM Products p
JOIN Inventory i ON i.product_id = p.product_id
WHERE p.product_id = 'SP001';

SELECT transaction_id, product_id, transaction_type, quantity,
       transaction_time, user_id, scan_point_id
FROM warehouse_transactions
WHERE transaction_id LIKE 'TEST_%'
ORDER BY transaction_time;
