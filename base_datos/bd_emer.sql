-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: app_emergencias
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
-- Table structure for table `accidentes`
--

DROP TABLE IF EXISTS `accidentes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accidentes` (
  `id_accidentes` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int DEFAULT NULL,
  `id_tip_acci` int DEFAULT NULL,
  `direccion` varchar(50) DEFAULT NULL,
  `fecha_hora` datetime DEFAULT NULL,
  `descripcion` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_accidentes`),
  KEY `fk_accidentes_usuario` (`id_usuario`),
  KEY `fk_accidentes_tipo_accidente` (`id_tip_acci`),
  CONSTRAINT `fk_accidentes_tipo_accidente` FOREIGN KEY (`id_tip_acci`) REFERENCES `tipo_accidente` (`id_tipo_acc`) ON UPDATE CASCADE,
  CONSTRAINT `fk_accidentes_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accidentes`
--

LOCK TABLES `accidentes` WRITE;
/*!40000 ALTER TABLE `accidentes` DISABLE KEYS */;
/*!40000 ALTER TABLE `accidentes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contactos`
--

DROP TABLE IF EXISTS `contactos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contactos` (
  `id_contactos` int NOT NULL AUTO_INCREMENT,
  `nro_emer` varchar(10) DEFAULT NULL,
  `nombre` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id_contactos`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contactos`
--

LOCK TABLES `contactos` WRITE;
/*!40000 ALTER TABLE `contactos` DISABLE KEYS */;
/*!40000 ALTER TABLE `contactos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalle_tuto`
--

DROP TABLE IF EXISTS `detalle_tuto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_tuto` (
  `id_datalle` int NOT NULL AUTO_INCREMENT,
  `id_tuto` int DEFAULT NULL,
  `imagenes` varchar(1) DEFAULT NULL,
  `descripcion` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_datalle`),
  KEY `fk_detalle_tuto_tutoriales` (`id_tuto`),
  CONSTRAINT `fk_detalle_tuto_tutoriales` FOREIGN KEY (`id_tuto`) REFERENCES `tutoriales` (`id_tuto`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_tuto`
--

LOCK TABLES `detalle_tuto` WRITE;
/*!40000 ALTER TABLE `detalle_tuto` DISABLE KEYS */;
/*!40000 ALTER TABLE `detalle_tuto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `modo_emergencia`
--

DROP TABLE IF EXISTS `modo_emergencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modo_emergencia` (
  `id_mod_emer` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int DEFAULT NULL,
  `direccion` varchar(50) DEFAULT NULL,
  `fecha_hora` datetime DEFAULT NULL,
  PRIMARY KEY (`id_mod_emer`),
  KEY `fk_modo_emergencia_usuario` (`id_usuario`),
  CONSTRAINT `fk_modo_emergencia_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modo_emergencia`
--

LOCK TABLES `modo_emergencia` WRITE;
/*!40000 ALTER TABLE `modo_emergencia` DISABLE KEYS */;
/*!40000 ALTER TABLE `modo_emergencia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipo_accidente`
--

DROP TABLE IF EXISTS `tipo_accidente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipo_accidente` (
  `id_tipo_acc` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int DEFAULT NULL,
  `direccion` varchar(50) DEFAULT NULL,
  `fecha_hora` datetime DEFAULT NULL,
  PRIMARY KEY (`id_tipo_acc`),
  KEY `fk_tipo_accidente_usuario` (`id_usuario`),
  CONSTRAINT `fk_tipo_accidente_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipo_accidente`
--

LOCK TABLES `tipo_accidente` WRITE;
/*!40000 ALTER TABLE `tipo_accidente` DISABLE KEYS */;
/*!40000 ALTER TABLE `tipo_accidente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tutoriales`
--

DROP TABLE IF EXISTS `tutoriales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tutoriales` (
  `id_tuto` int NOT NULL AUTO_INCREMENT,
  `titulo` varchar(15) DEFAULT NULL,
  `link` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_tuto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tutoriales`
--

LOCK TABLES `tutoriales` WRITE;
/*!40000 ALTER TABLE `tutoriales` DISABLE KEYS */;
/*!40000 ALTER TABLE `tutoriales` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(15) DEFAULT NULL,
  `ubicacion` varchar(50) DEFAULT NULL,
  `telefono` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-03 20:01:31
