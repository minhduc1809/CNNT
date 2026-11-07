-- 01_create_database.sql
-- Tao CSDL va 5 bang cho he thong quan ly kho.
-- Chay bang tai khoan co quyen CREATE DATABASE/TABLE.

CREATE DATABASE IF NOT EXISTS smart_warehouse
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE smart_warehouse;

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
    user_id   VARCHAR(30)  NOT NULL,
    username  VARCHAR(60)  NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role      ENUM('admin','warehouse','employee','viewer') NOT NULL,
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
