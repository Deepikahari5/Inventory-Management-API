CREATE DATABASE IF NOT EXISTS inventory_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE inventory_db;

CREATE TABLE IF NOT EXISTS categories (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  description VARCHAR(255) NULL,
  CONSTRAINT pk_categories PRIMARY KEY (id),
  CONSTRAINT uq_categories_name UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS suppliers (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(150) NOT NULL,
  email VARCHAR(150) NULL,
  CONSTRAINT pk_suppliers PRIMARY KEY (id),
  CONSTRAINT uq_suppliers_email UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS products (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(150) NOT NULL,
  description TEXT NULL,
  price NUMERIC(10,2) NOT NULL,
  quantity INT NOT NULL DEFAULT 0,
  category_id INT NOT NULL,
  supplier_id INT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk_products PRIMARY KEY (id),
  CONSTRAINT ck_products_price_non_negative CHECK (price >= 0),
  CONSTRAINT ck_products_quantity_non_negative CHECK (quantity >= 0),
  CONSTRAINT fk_products_category_id_categories FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE RESTRICT,
  CONSTRAINT fk_products_supplier_id_suppliers FOREIGN KEY (supplier_id) REFERENCES suppliers (id) ON DELETE SET NULL
);

INSERT INTO categories (name, description) VALUES
  ('Electronics', 'Electronic devices and accessories'),
  ('Stationery', 'Office and school supplies'),
  ('Furniture', 'Office furniture');

INSERT INTO suppliers (name, email) VALUES
  ('TechSource Ltd', 'sales@techsource.example'),
  ('PaperWorks Co', 'hello@paperworks.example');

INSERT INTO products (name, description, price, quantity, category_id, supplier_id) VALUES
  ('Wireless Mouse', 'Optical wireless mouse', 799.00, 25, 1, 1),
  ('USB Keyboard', 'Full-size USB keyboard', 1299.00, 8, 1, 1),
  ('A4 Notebook', '200 pages ruled', 120.00, 150, 2, 2),
  ('Office Chair', 'Ergonomic mesh chair', 7499.00, 4, 3, NULL);
