-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: smart_warehouse
-- ------------------------------------------------------
-- Server version	9.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
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
INSERT INTO `inventory` VALUES ('SP001',25,'2026-10-20 14:34:47'),('SP002',30,'2026-10-20 14:16:34'),('SP003',10,'2026-10-20 14:16:34'),('SP004',50,'2026-10-24 14:41:15'),('SP005',50,'2026-10-24 14:41:15'),('SP006',50,'2026-10-24 14:41:15'),('SP007',50,'2026-10-24 14:41:15'),('SP008',50,'2026-10-24 14:41:15'),('SP009',15,'2026-10-24 14:41:15'),('SP010',15,'2026-10-24 14:41:15'),('SP011',15,'2026-10-24 14:41:15'),('SP012',15,'2026-10-24 14:41:15'),('SP013',15,'2026-10-24 14:41:15'),('SP014',15,'2026-10-24 14:41:15'),('SP015',15,'2026-10-24 14:41:15'),('SP016',15,'2026-10-24 14:41:15'),('SP017',15,'2026-10-24 14:41:15'),('SP018',15,'2026-10-24 14:41:15'),('SP019',15,'2026-10-24 14:41:15'),('SP020',15,'2026-10-24 14:41:15'),('SP021',15,'2026-10-24 14:41:15'),('SP022',15,'2026-10-24 14:41:15'),('SP023',15,'2026-10-24 14:41:15'),('SP024',15,'2026-10-24 14:41:15'),('SP025',15,'2026-10-24 14:41:15'),('SP026',15,'2026-10-24 14:41:15'),('SP027',15,'2026-10-24 14:41:15'),('SP028',15,'2026-10-24 14:41:15'),('SP029',15,'2026-10-24 14:41:15'),('SP030',15,'2026-10-24 14:41:15'),('SP031',5,'2026-10-24 14:41:15'),('SP032',5,'2026-10-24 14:41:15'),('SP033',15,'2026-10-24 14:41:15'),('SP034',15,'2026-10-24 14:41:15'),('SP035',15,'2026-10-24 14:41:15'),('SP036',15,'2026-10-24 14:41:15'),('SP037',15,'2026-10-24 14:41:15'),('SP038',5,'2026-10-24 14:41:15'),('SP039',5,'2026-10-24 14:41:15'),('SP040',15,'2026-10-24 14:41:15'),('SP041',15,'2026-10-24 14:41:15'),('SP042',15,'2026-10-24 14:41:15'),('SP043',15,'2026-10-24 14:41:15'),('SP044',5,'2026-10-24 14:41:15'),('SP045',5,'2026-10-24 14:41:15'),('SP046',50,'2026-10-24 14:41:15'),('SP047',50,'2026-10-24 14:41:15'),('SP048',50,'2026-10-24 14:41:15'),('SP049',50,'2026-10-24 14:41:15'),('SP050',50,'2026-10-24 14:41:15'),('SP051',50,'2026-10-24 14:41:15'),('SP052',50,'2026-10-24 14:41:15'),('SP053',50,'2026-10-24 14:41:15'),('SP054',50,'2026-10-24 14:41:15'),('SP055',50,'2026-10-24 14:41:15'),('SP056',50,'2026-10-24 14:41:15'),('SP057',50,'2026-10-24 14:41:15'),('SP058',50,'2026-10-24 14:41:15'),('SP059',50,'2026-10-24 14:41:15'),('SP060',50,'2026-10-24 14:41:15'),('SP061',50,'2026-10-24 14:41:15'),('SP062',5,'2026-10-24 14:41:15'),('SP063',15,'2026-10-24 14:41:15'),('SP064',15,'2026-10-24 14:41:15'),('SP065',15,'2026-10-24 14:41:15'),('SP066',15,'2026-10-24 14:41:15'),('SP067',15,'2026-10-24 14:41:15'),('SP068',15,'2026-10-24 14:41:15'),('SP069',15,'2026-10-24 14:41:15'),('SP070',15,'2026-10-24 14:41:15'),('SP071',15,'2026-10-24 14:41:15'),('SP072',15,'2026-10-24 14:41:15'),('SP073',15,'2026-10-24 14:41:15'),('SP074',15,'2026-10-24 14:41:15'),('SP075',50,'2026-10-24 14:41:15'),('SP076',5,'2026-10-24 14:41:15'),('SP077',5,'2026-10-24 14:41:15'),('SP078',15,'2026-10-24 14:41:15'),('SP079',5,'2026-10-24 14:41:15'),('SP080',15,'2026-10-24 14:41:15'),('SP081',5,'2026-10-24 14:41:15'),('SP082',5,'2026-10-24 14:41:15'),('SP083',50,'2026-10-24 14:41:15'),('SP084',50,'2026-10-24 14:41:15'),('SP085',5,'2026-10-24 14:41:15'),('SP086',50,'2026-10-24 14:41:15'),('SP087',50,'2026-10-24 14:41:15'),('SP088',50,'2026-10-24 14:41:15'),('SP089',50,'2026-10-24 14:41:15'),('SP090',50,'2026-10-24 14:41:15'),('SP091',50,'2026-10-24 14:41:15'),('SP092',50,'2026-10-24 14:41:15'),('SP093',50,'2026-10-24 14:41:15'),('SP094',50,'2026-10-24 14:41:15'),('SP095',50,'2026-10-24 14:41:15'),('SP096',50,'2026-10-24 14:41:15'),('SP097',50,'2026-10-24 14:41:15'),('SP098',50,'2026-10-24 14:41:15'),('SP099',5,'2026-10-24 14:41:15'),('SP100',50,'2026-10-24 14:41:15');
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
INSERT INTO `warehouse_transactions` VALUES ('GD001','SP001','IMPORT',10,'2026-10-20 14:19:13','TK01','SCAN01'),('GD002','SP001','EXPORT',5,'2026-10-20 14:20:34','TK01','SCAN02');
/*!40000 ALTER TABLE `warehouse_transactions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-02  8:59:32
