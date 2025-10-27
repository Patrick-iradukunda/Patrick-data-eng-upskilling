USE inventory_system;

INSERT INTO customers (name, email, phone) VALUES
('John Doe', 'john@example.com', '+250700000001'),
('Jane Smith', 'jane@example.com', '+250700000002');

INSERT INTO products (name, category, price, stock_quantity, reorder_level) VALUES
('Laptop', 'Electronics', 1000.00, 10, 5),
('Mouse', 'Accessories', 50.00, 20, 5),
('Keyboard', 'Accessories', 80.00, 8, 5),
('Monitor', 'Electronics', 200.00, 4, 3);
