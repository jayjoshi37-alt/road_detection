-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: damage_road
-- ------------------------------------------------------
-- Server version	8.0.41

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
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'jay','joshi','jaykumarjoshi37@gmail.com',NULL,'engineer','scrypt:32768:8:1$Hajc6vBTBnmWEJHx$c7ad0b65382fcb0ec5046f544561464b2553376ce3ed5c16eb16efcb78f296384a802513c7363705e4c036fafb764b01bcc5634b36b618829d68da3542e87e9d','2025-11-20 09:18:00','avatar.jpg',''),(4,'amit','sawant',NULL,NULL,NULL,NULL,'2025-12-15 12:35:46',NULL,NULL),(5,'amit','sawant',NULL,NULL,NULL,NULL,'2025-12-15 17:36:05',NULL,NULL),(6,'%s','%s',NULL,NULL,NULL,NULL,'2025-12-15 17:37:21',NULL,NULL),(7,'shrikant','bhendekar','shrikant@gmail.com','asd','engineer','scrypt:32768:8:1$Xhw95n53yFbgxiN4$624663b4325b149d4bf6af8f636e3b73eee489006d4a46e5a5d53019520a8d82e0b2850b16fa58ec1ed194c68cd312e822820802b660419b4a1d9b8a5aefeefa','2025-12-15 17:49:00',NULL,NULL),(8,'litsbros','pvt ltd','litsbros@gmail.com','software company','other','scrypt:32768:8:1$6XoXNpFTVI8PO1sF$1f3e75e69c3e98418bc2565af2808e5decdc25c5a8ad344f56a024f557c889a0f1ea1c37b01b99e01392e23d01efaf680004f4edd22823a73179f3ea1b5aed67','2025-12-15 17:50:39',NULL,NULL),(9,'aarti','joshi','aartijoshi@gmail.com','asdfg','engineer','scrypt:32768:8:1$j02ID8RVUSBhonFr$f4c87beba54f989c6373e6e48e81b9a009e7f2c87f8cab6c887c19d31e023abefa3d3c6ec48c03bb8e7915409d2776273701b3d026c69328487497eaa24aac07','2025-12-15 17:59:51',NULL,NULL),(10,'testing','user','testing@gmail.com','','contractor','scrypt:32768:8:1$3MZowdEmqsRQSWKA$dcd87e0577b07c27370322d3717548d931637f71bbe86115be1663fcb396a58f611f18aae7a147ca6ca3e06543fe76a8225fa4a8eb09c095a2229a286e2dd693','2025-12-17 16:51:59',NULL,NULL);
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

-- Dump completed on 2025-12-24 15:04:10
