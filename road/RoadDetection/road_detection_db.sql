-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: road_detection_db
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `complaint_images`
--

DROP TABLE IF EXISTS `complaint_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `complaint_images` (
  `id` int NOT NULL AUTO_INCREMENT,
  `complaint_id` int NOT NULL,
  `filename` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_cimgs_complaint_id` (`complaint_id`),
  CONSTRAINT `fk_cimgs_complaint` FOREIGN KEY (`complaint_id`) REFERENCES `complaints` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complaint_images`
--

LOCK TABLES `complaint_images` WRITE;
/*!40000 ALTER TABLE `complaint_images` DISABLE KEYS */;
INSERT INTO `complaint_images` VALUES (1,1,'image_1.jpg','2025-11-21 15:20:48'),(2,2,'image_1.jpg','2025-11-21 15:23:25'),(3,3,'image_1.jpg','2025-11-21 15:26:55'),(4,4,'image_1.jpg','2025-11-21 15:29:09'),(5,5,'image_1.jpg','2025-11-21 15:36:00'),(10,10,'image_1.jpg','2025-12-15 18:08:16'),(11,11,'image_1.jpg','2025-12-15 23:44:32');
/*!40000 ALTER TABLE `complaint_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `complaint_replies`
--

DROP TABLE IF EXISTS `complaint_replies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `complaint_replies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `complaint_id` int NOT NULL,
  `message` text NOT NULL,
  `admin_username` varchar(100) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_complaint_id` (`complaint_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complaint_replies`
--

LOCK TABLES `complaint_replies` WRITE;
/*!40000 ALTER TABLE `complaint_replies` DISABLE KEYS */;
INSERT INTO `complaint_replies` VALUES (1,9,'solved','admin','2025-11-24 14:54:03'),(2,8,'solved please check','admin','2025-11-24 15:05:19'),(3,2,'street light implemented','admin','2025-11-24 15:25:42'),(4,5,'solved by the Department Admin','admin','2025-11-25 12:21:10'),(5,6,'fcredcf','admin','2025-11-25 12:37:24');
/*!40000 ALTER TABLE `complaint_replies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `complaint_reply_images`
--

DROP TABLE IF EXISTS `complaint_reply_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `complaint_reply_images` (
  `id` int NOT NULL AUTO_INCREMENT,
  `reply_id` int NOT NULL,
  `filename` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_reply_id` (`reply_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complaint_reply_images`
--

LOCK TABLES `complaint_reply_images` WRITE;
/*!40000 ALTER TABLE `complaint_reply_images` DISABLE KEYS */;
INSERT INTO `complaint_reply_images` VALUES (1,2,'image_1.jpg','2025-11-24 15:05:19'),(2,3,'image_1.jpg','2025-11-24 15:25:42'),(3,4,'image_1.jpg','2025-11-25 12:21:10'),(4,5,'image_1.jpg','2025-11-25 12:37:24');
/*!40000 ALTER TABLE `complaint_reply_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `complaints`
--

DROP TABLE IF EXISTS `complaints`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `complaints` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `title` varchar(150) NOT NULL,
  `category` varchar(50) NOT NULL,
  `location_text` varchar(255) DEFAULT NULL,
  `priority` enum('low','medium','high') NOT NULL DEFAULT 'low',
  `description` text NOT NULL,
  `contact` varchar(20) DEFAULT NULL,
  `anonymous` tinyint(1) NOT NULL DEFAULT '0',
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'New',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_complaints_user_id` (`user_id`),
  KEY `idx_complaints_status` (`status`),
  KEY `idx_complaints_created_at` (`created_at`),
  CONSTRAINT `fk_complaints_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complaints`
--

LOCK TABLES `complaints` WRITE;
/*!40000 ALTER TABLE `complaints` DISABLE KEYS */;
INSERT INTO `complaints` VALUES (1,1,'road potholes','Pothole','rathi nagar','low','asdfghjkqwertyuiopzxcvbnm','7666126392',0,21.027226,75.563008,'New','2025-11-21 15:20:48',NULL),(2,1,'road street light','Street Light','gadge nagar','low','lkjhgfdsamnbvcxzpoiuytrewq','7458963210',0,21.027226,75.563008,'Resolved','2025-11-21 15:23:25','2025-11-24 15:25:42'),(3,1,'road water logging','Water Logging','rajkamal','low','water logging','8547963210',0,20.950283,77.764511,'New','2025-11-21 15:26:55',NULL),(4,1,'signage','Signage','rajapeth','low','rajapeth','4785693210',0,21.027226,75.563008,'New','2025-11-21 15:29:08',NULL),(5,1,'crac','Cracks','rathi nagar','low','cddc','7458963210',0,20.950286,77.764507,'Resolved','2025-11-21 15:36:00','2025-11-25 12:21:10'),(10,1,'Road Problem','Pothole','Amravati','low','road damage',NULL,0,NULL,NULL,'New','2025-12-15 18:08:16',NULL),(11,1,'crack','Cracks','shankar nagar rd','low','cracks','7418529630',0,21.141914,79.085568,'New','2025-12-15 23:44:32',NULL);
/*!40000 ALTER TABLE `complaints` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `organization` varchar(255) DEFAULT NULL,
  `user_type` varchar(50) DEFAULT NULL,
  `password_hash` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `avatar` varchar(255) DEFAULT NULL,
  `userscol` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_users_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'jay','joshi','jaykumarjoshi37@gmail.com',NULL,'engineer','scrypt:32768:8:1$Hajc6vBTBnmWEJHx$c7ad0b65382fcb0ec5046f544561464b2553376ce3ed5c16eb16efcb78f296384a802513c7363705e4c036fafb764b01bcc5634b36b618829d68da3542e87e9d','2025-11-20 09:18:00','avatar.jpg',''),(4,'amit','sawant',NULL,NULL,NULL,NULL,'2025-12-15 12:35:46',NULL,NULL),(5,'amit','sawant',NULL,NULL,NULL,NULL,'2025-12-15 17:36:05',NULL,NULL),(6,'%s','%s',NULL,NULL,NULL,NULL,'2025-12-15 17:37:21',NULL,NULL),(7,'shrikant','bhendekar','shrikant@gmail.com','asd','engineer','scrypt:32768:8:1$Xhw95n53yFbgxiN4$624663b4325b149d4bf6af8f636e3b73eee489006d4a46e5a5d53019520a8d82e0b2850b16fa58ec1ed194c68cd312e822820802b660419b4a1d9b8a5aefeefa','2025-12-15 17:49:00',NULL,NULL),(8,'litsbros','pvt ltd','litsbros@gmail.com','software company','other','scrypt:32768:8:1$6XoXNpFTVI8PO1sF$1f3e75e69c3e98418bc2565af2808e5decdc25c5a8ad344f56a024f557c889a0f1ea1c37b01b99e01392e23d01efaf680004f4edd22823a73179f3ea1b5aed67','2025-12-15 17:50:39',NULL,NULL),(9,'aarti','joshi','aartijoshi@gmail.com','asdfg','engineer','scrypt:32768:8:1$j02ID8RVUSBhonFr$f4c87beba54f989c6373e6e48e81b9a009e7f2c87f8cab6c887c19d31e023abefa3d3c6ec48c03bb8e7915409d2776273701b3d026c69328487497eaa24aac07','2025-12-15 17:59:51',NULL,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-15 23:51:25
