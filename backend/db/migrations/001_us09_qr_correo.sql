-- Ejecución UNA sola vez sobre una base existente, con backup previo.
-- Antes de migrar, verificar que no haya duplicados de entradas activas
-- (id_funcion + id_butaca), códigos de reserva o tokens QR.

ALTER TABLE compras
  ADD COLUMN email_estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
  ADD COLUMN email_intentos INT NOT NULL DEFAULT 0,
  ADD COLUMN email_enviado_en DATETIME DEFAULT NULL,
  ADD UNIQUE KEY uq_codigo_reserva (codigo_reserva),
  ADD UNIQUE KEY uq_qr_token (qr_token);

-- La columna del dump era ordinaria; reemplazarla por una columna calculada.
-- Así al cancelar una entrada su butaca queda libre automáticamente.
ALTER TABLE entradas DROP COLUMN id_butaca_ocupada;
ALTER TABLE entradas
  ADD COLUMN id_butaca_ocupada INT GENERATED ALWAYS AS (
    CASE WHEN estado IN ('RESERVADA', 'OCUPADA') THEN id_butaca ELSE NULL END
  ) STORED,
  ADD UNIQUE KEY uq_entrada_funcion_activa (id_funcion, id_butaca_ocupada);
