# Flight Price Analysis Pipeline

End-to-end automated ETL and analytics pipeline for flight price data built with Apache Airflow, Pandas, MySQL, and PostgreSQL.

## Architecture Overview

```
CSV Data Source
      │
      ▼
EXTRACT (Pandas)
      │
      ▼
VALIDATE (Data Quality Checks)
      │
      ▼
TRANSFORM (Feature Engineering)
      │
      ├──────────────► MySQL (Raw & Staging Tables)
      │
      ▼
COMPUTE KPIs (Aggregations)
      │
      ▼
PostgreSQL (Analytics Tables)
```

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Orchestration | Apache Airflow |
| Language | Python 3.10 |
| Data Processing | Pandas |
| Staging Database | MySQL |
| Analytics Database | PostgreSQL |

## Pipeline Stages

### 1. Extract
Reads raw CSV data into Pandas DataFrame.

**Input:** `data/Flight_Price_Dataset_of_Bangladesh.csv`
**Output:** Raw DataFrame (57,000 rows)

### 2. Validate
Performs data quality checks and type conversions.

**Operations:**
- Column renaming and standardization
- DateTime parsing and validation
- Numeric type conversion
- Null value handling
- Data integrity checks

### 3. Transform
Feature engineering and data preparation.

**Operations:**
- Type casting for downstream processing
- Data normalization

### 4. Load to MySQL
Dual-table loading strategy for different use cases.

**Tables:**
- `flight_prices_raw`: Detailed schema for comprehensive analysis
- `flight_prices_staging`: Simplified schema for operational queries

**Method:** SQLAlchemy + PyMySQL
**Mode:** Replace (ensures fresh data on each run)

### 5. Compute KPIs
Generates analytical metrics from validated data.

**Outputs:**
- **Airline KPIs:** Average fare and booking count per airline
- **Top Routes:** Most popular city pairs by booking volume
- **Seasonal Trends:** Price variations across seasons (Regular, Eid, Hajj, Winter Holidays)

### 6. Load to PostgreSQL
Stores analytical results for business intelligence.

**Method:** SQLAlchemy + psycopg2
**Mode:** Replace (ensures fresh analytics on each run)

## Airflow DAG Configuration

**DAG ID:** `flight_price_analysis`
**Schedule:** Daily (`@daily`)
**Catchup:** Disabled
**Tags:** flight, etl, analytics

**Task Structure:**
```
run_pipeline (PythonOperator)
  │
  ├─ Extract
  ├─ Validate
  ├─ Transform
  ├─ Load MySQL (raw)
  ├─ Load MySQL (staging)
  ├─ Compute KPIs
  └─ Load PostgreSQL
```

## Installation & Setup

### Prerequisites
- Python 3.10+
- Apache Airflow
- MySQL Server
- PostgreSQL Server

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database connections:
   - MySQL: `localhost:3306/flight_staging`
   - PostgreSQL: `localhost:5432/flight_analytics`

3. Place data file:
```bash
mkdir -p data/
# Copy Flight_Price_Dataset_of_Bangladesh.csv to data/
```

4. Initialize Airflow:
```bash
airflow db init
```

## Running the Pipeline

### Trigger from Airflow CLI
```bash
airflow dags trigger flight_price_analysis
```

### Trigger from Airflow UI
1. Navigate to `http://localhost:8080`
2. Locate DAG: `flight_price_analysis`
3. Click the play button (▶) to trigger




## Key Insights

### Top Airlines by Average Fare
1. Turkish Airlines: 75,547 BDT
2. AirAsia: 74,534 BDT
3. Cathay Pacific: 73,325 BDT

### Busiest Routes
1. Rajshahi → Singapore: 417 bookings
2. Dhaka → Dubai: 413 bookings
3. Barisal → Toronto: 410 bookings

### Seasonal Pricing
1. Hajj: 97,144 BDT (highest)
2. Eid: 91,560 BDT
3. Winter Holidays: 79,677 BDT
4. Regular: 68,077 BDT (lowest)


## License

This project is part of a Data Engineering upskilling program.
