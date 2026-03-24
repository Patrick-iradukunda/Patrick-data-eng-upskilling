CREATE TABLE IF NOT EXISTS customers (
    customer_id   VARCHAR(20)  PRIMARY KEY,
    full_name     VARCHAR(100) NOT NULL,
    age           INTEGER      NOT NULL CHECK (age BETWEEN 1 AND 120),
    gender        VARCHAR(10)  NOT NULL,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS heartbeat_readings (
    id            BIGSERIAL    PRIMARY KEY,
    customer_id   VARCHAR(20)  NOT NULL REFERENCES customers(customer_id),
    timestamp     TIMESTAMPTZ  NOT NULL,
    heart_rate    INTEGER      NOT NULL,
    status        VARCHAR(20)  NOT NULL DEFAULT 'NORMAL',
    processed_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_heartbeat_timestamp
    ON heartbeat_readings (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_heartbeat_customer_timestamp
    ON heartbeat_readings (customer_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_heartbeat_status
    ON heartbeat_readings (status);

CREATE OR REPLACE VIEW anomaly_readings AS
SELECT
    r.id,
    r.customer_id,
    c.full_name,
    c.age,
    r.timestamp,
    r.heart_rate,
    r.status,
    r.processed_at
FROM heartbeat_readings r
JOIN customers c USING (customer_id)
WHERE r.status <> 'NORMAL'
ORDER BY r.timestamp DESC;

CREATE OR REPLACE VIEW customer_heartbeat_stats AS
SELECT
    c.customer_id,
    c.full_name,
    c.age,
    COUNT(r.id)                                          AS total_readings,
    ROUND(AVG(r.heart_rate)::NUMERIC, 1)                 AS avg_heart_rate,
    MIN(r.heart_rate)                                    AS min_heart_rate,
    MAX(r.heart_rate)                                    AS max_heart_rate,
    COUNT(r.id) FILTER (WHERE r.status = 'HIGH')         AS high_count,
    COUNT(r.id) FILTER (WHERE r.status = 'LOW')          AS low_count,
    COUNT(r.id) FILTER (WHERE r.status = 'CRITICAL')     AS critical_count,
    MAX(r.timestamp)                                     AS last_reading_at
FROM customers c
LEFT JOIN heartbeat_readings r USING (customer_id)
GROUP BY c.customer_id, c.full_name, c.age;

INSERT INTO customers (customer_id, full_name, age, gender) VALUES
    ('CUST_001', 'Alice Johnson',   34, 'Female'),
    ('CUST_002', 'Bob Williams',    52, 'Male'),
    ('CUST_003', 'Carol Martinez',  28, 'Female'),
    ('CUST_004', 'David Lee',       67, 'Male'),
    ('CUST_005', 'Emma Brown',      45, 'Female'),
    ('CUST_006', 'Frank Davis',     39, 'Male'),
    ('CUST_007', 'Grace Wilson',    73, 'Female'),
    ('CUST_008', 'Henry Taylor',    58, 'Male'),
    ('CUST_009', 'Isabella Moore',  22, 'Female'),
    ('CUST_010', 'James Anderson',  81, 'Male')
ON CONFLICT (customer_id) DO NOTHING;
