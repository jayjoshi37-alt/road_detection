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
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complaint_images`
--

LOCK TABLES `complaint_images` WRITE;
/*!40000 ALTER TABLE `complaint_images` DISABLE KEYS */;
INSERT INTO `complaint_images` VALUES (1,1,'image_1.jpg','2025-11-21 15:20:48'),(2,2,'image_1.jpg','2025-11-21 15:23:25'),(3,3,'image_1.jpg','2025-11-21 15:26:55'),(4,4,'image_1.jpg','2025-11-21 15:29:09'),(5,5,'image_1.jpg','2025-11-21 15:36:00'),(10,10,'image_1.jpg','2025-12-15 18:08:16'),(11,11,'image_1.jpg','2025-12-15 23:44:32'),(12,12,'image_1.jpg','2025-12-17 23:00:33'),(13,13,'original_1.jpg','2025-12-17 23:30:42'),(14,14,'original_1.png','2025-12-18 00:32:26'),(15,15,'original_1.jpg','2025-12-18 15:33:45'),(16,16,'original_1.jpg','2025-12-23 21:57:16'),(17,17,'original_1.jpg','2025-12-23 22:06:56'),(18,18,'original_1.jpg','2025-12-23 22:26:50'),(20,20,'original_1.png','2025-12-23 22:42:19'),(21,21,'original_1.jpg','2025-12-23 22:43:30'),(22,22,'original_1.jpg','2025-12-23 22:51:21'),(23,23,'original_1.jpg','2025-12-23 22:59:19'),(24,24,'original_1.jpg','2025-12-23 23:00:31'),(25,25,'original_1.jpg','2025-12-23 23:08:11'),(26,26,'original_1.jpg','2025-12-23 23:11:02'),(27,27,'original_1.jpg','2025-12-23 23:16:55'),(28,28,'original_1.jpg','2025-12-24 00:38:15'),(29,29,'original_1.jpg','2025-12-24 00:47:59'),(30,30,'original_1.jpg','2025-12-24 00:49:37'),(31,31,'original_1.jpg','2025-12-24 00:50:15'),(32,32,'original_1.jpg','2025-12-24 00:51:30'),(33,33,'original_1.jpg','2025-12-24 00:53:27'),(34,34,'original_1.jpg','2025-12-24 00:56:04'),(35,35,'original_1.jpg','2025-12-24 00:56:55'),(36,36,'original_1.jpg','2025-12-24 00:57:29'),(37,37,'original_1.jpg','2025-12-24 00:58:02'),(38,38,'original_1.jpg','2025-12-24 00:59:18'),(39,39,'original_1.jpg','2025-12-24 01:01:44'),(40,40,'original_1.jpg','2025-12-24 01:02:06'),(41,41,'original_1.jpg','2025-12-24 01:04:08'),(42,42,'original_1.jpg','2025-12-24 01:04:53'),(43,43,'original_1.jpg','2025-12-24 01:08:54'),(44,44,'original_1.jpg','2025-12-24 01:09:43'),(45,45,'original_1.jpg','2025-12-24 01:11:39'),(46,46,'original_1.jpg','2025-12-24 01:13:21'),(47,47,'original_1.jpg','2025-12-24 01:14:39'),(48,48,'original_1.jpg','2025-12-24 01:15:20'),(49,49,'original_1.jpg','2025-12-24 01:16:17'),(50,50,'original_1.jpg','2025-12-24 01:17:37'),(51,51,'original_1.jpg','2025-12-24 01:18:28'),(52,52,'original_1.jpg','2025-12-24 01:19:45'),(53,53,'original_1.jpg','2025-12-24 01:20:14'),(54,54,'original_1.jpg','2025-12-24 01:23:53'),(55,55,'original_1.jpg','2025-12-24 01:28:01'),(56,56,'original_1.jpg','2025-12-24 01:28:26'),(57,57,'original_1.jpg','2025-12-24 01:31:05'),(58,58,'original_1.jpg','2025-12-24 01:31:59'),(59,59,'original_1.jpg','2025-12-24 01:34:47'),(60,60,'original_1.jpg','2025-12-24 13:19:54'),(61,61,'original_1.jpg','2025-12-24 13:21:32'),(62,62,'original_1.jpg','2025-12-24 13:22:23'),(65,65,'original_1.jpg','2025-12-24 14:18:26');
/*!40000 ALTER TABLE `complaint_images` ENABLE KEYS */;
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
