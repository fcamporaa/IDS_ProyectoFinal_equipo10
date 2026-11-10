-- =============================================================================
-- Cine Paradiso - DDL de Base de Datos
-- Cátedra Lanzillotta - IDS 2026
-- Compatible con MySQL 8.0, MariaDB y TiDB Cloud (DDL Directo con AUTO_INCREMENT)
-- =============================================================================

CREATE DATABASE IF NOT EXISTS `proyecto_integrador`;
USE `proyecto_integrador`;

SET FOREIGN_KEY_CHECKS = 0;

-- 1. Locales (Complejos de Cines)
DROP TABLE IF EXISTS `locales`;
CREATE TABLE `locales` (
  `id_local` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `direccion` varchar(255) NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_local`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 2. Salas
DROP TABLE IF EXISTS `salas`;
CREATE TABLE `salas` (
  `id_sala` int(11) NOT NULL AUTO_INCREMENT,
  `id_local` int(11) NOT NULL,
  `numero` smallint(6) NOT NULL,
  `activa` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_sala`),
  KEY `id_local` (`id_local`),
  CONSTRAINT `salas_ibfk_1` FOREIGN KEY (`id_local`) REFERENCES `locales` (`id_local`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 3. Butacas
DROP TABLE IF EXISTS `butacas`;
CREATE TABLE `butacas` (
  `id_butaca` int(11) NOT NULL AUTO_INCREMENT,
  `id_sala` int(11) NOT NULL,
  `fila` varchar(5) NOT NULL,
  `numero` smallint(6) NOT NULL,
  `activa` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_butaca`),
  KEY `id_sala` (`id_sala`),
  CONSTRAINT `butacas_ibfk_1` FOREIGN KEY (`id_sala`) REFERENCES `salas` (`id_sala`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 4. Géneros de Películas
DROP TABLE IF EXISTS `generos`;
CREATE TABLE `generos` (
  `id_genero` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`id_genero`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 5. Películas
DROP TABLE IF EXISTS `peliculas`;
CREATE TABLE `peliculas` (
  `id_pelicula` int(11) NOT NULL AUTO_INCREMENT,
  `origen_api` enum('OMDB','TMDB','CUSTOM') NOT NULL,
  `id_api` varchar(50) DEFAULT NULL,
  `titulo` varchar(250) NOT NULL,
  `sinopsis` text DEFAULT NULL,
  `poster_url` varchar(1000) DEFAULT NULL,
  `trailer_url` varchar(1000) DEFAULT NULL,
  `duracion_min` smallint(6) DEFAULT NULL,
  `clasificacion` varchar(20) DEFAULT NULL,
  `anio_estreno` smallint(6) DEFAULT NULL,
  `activa` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_pelicula`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 6. Relación Películas y Géneros (Muchos a Muchos)
DROP TABLE IF EXISTS `pelicula_generos`;
CREATE TABLE `pelicula_generos` (
  `id_pelicula` int(11) NOT NULL,
  `id_genero` int(11) NOT NULL,
  PRIMARY KEY (`id_pelicula`,`id_genero`),
  KEY `id_genero` (`id_genero`),
  CONSTRAINT `pelicula_generos_ibfk_1` FOREIGN KEY (`id_pelicula`) REFERENCES `peliculas` (`id_pelicula`) ON DELETE CASCADE,
  CONSTRAINT `pelicula_generos_ibfk_2` FOREIGN KEY (`id_genero`) REFERENCES `generos` (`id_genero`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 7. Funciones
DROP TABLE IF EXISTS `funciones`;
CREATE TABLE `funciones` (
  `id_funcion` int(11) NOT NULL AUTO_INCREMENT,
  `id_pelicula` int(11) NOT NULL,
  `id_sala` int(11) NOT NULL,
  `inicio` datetime NOT NULL,
  `fin` datetime NOT NULL,
  `formato` enum('2D','3D','4D') NOT NULL,
  `idioma` varchar(50) DEFAULT NULL,
  `subtitulada` tinyint(1) NOT NULL DEFAULT 0,
  `precio_entrada` decimal(10,2) NOT NULL,
  `estado` enum('PROGRAMADA','EN_CURSO','CANCELADA','FINALIZADA') NOT NULL,
  PRIMARY KEY (`id_funcion`),
  KEY `id_pelicula` (`id_pelicula`),
  KEY `id_sala` (`id_sala`),
  CONSTRAINT `funciones_ibfk_1` FOREIGN KEY (`id_pelicula`) REFERENCES `peliculas` (`id_pelicula`),
  CONSTRAINT `funciones_ibfk_2` FOREIGN KEY (`id_sala`) REFERENCES `salas` (`id_sala`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 8. Usuarios
DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(120) NOT NULL,
  `email` varchar(255) NOT NULL,
  `numero_socio` varchar(30) DEFAULT NULL,
  `contrasena_hash` varchar(255) NOT NULL,
  `rol` enum('CLIENTE','ADMINISTRADOR') NOT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT current_timestamp(),
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 9. Servicios (Candy Bar)
DROP TABLE IF EXISTS `servicios`;
CREATE TABLE `servicios` (
  `id_servicio` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `tipo` enum('COMIDA','BEBIDA') NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_servicio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 10. Compras
DROP TABLE IF EXISTS `compras`;
CREATE TABLE `compras` (
  `id_compra` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `id_funcion` int(11) NOT NULL,
  `codigo_reserva` varchar(40) NOT NULL,
  `email_comprobante` varchar(255) DEFAULT NULL,
  `creada_en` datetime NOT NULL DEFAULT current_timestamp(),
  `estado` enum('PENDIENTE','PAGADA','CANCELADA') NOT NULL,
  `medio_pago` varchar(50) DEFAULT NULL,
  `subtotal_entradas` decimal(10,2) NOT NULL,
  `subtotal_servicios` decimal(10,2) NOT NULL,
  `cargo_servicio` decimal(10,2) NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `qr_token` varchar(160) DEFAULT NULL,
  `qr_validado_en` datetime DEFAULT NULL,
  `cancelada_en` datetime DEFAULT NULL,
  PRIMARY KEY (`id_compra`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_funcion` (`id_funcion`),
  CONSTRAINT `compras_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `compras_ibfk_2` FOREIGN KEY (`id_funcion`) REFERENCES `funciones` (`id_funcion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 11. Compra Servicios (Detalle de Candy Bar en Compra)
DROP TABLE IF EXISTS `compra_servicios`;
CREATE TABLE `compra_servicios` (
  `id_compra_servicio` int(11) NOT NULL AUTO_INCREMENT,
  `id_compra` int(11) NOT NULL,
  `id_servicio` int(11) NOT NULL,
  `cantidad` smallint(6) NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id_compra_servicio`),
  KEY `id_compra` (`id_compra`),
  KEY `id_servicio` (`id_servicio`),
  CONSTRAINT `compra_servicios_ibfk_1` FOREIGN KEY (`id_compra`) REFERENCES `compras` (`id_compra`) ON DELETE CASCADE,
  CONSTRAINT `compra_servicios_ibfk_2` FOREIGN KEY (`id_servicio`) REFERENCES `servicios` (`id_servicio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 12. Entradas
DROP TABLE IF EXISTS `entradas`;
CREATE TABLE `entradas` (
  `id_entrada` int(11) NOT NULL AUTO_INCREMENT,
  `id_compra` int(11) DEFAULT NULL,
  `id_funcion` int(11) NOT NULL,
  `id_butaca` int(11) NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `estado` enum('DISPONIBLE','RESERVADA','OCUPADA','CANCELADA') NOT NULL,
  `id_butaca_ocupada` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_entrada`),
  KEY `id_compra` (`id_compra`),
  KEY `id_funcion` (`id_funcion`),
  KEY `id_butaca` (`id_butaca`),
  CONSTRAINT `entradas_ibfk_1` FOREIGN KEY (`id_compra`) REFERENCES `compras` (`id_compra`) ON DELETE CASCADE,
  CONSTRAINT `entradas_ibfk_2` FOREIGN KEY (`id_funcion`) REFERENCES `funciones` (`id_funcion`),
  CONSTRAINT `entradas_ibfk_3` FOREIGN KEY (`id_butaca`) REFERENCES `butacas` (`id_butaca`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 13. Reseñas
DROP TABLE IF EXISTS `resenas`;
CREATE TABLE `resenas` (
  `id_resena` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `id_pelicula` int(11) NOT NULL,
  `id_compra` int(11) NOT NULL,
  `puntuacion` tinyint(4) NOT NULL,
  `comentario` text DEFAULT NULL,
  `creada_en` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id_resena`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_pelicula` (`id_pelicula`),
  KEY `id_compra` (`id_compra`),
  CONSTRAINT `resenas_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `resenas_ibfk_2` FOREIGN KEY (`id_pelicula`) REFERENCES `peliculas` (`id_pelicula`),
  CONSTRAINT `resenas_ibfk_3` FOREIGN KEY (`id_compra`) REFERENCES `compras` (`id_compra`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 14. Validaciones QR
DROP TABLE IF EXISTS `validaciones_qr`;
CREATE TABLE `validaciones_qr` (
  `id_validacion` int(11) NOT NULL AUTO_INCREMENT,
  `id_compra` int(11) NOT NULL,
  `id_administrador` int(11) NOT NULL,
  `fecha_validacion` datetime NOT NULL,
  `resultado` enum('EXITO','FALLIDO','REUTILIZADO') NOT NULL,
  PRIMARY KEY (`id_validacion`),
  KEY `id_compra` (`id_compra`),
  KEY `id_administrador` (`id_administrador`),
  CONSTRAINT `validaciones_qr_ibfk_1` FOREIGN KEY (`id_compra`) REFERENCES `compras` (`id_compra`),
  CONSTRAINT `validaciones_qr_ibfk_2` FOREIGN KEY (`id_administrador`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

SET FOREIGN_KEY_CHECKS = 1;
