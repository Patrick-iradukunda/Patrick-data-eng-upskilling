# 🎬 TMDB Movie Analysis with PySpark

## 📌 Project Overview

This project analyzes movie data fetched from **The Movie Database (TMDB) API** using **PySpark**.  
The aim is to demonstrate big data processing concepts, data cleaning, transformation, analysis, and visualization using Spark.



---

## 🎯 Project Objectives

- Fetch real-world movie data from the TMDB API
- Store raw movie data in JSON format
- Load and process data using **PySpark**
- Clean and transform the dataset
- Perform analytical queries on movies
- Visualize insights using Matplotlib
- Save cleaned data in **Parquet format**

---


---

## 🛠️ Technologies Used

- Python 3.12  
- PySpark 4.x  
- Jupyter Notebook / JupyterLab  
- TMDB REST API  
- Pandas  
- Matplotlib  
- JSON & Parquet file formats  

---

## 📥 Data Source

- **API:** The Movie Database (TMDB)
- **Endpoint:** `https://api.themoviedb.org/3/movie/{movie_id}`
- **Data Fields Include:**
  - Movie title
  - Budget
  - Revenue
  - Runtime
  - Popularity
  - Ratings
  - Genres
  - Release date

---

## ⚙️ Data Collection Process

1. A Python script (`fetch_pyspark_data.py`) connects to the TMDB API.
2. Predefined movie IDs are queried.
3. Invalid movie IDs are skipped safely.
4. Valid movie records are saved as:
 
 
---

## 🔄 Data Processing with PySpark

All processing is performed inside the notebook.

### Spark Session
A Spark session is initialized for local execution.

### Schema Definition
A strict schema is applied to:
- Prevent `_corrupt_record` issues
- Enforce correct data types

### Data Loading
The JSON file is loaded safely using the predefined schema.

---

## 🧠 Data Cleaning & Feature Engineering

- Movies with missing or zero budget/revenue are removed
- Invalid records are filtered out
- New columns created:
- Budget (Million USD)
- Revenue (Million USD)
- Profit (Million USD)

---

## 📊 Analysis Performed

- Top 10 highest revenue movies
- Most profitable movies
- Average rating vs revenue
- Genre-based analysis
- Popularity comparison

---

## 📈 Data Visualization

Visualizations are created using **Matplotlib**, including:

- Bar charts of top revenue movies
- Clear labels and titles
- Spark-to-Pandas conversion only when necessary

---

## 💾 Data Output

The cleaned dataset is saved in Parquet format:

---

## ✅ Key Outcomes

- Successfully processed real-world API data using PySpark
- Applied schema-based Spark processing
- Generated financial and popularity insights
- Followed professional project structure
- Produced optimized Parquet output

---

