-- MySQL dump 10.13  Distrib 9.3.0, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: smart_warehouse
-- ------------------------------------------------------
-- Server version	9.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `inventory`
--

DROP TABLE IF EXISTS `inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventory` (
  `product_id` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `quantity` int NOT NULL DEFAULT '0',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`product_id`),
  CONSTRAINT `fk_inventory_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
  CONSTRAINT `chk_inventory_quantity` CHECK ((`quantity` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory`
--

LOCK TABLES `inventory` WRITE;
/*!40000 ALTER TABLE `inventory` DISABLE KEYS */;
INSERT INTO `inventory` VALUES ('SP001',33,'2026-11-16 02:31:59'),('SP002',146,'2026-11-16 02:32:13'),('SP003',25,'2026-11-07 04:10:30'),('SP004',80,'2026-11-07 04:10:37'),('SP005',42,'2026-11-07 04:10:52'),('SP006',75,'2026-11-07 04:11:00'),('SP007',62,'2026-11-07 04:11:07'),('SP008',47,'2026-11-07 04:11:15'),('SP009',15,'2026-10-24 14:41:15'),('SP010',15,'2026-10-24 14:41:15'),('SP011',15,'2026-10-24 14:41:15'),('SP012',15,'2026-10-24 14:41:15'),('SP013',15,'2026-10-24 14:41:15'),('SP014',15,'2026-10-24 14:41:15'),('SP015',15,'2026-10-24 14:41:15'),('SP016',15,'2026-10-24 14:41:15'),('SP017',15,'2026-10-24 14:41:15'),('SP018',15,'2026-10-24 14:41:15'),('SP019',15,'2026-10-24 14:41:15'),('SP020',15,'2026-10-24 14:41:15'),('SP021',15,'2026-10-24 14:41:15'),('SP022',15,'2026-10-24 14:41:15'),('SP023',15,'2026-10-24 14:41:15'),('SP024',15,'2026-10-24 14:41:15'),('SP025',15,'2026-10-24 14:41:15'),('SP026',15,'2026-10-24 14:41:15'),('SP027',15,'2026-10-24 14:41:15'),('SP028',15,'2026-10-24 14:41:15'),('SP029',15,'2026-10-24 14:41:15'),('SP030',15,'2026-10-24 14:41:15'),('SP031',5,'2026-10-24 14:41:15'),('SP032',5,'2026-10-24 14:41:15'),('SP033',15,'2026-10-24 14:41:15'),('SP034',15,'2026-10-24 14:41:15'),('SP035',15,'2026-10-24 14:41:15'),('SP036',15,'2026-10-24 14:41:15'),('SP037',15,'2026-10-24 14:41:15'),('SP038',5,'2026-10-24 14:41:15'),('SP039',5,'2026-10-24 14:41:15'),('SP040',15,'2026-10-24 14:41:15'),('SP041',15,'2026-10-24 14:41:15'),('SP042',15,'2026-10-24 14:41:15'),('SP043',15,'2026-10-24 14:41:15'),('SP044',5,'2026-10-24 14:41:15'),('SP045',5,'2026-10-24 14:41:15'),('SP046',50,'2026-10-24 14:41:15'),('SP047',50,'2026-10-24 14:41:15'),('SP048',50,'2026-10-24 14:41:15'),('SP049',50,'2026-10-24 14:41:15'),('SP050',50,'2026-10-24 14:41:15'),('SP051',50,'2026-10-24 14:41:15'),('SP052',50,'2026-10-24 14:41:15'),('SP053',50,'2026-10-24 14:41:15'),('SP054',50,'2026-10-24 14:41:15'),('SP055',50,'2026-10-24 14:41:15'),('SP056',50,'2026-10-24 14:41:15'),('SP057',50,'2026-10-24 14:41:15'),('SP058',50,'2026-10-24 14:41:15'),('SP059',50,'2026-10-24 14:41:15'),('SP060',50,'2026-10-24 14:41:15'),('SP061',50,'2026-10-24 14:41:15'),('SP062',5,'2026-10-24 14:41:15'),('SP063',15,'2026-10-24 14:41:15'),('SP064',15,'2026-10-24 14:41:15'),('SP065',15,'2026-10-24 14:41:15'),('SP066',15,'2026-10-24 14:41:15'),('SP067',15,'2026-10-24 14:41:15'),('SP068',15,'2026-10-24 14:41:15'),('SP069',15,'2026-10-24 14:41:15'),('SP070',15,'2026-10-24 14:41:15'),('SP071',15,'2026-10-24 14:41:15'),('SP072',15,'2026-10-24 14:41:15'),('SP073',15,'2026-10-24 14:41:15'),('SP074',15,'2026-10-24 14:41:15'),('SP075',50,'2026-10-24 14:41:15'),('SP076',5,'2026-10-24 14:41:15'),('SP077',5,'2026-10-24 14:41:15'),('SP078',15,'2026-10-24 14:41:15'),('SP079',5,'2026-10-24 14:41:15'),('SP080',15,'2026-10-24 14:41:15'),('SP081',5,'2026-10-24 14:41:15'),('SP082',5,'2026-10-24 14:41:15'),('SP083',50,'2026-10-24 14:41:15'),('SP084',50,'2026-10-24 14:41:15'),('SP085',5,'2026-10-24 14:41:15'),('SP086',50,'2026-10-24 14:41:15'),('SP087',50,'2026-10-24 14:41:15'),('SP088',50,'2026-10-24 14:41:15'),('SP089',50,'2026-10-24 14:41:15'),('SP090',50,'2026-10-24 14:41:15'),('SP091',50,'2026-10-24 14:41:15'),('SP092',50,'2026-10-24 14:41:15'),('SP093',50,'2026-10-24 14:41:15'),('SP094',50,'2026-10-24 14:41:15'),('SP095',50,'2026-10-24 14:41:15'),('SP096',50,'2026-10-24 14:41:15'),('SP097',50,'2026-10-24 14:41:15'),('SP098',50,'2026-10-24 14:41:15'),('SP099',5,'2026-10-24 14:41:15'),('SP100',50,'2026-10-24 14:41:15');
/*!40000 ALTER TABLE `inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `product_id` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `product_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `unit` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES ('SP001','Ban phim','Cai','2026-10-20 14:16:34'),('SP002','Chuot may tinh','Cai','2026-10-20 14:16:34'),('SP003','Man hinh','Cai','2026-10-20 14:16:34'),('SP004','Ban di chuot','Cai','2026-10-24 14:39:49'),('SP005','Tai nghe','Cai','2026-10-24 14:39:49'),('SP006','Webcam','Cai','2026-10-24 14:39:49'),('SP007','Loa vi tinh','Cai','2026-10-24 14:39:49'),('SP008','Microphone','Cai','2026-10-24 14:39:49'),('SP009','USB 32GB','Cai','2026-10-24 14:39:49'),('SP010','USB 64GB','Cai','2026-10-24 14:39:49'),('SP011','The nho 64GB','Cai','2026-10-24 14:39:49'),('SP012','O cung SSD 256GB','Cai','2026-10-24 14:39:49'),('SP013','O cung SSD 512GB','Cai','2026-10-24 14:39:49'),('SP014','O cung HDD 1TB','Cai','2026-10-24 14:39:49'),('SP015','RAM 8GB','Cai','2026-10-24 14:39:49'),('SP016','RAM 16GB','Cai','2026-10-24 14:39:49'),('SP017','Card mang','Cai','2026-10-24 14:39:49'),('SP018','Bo phat WiFi','Cai','2026-10-24 14:39:49'),('SP019','Router','Cai','2026-10-24 14:39:49'),('SP020','Switch mang','Cai','2026-10-24 14:39:49'),('SP021','Day mang 1m','Cai','2026-10-24 14:39:49'),('SP022','Day mang 5m','Cai','2026-10-24 14:39:49'),('SP023','Cap HDMI','Cai','2026-10-24 14:39:49'),('SP024','Cap VGA','Cai','2026-10-24 14:39:49'),('SP025','Cap USB','Cai','2026-10-24 14:39:49'),('SP026','Bo chia USB','Cai','2026-10-24 14:39:49'),('SP027','Sac laptop','Cai','2026-10-24 14:39:49'),('SP028','Pin laptop','Cai','2026-10-24 14:39:49'),('SP029','De tan nhiet laptop','Cai','2026-10-24 14:39:49'),('SP030','Gia do laptop','Cai','2026-10-24 14:39:49'),('SP031','Laptop van phong','Chiec','2026-10-24 14:39:49'),('SP032','May tinh de ban','Chiec','2026-10-24 14:39:49'),('SP033','Ban phim co','Cai','2026-10-24 14:39:49'),('SP034','Ban phim khong day','Cai','2026-10-24 14:39:49'),('SP035','Chuot khong day','Cai','2026-10-24 14:39:49'),('SP036','Chuot gaming','Cai','2026-10-24 14:39:49'),('SP037','Lot chuot','Cai','2026-10-24 14:39:49'),('SP038','Man hinh 24 inch','Chiec','2026-10-24 14:39:49'),('SP039','Man hinh 27 inch','Chiec','2026-10-24 14:39:49'),('SP040','Gia treo man hinh','Cai','2026-10-24 14:39:49'),('SP041','Day nguon','Cai','2026-10-24 14:39:49'),('SP042','O cam dien','Cai','2026-10-24 14:39:49'),('SP043','Bo luu dien','Cai','2026-10-24 14:39:49'),('SP044','May in laser','Chiec','2026-10-24 14:39:49'),('SP045','May scan','Chiec','2026-10-24 14:39:49'),('SP046','Muc in den','Cai','2026-10-24 14:39:49'),('SP047','Muc in mau','Cai','2026-10-24 14:39:49'),('SP048','Giay in A4','Bo','2026-10-24 14:39:49'),('SP049','Giay in A3','Bo','2026-10-24 14:39:49'),('SP050','Bia ho so','Bo','2026-10-24 14:39:49'),('SP051','But bi','Bo','2026-10-24 14:39:49'),('SP052','But chi','Bo','2026-10-24 14:39:49'),('SP053','So ghi chep','Bo','2026-10-24 14:39:49'),('SP054','Ke dung tai lieu','Cai','2026-10-24 14:39:49'),('SP055','Khay dung giay','Cai','2026-10-24 14:39:49'),('SP056','Ghim bam','Bo','2026-10-24 14:39:49'),('SP057','May bam kim','Cai','2026-10-24 14:39:49'),('SP058','Bang dinh','Bo','2026-10-24 14:39:49'),('SP059','Keo van phong','Bo','2026-10-24 14:39:49'),('SP060','Thuoc ke','Bo','2026-10-24 14:39:49'),('SP061','May tinh cam tay','Cai','2026-10-24 14:39:49'),('SP062','May chieu','Chiec','2026-10-24 14:39:49'),('SP063','Man chieu','Cai','2026-10-24 14:39:49'),('SP064','Dieu khien may chieu','Cai','2026-10-24 14:39:49'),('SP065','Day DisplayPort','Cai','2026-10-24 14:39:49'),('SP066','Cap chuyen USB-C','Cai','2026-10-24 14:39:49'),('SP067','Hub USB-C','Cai','2026-10-24 14:39:49'),('SP068','Dock laptop','Cai','2026-10-24 14:39:49'),('SP069','Adapter mang USB','Cai','2026-10-24 14:39:49'),('SP070','O cung di dong','Cai','2026-10-24 14:39:49'),('SP071','Tui dung laptop','Cai','2026-10-24 14:39:49'),('SP072','Ba lo laptop','Cai','2026-10-24 14:39:49'),('SP073','Khoa laptop','Cai','2026-10-24 14:39:49'),('SP074','Quat USB','Cai','2026-10-24 14:39:49'),('SP075','Den ban LED','Cai','2026-10-24 14:39:49'),('SP076','Camera an ninh','Chiec','2026-10-24 14:39:49'),('SP077','Dau ghi camera','Chiec','2026-10-24 14:39:49'),('SP078','The tu camera','Cai','2026-10-24 14:39:49'),('SP079','May cham cong','Chiec','2026-10-24 14:39:49'),('SP080','Dau doc the','Cai','2026-10-24 14:39:49'),('SP081','May quet ma vach','Chiec','2026-10-24 14:39:49'),('SP082','May in ma vach','Chiec','2026-10-24 14:39:49'),('SP083','Tem ma vach','Bo','2026-10-24 14:39:49'),('SP084','Giay in nhiet','Bo','2026-10-24 14:39:49'),('SP085','Can dien tu','Chiec','2026-10-24 14:39:49'),('SP086','Xe day hang','Cai','2026-10-24 14:39:49'),('SP087','Ke de hang','Cai','2026-10-24 14:39:49'),('SP088','Thung nhua','Bo','2026-10-24 14:39:49'),('SP089','Hop dung linh kien','Cai','2026-10-24 14:39:49'),('SP090','Tui chong tinh dien','Bo','2026-10-24 14:39:49'),('SP091','Day rut nhua','Bo','2026-10-24 14:39:49'),('SP092','Bang nhan hang','Bo','2026-10-24 14:39:49'),('SP093','Gang tay bao ho','Bo','2026-10-24 14:39:49'),('SP094','Kinh bao ho','Bo','2026-10-24 14:39:49'),('SP095','Khau trang','Bo','2026-10-24 14:39:49'),('SP096','Bo dung cu sua chua','Cai','2026-10-24 14:39:49'),('SP097','Tua vit','Cai','2026-10-24 14:39:49'),('SP098','Kep day mang','Cai','2026-10-24 14:39:49'),('SP099','May khoan mini','Chiec','2026-10-24 14:39:49'),('SP100','Hop dung dung cu','Cai','2026-10-24 14:39:49');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scanpoints`
--

DROP TABLE IF EXISTS `scanpoints`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `scanpoints` (
  `scan_point_id` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `scan_point_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`scan_point_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scanpoints`
--

LOCK TABLES `scanpoints` WRITE;
/*!40000 ALTER TABLE `scanpoints` DISABLE KEYS */;
INSERT INTO `scanpoints` VALUES ('SCAN01','Diem quet 1'),('SCAN02','Diem quet 2');
/*!40000 ALTER TABLE `scanpoints` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `username` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('admin','warehouse','employee','viewer') COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('AD01','admin_demo','Quan tri vien mau','admin'),('NV01','nhanvien_demo','Nhan vien mau','employee'),('NV02','nv02_demo','Nhan vien mau 2','employee'),('TK01','thukho_demo','Thu kho mau','warehouse'),('VIEW01','viewer_demo','Tai khoan chi xem','viewer');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `warehouse_transactions`
--

DROP TABLE IF EXISTS `warehouse_transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warehouse_transactions` (
  `transaction_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `product_id` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `transaction_type` enum('IMPORT','EXPORT') COLLATE utf8mb4_unicode_ci NOT NULL,
  `quantity` int NOT NULL,
  `transaction_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `scan_point_id` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`transaction_id`),
  KEY `fk_transaction_scan` (`scan_point_id`),
  KEY `idx_transaction_product_time` (`product_id`,`transaction_time`),
  KEY `idx_transaction_user` (`user_id`),
  CONSTRAINT `fk_transaction_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
  CONSTRAINT `fk_transaction_scan` FOREIGN KEY (`scan_point_id`) REFERENCES `scanpoints` (`scan_point_id`),
  CONSTRAINT `fk_transaction_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `chk_transaction_quantity` CHECK ((`quantity` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warehouse_transactions`
--

LOCK TABLES `warehouse_transactions` WRITE;
/*!40000 ALTER TABLE `warehouse_transactions` DISABLE KEYS */;
INSERT INTO `warehouse_transactions` VALUES ('GD001','SP001','IMPORT',10,'2026-10-20 14:19:13','TK01','SCAN01'),('GD002','SP001','EXPORT',5,'2026-10-20 14:20:34','TK01','SCAN02'),('MC_EXPORT_01','SP001','EXPORT',2,'2026-11-16 01:33:37','NV01','SCAN02'),('MC_IMPORT_01','SP001','IMPORT',5,'2026-11-16 01:33:37','TK01','SCAN01'),('SCAN01-20261107-0001','SP001','IMPORT',10,'2026-11-07 04:08:00','TK01','SCAN01'),('SCAN01-20261107-0002','SP002','IMPORT',20,'2026-11-07 04:10:00','TK01','SCAN01'),('SCAN01-20261107-0003','SP003','IMPORT',15,'2026-11-07 04:10:10','TK01','SCAN01'),('SCAN01-20261107-0004','SP005','EXPORT',8,'2026-11-07 04:10:40','NV02','SCAN01'),('SCAN01-20261107-0005','SP007','IMPORT',12,'2026-11-07 04:11:00','NV01','SCAN01'),('SCAN01-KT1-IN-1794025503','SP002','IMPORT',20,'2026-11-07 04:25:05','TK01','SCAN01'),('SCAN01-KT1-IN-1794025538','SP002','IMPORT',20,'2026-11-07 04:25:40','TK01','SCAN01'),('SCAN01-KT1-IN-1794025586','SP002','IMPORT',20,'2026-11-07 04:26:28','TK01','SCAN01'),('SCAN01-KT1-IN-1794061546','SP002','IMPORT',20,'2026-11-07 14:25:48','TK01','SCAN01'),('SCAN01-KT1-IN-1794063486','SP002','IMPORT',20,'2026-11-07 14:58:08','TK01','SCAN01'),('SCAN01-KT1-IN-1794795979','SP002','IMPORT',20,'2026-11-16 02:26:21','TK01','SCAN01'),('SCAN01-KT1-IN-1794796033','SP002','IMPORT',20,'2026-11-16 02:27:15','TK01','SCAN01'),('SCAN01-KT1-IN-1794796327','SP002','IMPORT',20,'2026-11-16 02:32:09','TK01','SCAN01'),('SCAN02-20261107-0001','SP004','IMPORT',30,'2026-11-07 04:10:20','NV01','SCAN02'),('SCAN02-20261107-0002','SP001','EXPORT',5,'2026-11-07 04:10:30','TK01','SCAN02'),('SCAN02-20261107-0003','SP006','IMPORT',25,'2026-11-07 04:10:50','TK01','SCAN02'),('SCAN02-20261107-0004','SP008','EXPORT',3,'2026-11-07 04:11:10','TK01','SCAN02'),('SCAN02-KT1-OUT-1794025505','SP002','EXPORT',8,'2026-11-07 04:25:10','TK01','SCAN02'),('SCAN02-KT1-OUT-1794025540','SP002','EXPORT',8,'2026-11-07 04:25:45','TK01','SCAN02'),('SCAN02-KT1-OUT-1794025588','SP002','EXPORT',8,'2026-11-07 04:26:32','TK01','SCAN02'),('SCAN02-KT1-OUT-1794061548','SP002','EXPORT',8,'2026-11-07 14:25:53','TK01','SCAN02'),('SCAN02-KT1-OUT-1794063488','SP002','EXPORT',8,'2026-11-07 14:58:12','TK01','SCAN02'),('SCAN02-KT1-OUT-1794795981','SP002','EXPORT',8,'2026-11-16 02:26:25','TK01','SCAN02'),('SCAN02-KT1-OUT-1794796035','SP002','EXPORT',8,'2026-11-16 02:27:20','TK01','SCAN02'),('SCAN02-KT1-OUT-1794796329','SP002','EXPORT',8,'2026-11-16 02:32:13','TK01','SCAN02'),('TEST-E-1794025361981','SP001','IMPORT',2,'2026-11-07 04:22:44','NV01','SCAN01'),('TEST-E-1794025377533','SP001','IMPORT',2,'2026-11-07 04:22:59','NV01','SCAN01'),('TEST-E01','SP001','IMPORT',2,'2026-11-07 04:21:46','NV01','SCAN01'),('TEST-TK-1794025366127','SP001','EXPORT',2,'2026-11-07 04:22:48','TK01','SCAN02'),('TEST-TK-1794025381689','SP001','EXPORT',2,'2026-11-07 04:23:03','TK01','SCAN02'),('TEST-TK01','SP001','EXPORT',2,'2026-11-07 04:21:50','TK01','SCAN02'),('TXN-E-IN-1794025487350','SP001','IMPORT',3,'2026-11-07 04:24:49','NV01','SCAN01'),('TXN-E-IN-1794025522303','SP001','IMPORT',3,'2026-11-07 04:25:24','NV01','SCAN01'),('TXN-E-IN-1794025569674','SP001','IMPORT',3,'2026-11-07 04:26:11','NV01','SCAN01'),('TXN-E-IN-1794061530191','SP001','IMPORT',3,'2026-11-07 14:25:32','NV01','SCAN01'),('TXN-E-IN-1794063470115','SP001','IMPORT',3,'2026-11-07 14:57:52','NV01','SCAN01'),('TXN-E-IN-1794795963063','SP001','IMPORT',3,'2026-11-16 02:26:05','NV01','SCAN01'),('TXN-E-IN-1794796017400','SP001','IMPORT',3,'2026-11-16 02:26:59','NV01','SCAN01'),('TXN-E-IN-1794796311318','SP001','IMPORT',3,'2026-11-16 02:31:53','NV01','SCAN01'),('TXN-W-OUT-1794025493670','SP001','EXPORT',3,'2026-11-07 04:24:55','TK01','SCAN02'),('TXN-W-OUT-1794025528507','SP001','EXPORT',3,'2026-11-07 04:25:30','TK01','SCAN02'),('TXN-W-OUT-1794025575875','SP001','EXPORT',3,'2026-11-07 04:26:17','TK01','SCAN02'),('TXN-W-OUT-1794061536480','SP001','EXPORT',3,'2026-11-07 14:25:38','TK01','SCAN02'),('TXN-W-OUT-1794063476345','SP001','EXPORT',3,'2026-11-07 14:57:58','TK01','SCAN02'),('TXN-W-OUT-1794795969260','SP001','EXPORT',3,'2026-11-16 02:26:11','TK01','SCAN02'),('TXN-W-OUT-1794796023611','SP001','EXPORT',3,'2026-11-16 02:27:05','TK01','SCAN02'),('TXN-W-OUT-1794796317472','SP001','EXPORT',3,'2026-11-16 02:31:59','TK01','SCAN02');
/*!40000 ALTER TABLE `warehouse_transactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'smart_warehouse'
--

--
-- Dumping routines for database 'smart_warehouse'
--
/*!50003 DROP PROCEDURE IF EXISTS `sp_warehouse_transaction` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_warehouse_transaction`(
    IN p_transaction_id VARCHAR(50),
    IN p_product_id VARCHAR(30),
    IN p_transaction_type VARCHAR(10),
    IN p_quantity INT,
    IN p_user_id VARCHAR(30),
    IN p_scan_point_id VARCHAR(30)
)
BEGIN
    DECLARE v_stock INT DEFAULT NULL;
    DECLARE v_product_count INT DEFAULT 0;
    DECLARE v_user_count INT DEFAULT 0;
    DECLARE v_scan_count INT DEFAULT 0;
    DECLARE v_transaction_count INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_transaction_id IS NULL OR TRIM(p_transaction_id) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Ma giao dich khong duoc de trong';
    END IF;

    IF p_quantity IS NULL OR p_quantity <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'So luong phai lon hon 0';
    END IF;

    IF p_transaction_type IS NULL
       OR p_transaction_type NOT IN ('IMPORT', 'EXPORT') THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loai giao dich phai la IMPORT hoac EXPORT';
    END IF;

    START TRANSACTION;

    SELECT COUNT(*) INTO v_transaction_count
    FROM warehouse_transactions
    WHERE transaction_id = p_transaction_id;

    IF v_transaction_count > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Ma giao dich da ton tai';
    END IF;

    SELECT COUNT(*) INTO v_product_count
    FROM Products
    WHERE product_id = p_product_id;

    IF v_product_count = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Khong tim thay san pham';
    END IF;

    SELECT COUNT(*) INTO v_user_count
    FROM Users
    WHERE user_id = p_user_id;

    IF v_user_count = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Khong tim thay nguoi dung';
    END IF;

    SELECT COUNT(*) INTO v_scan_count
    FROM ScanPoints
    WHERE scan_point_id = p_scan_point_id;

    IF v_scan_count = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Khong tim thay diem quet';
    END IF;

    SELECT quantity INTO v_stock
    FROM Inventory
    WHERE product_id = p_product_id
    FOR UPDATE;

    IF p_transaction_type = 'EXPORT'
       AND v_stock < p_quantity THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Ton kho khong du de xuat';
    END IF;

    IF p_transaction_type = 'IMPORT' THEN
        UPDATE Inventory
        SET quantity = quantity + p_quantity
        WHERE product_id = p_product_id;
    ELSE
        UPDATE Inventory
        SET quantity = quantity - p_quantity
        WHERE product_id = p_product_id;
    END IF;

    INSERT INTO warehouse_transactions (
        transaction_id,
        product_id,
        transaction_type,
        quantity,
        user_id,
        scan_point_id
    )
    VALUES (
        p_transaction_id,
        p_product_id,
        p_transaction_type,
        p_quantity,
        p_user_id,
        p_scan_point_id
    );

    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-16  9:53:40
