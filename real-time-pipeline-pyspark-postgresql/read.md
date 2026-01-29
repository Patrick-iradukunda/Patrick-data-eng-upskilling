

# Real-Time Data Pipeline with PySpark & PostgreSQL

##  Project Overview
This project implements a real-time data pipeline that simulates an e-commerce platform generating user activity events such as product views and purchases.

Fake event data is continuously generated as CSV files, streamed using Apache Spark Structured Streaming, and stored in a PostgreSQL database for querying and analysis.

---

##  System Architecture

Data Generator (Python + Faker)
        |
        v
CSV Files (data/raw)
        |
        v
Spark Structured Streaming
        |
        v
PostgreSQL Database (user_events table)

---

##  Technologies Used

- Python 3
- Apache Spark (PySpark Structured Streaming)
- PostgreSQL
- Faker
- Pandas
- JDBC PostgreSQL Driver
- Linux (WSL Ubuntu)





##  How to Run the Project

### 1️⃣ Activate Virtual Environment

cd real-time-pipeline-pyspark-postgresql
source venv/bin/activate

---

### 2️⃣ Start PostgreSQL Service

sudo service postgresql start

psql -h localhost -U postgres -W

Create database and table:

CREATE DATABASE ecommerce_db;

\c ecommerce_db

CREATE TABLE IF NOT EXISTS user_events (
    user_id INT,
    product_id INT,
    action VARCHAR(10),
    timestamp TIMESTAMP,
    price NUMERIC,
    category VARCHAR(50)
);

---

### 3️⃣ Configure Database Connection

Edit:

config/postgres_connection.txt

Example:

host=localhost
port=5432
database=ecommerce_db
user=postgres
password=your_password

---

### 4️⃣ Start the Data Generator

Open a new terminal:

python src/data_generator.py

CSV files will be generated inside:

data/raw/

---

### 5️⃣ Start Spark Streaming Pipeline

In another terminal or notebook:

python src/spark_streaming_to_postgres.py

Spark will automatically ingest new CSV files.

---

### 6️⃣ Verify Data in PostgreSQL

psql -h localhost -U postgres -W -d ecommerce_db

Run:

SELECT COUNT(*) FROM user_events;
SELECT * FROM user_events LIMIT 10;

---

##  Testing Checklist

- CSV files generated correctly
- Spark detects new files
- Data written into PostgreSQL
- Record count increases continuously

---

##  Performance Metrics (Sample)

- Latency: 2–5 seconds per batch
- Throughput: 100–300 rows per minute
- Stability: Continuous processing

---


