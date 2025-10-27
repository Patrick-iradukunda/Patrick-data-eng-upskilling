# Inventory and Order Management System

This repository contains a simplified, beginner-friendly SQL inventory and order management schema intended for learning and small demos. All SQL files live in the `db/` folder. The `ERD/` helper files have been removed; only the final assets were kept previously and the folder is now deleted per project cleanup.

What is included (db/):

- `schema.sql` — creates the `inventory_system` database and core tables:
  - `customers` (customer_id PK)
  - `products` (product_id PK) with `price`, `stock_quantity`, `reorder_level`
  - `orders` (order_id PK, customer_id FK)
  - `order_details` (order_detail_id PK, order_id FK, product_id FK)
  - `inventory_logs` (log_id PK, product_id FK)
- `sample_data.sql` — small set of sample customers and products
- `order_placement.sql` — JSON-based `place_order(customer_id, items_json)` procedure that:
  - accepts multiple items in a single call (JSON array of {product_id, quantity})
  - validates customer and product existence
  - checks stock and performs the whole order in a single transaction
  - deducts product stock, inserts `order_details`, logs inventory changes
  - computes and applies a bulk discount (10% for >=10 items, 20% for >=20 items)
- `replenishment.sql` — restocking helper that:
  - finds low-stock products (stock_quantity <= reorder_level)
  - applies a configurable restock amount to only the affected rows
  - inserts `inventory_logs` for the exact rows updated
- `views.sql` — convenience views: `order_summary` (order-level summary) and `stock_status` (low-stock flag)
- `reports.sql` — sample reporting queries: order lists, low-stock products, customer tiers, per-order bulk discount rate

Implementation vs. lab requirements (quick mapping):

- Schema (Phase 1): Implemented — core tables and foreign keys are present in `schema.sql`.
- Order placement (Phase 2): Implemented with `order_placement.sql` — supports multi-product orders, validations, stock updates and inventory logging. Bulk discounts are applied at order time.
- Inventory tracking (Phase 2): Implemented — `inventory_logs` records order and replenishment changes.
- Monitoring & Reporting (Phase 3): Implemented — `views.sql` and `reports.sql` provide order summaries, low-stock reports, and customer-tier calculations.
- Replenishment (Phase 4): Implemented — `replenishment.sql` identifies low-stock products, updates stock, and logs replenishments for those specific products. (Manual run; no scheduler/event configured.)

Notes and small caveats

- The `place_order` procedure expects a JSON array payload; example:

```sql
CALL place_order(1, '[{"product_id":1,"quantity":2},{"product_id":2,"quantity":3}]');
```

- The replenishment script uses a temporary table to ensure logs match the rows that were updated.
- No scheduled automation (cron/event) was added; replenishment is a manual script you can run on demand.
- Indexing beyond primary keys is left minimal; add indexes if you see performance concerns on large datasets.

Quick steps to run in MySQL Workbench

1. Open MySQL Workbench and connect to your server.
2. Run `db/schema.sql` to create the `inventory_system` database and tables.
3. Run `db/sample_data.sql` to insert example customers and products.
4. Run `db/order_placement.sql` to create the JSON-capable `place_order` procedure.
5. Run `db/views.sql` to create the convenience views.
6. Optionally run queries in `db/reports.sql` and `db/replenishment.sql` to explore reporting and stock management.

If MySQL Workbench blocks an UPDATE (safe update mode), run:

```sql
SET SQL_SAFE_UPDATES = 0;
```

If you'd like, I can also:

- add a tiny `verify_counts.sql` file that prints row counts for all core tables after setup
- implement an automated event to call `replenishment.sql` on a schedule (MySQL EVENT)

---
