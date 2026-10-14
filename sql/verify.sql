USE inventory_db;

SHOW TABLES;
SELECT * FROM alembic_version;

DESCRIBE products;
DESCRIBE suppliers;
SHOW CREATE TABLE products\G
SHOW CREATE TABLE suppliers\G

SELECT 'categories' AS tbl, COUNT(*) AS total FROM categories
UNION ALL SELECT 'suppliers', COUNT(*) FROM suppliers
UNION ALL SELECT 'products', COUNT(*) FROM products;

SELECT id, name, sku, quantity, reorder_level, created_at, updated_at FROM products;
SELECT id, name, email, phone, address, is_active FROM suppliers;

INSERT INTO products (name, sku, price, category_id)
VALUES ('Default Check Item', 'DEFAULT-CHECK-1', 10.00, 1);
SELECT id, sku, reorder_level FROM products WHERE sku = 'DEFAULT-CHECK-1';

INSERT INTO suppliers (name) VALUES ('Default Check Supplier');
SELECT id, name, phone, address, is_active FROM suppliers WHERE name = 'Default Check Supplier';

INSERT INTO products (name, sku, price, category_id)
VALUES ('Duplicate SKU Item', 'DEFAULT-CHECK-1', 10.00, 1);

UPDATE products SET quantity = quantity + 1 WHERE sku = 'DEFAULT-CHECK-1';
SELECT sku, created_at, updated_at FROM products WHERE sku = 'DEFAULT-CHECK-1';

DELETE FROM products WHERE sku = 'DEFAULT-CHECK-1';
DELETE FROM suppliers WHERE name = 'Default Check Supplier';
