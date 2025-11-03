

USE inventory_system;

DROP PROCEDURE IF EXISTS place_order;
DROP PROCEDURE IF EXISTS place_order_from_temp;

DELIMITER $$

CREATE PROCEDURE place_order(
        IN p_customer_id INT,
        IN p_items JSON
)
sp_label: BEGIN
    DECLARE i INT DEFAULT 0;
    DECLARE len INT DEFAULT 0;
    DECLARE v_order_id INT;
    DECLARE v_customer_count INT DEFAULT 0;
    DECLARE v_product_id INT;
    DECLARE v_quantity INT;
    DECLARE v_price DECIMAL(10,2);
    DECLARE v_stock INT;
    DECLARE v_line_total DECIMAL(10,2);
    DECLARE v_total DECIMAL(12,2) DEFAULT 0.00;
    DECLARE v_total_quantity INT DEFAULT 0;
    DECLARE v_discount_rate DECIMAL(4,2) DEFAULT 0.00;

    SELECT COUNT(*) INTO v_customer_count FROM customers WHERE customer_id = p_customer_id;
    IF v_customer_count = 0 THEN
        SELECT 'Invalid customer_id' AS error;
        LEAVE sp_label;
    END IF;

    IF p_items IS NULL OR NOT JSON_VALID(p_items) THEN
        SELECT 'Invalid or missing items JSON' AS error;
        LEAVE sp_label;
    END IF;

    SET len = JSON_LENGTH(p_items);
    IF len IS NULL OR len = 0 THEN
        SELECT 'No items provided' AS error;
        LEAVE sp_label;
    END IF;

    START TRANSACTION;

    INSERT INTO orders (customer_id) VALUES (p_customer_id);
    SET v_order_id = LAST_INSERT_ID();

    WHILE i < len DO
        SET v_product_id = CAST(JSON_UNQUOTE(JSON_EXTRACT(p_items, CONCAT('$[', i, '].product_id'))) AS UNSIGNED);
        SET v_quantity   = CAST(JSON_UNQUOTE(JSON_EXTRACT(p_items, CONCAT('$[', i, '].quantity'))) AS UNSIGNED);

        SELECT price, stock_quantity INTO v_price, v_stock
        FROM products
        WHERE product_id = v_product_id
        FOR UPDATE;

        IF v_price IS NULL THEN
            ROLLBACK;
            SELECT CONCAT('Product not found: ', v_product_id) AS error;
            LEAVE sp_label;
        END IF;

        IF v_stock < v_quantity THEN
            ROLLBACK;
            SELECT CONCAT('Insufficient stock for product ', v_product_id) AS error;
            LEAVE sp_label;
        END IF;

        SET v_line_total = v_price * v_quantity;

        INSERT INTO order_details (order_id, product_id, quantity, price)
        VALUES (v_order_id, v_product_id, v_quantity, v_price);

        UPDATE products
        SET stock_quantity = stock_quantity - v_quantity
        WHERE product_id = v_product_id;

        INSERT INTO inventory_logs (product_id, change_type, quantity_changed)
        VALUES (v_product_id, 'Order', -v_quantity);

        SET v_total = v_total + v_line_total;
        SET v_total_quantity = v_total_quantity + v_quantity;

        SET i = i + 1;
    END WHILE;

    IF v_total_quantity >= 20 THEN
        SET v_discount_rate = 0.20;
    ELSEIF v_total_quantity >= 10 THEN
        SET v_discount_rate = 0.10;
    ELSE
        SET v_discount_rate = 0.00;
    END IF;

    SET v_total = ROUND(v_total * (1 - v_discount_rate), 2);

    UPDATE orders SET total_amount = v_total WHERE order_id = v_order_id;

    COMMIT;

    SELECT 'Order placed successfully' AS message,
           v_order_id AS order_id,
           v_total AS total_amount,
           v_discount_rate AS discount_rate;
END sp_label$$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE place_order_from_temp(IN p_customer_id INT)
BEGIN
    DECLARE v_json TEXT DEFAULT '[]';

    SELECT CONCAT('[', IFNULL(GROUP_CONCAT(CONCAT('{"product_id":',product_id,',"quantity":',quantity,'}') SEPARATOR ','), ''), ']')
    INTO v_json
    FROM temp_order_lines;

    IF v_json = '[]' THEN
        SELECT 'No items in temp_order_lines' AS error;
    ELSE
        CALL place_order(p_customer_id, v_json);
    END IF;
END$$

DELIMITER ;
