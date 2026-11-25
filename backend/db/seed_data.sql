-- =============================================================================
-- Datos Semilla (Seeds) para Cine Paradiso - Presentación y Exposición Final
-- Cátedra Lanzillotta - IDS 2026
-- Compatible con MySQL 8.0, MariaDB y TiDB Cloud
-- =============================================================================
SET NAMES utf8mb4;
USE `proyecto_integrador`;

-- -----------------------------------------------------------------------------
-- 1. USUARIOS DE PRUEBA
-- Contraseñas hasheadas con bcrypt (Password: Admin1234! / Cliente1234!):
-- 1: Administrador Cine   (admin@cineparadiso.com)
-- 2: Juan Pérez           (cliente@cineparadiso.com)
-- 3: María Gómez          (maria@cineparadiso.com)
-- 4: Lucas Rossi          (lucas@cineparadiso.com)
-- 5: Sofía Benítez        (sofia@cineparadiso.com)
-- 6: Carlos Méndez        (carlos@cineparadiso.com)
-- 7: Valentina López      (valentina@cineparadiso.com)
-- 8: Martín Díaz          (martin@cineparadiso.com)
-- -----------------------------------------------------------------------------
INSERT INTO `usuarios` (`id_usuario`, `nombre`, `email`, `numero_socio`, `contrasena_hash`, `rol`, `activo`) VALUES
(1, 'Administrador Cine', 'admin@cineparadiso.com', 'SOC-0001', '$2b$12$3sW5bQeAQI0lbQ7XD53HYOT053SWrnV118X25j2Xh7Zcin0Vo/FOW', 'ADMINISTRADOR', 1),
(2, 'Juan Pérez', 'cliente@cineparadiso.com', 'SOC-1002', '$2b$12$TQQG6hcUWZH399ePetm4suxPing6QKpBDiKJQI93ywVZAg5c3laji', 'CLIENTE', 1),
(3, 'María Gómez', 'maria@cineparadiso.com', 'SOC-1003', '$2b$12$TQQG6hcUWZH399ePetm4suxPing6QKpBDiKJQI93ywVZAg5c3laji', 'CLIENTE', 1),
(4, 'Lucas Rossi', 'lucas@cineparadiso.com', 'SOC-1004', '$2b$12$TQQG6hcUWZH399ePetm4suxPing6QKpBDiKJQI93ywVZAg5c3laji', 'CLIENTE', 1),
(5, 'Sofía Benítez', 'sofia@cineparadiso.com', 'SOC-1005', '$2b$12$TQQG6hcUWZH399ePetm4suxPing6QKpBDiKJQI93ywVZAg5c3laji', 'CLIENTE', 1),
(6, 'Carlos Méndez', 'carlos@cineparadiso.com', 'SOC-1006', '$2b$12$TQQG6hcUWZH399ePetm4suxPing6QKpBDiKJQI93ywVZAg5c3laji', 'CLIENTE', 1),
(7, 'Valentina López', 'valentina@cineparadiso.com', 'SOC-1007', '$2b$12$TQQG6hcUWZH399ePetm4suxPing6QKpBDiKJQI93ywVZAg5c3laji', 'CLIENTE', 1),
(8, 'Martín Díaz', 'martin@cineparadiso.com', 'SOC-1008', '$2b$12$TQQG6hcUWZH399ePetm4suxPing6QKpBDiKJQI93ywVZAg5c3laji', 'CLIENTE', 1)
ON DUPLICATE KEY UPDATE `email` = VALUES(`email`), `nombre` = VALUES(`nombre`), `rol` = VALUES(`rol`);

-- -----------------------------------------------------------------------------
-- 2. GÉNEROS CINEMATOGRÁFICOS (8 Géneros Canónicos)
-- -----------------------------------------------------------------------------
INSERT INTO `generos` (`id_genero`, `nombre`) VALUES
(1, 'Acción'),
(2, 'Ciencia Ficción'),
(3, 'Aventura'),
(4, 'Drama'),
(5, 'Comedia'),
(6, 'Animación'),
(7, 'Suspenso'),
(8, 'Terror')
ON DUPLICATE KEY UPDATE `nombre` = VALUES(`nombre`);

-- -----------------------------------------------------------------------------
-- 3. LOCALES / COMPLEJOS (3 Sedes Diferenciadas)
-- -----------------------------------------------------------------------------
INSERT INTO `locales` (`id_local`, `nombre`, `direccion`, `activo`) VALUES
(1, 'Cine Paradiso Centro', 'Av. Corrientes 1240, CABA', 1),
(2, 'Cine Paradiso Palermo', 'Av. Santa Fe 3200, CABA', 1),
(3, 'Cine Paradiso Belgrano', 'Av. Cabildo 2180, CABA', 1)
ON DUPLICATE KEY UPDATE `nombre` = VALUES(`nombre`), `direccion` = VALUES(`direccion`);

-- -----------------------------------------------------------------------------
-- 4. SALAS
-- Local 1 (Centro):
--   Sala 1: Sala Premium (con filas VIP E, F, G y Generales A, B, C, D)
--   Sala 2: Sala Estándar (solo filas Generales A, B, C, D; sin puestos VIP)
-- Local 2 (Palermo):
--   Sala 3: Sala 3D Palermo (con filas VIP E, F)
-- Local 3 (Belgrano):
--   Sala 4: Sala Tradicional Belgrano (solo Generales A, B, C; sin puestos VIP)
-- -----------------------------------------------------------------------------
INSERT INTO `salas` (`id_sala`, `id_local`, `numero`, `activa`) VALUES
(1, 1, 1, 1),
(2, 1, 2, 1),
(3, 2, 1, 1),
(4, 3, 1, 1)
ON DUPLICATE KEY UPDATE `numero` = VALUES(`numero`), `id_local` = VALUES(`id_local`);

