USE inventory_system;

CREATE VIEW order_summary AS
SELECT
    o.order_id,
    c.customer_id,
    c.name AS customer_name,
    o.order_date,
    o.total_amount,
    COUNT(od.order_detail_id) AS items_count
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN order_details od ON o.order_id = od.order_id
GROUP BY o.order_id, c.customer_id, c.name, o.order_date, o.total_amount;

CREATE VIEW stock_status AS
SELECT
    product_id,
    name AS product_name,
    USE inventory_system;

    CREATE VIEW order_summary AS
    SELECT
        o.order_id,
        c.customer_id,
        c.name AS customer_name,
        o.order_date,
        o.total_amount,
        COUNT(od.order_detail_id) AS items_count
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    LEFT JOIN order_details od ON o.order_id = od.order_id
    GROUP BY o.order_id, c.customer_id, c.name, o.order_date, o.total_amount;

    CREATE VIEW stock_status AS
    SELECT
        product_id,
        name AS product_name,
        category,
        stock_quantity,
        reorder_level,
        CASE WHEN stock_quantity <= reorder_level THEN 1 ELSE 0 END AS needs_reorder
    FROM products;
