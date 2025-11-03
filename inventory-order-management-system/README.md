# Inventory and Order Management System - Implementation Report

This repository contains a small MySQL-based Inventory and Order Management System implemented with plain SQL files. The `db/` folder contains the schema, sample data, stored procedures, views, replenishment automation and reporting queries.

This README includes a concise, file-by-file mapping that describes what is implemented in each SQL file so it's clear what to run and what to expect.

## At a glance

- Database name: `inventory_system` (created by `db/schema.sql`)
- Core tables: `customers`, `products`, `orders`, `order_details`, `inventory_logs`
- Views: `order_summary`, `stock_status` (in `db/views.sql`)
- Stored procedures: `place_order`, `place_order_from_temp`, `auto_replenish_stock` (in `db/order_placement.sql` and `db/replenishment.sql`)
- Event: `daily_stock_replenishment` (created in `db/replenishment.sql`)

## Files in db/

Each file below includes a short description of what's implemented and any key usage notes.

- `schema.sql`

  - Purpose: create the `inventory_system` database and all core tables + indexes.
  - Implements: `customers`, `products`, `orders`, `order_details`, `inventory_logs` with foreign keys, CHECK constraints and indexes (`idx_products_category`, `idx_order_details_product`, `idx_orders_order_date`). Uses InnoDB and sets strict SQL mode for safety.
  - Usage: `mysql < db/schema.sql`

- `sample_data.sql`

  - Purpose: populate small sample dataset for manual testing.
  - Implements: two customers and four products (Laptop, Mouse, Keyboard, Monitor) with initial `stock_quantity` and `reorder_level` values.
  - Usage: `mysql -D inventory_system < db/sample_data.sql`

- `order_placement.sql`

  - Purpose: transactional order placement and helper to place orders from a temporary table.
  - Implements:
    - `place_order(p_customer_id INT, p_items JSON)`: accepts a JSON array of {product_id, quantity}, validates customer and stock, deducts stock inside a transaction, inserts into `orders` and `order_details`, writes `inventory_logs`, applies bulk discounts (10% for 10–19 items, 20% for 20+ items), and returns summary on success or descriptive error on failure.
    - `place_order_from_temp(p_customer_id INT)`: builds JSON from `temp_order_lines` and calls `place_order`.
  - Notes: `place_order` uses `SELECT ... FOR UPDATE` to lock product rows and ensure safe stock deduction.
  - Usage: `mysql -D inventory_system < db/order_placement.sql` (then `CALL place_order(...)`)

- `replenishment.sql`

  - Purpose: manual and automated stock replenishment.
  - Implements:
    - A manual restock script (adds a fixed restock amount — default 50 units — to all products with `stock_quantity <= reorder_level`, logs the change to `inventory_logs`).
    - `auto_replenish_stock()` stored procedure that performs the same logic inside a procedure.
    - `daily_stock_replenishment` EVENT which calls `auto_replenish_stock()` once per day at 02:00 by default.
  - Notes: enables the global event scheduler and creates the EVENT. Verify with `SHOW EVENTS FROM inventory_system;` and `CALL auto_replenish_stock();`.
  - Usage: `mysql -D inventory_system < db/replenishment.sql`

- `views.sql`

  - Purpose: simplified read-only views for common queries.
  - Implements:
    - `order_summary` view: aggregates order header, customer name, order date, total amount and items count.
    - `stock_status` view: product-level stock with `needs_reorder` flag (1 when `stock_quantity <= reorder_level`).
  - Usage: `mysql -D inventory_system < db/views.sql`

- `reports.sql`
  - Purpose: reporting and verification queries used for monitoring and tests.
  - Implements useful queries: recent orders, low-stock listing, customer tiers (Bronze/Silver/Gold by spend), bulk-discount analysis, table/view/procedure/event verification, inventory logs summary, foreign key and index listing.
  - Usage: run queries from within a MySQL client connected to `inventory_system`, e.g. `mysql -D inventory_system < db/reports.sql` or paste the queries directly to inspect results.
  - The file has been refactored to a concise, comment-free form (under 80 lines) and includes two CTE/window examples: `customer_spend` (rank by spend) and `orders_with_running_total` (running totals).

## Recommended order to set up and test locally

1. Create schema and tables: `mysql < db/schema.sql`
2. Load sample data: `mysql -D inventory_system < db/sample_data.sql`
3. Install procedures: `mysql -D inventory_system < db/order_placement.sql`
4. Create views: `mysql -D inventory_system < db/views.sql`
5. Enable automation: `mysql -D inventory_system < db/replenishment.sql`
6. Run the reports/verification queries: `mysql -D inventory_system < db/reports.sql`
