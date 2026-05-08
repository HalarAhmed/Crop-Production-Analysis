<<<<<<< HEAD
# Agricultural Crop Analysis & Production Prediction (DBMS + ML)

Full-stack semester project using:

- **FastAPI** (backend API)
- **Streamlit + Plotly** (modern dashboard)
- **PostgreSQL + SQLAlchemy** (database)
- **Pre-trained per-crop ML models** (`.pkl`) loaded at prediction time (no retraining)

## Project structure

```
CS-232/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   └── routes/
├── frontend/
│   └── app.py
├── ml_models/
│   └── (place your .pkl files here)
├── .env.example
├── requirements.txt
└── README.md
```

## Backend API (FastAPI)

### Required routes

- **GET `/crops`**
  - Returns all crop names from table `crop`
- **GET `/historical-data`**
  - Query params: `crop_name`, `start_year`, `end_year`
  - Returns points: `fiscal_year`, `rainfall`, `avg_temperature`, `production`
  - Uses DB view `ml_ready_data`
  - `start_year/end_year` can be either:
    - **4-digit start year** like `1980` (filters by first 4 digits in `fiscal_year` like `1980-81`)
    - **exact fiscal_year label** like `1980-81` (string range)
- **POST `/predict`**
  - JSON: `crop_name`, `rainfall`, `avg_temperature`
  - Returns: `predicted_production`

## ML models folder + naming rules (IMPORTANT)

This project loads **a scaler + model per crop** (as your earlier training script produced).

### Place files here

- Put model artifacts in: `ml_models/`

### Supported file names

For a crop name like `Sugar Cane`, the slug becomes `sugar_cane` and the backend will look for:

- **Preferred**
  - `ml_models/model_sugar_cane.pkl`
  - `ml_models/scaler_sugar_cane.pkl`
- **Also accepted**
  - `ml_models/sugar_cane.pkl`
  - `ml_models/scaler_sugar_cane.pkl`

### Feature order (must match training)

The backend builds the feature vector exactly as:

1. `rainfall`
2. `avg_temperature`

## Local setup (Windows)

### 1) Create venv + install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2) Configure `.env`

Copy `.env.example` to `.env` and set:

```env
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DBNAME
ML_MODELS_DIR=ml_models
```

### 3) Run backend

```powershell
python -m backend.main
```

Backend runs on `http://127.0.0.1:8000` by default.

### 4) Run Streamlit dashboard

```powershell
streamlit run frontend/app.py
```

Optional (if your API is not on default):

```powershell
$env:API_BASE_URL="http://127.0.0.1:8000"
streamlit run frontend/app.py
```

## Notes

- Database is assumed to already exist and contain real data for tables:
  - `crop`, `year`, `productiondata`, `weatherdata`
  - view: `ml_ready_data`
- No model retraining happens in this app; it only loads your saved `.pkl` files.
=======
# Crop-Production-Analysis
>>>>>>> 54589ab7b2a2ebe32535cf811401320fa6d1f08d
