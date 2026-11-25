-- Migración para BDs existentes creadas antes de "Apartar butacas temporalmente".
-- En BDs nuevas init_db.sql ya crea esta tabla; este script es idempotente.
CREATE TABLE IF NOT EXISTS `reservas_temporales_butacas` (
  `id_reserva_temporal` int(11) NOT NULL AUTO_INCREMENT,
  `id_funcion` int(11) NOT NULL,
  `id_butaca` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `token_reserva` varchar(64) NOT NULL,
  `expira_en` datetime NOT NULL,
  PRIMARY KEY (`id_reserva_temporal`),
  UNIQUE KEY `uq_reserva_temporal_butaca` (`id_funcion`,`id_butaca`),
  KEY `idx_reserva_temporal_token` (`token_reserva`),
  KEY `idx_reserva_temporal_expira` (`expira_en`),
  CONSTRAINT `reservas_temporales_funcion_fk` FOREIGN KEY (`id_funcion`) REFERENCES `funciones` (`id_funcion`) ON DELETE CASCADE,
  CONSTRAINT `reservas_temporales_butaca_fk` FOREIGN KEY (`id_butaca`) REFERENCES `butacas` (`id_butaca`) ON DELETE CASCADE,
  CONSTRAINT `reservas_temporales_usuario_fk` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
