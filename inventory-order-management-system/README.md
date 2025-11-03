# Inventory and Order Management System

A MySQL-based inventory and order management system with automated stock replenishment, transactional order processing, and comprehensive reporting capabilities.

## Database Overview

- **Database name**: `inventory_system`
- **Core tables**: `customers`, `products`, `orders`, `order_details`, `inventory_logs`
- **Views**: `order_summary`, `stock_status`
- **Stored procedures**: `place_order`, `place_order_from_temp`, `auto_replenish_stock`
- **Event**: `daily_stock_replenishment`

## Quick Start

Execute the following SQL files in MySQL Workbench in this exact order:

1. `schema.sql` - Creates database and tables
2. `sample_data.sql` - Loads sample data (4 customers, 6 products, 5 orders)
3. `order_placement.sql` - Creates order processing procedures
4. `views.sql` - Creates summary views
5. `replenishment.sql` - Sets up automated stock replenishment
6. `reports.sql` - Run individual queries for analysis

## File Descriptions

### schema.sql

Creates the database schema with all tables, foreign keys, and indexes.

**Features:**

- Automatic cleanup with `DROP TABLE IF EXISTS` statements
- InnoDB engine with strict SQL mode
- CHECK constraints for data validation
- Indexed columns for optimized queries (`category`, `product_id`, `order_date`)

**Tables:**

- `customers` - Customer information
- `products` - Product catalog with stock levels
- `orders` - Order headers
- `order_details` - Order line items
- `inventory_logs` - Audit trail for inventory changes

**Usage:**

```sql
-- In MySQL Workbench, press Ctrl+Shift+Enter
```

### sample_data.sql

Populates the database with realistic sample data for testing.

**Features:**

- Safe update mode handling for batch operations
- Automatic cleanup of existing data
- Auto-increment counter reset
- 4 customers, 6 products, 5 orders with 14 line items
- 22 inventory log entries tracking all stock movements

**Data includes:**

- Initial stock receipts
- Order transactions with stock deductions
- Replenishment activities
- Final stock quantities reflecting all transactions

**Usage:**

```sql
-- Loads complete dataset with referential integrity
```

### order_placement.sql

Implements transactional order processing with comprehensive validation.

**Procedures:**

#### place_order(p_customer_id, p_items)

Places an order with automatic stock validation and inventory tracking.

**Parameters:**

- `p_customer_id` - Customer ID (validated against customers table)
- `p_items` - JSON array: `[{"product_id": 1, "quantity": 2}]`

**Features:**

- Customer validation
- JSON input validation
- Stock availability checking with row-level locking
- Automatic stock deduction
- Inventory logging
- Bulk discounts (10% for 10-19 items, 20% for 20+ items)
- Transaction rollback on errors

**Example:**

```sql
CALL place_order(1, '[{"product_id": 1, "quantity": 2}, {"product_id": 3, "quantity": 1}]');
```

#### place_order_from_temp(p_customer_id)

Places an order using data from a `temp_order_lines` table (requires separate table creation).

### views.sql

Creates database views for simplified querying.

**Views:**

#### order_summary

Aggregated order information with customer details and item counts.

**Columns:** `order_id`, `customer_id`, `customer_name`, `order_date`, `total_amount`, `items_count`

#### stock_status

Current stock levels with reorder indicators.

**Columns:** `product_id`, `product_name`, `category`, `stock_quantity`, `reorder_level`, `needs_reorder`

**Usage:**

```sql
SELECT * FROM order_summary WHERE order_date >= '2025-11-01';
SELECT * FROM stock_status WHERE needs_reorder = 1;
```

### replenishment.sql

Automated and manual stock replenishment system.

**Features:**

**Manual Replenishment:**

- Identifies low stock products
- Adds 50 units to products at or below reorder level
- Logs replenishment to `inventory_logs`
- Safe update mode handling

**Automated Replenishment:**

- `auto_replenish_stock()` procedure
- `daily_stock_replenishment` event (runs daily at 2:00 AM)
- Enables global event scheduler

**Usage:**

```sql
-- Manual execution
SET @restock_amount = 50;
-- Run the replenishment script

-- Check event status
SHOW EVENTS FROM inventory_system;

-- Call procedure manually
CALL auto_replenish_stock();
```

### reports.sql

Collection of analytical queries for business intelligence.

**Available Reports:**

1. All orders with customer details and item counts
2. Low stock products requiring replenishment
3. Customer spending tiers (Bronze/Silver/Gold based on total spend)
4. Bulk discount eligibility by order
5. Table row counts across all tables
6. List of all views in the database
7. List of all stored procedures
8. Active events and schedules
9. Inventory change type summary
10. Foreign key relationships
11. Database indexes
12. Customer spending rankings (with RANK window function)
13. Running total of orders by customer (with window functions)

**Usage:**

```sql
-- Execute individual queries as needed
-- Each query is independent and can run separately
```

## Key Features

### Data Integrity

- Foreign key constraints with cascading deletes
- CHECK constraints for non-negative values
- UNIQUE constraint on customer emails
- Transactional order processing with rollback capability

### Performance Optimization

- Indexed columns for frequent queries
- Row-level locking for concurrent order processing
- InnoDB storage engine for ACID compliance

### Safe Operations

- `DROP IF EXISTS` statements prevent execution errors
- Safe update mode management for batch operations
- Automatic cleanup before data insertion

### Automation

- Scheduled daily stock replenishment
- Automatic inventory logging on all stock changes
- Event scheduler for background tasks

## Technical Specifications

- **MySQL Version**: 8.0+ (requires JSON functions)
- **Character Set**: UTF-8 (utf8mb4)
- **Collation**: utf8mb4_unicode_ci
- **Storage Engine**: InnoDB
- **SQL Mode**: STRICT_ALL_TABLES, NO_ENGINE_SUBSTITUTION

## Sample Data Statistics

After running `sample_data.sql`:

- **Customers**: 4
- **Products**: 6
- **Orders**: 5
- **Order Details**: 14 line items
- **Inventory Logs**: 22 entries

## Troubleshooting

**Safe Update Mode Errors:**
The scripts automatically handle safe update mode by temporarily disabling it for batch operations.

**Duplicate Entry Errors:**
All scripts include cleanup statements (`DELETE`, `DROP IF EXISTS`) to handle re-execution.

**Procedure Syntax Errors:**
Ensure DELIMITER statements are processed correctly in MySQL Workbench. Use `Ctrl+Shift+Enter` to execute entire files.

**Event Scheduler:**
Verify event scheduler is enabled:

```sql
SHOW VARIABLES LIKE 'event_scheduler';
SET GLOBAL event_scheduler = ON;
```

## License

This is a sample educational project for learning MySQL database design and stored procedures.

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
