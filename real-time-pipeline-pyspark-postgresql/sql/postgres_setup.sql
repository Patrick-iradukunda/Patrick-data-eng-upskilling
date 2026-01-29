CREATE DATABASE ecommerce_db ;

CREATE TABLE user_events (
    user_id INT,
    product_id INT,
    action VARCHAR(10),
    timestamp TIMESTAMP,
    price NUMERIC,
    category VARCHAR(50)
);
