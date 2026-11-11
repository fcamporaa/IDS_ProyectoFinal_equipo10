-- =============================================================================
-- Datos Semilla (Seeds) para Cine Paradiso
-- Cátedra Lanzillotta - IDS 2026
-- =============================================================================

USE `proyecto_integrador`;

-- 1. Usuarios de prueba (contraseñas hasheadas con bcrypt)
-- Admin:   admin@cineparadiso.com   | Password: Admin1234!
-- Cliente: cliente@cineparadiso.com | Password: Cliente1234!
INSERT INTO `usuarios` (`id_usuario`, `nombre`, `email`, `numero_socio`, `contrasena_hash`, `rol`, `activo`) VALUES
(1, 'Administrador Cine', 'admin@cineparadiso.com', 'SOC-0001', '$2b$12$3sW5bQeAQI0lbQ7XD53HYOT053SWrnV118X25j2Xh7Zcin0Vo/FOW', 'ADMINISTRADOR', 1),
(2, 'Juan Pérez', 'cliente@cineparadiso.com', 'SOC-1002', '$2b$12$TQQG6hcUWZH399ePetm4suxPing6QKpBDiKJQI93ywVZAg5c3laji', 'CLIENTE', 1)
ON DUPLICATE KEY UPDATE `email` = VALUES(`email`);

-- 2. Géneros de Películas
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

-- 3. Complejos (Locales)
INSERT INTO `locales` (`id_local`, `nombre`, `direccion`, `activo`) VALUES
(1, 'Cine Paradiso Centro', 'Av. Corrientes 1240, CABA', 1),
(2, 'Cine Paradiso Palermo', 'Av. Santa Fe 3200, CABA', 1)
ON DUPLICATE KEY UPDATE `nombre` = VALUES(`nombre`);

-- 4. Salas
INSERT INTO `salas` (`id_sala`, `id_local`, `numero`, `activa`) VALUES
(1, 1, 1, 1),
(2, 1, 2, 1),
(3, 2, 1, 1)
ON DUPLICATE KEY UPDATE `numero` = VALUES(`numero`);

-- 5. Butacas para Salas 1 y 2 (Filas A, B, C; Butacas 1 a 6)
INSERT INTO `butacas` (`id_butaca`, `id_sala`, `fila`, `numero`, `activa`) VALUES
-- Sala 1
(1, 1, 'A', 1, 1), (2, 1, 'A', 2, 1), (3, 1, 'A', 3, 1), (4, 1, 'A', 4, 1), (5, 1, 'A', 5, 1), (6, 1, 'A', 6, 1),
(7, 1, 'B', 1, 1), (8, 1, 'B', 2, 1), (9, 1, 'B', 3, 1), (10, 1, 'B', 4, 1), (11, 1, 'B', 5, 1), (12, 1, 'B', 6, 1),
(13, 1, 'C', 1, 1), (14, 1, 'C', 2, 1), (15, 1, 'C', 3, 1), (16, 1, 'C', 4, 1), (17, 1, 'C', 5, 1), (18, 1, 'C', 6, 1),
-- Sala 2
(19, 2, 'A', 1, 1), (20, 2, 'A', 2, 1), (21, 2, 'A', 3, 1), (22, 2, 'A', 4, 1),
(23, 2, 'B', 1, 1), (24, 2, 'B', 2, 1), (25, 2, 'B', 3, 1), (26, 2, 'B', 4, 1)
ON DUPLICATE KEY UPDATE `activa` = VALUES(`activa`);

-- 6. Películas
INSERT INTO `peliculas` (`id_pelicula`, `origen_api`, `id_api`, `titulo`, `sinopsis`, `poster_url`, `trailer_url`, `duracion_min`, `clasificacion`, `anio_estreno`, `activa`) VALUES
(1, 'OMDB', 'tt15239678', 'Dune: Parte Dos', 'Paul Atreides se une a Chani y a los Fremen mientras busca venganza contra los conspiradores que destruyeron a su familia.', 'https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg', 'https://www.youtube.com/embed/Way9Dexny3w', 166, '+13', 2024, 1),
(2, 'OMDB', 'tt15398776', 'Oppenheimer', 'La historia del físico estadounidense J. Robert Oppenheimer, su papel en el Proyecto Manhattan y el desarrollo de la bomba atómica.', 'https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg', 'https://www.youtube.com/embed/uYPbbksJxIg', 180, '+16', 2023, 1),
(3, 'OMDB', 'tt9362722', 'Spider-Man: Across the Spider-Verse', 'Miles Morales es catapultado a través del Multiverso, donde se encuentra con un equipo de Spider-People encargados de proteger su existencia.', 'https://image.tmdb.org/t/p/w500/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg', 'https://www.youtube.com/embed/cqGjhVJWtEg', 140, 'ATP', 2023, 1)
ON DUPLICATE KEY UPDATE `titulo` = VALUES(`titulo`);

