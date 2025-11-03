

USE inventory_system;

SELECT o.order_id,o.order_date,o.total_amount,c.customer_id,c.name AS customer_name,COUNT(od.order_detail_id) AS total_items
FROM orders o JOIN customers c ON o.customer_id=c.customer_id LEFT JOIN order_details od ON o.order_id=od.order_id
GROUP BY o.order_id,o.order_date,o.total_amount,c.customer_id,c.name ORDER BY o.order_date DESC;

SELECT product_id,name,stock_quantity,reorder_level FROM products WHERE stock_quantity<=reorder_level ORDER BY stock_quantity ASC;

SELECT c.customer_id,c.name,COALESCE(SUM(o.total_amount),0) AS total_spent,
CASE WHEN COALESCE(SUM(o.total_amount),0)>=1000 THEN 'Gold' WHEN COALESCE(SUM(o.total_amount),0)>=500 THEN 'Silver' ELSE 'Bronze' END AS tier
FROM customers c LEFT JOIN orders o ON c.customer_id=o.customer_id GROUP BY c.customer_id,c.name ORDER BY total_spent DESC;

SELECT o.order_id,SUM(od.quantity) AS total_quantity,CASE WHEN SUM(od.quantity)>=20 THEN 0.20 WHEN SUM(od.quantity)>=10 THEN 0.10 ELSE 0.00 END AS bulk_discount_rate
FROM orders o JOIN order_details od ON o.order_id=od.order_id GROUP BY o.order_id;

SELECT 'customers' AS table_name,COUNT(*) FROM customers
UNION ALL SELECT 'products',COUNT(*) FROM products
UNION ALL SELECT 'orders',COUNT(*) FROM orders
UNION ALL SELECT 'order_details',COUNT(*) FROM order_details
UNION ALL SELECT 'inventory_logs',COUNT(*) FROM inventory_logs;

SELECT TABLE_NAME AS view_name FROM information_schema.VIEWS WHERE TABLE_SCHEMA='inventory_system' ORDER BY TABLE_NAME;

SELECT ROUTINE_NAME AS procedure_name FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA='inventory_system' AND ROUTINE_TYPE='PROCEDURE' ORDER BY ROUTINE_NAME;

SELECT event_name,status,interval_value,interval_field FROM information_schema.events WHERE event_schema='inventory_system';

SELECT change_type,COUNT(*) AS log_count,SUM(ABS(quantity_changed)) AS total_quantity_changed FROM inventory_logs GROUP BY change_type;

SELECT TABLE_NAME,CONSTRAINT_NAME,REFERENCED_TABLE_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA='inventory_system' AND REFERENCED_TABLE_NAME IS NOT NULL ORDER BY TABLE_NAME;

SELECT TABLE_NAME,INDEX_NAME,COLUMN_NAME FROM information_schema.STATISTICS WHERE TABLE_SCHEMA='inventory_system' AND INDEX_NAME!='PRIMARY' ORDER BY TABLE_NAME,INDEX_NAME;

WITH customer_spend AS (SELECT c.customer_id,c.name AS customer_name,COALESCE(SUM(o.total_amount),0) AS total_spent FROM customers c LEFT JOIN orders o ON c.customer_id=o.customer_id GROUP BY c.customer_id,c.name)
SELECT customer_id,customer_name,total_spent,RANK() OVER (ORDER BY total_spent DESC) AS spend_rank FROM customer_spend ORDER BY total_spent DESC;

WITH orders_with_running_total AS (SELECT o.order_id,o.customer_id,o.order_date,o.total_amount FROM orders o)
SELECT order_id,customer_id,order_date,total_amount,SUM(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total_by_customer FROM orders_with_running_total ORDER BY customer_id,order_date;
