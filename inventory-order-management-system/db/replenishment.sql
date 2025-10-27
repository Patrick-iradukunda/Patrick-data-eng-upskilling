USE inventory_system;

SET @restock_amount = 50;

DROP TEMPORARY TABLE IF EXISTS tmp_restock;
CREATE TEMPORARY TABLE tmp_restock AS
SELECT product_id, stock_quantity AS prev_stock
FROM products
WHERE stock_quantity <= reorder_level;

SELECT product_id, prev_stock FROM tmp_restock;

UPDATE products p
JOIN tmp_restock t ON p.product_id = t.product_id
SET p.stock_quantity = p.stock_quantity + @restock_amount;

INSERT INTO inventory_logs (product_id, change_type, quantity_changed)
SELECT product_id, 'Replenishment', @restock_amount
FROM tmp_restock;

DROP TEMPORARY TABLE IF EXISTS tmp_restock;

SELECT product_id, name, stock_quantity, reorder_level
FROM products
WHERE stock_quantity <= reorder_level;