-- 7. Asociación Película - Géneros
INSERT INTO `pelicula_generos` (`id_pelicula`, `id_genero`) VALUES
(1, 2), -- Dune: Ciencia Ficción
(1, 3), -- Dune: Aventura
(2, 4), -- Oppenheimer: Drama
(3, 6), -- Spider-Man: Animación
(3, 1)  -- Spider-Man: Acción
ON DUPLICATE KEY UPDATE `id_pelicula` = VALUES(`id_pelicula`);

-- 8. Funciones (Horarios futuros usando DATE_ADD para vigencia prolongada)
INSERT INTO `funciones` (`id_funcion`, `id_pelicula`, `id_sala`, `inicio`, `fin`, `formato`, `idioma`, `subtitulada`, `precio_entrada`, `estado`) VALUES
(1, 1, 1, DATE_ADD(NOW(), INTERVAL 7 DAY), DATE_ADD(NOW(), INTERVAL 7 DAY) + INTERVAL 166 MINUTE, '4D', 'Inglés', 1, 6500.00, 'PROGRAMADA'),
(2, 1, 1, DATE_ADD(NOW(), INTERVAL 14 DAY), DATE_ADD(NOW(), INTERVAL 14 DAY) + INTERVAL 166 MINUTE, '4D', 'Inglés', 1, 6500.00, 'PROGRAMADA'),
(3, 2, 2, DATE_ADD(NOW(), INTERVAL 10 DAY), DATE_ADD(NOW(), INTERVAL 10 DAY) + INTERVAL 180 MINUTE, '2D', 'Inglés', 1, 4800.00, 'PROGRAMADA'),
(4, 3, 3, DATE_ADD(NOW(), INTERVAL 15 DAY), DATE_ADD(NOW(), INTERVAL 15 DAY) + INTERVAL 140 MINUTE, '3D', 'Español', 0, 5200.00, 'PROGRAMADA')
ON DUPLICATE KEY UPDATE `inicio` = VALUES(`inicio`), `fin` = VALUES(`fin`), `estado` = VALUES(`estado`);

-- 9. Entradas disponibles para las funciones
INSERT INTO `entradas` (`id_entrada`, `id_funcion`, `id_butaca`, `precio_unitario`, `estado`) VALUES
(1, 1, 1, 6500.00, 'DISPONIBLE'),
(2, 1, 2, 6500.00, 'DISPONIBLE'),
(3, 1, 3, 6500.00, 'DISPONIBLE'),
(4, 1, 4, 6500.00, 'DISPONIBLE'),
(5, 1, 5, 6500.00, 'DISPONIBLE'),
(6, 1, 6, 6500.00, 'DISPONIBLE'),
(7, 2, 1, 6500.00, 'DISPONIBLE'),
(8, 2, 2, 6500.00, 'DISPONIBLE'),
(9, 3, 19, 4800.00, 'DISPONIBLE'),
(10, 3, 20, 4800.00, 'DISPONIBLE')
ON DUPLICATE KEY UPDATE `estado` = VALUES(`estado`);

-- 10. Servicios Adicionales (Candy Bar)
INSERT INTO `servicios` (`id_servicio`, `nombre`, `tipo`, `precio`, `activo`) VALUES
(1, 'Combo Popcorn Grande + Gaseosa', 'COMIDA', 8500.00, 1),
(2, 'Gaseosa Mediana 500ml', 'BEBIDA', 3200.00, 1),
(3, 'Nachos con Queso Cheddar', 'COMIDA', 6400.00, 1),
(4, 'Agua Mineral 500ml', 'BEBIDA', 2500.00, 1)
ON DUPLICATE KEY UPDATE `precio` = VALUES(`precio`);

