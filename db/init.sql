-- Script de inicialización de la base de datos.
-- PostgreSQL lo ejecuta UNA SOLA VEZ, la primera vez que se crea el volumen de datos.

CREATE TABLE IF NOT EXISTS productos (
    id        SERIAL PRIMARY KEY,
    nombre    VARCHAR(100)   NOT NULL,
    precio    NUMERIC(12, 2) NOT NULL CHECK (precio >= 0),
    stock     INTEGER        NOT NULL DEFAULT 0 CHECK (stock >= 0),
    creado_en TIMESTAMP      NOT NULL DEFAULT NOW()
);

INSERT INTO productos (nombre, precio, stock) VALUES
    ('Teclado mecánico',    120000, 15),
    ('Mouse inalámbrico',    65000, 30),
    ('Monitor 24 pulgadas', 650000,  8);
