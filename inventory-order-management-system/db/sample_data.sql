

USE inventory_system;

SET SQL_SAFE_UPDATES = 0;

DELETE FROM inventory_logs;
DELETE FROM order_details;
DELETE FROM orders;
DELETE FROM products;
DELETE FROM customers;

ALTER TABLE customers AUTO_INCREMENT = 1;
ALTER TABLE products AUTO_INCREMENT = 1;
ALTER TABLE orders AUTO_INCREMENT = 1;
ALTER TABLE order_details AUTO_INCREMENT = 1;
ALTER TABLE inventory_logs AUTO_INCREMENT = 1;

INSERT INTO customers (name, email, phone) VALUES
INSERT INTO customers (name, email, phone) VALUES
('John Doe', 'john@example.com', '+250700000001'),
('Jane Smith', 'jane@example.com', '+250700000002'),
('Alice Johnson', 'alice@example.com', '+250700000003'),
('Bob Williams', 'bob@example.com', '+250700000004');

-- Insert products with adequate initial stock levels
INSERT INTO products (name, category, price, stock_quantity, reorder_level) VALUES
('Laptop', 'Electronics', 1000.00, 50, 5),
('Mouse', 'Accessories', 50.00, 100, 5),
('Keyboard', 'Accessories', 80.00, 75, 5),
('Monitor', 'Electronics', 200.00, 30, 3),
('Headphones', 'Accessories', 120.00, 40, 8),
('Webcam', 'Electronics', 150.00, 25, 5);

INSERT INTO inventory_logs (product_id, change_type, quantity_changed, change_date) VALUES
(1, 'Initial Stock', 50, '2025-11-01 08:00:00'),
(2, 'Initial Stock', 100, '2025-11-01 08:00:00'),
(3, 'Initial Stock', 75, '2025-11-01 08:00:00'),
(4, 'Initial Stock', 30, '2025-11-01 08:00:00'),
(5, 'Initial Stock', 40, '2025-11-01 08:00:00'),
(6, 'Initial Stock', 25, '2025-11-01 08:00:00');

INSERT INTO orders (order_id, customer_id, order_date, total_amount) VALUES
(1, 1, '2025-11-15 10:30:00', 2130.00),
(2, 2, '2025-11-18 14:20:00', 370.00),
(3, 1, '2025-11-22 09:15:00', 1200.00),
(4, 3, '2025-11-25 16:45:00', 430.00),
(5, 4, '2025-11-28 11:00:00', 710.00);

INSERT INTO order_details (order_id, product_id, quantity, price) VALUES
(1, 1, 2, 1000.00),
(1, 3, 1, 80.00),
(1, 2, 3, 50.00),
(2, 4, 1, 200.00),
(2, 5, 1, 120.00),
(2, 2, 2, 50.00),
(3, 1, 1, 1000.00),
(3, 2, 4, 50.00),
(4, 3, 2, 80.00),
(4, 6, 1, 150.00),
(4, 5, 1, 120.00),
(5, 4, 1, 200.00),
(5, 5, 3, 120.00),
(5, 6, 1, 150.00);

INSERT INTO inventory_logs (product_id, change_type, quantity_changed, change_date) VALUES
(1, 'Order', -2, '2025-11-15 10:30:00'),
(3, 'Order', -1, '2025-11-15 10:30:00'),
(2, 'Order', -3, '2025-11-15 10:30:00'),
(4, 'Order', -1, '2025-11-18 14:20:00'),
(5, 'Order', -1, '2025-11-18 14:20:00'),
(2, 'Order', -2, '2025-11-18 14:20:00'),
(2, 'Replenishment', 50, '2025-11-20 09:00:00'),
(1, 'Order', -1, '2025-11-22 09:15:00'),
(2, 'Order', -4, '2025-11-22 09:15:00'),
(3, 'Order', -2, '2025-11-25 16:45:00'),
(6, 'Order', -1, '2025-11-25 16:45:00'),
(5, 'Order', -1, '2025-11-25 16:45:00'),
(4, 'Order', -1, '2025-11-28 11:00:00'),
(5, 'Order', -3, '2025-11-28 11:00:00'),
(6, 'Order', -1, '2025-11-28 11:00:00'),
(5, 'Replenishment', 30, '2025-11-29 10:00:00');

UPDATE products SET stock_quantity = 47 WHERE product_id = 1;
UPDATE products SET stock_quantity = 141 WHERE product_id = 2;
UPDATE products SET stock_quantity = 72 WHERE product_id = 3;
UPDATE products SET stock_quantity = 28 WHERE product_id = 4;
UPDATE products SET stock_quantity = 65 WHERE product_id = 5;
UPDATE products SET stock_quantity = 23 WHERE product_id = 6;

SELECT 'Sample data loaded successfully!' AS status;
SELECT 'Sample data loaded successfully!' AS status;
SELECT COUNT(*) AS total_customers FROM customers;
SELECT COUNT(*) AS total_products FROM products;
SELECT COUNT(*) AS total_orders FROM orders;
SELECT COUNT(*) AS total_order_details FROM order_details;
SELECT COUNT(*) AS total_inventory_logs FROM inventory_logs;

SET SQL_SAFE_UPDATES = 1;