-- -----------------------------------------------------------------------------
-- 5. BUTACAS
-- Regla de Negocio: En la UI del frontend, las filas 'E', 'F' y 'G' son VIP D-BOX,
-- mientras que 'A', 'B', 'C' y 'D' son Generales.
-- -----------------------------------------------------------------------------
INSERT INTO `butacas` (`id_butaca`, `id_sala`, `fila`, `numero`, `activa`) VALUES
-- Sala 1 (Local 1 - Centro): 42 Butacas (Generales A-D + VIP E-G)
(1, 1, 'A', 1, 1), (2, 1, 'A', 2, 1), (3, 1, 'A', 3, 1), (4, 1, 'A', 4, 1), (5, 1, 'A', 5, 1), (6, 1, 'A', 6, 1),
(7, 1, 'B', 1, 1), (8, 1, 'B', 2, 1), (9, 1, 'B', 3, 1), (10, 1, 'B', 4, 1), (11, 1, 'B', 5, 1), (12, 1, 'B', 6, 1),
(13, 1, 'C', 1, 1), (14, 1, 'C', 2, 1), (15, 1, 'C', 3, 1), (16, 1, 'C', 4, 1), (17, 1, 'C', 5, 1), (18, 1, 'C', 6, 1),
(19, 1, 'D', 1, 1), (20, 1, 'D', 2, 1), (21, 1, 'D', 3, 1), (22, 1, 'D', 4, 1), (23, 1, 'D', 5, 1), (24, 1, 'D', 6, 1),
(25, 1, 'E', 1, 1), (26, 1, 'E', 2, 1), (27, 1, 'E', 3, 1), (28, 1, 'E', 4, 1), (29, 1, 'E', 5, 1), (30, 1, 'E', 6, 1),
(31, 1, 'F', 1, 1), (32, 1, 'F', 2, 1), (33, 1, 'F', 3, 1), (34, 1, 'F', 4, 1), (35, 1, 'F', 5, 1), (36, 1, 'F', 6, 1),
(37, 1, 'G', 1, 1), (38, 1, 'G', 2, 1), (39, 1, 'G', 3, 1), (40, 1, 'G', 4, 1), (41, 1, 'G', 5, 1), (42, 1, 'G', 6, 1),

-- Sala 2 (Local 1 - Centro): 24 Butacas (Solo Generales A-D, SIN VIP)
(43, 2, 'A', 1, 1), (44, 2, 'A', 2, 1), (45, 2, 'A', 3, 1), (46, 2, 'A', 4, 1), (47, 2, 'A', 5, 1), (48, 2, 'A', 6, 1),
(49, 2, 'B', 1, 1), (50, 2, 'B', 2, 1), (51, 2, 'B', 3, 1), (52, 2, 'B', 4, 1), (53, 2, 'B', 5, 1), (54, 2, 'B', 6, 1),
(55, 2, 'C', 1, 1), (56, 2, 'C', 2, 1), (57, 2, 'C', 3, 1), (58, 2, 'C', 4, 1), (59, 2, 'C', 5, 1), (60, 2, 'C', 6, 1),
(61, 2, 'D', 1, 1), (62, 2, 'D', 2, 1), (63, 2, 'D', 3, 1), (64, 2, 'D', 4, 1), (65, 2, 'D', 5, 1), (66, 2, 'D', 6, 1),

-- Sala 3 (Local 2 - Palermo): 30 Butacas (Generales A-C + VIP E-F)
(67, 3, 'A', 1, 1), (68, 3, 'A', 2, 1), (69, 3, 'A', 3, 1), (70, 3, 'A', 4, 1), (71, 3, 'A', 5, 1), (72, 3, 'A', 6, 1),
(73, 3, 'B', 1, 1), (74, 3, 'B', 2, 1), (75, 3, 'B', 3, 1), (76, 3, 'B', 4, 1), (77, 3, 'B', 5, 1), (78, 3, 'B', 6, 1),
(79, 3, 'C', 1, 1), (80, 3, 'C', 2, 1), (81, 3, 'C', 3, 1), (82, 3, 'C', 4, 1), (83, 3, 'C', 5, 1), (84, 3, 'C', 6, 1),
(85, 3, 'E', 1, 1), (86, 3, 'E', 2, 1), (87, 3, 'E', 3, 1), (88, 3, 'E', 4, 1), (89, 3, 'E', 5, 1), (90, 3, 'E', 6, 1),
(91, 3, 'F', 1, 1), (92, 3, 'F', 2, 1), (93, 3, 'F', 3, 1), (94, 3, 'F', 4, 1), (95, 3, 'F', 5, 1), (96, 3, 'F', 6, 1),

-- Sala 4 (Local 3 - Belgrano): 18 Butacas (Solo Generales A-C, SIN VIP)
(97, 4, 'A', 1, 1), (98, 4, 'A', 2, 1), (99, 4, 'A', 3, 1), (100, 4, 'A', 4, 1), (101, 4, 'A', 5, 1), (102, 4, 'A', 6, 1),
(103, 4, 'B', 1, 1), (104, 4, 'B', 2, 1), (105, 4, 'B', 3, 1), (106, 4, 'B', 4, 1), (107, 4, 'B', 5, 1), (108, 4, 'B', 6, 1),
(109, 4, 'C', 1, 1), (110, 4, 'C', 2, 1), (111, 4, 'C', 3, 1), (112, 4, 'C', 4, 1), (113, 4, 'C', 5, 1), (114, 4, 'C', 6, 1)
ON DUPLICATE KEY UPDATE `activa` = VALUES(`activa`);

