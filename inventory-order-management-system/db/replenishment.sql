

USE inventory_system;

SET @restock_amount = 50;

SET SQL_SAFE_UPDATES = 0;

WITH low_stock AS (
    SELECT product_id, stock_quantity AS prev_stock
    FROM products
    WHERE stock_quantity <= reorder_level
)
SELECT product_id, prev_stock FROM low_stock;

UPDATE products p
SET p.stock_quantity = p.stock_quantity + @restock_amount
WHERE p.stock_quantity <= p.reorder_level;

INSERT INTO inventory_logs (product_id, change_type, quantity_changed)
SELECT product_id, 'Replenishment', @restock_amount
FROM products
WHERE stock_quantity - @restock_amount <= reorder_level;

SET SQL_SAFE_UPDATES = 1;

SELECT product_id, name, stock_quantity, reorder_level
FROM products
WHERE stock_quantity <= reorder_level;

SET GLOBAL event_scheduler = ON;

DROP PROCEDURE IF EXISTS auto_replenish_stock;

DELIMITER $$
CREATE PROCEDURE auto_replenish_stock()
BEGIN
    DECLARE v_restock_amount INT DEFAULT 50;
    
    UPDATE products p
    SET p.stock_quantity = p.stock_quantity + v_restock_amount
    WHERE p.stock_quantity <= p.reorder_level;

    INSERT INTO inventory_logs (product_id, change_type, quantity_changed)
    SELECT product_id, 'Auto-Replenishment', v_restock_amount
    FROM products
    WHERE stock_quantity - v_restock_amount <= reorder_level;
END$$
DELIMITER ;

DROP EVENT IF EXISTS daily_stock_replenishment;

CREATE EVENT daily_stock_replenishment
ON SCHEDULE EVERY 1 DAY
STARTS TIMESTAMP(CURRENT_DATE) + INTERVAL 2 HOUR
DO
    CALL auto_replenish_stock();

SELECT 'Automated replenishment event created successfully!' AS message;
SELECT event_name, event_definition, status, on_completion
FROM information_schema.events
WHERE event_schema = 'inventory_system';
