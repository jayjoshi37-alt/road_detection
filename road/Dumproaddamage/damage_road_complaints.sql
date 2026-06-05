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
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complaints`
--

LOCK TABLES `complaints` WRITE;
/*!40000 ALTER TABLE `complaints` DISABLE KEYS */;
INSERT INTO `complaints` VALUES (1,1,'road potholes','Pothole','rathi nagar','low','asdfghjkqwertyuiopzxcvbnm','7666126392',0,21.027226,75.563008,'New','2025-11-21 15:20:48',NULL),(2,1,'road street light','Street Light','gadge nagar','low','lkjhgfdsamnbvcxzpoiuytrewq','7458963210',0,21.027226,75.563008,'Resolved','2025-11-21 15:23:25','2025-11-24 15:25:42'),(3,1,'road water logging','Water Logging','rajkamal','low','water logging','8547963210',0,20.950283,77.764511,'New','2025-11-21 15:26:55',NULL),(4,1,'signage','Signage','rajapeth','low','rajapeth','4785693210',0,21.027226,75.563008,'New','2025-11-21 15:29:08',NULL),(5,1,'crac','Cracks','rathi nagar','low','cddc','7458963210',0,20.950286,77.764507,'Resolved','2025-11-21 15:36:00','2025-11-25 12:21:10'),(10,1,'Road Problem','Pothole','Amravati','low','road damage',NULL,0,NULL,NULL,'New','2025-12-15 18:08:16',NULL),(11,1,'crack','Cracks','shankar nagar rd','low','cracks','7418529630',0,21.141914,79.085568,'New','2025-12-15 23:44:32',NULL),(12,10,'road damage','Pothole','street 2','low','..',NULL,0,NULL,NULL,'New','2025-12-17 23:00:33',NULL),(13,10,'road 3','Pothole','street 4','low','ww',NULL,0,NULL,NULL,'New','2025-12-17 23:30:42',NULL),(14,10,'road 4','Pothole','street 5','high','qa',NULL,0,NULL,NULL,'New','2025-12-18 00:32:26',NULL),(15,10,'road 6','Pothole','street 20','low','sdsd',NULL,0,NULL,NULL,'New','2025-12-18 15:33:45',NULL),(16,10,'crack','Cracks','a','low','adadas',NULL,0,NULL,NULL,'New','2025-12-23 21:57:16',NULL),(17,10,'crack','Cracks','aa','low','aaa',NULL,0,NULL,NULL,'New','2025-12-23 22:06:56',NULL),(18,10,'safafaasfa','Cracks','sffssf','low','asffsff',NULL,0,NULL,NULL,'New','2025-12-23 22:26:50',NULL),(20,10,'aaaaaaa','Pothole','aaaaaa','low','aaaaa',NULL,0,NULL,NULL,'New','2025-12-23 22:42:19',NULL),(21,10,'sssssss','Pothole','ssssss','low','ssssss',NULL,0,NULL,NULL,'New','2025-12-23 22:43:30',NULL),(22,10,'dsdsd','Pothole','dsdsdsd','low','sdsdsds',NULL,0,NULL,NULL,'New','2025-12-23 22:51:21',NULL),(23,10,'aaaaafff','Pothole','aaaaafff','low','aaaaafff',NULL,0,NULL,NULL,'New','2025-12-23 22:59:19',NULL),(24,10,'aaaacccc','Cracks','cccc','low','ccasasdasd',NULL,0,NULL,NULL,'New','2025-12-23 23:00:31',NULL),(25,10,'sdssdsdsdsdsdssds','Pothole','dsdsdsds','low','dsdsdsdsd',NULL,0,NULL,NULL,'New','2025-12-23 23:08:11',NULL),(26,10,'adsadadasdasd','Pothole','sadasd','low','asdsdad',NULL,0,NULL,NULL,'New','2025-12-23 23:11:01',NULL),(27,10,'sds','Cracks','a','low','a',NULL,0,NULL,NULL,'New','2025-12-23 23:16:55',NULL),(28,10,'a','Pothole','a','low','a',NULL,0,NULL,NULL,'New','2025-12-24 00:38:15',NULL),(29,10,'a','Pothole','s','low','d',NULL,0,NULL,NULL,'New','2025-12-24 00:47:59',NULL),(30,10,'s','Pothole','d','low','ds',NULL,0,NULL,NULL,'New','2025-12-24 00:49:37',NULL),(31,10,'a','Pothole','a','low','a',NULL,0,NULL,NULL,'New','2025-12-24 00:50:15',NULL),(32,10,'sdsd','Pothole','sds','low','sdsd',NULL,0,NULL,NULL,'New','2025-12-24 00:51:30',NULL),(33,10,'ssds','Pothole','s','low','d',NULL,0,NULL,NULL,'New','2025-12-24 00:53:27',NULL),(34,10,'sd','Cracks','s','low','sds',NULL,0,NULL,NULL,'New','2025-12-24 00:56:04',NULL),(35,10,'s','Cracks','a','low','a',NULL,0,NULL,NULL,'New','2025-12-24 00:56:55',NULL),(36,10,'h','Pothole','h','low','h',NULL,0,NULL,NULL,'New','2025-12-24 00:57:29',NULL),(37,10,'h','Pothole','f','low','f',NULL,0,NULL,NULL,'New','2025-12-24 00:58:02',NULL),(38,10,'s','Pothole','s','low','s',NULL,0,NULL,NULL,'New','2025-12-24 00:59:18',NULL),(39,10,'a','Cracks','a','low','a',NULL,0,NULL,NULL,'New','2025-12-24 01:01:44',NULL),(40,10,'s','Cracks','s','low','s',NULL,0,NULL,NULL,'New','2025-12-24 01:02:06',NULL),(41,10,'ssd','Pothole','sds','low','sds',NULL,0,NULL,NULL,'New','2025-12-24 01:04:08',NULL),(42,10,'ewew','Pothole','wew','low','wewe',NULL,0,NULL,NULL,'New','2025-12-24 01:04:53',NULL),(43,10,'asa','Pothole','sa','low','sas',NULL,0,NULL,NULL,'New','2025-12-24 01:08:54',NULL),(44,10,'sds','Pothole','sdsd','low','sdsds',NULL,0,NULL,NULL,'New','2025-12-24 01:09:43',NULL),(45,10,'sds','Pothole','sds','low','ds',NULL,0,NULL,NULL,'New','2025-12-24 01:11:39',NULL),(46,10,'sds','Cracks','dsds','low','sdsd',NULL,0,NULL,NULL,'New','2025-12-24 01:13:21',NULL),(47,10,'sds','Pothole','sd','low','sdsd',NULL,0,NULL,NULL,'New','2025-12-24 01:14:39',NULL),(48,10,'sds','Pothole','sds','low','dsd',NULL,0,NULL,NULL,'New','2025-12-24 01:15:20',NULL),(49,10,'sdsd','Cracks','sds','low','sds',NULL,0,NULL,NULL,'New','2025-12-24 01:16:17',NULL),(50,10,'s','Pothole','s','low','s',NULL,0,NULL,NULL,'New','2025-12-24 01:17:37',NULL),(51,10,'ss','Water Logging','s','low','s',NULL,0,NULL,NULL,'New','2025-12-24 01:18:28',NULL),(52,10,'dsds','Pothole','s','low','s',NULL,0,NULL,NULL,'New','2025-12-24 01:19:45',NULL),(53,10,'dsds','Pothole','dsds','low','ds',NULL,0,NULL,NULL,'New','2025-12-24 01:20:14',NULL),(54,10,'gfgf','Pothole','fgf','low','fgf',NULL,0,NULL,NULL,'New','2025-12-24 01:23:53',NULL),(55,10,'s','Pothole','s','low','s',NULL,0,NULL,NULL,'New','2025-12-24 01:28:01',NULL),(56,10,'s','Pothole','s','low','s',NULL,0,NULL,NULL,'New','2025-12-24 01:28:26',NULL),(57,10,'sasa','Pothole','as','low','a',NULL,0,NULL,NULL,'New','2025-12-24 01:31:05',NULL),(58,10,'as','Pothole','sa','low','a',NULL,0,NULL,NULL,'New','2025-12-24 01:31:59',NULL),(59,10,'a','Pothole','a','low','a',NULL,0,NULL,NULL,'New','2025-12-24 01:34:47',NULL),(60,10,'sds','Cracks','ds','low','sd',NULL,0,NULL,NULL,'New','2025-12-24 13:19:54',NULL),(61,10,'sdsds','Cracks','sds','low','dsd',NULL,0,NULL,NULL,'New','2025-12-24 13:21:32',NULL),(62,10,'sds','Cracks','sdsd','low','sdd',NULL,0,NULL,NULL,'New','2025-12-24 13:22:23',NULL),(65,10,'ss','Pothole','ds','low','sds',NULL,0,NULL,NULL,'New','2025-12-24 14:18:26',NULL);
/*!40000 ALTER TABLE `complaints` ENABLE KEYS */;
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