-- -----------------------------------------------------------------------------
-- 6. PELÍCULAS (Consistentes con OMDb / IMDb tt IDs reales, pósters oficiales y tráilers)
-- -----------------------------------------------------------------------------
INSERT INTO `peliculas` (`id_pelicula`, `origen_api`, `id_api`, `titulo`, `sinopsis`, `poster_url`, `trailer_url`, `duracion_min`, `clasificacion`, `anio_estreno`, `activa`) VALUES
(1, 'OMDB', 'tt15239678', 'Dune: Parte Dos', 'Paul Atreides se une a Chani y a los Fremen mientras busca venganza contra los conspiradores que destruyeron a su familia.', 'https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg', 'https://www.youtube.com/embed/Way9Dexny3w', 166, '+13', 2024, 1),
(2, 'OMDB', 'tt15398776', 'Oppenheimer', 'La historia del físico estadounidense J. Robert Oppenheimer, su papel en el Proyecto Manhattan y el desarrollo de la bomba atómica.', 'https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg', 'https://www.youtube.com/embed/uYPbbksJxIg', 180, '+16', 2023, 1),
(3, 'OMDB', 'tt9362722', 'Spider-Man: Across the Spider-Verse', 'Miles Morales es catapultado a través del Multiverso, donde se encuentra con un equipo de Spider-People encargados de proteger su existencia.', 'https://image.tmdb.org/t/p/w500/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg', 'https://www.youtube.com/embed/cqGjhVJWtEg', 140, 'ATP', 2023, 1),
(4, 'OMDB', 'tt22022452', 'IntensaMente 2', 'Riley entra en la adolescencia y el cuartel general sufre una repentina demolición para hacer sitio a nuevas emociones inesperadas: Ansiedad, Envidia, Ennui y Vergüenza.', 'https://image.tmdb.org/t/p/w500/vpnVM9B6NMmQpWeZvzLvDESb2QY.jpg', 'https://www.youtube.com/embed/L4DrolmDxmw', 96, 'ATP', 2024, 1),
(5, 'OMDB', 'tt18411490', 'Alien: Romulus', 'Jóvenes colonizadores espaciales se encuentran cara a cara con la forma de vida más aterradora del universo mientras exploran una estación espacial abandonada.', 'https://image.tmdb.org/t/p/w500/b33nnKl1GSFbao4l3fZDDqsMx0F.jpg', 'https://www.youtube.com/embed/x0XDEhP4MQs', 119, '+16', 2024, 1),
(6, 'OMDB', 'tt1517268', 'Barbie', 'Barbie y Ken se lo están pasando en grande en el colorido y aparentemente perfecto mundo de Barbie Land. Sin embargo, cuando tienen la oportunidad de ir al mundo real, pronto descubren las alegrías y los peligros de vivir entre los humanos.', 'https://image.tmdb.org/t/p/w500/iuFNMS8U5cb6xfzi51Dbkovj7vM.jpg', 'https://www.youtube.com/embed/pBk4NYhWNMM', 114, 'ATP', 2023, 1),
(7, 'OMDB', 'tt0111161', 'Sueños de Libertad', 'Dos hombres encarcelados forjan una amistad a lo largo de varios años, encontrando consuelo y redención a través de actos de decencia común.', 'https://image.tmdb.org/t/p/w500/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg', 'https://www.youtube.com/embed/6hB3S9bIaco', 142, '+13', 1994, 1)
ON DUPLICATE KEY UPDATE `titulo` = VALUES(`titulo`), `sinopsis` = VALUES(`sinopsis`), `poster_url` = VALUES(`poster_url`), `trailer_url` = VALUES(`trailer_url`);

-- -----------------------------------------------------------------------------
-- 7. ASOCIACIÓN PELÍCULAS - GÉNEROS (Cubre los 8 géneros para filtros de Cartelera)
-- 1: Acción, 2: Ciencia Ficción, 3: Aventura, 4: Drama, 5: Comedia, 6: Animación, 7: Suspenso, 8: Terror
-- -----------------------------------------------------------------------------
INSERT INTO `pelicula_generos` (`id_pelicula`, `id_genero`) VALUES
(1, 2), -- Dune: Ciencia Ficción
(1, 3), -- Dune: Aventura
(2, 4), -- Oppenheimer: Drama
(2, 7), -- Oppenheimer: Suspenso
(3, 1), -- Spider-Man: Acción
(3, 6), -- Spider-Man: Animación
(4, 6), -- IntensaMente 2: Animación
(4, 5), -- IntensaMente 2: Comedia
(5, 8), -- Alien Romulus: Terror
(5, 2), -- Alien Romulus: Ciencia Ficción
(6, 5), -- Barbie: Comedia
(6, 3), -- Barbie: Aventura
(7, 4)  -- Sueños de Libertad: Drama
ON DUPLICATE KEY UPDATE `id_pelicula` = VALUES(`id_pelicula`);

