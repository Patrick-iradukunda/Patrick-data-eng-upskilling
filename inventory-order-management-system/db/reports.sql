USE inventory_system;

SELECT
    o.order_id,
    o.order_date,
    o.total_amount,
    c.customer_id,
    c.name AS customer_name,
    COUNT(od.order_detail_id) AS total_items
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN order_details od ON o.order_id = od.order_id
GROUP BY o.order_id, o.order_date, o.total_amount, c.customer_id, c.name
ORDER BY o.order_date DESC;

SELECT product_id, name, stock_quantity, reorder_level
FROM products
WHERE stock_quantity <= reorder_level
ORDER BY stock_quantity ASC;

SELECT
    c.customer_id,
    c.name,
    SUM(o.total_amount) AS total_spent,
    CASE
        WHEN SUM(o.total_amount) >= 1000 THEN 'Gold'
        WHEN SUM(o.total_amount) >= 500 THEN 'Silver'
        ELSE 'Bronze'
    END AS tier
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC;

SELECT
    o.order_id,
    SUM(od.quantity) AS total_quantity,
    CASE
        WHEN SUM(od.quantity) >= 20 THEN 0.20
        WHEN SUM(od.quantity) >= 10 THEN 0.10
        ELSE 0.00
    END AS bulk_discount_rate
FROM orders o
JOIN order_details od ON o.order_id = od.order_id
GROUP BY o.order_id;
