CREATE DATABASE IF NOT EXISTS articulos_policiales;
USE articulos_policiales;

-- ======================
-- TABLA USUARIOS
-- ======================
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

<<<<<<< HEAD
CREATE TABLE IF NOT EXISTS categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cantidad INT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    id_categoria INT NOT NULL,
    id_usuario INT NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);
=======
-- ======================
-- TABLA CATEGORIAS
-- ======================
CREATE TABLE IF NOT EXISTS categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(100) NOT NULL
);

-- ======================
-- TABLA PROVEEDORES
-- ======================
CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- ======================
-- TABLA PRODUCTOS MYSQL (IMPORTANTE)
-- ======================
CREATE TABLE IF NOT EXISTS productos_mysql (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    id_categoria INT,
    id_proveedor INT,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
);

-- ======================
-- DATOS INICIALES
-- ======================
INSERT INTO categorias (nombre_categoria) VALUES ('Seguridad');
INSERT INTO proveedores (nombre) VALUES ('Proveedor Demo');
>>>>>>> 0e5214774571f1b78569c79eb4fd6b055c3e0d2e