-- -----------------------------------------------------------------------------
-- 8. SERVICIOS EXTRAS (Candy Bar con Cobertura Completa de los 5 Tipos)
-- -----------------------------------------------------------------------------
INSERT INTO `servicios` (`id_servicio`, `nombre`, `tipo`, `precio`, `activo`, `imagen_url`) VALUES
(1, 'Combo Mega Popcorn + 2 Gaseosas', 'COMBO', 9500.00, 1, 'https://images.unsplash.com/photo-1578849278619-e73505e9610f?auto=format&fit=crop&w=600&q=80'),
(2, 'Popcorn Balde Gigante Manteca', 'COMIDA', 6200.00, 1, 'https://images.unsplash.com/photo-1585647347483-22b66260dfff?auto=format&fit=crop&w=600&q=80'),
(3, 'Nachos con Cheddar Caliente', 'COMIDA', 5800.00, 1, 'https://images.unsplash.com/photo-1513456852971-30c0b8199d4d?auto=format&fit=crop&w=600&q=80'),
(4, 'Gaseosa Grande 750ml', 'BEBIDA', 3500.00, 1, 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=600&q=80'),
(5, 'Agua Mineral de Manantial 500ml', 'BEBIDA', 2400.00, 1, 'https://imgs.search.brave.com/L01DvhVynAsq21PQw2LyI1H2rr4I7h7nqBddPh0OzWQ/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5pc3RvY2twaG90/by5jb20vaWQvNDU0/MjczMzk5L2VzL2Zv/dG8vdmVydGllbmRv/LWFndWEtZGUtYm90/ZWxsYS1lbi12aWRy/aW8tc29icmUtZm9u/ZG8tYXp1bC5qcGc_/cz02MTJ4NjEyJnc9/MCZrPTIwJmM9dVNI/Y0RudWhPb2JVMlhC/cHFmYm5jMGtfaHNS/Mm56S1FfNE0yYmhy/SXM2cz0'),
(6, 'Vaso Coleccionable Edición 3D', 'OBJETO', 4500.00, 1, 'https://imgs.search.brave.com/efH8FqnxxQvqZp-8XxwFgtsTLlyH2gy9YMNpJvLTTd8/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9odHRw/Mi5tbHN0YXRpYy5j/b20vRF9RX05QXzJY/Xzk3OTYzOC1NTFU3/NzgxNzc1MTAzOF8w/NzIwMjQtVi53ZWJw'),
(7, 'Balde Metálico de Colección', 'OBJETO', 5200.00, 1, 'https://imgs.search.brave.com/S7iu1v6Z5ptXhO65UGG_k_h4AR5Ty3I00UsWUxuzeXs/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly90aWVu/ZGEuY2hpbGRyZW5z/LmNvbS5hci9zZXJ2/ZV9hcHBfYXNzZXQu/cGhwP2tpbmQ9cHJv/ZCZzej1ncmFuZGVz/JmZuPWYxXzQwMzY0/LmpwZyZ3PTkwMCZm/bXQ9d2VicA'),
(8, 'Promo 2x1 Popcorn Mediano', 'PROMOCION', 4900.00, 1, 'https://images.unsplash.com/photo-1505686994434-e3cc5abf1330?auto=format&fit=crop&w=600&q=80')
ON DUPLICATE KEY UPDATE `nombre` = VALUES(`nombre`), `tipo` = VALUES(`tipo`), `precio` = VALUES(`precio`), `imagen_url` = VALUES(`imagen_url`);

-- -----------------------------------------------------------------------------
-- 9. MATRIZ DE FUNCIONES CINEMATOGRÁFICAS (Distribución Cruzada y Realista de Sedes)
--
-- DUNE: PARTE DOS (Película 1) -> Presente en las 3 SEDES (Centro, Palermo, Belgrano)
-- OPPENHEIMER (Película 2)     -> Presente en 2 SEDES (Centro, Palermo)
-- SPIDER-MAN (Película 3)      -> Presente en 2 SEDES (Palermo, Belgrano)
-- INTENSAMENTE 2 (Película 4)  -> Presente en 2 SEDES (Centro, Belgrano)
-- ALIEN: ROMULUS (Película 5)  -> Presente en 1 SEDE (Centro 4D exclusivo)
-- BARBIE (Película 6)          -> Presente en 1 SEDE (Palermo)
-- SUEÑOS DE LIBERTAD (Pel. 7)  -> Presente en 1 SEDE (Belgrano), sin reseñas
--
-- REGLA DEMO QR: Función 1 en DATE_ADD(NOW(), INTERVAL 15 MINUTE)
-- FUNCIONES HISTÓRICAS: Funciones 14 a 19 finalizadas para habilitar reseñas reales
-- -----------------------------------------------------------------------------
INSERT INTO `funciones` (`id_funcion`, `id_pelicula`, `id_sala`, `inicio`, `fin`, `formato`, `idioma`, `subtitulada`, `precio_entrada`, `estado`) VALUES
-- --- DUNE 2 (3 Sedes) ---
-- Función 1 (Demo QR en vivo): Centro - Sala 1 (4D VIP), inicia en 15 min
(1, 1, 1, DATE_ADD(NOW(), INTERVAL 15 MINUTE), DATE_ADD(NOW(), INTERVAL 15 MINUTE) + INTERVAL 166 MINUTE, '4D', 'Inglés', 1, 6500.00, 'PROGRAMADA'),
-- Función 2: Centro - Sala 2 (2D Estándar sin VIP), mañana a las 21:00 hs
(2, 1, 2, TIMESTAMP(CURDATE() + INTERVAL 1 DAY, '21:00:00'), TIMESTAMP(CURDATE() + INTERVAL 1 DAY, '21:00:00') + INTERVAL 166 MINUTE, '2D', 'Español', 0, 4800.00, 'PROGRAMADA'),
-- Función 3: Palermo - Sala 3 (3D VIP), en 2 días a las 19:00 hs
(3, 1, 3, TIMESTAMP(CURDATE() + INTERVAL 2 DAY, '19:00:00'), TIMESTAMP(CURDATE() + INTERVAL 2 DAY, '19:00:00') + INTERVAL 166 MINUTE, '3D', 'Inglés', 1, 5800.00, 'PROGRAMADA'),
-- Función 4: Belgrano - Sala 4 (2D Tradicional), en 3 días a las 18:00 hs
(4, 1, 4, TIMESTAMP(CURDATE() + INTERVAL 3 DAY, '18:00:00'), TIMESTAMP(CURDATE() + INTERVAL 3 DAY, '18:00:00') + INTERVAL 166 MINUTE, '2D', 'Español', 0, 4500.00, 'PROGRAMADA'),

-- --- OPPENHEIMER (2 Sedes) ---
-- Función 5: Centro - Sala 2 (2D), en 2 días a las 20:00 hs
(5, 2, 2, TIMESTAMP(CURDATE() + INTERVAL 2 DAY, '20:00:00'), TIMESTAMP(CURDATE() + INTERVAL 2 DAY, '20:00:00') + INTERVAL 180 MINUTE, '2D', 'Inglés', 1, 4800.00, 'PROGRAMADA'),
-- Función 6: Palermo - Sala 3 (2D VIP), en 4 días a las 21:00 hs
(6, 2, 3, TIMESTAMP(CURDATE() + INTERVAL 4 DAY, '21:00:00'), TIMESTAMP(CURDATE() + INTERVAL 4 DAY, '21:00:00') + INTERVAL 180 MINUTE, '2D', 'Inglés', 1, 5200.00, 'PROGRAMADA'),

-- --- SPIDER-MAN: ACROSS THE SPIDER-VERSE (2 Sedes) ---
-- Función 7: Palermo - Sala 3 (3D VIP), mañana a las 16:00 hs
(7, 3, 3, TIMESTAMP(CURDATE() + INTERVAL 1 DAY, '16:00:00'), TIMESTAMP(CURDATE() + INTERVAL 1 DAY, '16:00:00') + INTERVAL 140 MINUTE, '3D', 'Español', 0, 5500.00, 'PROGRAMADA'),
-- Función 8: Belgrano - Sala 4 (2D Tradicional), en 3 días a las 17:00 hs
(8, 3, 4, TIMESTAMP(CURDATE() + INTERVAL 3 DAY, '17:00:00'), TIMESTAMP(CURDATE() + INTERVAL 3 DAY, '17:00:00') + INTERVAL 140 MINUTE, '2D', 'Español', 0, 4500.00, 'PROGRAMADA'),

-- --- INTENSAMENTE 2 (2 Sedes) ---
-- Función 9: Centro - Sala 1 (4D VIP), mañana a las 17:00 hs
(9, 4, 1, TIMESTAMP(CURDATE() + INTERVAL 1 DAY, '17:00:00'), TIMESTAMP(CURDATE() + INTERVAL 1 DAY, '17:00:00') + INTERVAL 96 MINUTE, '4D', 'Español', 0, 6200.00, 'PROGRAMADA'),
-- Función 10: Belgrano - Sala 4 (2D Tradicional), en 4 días a las 15:00 hs
(10, 4, 4, TIMESTAMP(CURDATE() + INTERVAL 4 DAY, '15:00:00'), TIMESTAMP(CURDATE() + INTERVAL 4 DAY, '15:00:00') + INTERVAL 96 MINUTE, '2D', 'Español', 0, 4200.00, 'PROGRAMADA'),

-- --- ALIEN: ROMULUS (1 Sede Exclusiva) ---
-- Función 11: Centro - Sala 1 (4D VIP), en 5 días a las 22:30 hs
(11, 5, 1, TIMESTAMP(CURDATE() + INTERVAL 5 DAY, '22:30:00'), TIMESTAMP(CURDATE() + INTERVAL 5 DAY, '22:30:00') + INTERVAL 119 MINUTE, '4D', 'Inglés', 1, 6800.00, 'PROGRAMADA'),

-- --- BARBIE (1 Sede) ---
-- Función 12: Palermo - Sala 3 (2D VIP), en 6 días a las 19:00 hs
(12, 6, 3, TIMESTAMP(CURDATE() + INTERVAL 6 DAY, '19:00:00'), TIMESTAMP(CURDATE() + INTERVAL 6 DAY, '19:00:00') + INTERVAL 114 MINUTE, '2D', 'Español', 0, 4800.00, 'PROGRAMADA'),

-- --- SUEÑOS DE LIBERTAD (1 Sede, SIN RESEÑAS) ---
-- Función 13: Belgrano - Sala 4 (2D Tradicional), en 7 días a las 20:00 hs
(13, 7, 4, TIMESTAMP(CURDATE() + INTERVAL 7 DAY, '20:00:00'), TIMESTAMP(CURDATE() + INTERVAL 7 DAY, '20:00:00') + INTERVAL 142 MINUTE, '2D', 'Inglés', 1, 4500.00, 'PROGRAMADA'),

-- --- FUNCIONES HISTÓRICAS FINALIZADAS (Para respaldo de asistencia en reseñas) ---
-- Función 14: Dune 2 (hace 3 días en Centro)
(14, 1, 1, TIMESTAMP(CURDATE() - INTERVAL 3 DAY, '20:00:00'), TIMESTAMP(CURDATE() - INTERVAL 3 DAY, '20:00:00') + INTERVAL 166 MINUTE, '2D', 'Inglés', 1, 4500.00, 'FINALIZADA'),
-- Función 15: Oppenheimer (hace 4 días en Centro)
(15, 2, 2, TIMESTAMP(CURDATE() - INTERVAL 4 DAY, '21:00:00'), TIMESTAMP(CURDATE() - INTERVAL 4 DAY, '21:00:00') + INTERVAL 180 MINUTE, '2D', 'Inglés', 1, 4800.00, 'FINALIZADA'),
-- Función 16: Spider-Man (hace 5 días en Palermo)
(16, 3, 3, TIMESTAMP(CURDATE() - INTERVAL 5 DAY, '18:00:00'), TIMESTAMP(CURDATE() - INTERVAL 5 DAY, '18:00:00') + INTERVAL 140 MINUTE, '3D', 'Español', 0, 5200.00, 'FINALIZADA'),
-- Función 17: IntensaMente 2 (hace 4 días en Belgrano)
(17, 4, 4, TIMESTAMP(CURDATE() - INTERVAL 4 DAY, '16:00:00'), TIMESTAMP(CURDATE() - INTERVAL 4 DAY, '16:00:00') + INTERVAL 96 MINUTE, '2D', 'Español', 0, 4200.00, 'FINALIZADA'),
-- Función 18: Alien: Romulus (hace 6 días en Centro)
(18, 5, 1, TIMESTAMP(CURDATE() - INTERVAL 6 DAY, '22:00:00'), TIMESTAMP(CURDATE() - INTERVAL 6 DAY, '22:00:00') + INTERVAL 119 MINUTE, '4D', 'Inglés', 1, 6500.00, 'FINALIZADA'),
-- Función 19: Barbie (hace 7 días en Palermo)
(19, 6, 3, TIMESTAMP(CURDATE() - INTERVAL 7 DAY, '19:00:00'), TIMESTAMP(CURDATE() - INTERVAL 7 DAY, '19:00:00') + INTERVAL 114 MINUTE, '2D', 'Español', 0, 4800.00, 'FINALIZADA')
ON DUPLICATE KEY UPDATE `inicio` = VALUES(`inicio`), `fin` = VALUES(`fin`), `precio_entrada` = VALUES(`precio_entrada`), `estado` = VALUES(`estado`);

-- -----------------------------------------------------------------------------
-- 10. COMPRAS PRECARGADAS
-- Compra 1: Juan Pérez (id 2) para Función 1 (+15 min). Lista para validación QR en vivo.
-- Token QR conocido: DEMO-VALIDAR-QR-EXITO-2026
--
-- Compras 2 a 15: Compras pasadas con QR validado en puerta (asistencia confirmada),
-- realizadas por distintos clientes para respaldar reseñas positivas, intermedias y críticas.
-- -----------------------------------------------------------------------------
INSERT INTO `compras` (`id_compra`, `id_usuario`, `id_funcion`, `codigo_reserva`, `email_comprobante`, `creada_en`, `estado`, `medio_pago`, `subtotal_entradas`, `subtotal_servicios`, `cargo_servicio`, `total`, `qr_token`, `qr_validado_en`, `cancelada_en`) VALUES
-- Compra 1: Juan Pérez en Función 1 (Demo QR en vivo)
(1, 2, 1, 'RES-DEMO-001', 'cliente@cineparadiso.com', DATE_SUB(NOW(), INTERVAL 1 HOUR), 'PAGADA', 'TARJETA_SIMULADA', 13000.00, 9500.00, 0.00, 22500.00, 'DEMO-VALIDAR-QR-EXITO-2026', NULL, NULL),

-- Compras para Dune 2 (Función 14): María Gómez, Lucas Rossi y Carlos Méndez
(2, 3, 14, 'RES-HIST-002', 'maria@cineparadiso.com', TIMESTAMP(CURDATE() - INTERVAL 4 DAY, '15:30:00'), 'PAGADA', 'TARJETA_SIMULADA', 4500.00, 3500.00, 0.00, 8000.00, 'TOKEN-HIST-002', TIMESTAMP(CURDATE() - INTERVAL 3 DAY, '19:45:00'), NULL),
(3, 4, 14, 'RES-HIST-003', 'lucas@cineparadiso.com', TIMESTAMP(CURDATE() - INTERVAL 4 DAY, '16:00:00'), 'PAGADA', 'TARJETA_SIMULADA', 4500.00, 0.00, 0.00, 4500.00, 'TOKEN-HIST-003', TIMESTAMP(CURDATE() - INTERVAL 3 DAY, '19:50:00'), NULL),
(4, 6, 14, 'RES-HIST-004', 'carlos@cineparadiso.com', TIMESTAMP(CURDATE() - INTERVAL 4 DAY, '17:00:00'), 'PAGADA', 'TARJETA_SIMULADA', 4500.00, 6200.00, 0.00, 10700.00, 'TOKEN-HIST-004', TIMESTAMP(CURDATE() - INTERVAL 3 DAY, '19:55:00'), NULL),

-- Compras para Oppenheimer (Función 15): Sofía Benítez, Martín Díaz y Valentina López
(5, 5, 15, 'RES-HIST-005', 'sofia@cineparadiso.com', TIMESTAMP(CURDATE() - INTERVAL 5 DAY, '14:20:00'), 'PAGADA', 'TARJETA_SIMULADA', 4800.00, 6200.00, 0.00, 11000.00, 'TOKEN-HIST-005', TIMESTAMP(CURDATE() - INTERVAL 4 DAY, '20:40:00'), NULL),
(6, 8, 15, 'RES-HIST-006', 'martin@cineparadiso.com', TIMESTAMP(CURDATE() - INTERVAL 5 DAY, '15:00:00'), 'PAGADA', 'TARJETA_SIMULADA', 4800.00, 0.00, 0.00, 4800.00, 'TOKEN-HIST-006', TIMESTAMP(CURDATE() - INTERVAL 4 DAY, '20:45:00'), NULL),
(7, 7, 15, 'RES-HIST-007', 'valentina@cineparadiso.com', TIMESTAMP(CURDATE() - INTERVAL 5 DAY, '15:30:00'), 'PAGADA', 'TARJETA_SIMULADA', 4800.00, 2400.00, 0.00, 7200.00, 'TOKEN-HIST-007', TIMESTAMP(CURDATE() - INTERVAL 4 DAY, '20:50:00'), NULL),

-- Compras para Spider-Man (Función 16): Lucas Rossi y María Gómez
(8, 4, 16, 'RES-HIST-008', 'lucas@cineparadiso.com', TIMESTAMP(CURDATE() - INTERVAL 6 DAY, '12:00:00'), 'PAGADA', 'TARJETA_SIMULADA', 5200.00, 5800.00, 0.00, 11000.00, 'TOKEN-HIST-008', TIMESTAMP(CURDATE() - INTERVAL 5 DAY, '17:40:00'), NULL),
(9, 3, 16, 'RES-HIST-009', 'maria@cineparadiso.com', TIMESTAMP(CURDATE() - INTERVAL 6 DAY, '13:00:00'), 'PAGADA', 'TARJETA_SIMULADA', 5200.00, 0.00, 0.00, 5200.00, 'TOKEN-HIST-009', TIMESTAMP(CURDATE() - INTERVAL 5 DAY, '17:45:00'), NULL),

-- Compras para IntensaMente 2 (Función 17): Valentina López y Sofía Benítez
(10, 7, 17, 'RES-HIST-010', 'valentina@cineparadiso.com', TIMESTAMP(CURDATE() - INTERVAL 5 DAY, '11:00:00'), 'PAGADA', 'TARJETA_SIMULADA', 4200.00, 4500.00, 0.00, 8700.00, 'TOKEN-HIST-010', TIMESTAMP(CURDATE() - INTERVAL 4 DAY, '15:45:00'), NULL),
(11, 5, 17, 'RES-HIST-011', 'sofia@cineparadiso.com', TIMESTAMP(CURDATE() - INTERVAL 5 DAY, '11:30:00'), 'PAGADA', 'TARJETA_SIMULADA', 4200.00, 0.00, 0.00, 4200.00, 'TOKEN-HIST-011', TIMESTAMP(CURDATE() - INTERVAL 4 DAY, '15:50:00'), NULL),

-- Compras para Alien: Romulus (Función 18): Carlos Méndez y Martín Díaz
(12, 6, 18, 'RES-HIST-012', 'carlos@cineparadiso.com', TIMESTAMP(CURDATE() - INTERVAL 7 DAY, '19:00:00'), 'PAGADA', 'TARJETA_SIMULADA', 6500.00, 5200.00, 0.00, 11700.00, 'TOKEN-HIST-012', TIMESTAMP(CURDATE() - INTERVAL 6 DAY, '21:40:00'), NULL),
(13, 8, 18, 'RES-HIST-013', 'martin@cineparadiso.com', TIMESTAMP(CURDATE() - INTERVAL 7 DAY, '19:30:00'), 'PAGADA', 'TARJETA_SIMULADA', 6500.00, 0.00, 0.00, 6500.00, 'TOKEN-HIST-013', TIMESTAMP(CURDATE() - INTERVAL 6 DAY, '21:45:00'), NULL),

-- Compras para Barbie (Función 19): María Gómez y Lucas Rossi
(14, 3, 19, 'RES-HIST-014', 'maria@cineparadiso.com', TIMESTAMP(CURDATE() - INTERVAL 8 DAY, '16:00:00'), 'PAGADA', 'TARJETA_SIMULADA', 4800.00, 4900.00, 0.00, 9700.00, 'TOKEN-HIST-014', TIMESTAMP(CURDATE() - INTERVAL 7 DAY, '18:40:00'), NULL),
(15, 4, 19, 'RES-HIST-015', 'lucas@cineparadiso.com', TIMESTAMP(CURDATE() - INTERVAL 8 DAY, '16:30:00'), 'PAGADA', 'TARJETA_SIMULADA', 4800.00, 0.00, 0.00, 4800.00, 'TOKEN-HIST-015', TIMESTAMP(CURDATE() - INTERVAL 7 DAY, '18:45:00'), NULL)
ON DUPLICATE KEY UPDATE `estado` = VALUES(`estado`), `qr_token` = VALUES(`qr_token`), `qr_validado_en` = VALUES(`qr_validado_en`);

-- -----------------------------------------------------------------------------
-- 11. DETALLE DE SERVICIOS POR COMPRA
-- -----------------------------------------------------------------------------
INSERT INTO `compra_servicios` (`id_compra_servicio`, `id_compra`, `id_servicio`, `cantidad`, `precio_unitario`) VALUES
(1, 1, 1, 1, 9500.00), -- Combo Mega Popcorn para Compra 1
(2, 2, 4, 1, 3500.00), -- Gaseosa Grande para Compra 2
(3, 4, 2, 1, 6200.00), -- Popcorn Balde para Compra 4
(4, 5, 2, 1, 6200.00), -- Popcorn Balde para Compra 5
(5, 7, 5, 1, 2400.00), -- Agua Mineral para Compra 7
(6, 8, 3, 1, 5800.00), -- Nachos Cheddar para Compra 8
(7, 10, 6, 1, 4500.00), -- Vaso 3D para Compra 10
(8, 12, 7, 1, 5200.00), -- Balde Metálico para Compra 12
(9, 14, 8, 1, 4900.00)  -- Promo 2x1 Popcorn para Compra 14
ON DUPLICATE KEY UPDATE `cantidad` = VALUES(`cantidad`);

-- -----------------------------------------------------------------------------
-- 12. ENTRADAS VENDIDAS / OCUPADAS
-- -----------------------------------------------------------------------------
INSERT INTO `entradas` (`id_entrada`, `id_compra`, `id_funcion`, `id_butaca`, `precio_unitario`, `estado`) VALUES
-- Compra 1 ocupa las butacas 25 y 26 (Fila E, VIP D-BOX de Sala 1) en Función 1
(1, 1, 1, 25, 6500.00, 'OCUPADA'),
(2, 1, 1, 26, 6500.00, 'OCUPADA'),

-- Dune 2 (Función 14, Sala 1)
(3, 2, 14, 1, 4500.00, 'OCUPADA'),
(4, 3, 14, 2, 4500.00, 'OCUPADA'),
(5, 4, 14, 3, 4500.00, 'OCUPADA'),

-- Oppenheimer (Función 15, Sala 2)
(6, 5, 15, 43, 4800.00, 'OCUPADA'),
(7, 6, 15, 44, 4800.00, 'OCUPADA'),
(8, 7, 15, 45, 4800.00, 'OCUPADA'),

-- Spider-Man (Función 16, Sala 3)
(9, 8, 16, 67, 5200.00, 'OCUPADA'),
(10, 9, 16, 68, 5200.00, 'OCUPADA'),

-- IntensaMente 2 (Función 17, Sala 4)
(11, 10, 17, 97, 4200.00, 'OCUPADA'),
(12, 11, 17, 98, 4200.00, 'OCUPADA'),

-- Alien: Romulus (Función 18, Sala 1)
(13, 12, 18, 7, 6500.00, 'OCUPADA'),
(14, 13, 18, 8, 6500.00, 'OCUPADA'),

-- Barbie (Función 19, Sala 3)
(15, 14, 19, 73, 4800.00, 'OCUPADA'),
(16, 15, 19, 74, 4800.00, 'OCUPADA')
ON DUPLICATE KEY UPDATE `estado` = VALUES(`estado`), `precio_unitario` = VALUES(`precio_unitario`);

-- -----------------------------------------------------------------------------
-- 13. RESEÑAS PRECARGADAS (Reseñas Variadas: Excelentes, Regulares y Críticas)
-- Películas 1 a 6 cuentan con reseñas.
-- Película 7 (Sueños de Libertad) queda con 0 RESEÑAS para la demo en vivo.
-- -----------------------------------------------------------------------------
INSERT INTO `resenas` (`id_resena`, `id_usuario`, `id_pelicula`, `id_compra`, `puntuacion`, `comentario`, `creada_en`) VALUES
-- --- DUNE: PARTE DOS (id_pelicula: 1) ---
(1, 3, 1, 2, 5, '¡Una obra maestra visual y sonora! Los efectos especiales y la música te sumergen por completo en Arrakis.', TIMESTAMP(CURDATE() - INTERVAL 2 DAY, '11:15:00')),
(2, 4, 1, 3, 4, 'Excelente secuela, con un ritmo impecable. La butaca VIP en la sala 4D realmente marca la diferencia.', TIMESTAMP(CURDATE() - INTERVAL 2 DAY, '16:40:00')),
(3, 6, 1, 4, 2, 'Visualmente espectacular pero se me hizo larguísima y bastante pesada en el segundo acto. Esperaba más acción.', TIMESTAMP(CURDATE() - INTERVAL 2 DAY, '18:20:00')),

-- --- OPPENHEIMER (id_pelicula: 2) ---
(4, 5, 2, 5, 5, 'Una actuación magistral de Cillian Murphy y una tensión constante. Totalmente recomendable verla en pantalla grande.', TIMESTAMP(CURDATE() - INTERVAL 3 DAY, '10:00:00')),
(5, 7, 2, 7, 4, 'Gran recreación histórica. Mucho diálogo técnico que requiere concentración, pero el montaje final es brillante.', TIMESTAMP(CURDATE() - INTERVAL 3 DAY, '12:30:00')),
(6, 8, 2, 6, 2, 'El sonido de las explosiones es ensordecedor y tapa los diálogos. Se vuelve monótona con tantas idas y vueltas temporales.', TIMESTAMP(CURDATE() - INTERVAL 3 DAY, '14:10:00')),

-- --- SPIDER-MAN: ACROSS THE SPIDER-VERSE (id_pelicula: 3) ---
(7, 4, 3, 8, 5, 'La mejor película de animación del año. El estilo visual y la banda sonora son una locura absoluta.', TIMESTAMP(CURDATE() - INTERVAL 4 DAY, '14:20:00')),
(8, 3, 3, 9, 1, 'Demasiado estímulo visual caótico, salí con dolor de cabeza. Además te deja con un corte abrupto sin final real.', TIMESTAMP(CURDATE() - INTERVAL 4 DAY, '17:50:00')),

-- --- INTENSAMENTE 2 (id_pelicula: 4) ---
(9, 7, 4, 10, 4, 'Muy linda representación de la ansiedad en la adolescencia. Ideal para ir en familia.', TIMESTAMP(CURDATE() - INTERVAL 3 DAY, '18:00:00')),
(10, 5, 4, 11, 2, 'Bastante inferior a la primera entrega. Se siente repetitiva y los chistes son predecibles.', TIMESTAMP(CURDATE() - INTERVAL 3 DAY, '19:15:00')),

-- --- ALIEN: ROMULUS (id_pelicula: 5) ---
(11, 6, 5, 12, 5, 'Volvió el terror espacial con la tensión de las primeras entregas. Los efectos prácticos son increíbles.', TIMESTAMP(CURDATE() - INTERVAL 5 DAY, '11:00:00')),
(12, 8, 5, 13, 2, 'Demasiado fanservice y gore sin sentido. Copia escenas enteras de las películas clásicas sin aportar nada nuevo.', TIMESTAMP(CURDATE() - INTERVAL 5 DAY, '15:30:00')),

-- --- BARBIE (id_pelicula: 6) ---
(13, 3, 6, 14, 4, 'Divertida, colorida y con números musicales geniales. Ryan Gosling se roba cada escena en la que aparece.', TIMESTAMP(CURDATE() - INTERVAL 6 DAY, '12:00:00')),
(14, 4, 6, 15, 1, 'No me gustó para nada. El guion se vuelve muy forzado a mitad de película y el humor no me funcionó.', TIMESTAMP(CURDATE() - INTERVAL 6 DAY, '16:45:00'))
ON DUPLICATE KEY UPDATE `puntuacion` = VALUES(`puntuacion`), `comentario` = VALUES(`comentario`);
