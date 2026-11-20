-- =====================================================================
-- Đề tài 22 - Hệ thống quản lý kho hàng thông minh
-- SV1 - Mô hình dữ liệu (CV01, Công việc 2)
-- CSDL: SQLite 3 (đi kèm Python 3, không cần cài thêm)
-- Phiên bản thiết kế: v1.0 - 26/10/2026
-- Chạy: sqlite3 kho.db < schema.sql   hoặc   python kiem_tra_thiet_ke.py
-- =====================================================================

PRAGMA foreign_keys = ON;   -- SQLite mặc định TẮT khóa ngoại, phải bật ở mỗi kết nối

-- ---------------------------------------------------------------------
-- 1. Users - tài khoản và vai trò
--    ADMIN    : quản trị hệ thống (tài khoản, điểm quét, sao lưu)
--    THUKHO   : thủ kho (ghi nhập/xuất, sửa danh mục hàng)
--    NHANVIEN : nhân viên kho (chỉ ghi nhập/xuất tại điểm quét)
--    QUANLY   : người quản lý (CHỈ XEM tồn kho và lịch sử - dùng cho KT3)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Users (
    username       TEXT PRIMARY KEY,
    full_name      TEXT NOT NULL,
    role           TEXT NOT NULL CHECK (role IN ('ADMIN','THUKHO','NHANVIEN','QUANLY')),
    password_hash  TEXT NOT NULL,                 -- lưu băm (SHA-256 + salt), không lưu mật khẩu gốc
    is_active      INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1)),
    created_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now','localtime'))
);

-- ---------------------------------------------------------------------
-- 2. ScanPoints - điểm quét mã
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ScanPoints (
    scan_point_id  TEXT PRIMARY KEY CHECK (scan_point_id GLOB 'SP[0-9][0-9]'),
    name           TEXT NOT NULL,
    location       TEXT,
    ip_address     TEXT,                          -- IP dự kiến khi triển khai thật (bảng IP)
    is_active      INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1))
);

-- ---------------------------------------------------------------------
-- 3. Products - danh mục hàng hóa
--    product_code chính là nội dung mã vạch in trên hàng
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Products (
    product_code   TEXT PRIMARY KEY CHECK (length(product_code) BETWEEN 3 AND 20),
    product_name   TEXT NOT NULL,
    unit           TEXT NOT NULL,                 -- đơn vị tính: cái, hộp, thùng...
    is_active      INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1))
);

-- ---------------------------------------------------------------------
-- 4. Inventory - số lượng tồn hiện tại (quan hệ 1-1 với Products)
--    CHECK quantity >= 0 là lớp chặn cuối: không bao giờ tồn âm
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Inventory (
    product_code   TEXT PRIMARY KEY REFERENCES Products(product_code),
    quantity       INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    last_txn_id    TEXT,                          -- giao dịch gần nhất làm thay đổi tồn
    updated_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now','localtime'))
);

-- ---------------------------------------------------------------------
-- 5. Transactions - lịch sử nhập/xuất (chỉ thêm, không sửa/xóa)
--    txn_id do MÁY KHÁCH sinh ra trước khi gửi -> gửi lại khi mất mạng
--    vẫn giữ nguyên txn_id, máy chủ nhận ra trùng (KT2)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Transactions (
    txn_id         TEXT PRIMARY KEY,              -- VD: SP01-20261026-0001 (UNIQUE ngầm định)
    product_code   TEXT NOT NULL REFERENCES Products(product_code),
    txn_type       TEXT NOT NULL CHECK (txn_type IN ('NHAP','XUAT')),
    quantity       INTEGER NOT NULL CHECK (quantity > 0 AND quantity <= 10000),
    username       TEXT NOT NULL REFERENCES Users(username),
    scan_point_id  TEXT NOT NULL REFERENCES ScanPoints(scan_point_id),
    client_time    TEXT NOT NULL,                 -- thời điểm quét tại máy khách
    server_time    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now','localtime')),
    stock_after    INTEGER NOT NULL CHECK (stock_after >= 0),  -- tồn sau giao dịch, để đối chiếu
    note           TEXT
);

CREATE INDEX IF NOT EXISTS idx_txn_product ON Transactions(product_code, server_time);
CREATE INDEX IF NOT EXISTS idx_txn_time    ON Transactions(server_time);

-- Lịch sử giao dịch là bất biến: chặn UPDATE/DELETE ngay trong CSDL
CREATE TRIGGER IF NOT EXISTS trg_txn_no_update
BEFORE UPDATE ON Transactions
BEGIN
    SELECT RAISE(ABORT, 'Transactions la bang chi them: khong duoc sua');
END;

CREATE TRIGGER IF NOT EXISTS trg_txn_no_delete
BEFORE DELETE ON Transactions
BEGIN
    SELECT RAISE(ABORT, 'Transactions la bang chi them: khong duoc xoa');
END;

-- ---------------------------------------------------------------------
-- 6. AuditLog (bổ sung) - ghi MỌI yêu cầu đến máy chủ, kể cả bị từ chối
--    Dùng để chứng minh phát hiện trùng/thao tác không hợp lệ (SV4)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS AuditLog (
    log_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    log_time       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now','localtime')),
    username       TEXT,
    scan_point_id  TEXT,
    txn_id         TEXT,
    action         TEXT NOT NULL,                 -- WRITE_TXN, READ_INVENTORY, LOGIN, BACKUP, RESTORE...
    result         TEXT NOT NULL CHECK (result IN ('OK','REJECTED','ERROR')),
    error_code     TEXT,                          -- DUPLICATE_TXN, INSUFFICIENT_STOCK, FORBIDDEN...
    detail         TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_time ON AuditLog(log_time);

-- ---------------------------------------------------------------------
-- View đối chiếu: tồn lưu trong Inventory phải bằng tồn tính lại từ lịch sử
-- Dùng sau khi khôi phục bản sao (KT3) và sau khi mất mạng (YC4)
-- ---------------------------------------------------------------------
CREATE VIEW IF NOT EXISTS v_doi_chieu_ton AS
SELECT  p.product_code,
        p.product_name,
        COALESCE(i.quantity, 0)                                            AS ton_luu_tru,
        COALESCE(SUM(CASE WHEN t.txn_type = 'NHAP' THEN t.quantity
                          WHEN t.txn_type = 'XUAT' THEN -t.quantity END), 0) AS ton_tinh_lai,
        COALESCE(i.quantity, 0) -
        COALESCE(SUM(CASE WHEN t.txn_type = 'NHAP' THEN t.quantity
                          WHEN t.txn_type = 'XUAT' THEN -t.quantity END), 0) AS chenh_lech
FROM Products p
LEFT JOIN Inventory    i ON i.product_code = p.product_code
LEFT JOIN Transactions t ON t.product_code = p.product_code
GROUP BY p.product_code, p.product_name, i.quantity;
