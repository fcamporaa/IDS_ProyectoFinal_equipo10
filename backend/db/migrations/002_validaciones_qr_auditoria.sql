-- Habilita auditar intentos con QR inexistente, sin inventar una compra.
-- Ejecutar una sola vez tras cargar backend/db/init_db.sql.
-- Es compatible con la migración US-09 (001_us09_qr_correo.sql).
ALTER TABLE validaciones_qr
    MODIFY COLUMN id_compra INT(11) NULL;
