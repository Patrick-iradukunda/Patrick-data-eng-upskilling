#  Flight Fare Prediction API

End-to-end ML project predicting flight fares in Bangladesh using **FastAPI** and **scikit-learn**. Covers data cleaning, EDA, model training, evaluation, and live predictions.

---

##  Tech Stack
**FastAPI** · **scikit-learn** · **pandas / numpy** · **matplotlib / seaborn** · **joblib** · **JupyterLab** · **pytest**

---

##  Setup

```bash
pip install -r requirements.txt
```

Place your dataset at `data/Flight_Price_Dataset_of_Bangladesh.csv`

Create `.env`:
```env
APP_NAME=Flight Fare Prediction API
APP_VERSION=1.0.0
DEBUG=True
DATA_PATH=data/Flight_Price_Dataset_of_Bangladesh.csv
MODEL_DIR=saved_models
```

---

##  Run the API

```bash
uvicorn app.main:app --reload
```

Swagger docs → `http://localhost:8000/docs`

---

##  Run the Notebook

```bash
python -m jupyter lab
```

Open `notebooks/eda_analysis.ipynb` → **Run → Run All Cells**

| Section | Content |
|---|---|
| 1–2 | Imports, data loading & inspection |
| 3–4 | Data cleaning & feature engineering |
| 5 | EDA — distributions, airlines, seasons, routes, heatmap |
| 6–7 | Model preparation & evaluation helper |
| 8 | Baseline — Linear Regression |
| 9 | Advanced models with GridSearchCV |
| 10 | Model comparison table & charts |
| 11 | Feature importance |
| 12 | Residual analysis |
| 13 | Ridge vs Lasso regularization |
| 14 | Key insights & recommendations |

---

## Testing API Endpoints

 Tip: Use **Swagger UI** at `http://localhost:8000/docs` — click any endpoint → **Try it out** → **Execute**

### 1. Health check
```bash
curl http://localhost:8000/api/v1/health/
```

### 2. Raw data summary
```bash
curl http://localhost:8000/api/v1/data/raw/summary
curl http://localhost:8000/api/v1/data/cleaning-report
```

### 3. EDA endpoints
```bash
curl http://localhost:8000/api/v1/eda/kpis
curl http://localhost:8000/api/v1/eda/fare-distribution
curl http://localhost:8000/api/v1/eda/fare-by-airline
curl http://localhost:8000/api/v1/eda/fare-by-season
curl http://localhost:8000/api/v1/eda/monthly-trend
curl http://localhost:8000/api/v1/eda/correlation
```

### 4. Train all models  Run this first
```bash
curl -X POST http://localhost:8000/api/v1/train/
```

### 5. Model results
```bash
curl http://localhost:8000/api/v1/train/comparison
curl http://localhost:8000/api/v1/train/feature-importance
```

### 6. Predict a fare
```bash
curl -X POST http://localhost:8000/api/v1/predict/ \
  -H "Content-Type: application/json" \
  -d '{
    "airline": "Us-Bangla Airlines",
    "source": "Dhaka",
    "destination": "Chittagong",
    "base_fare": 3500.0,
    "tax_surcharge": 800.0,
    "month": 6,
    "day": 15,
    "weekday": 2,
    "season": "summer"
  }'
```

---

##  Models

| Model | Tuned |
|---|---|
| Linear Regression | — |
| Ridge Regression | ✅ |
| Lasso Regression | ✅ |
| Decision Tree | ✅ |
| Random Forest | ✅ |
| Gradient Boosting | ✅ |

Best model is auto-selected and saved after training.

---

##  Run Tests

```bash
PYTHONPATH=. pytest tests/ -v
```

---

 Always call `POST /api/v1/train/` before `POST /api/v1/predict/`
