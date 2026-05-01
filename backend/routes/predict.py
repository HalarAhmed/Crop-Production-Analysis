from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
from fastapi import APIRouter, HTTPException

from ..config import settings
from ..schemas import PredictRequest

router = APIRouter(tags=["prediction"])


def _slugify_crop(crop_name: str) -> str:
    return crop_name.strip().lower().replace(" ", "_")


def _candidate_paths(models_dir: Path, slug: str) -> dict:
    """
    Supports multiple naming conventions, but prefers:
      - model_{slug}.pkl + scaler_{slug}.pkl
    Also allows:
      - {slug}.pkl + scaler_{slug}.pkl
      - model_{slug}.pkl + {slug}_scaler.pkl
    """
    return {
        "model": [
            models_dir / f"model_{slug}.pkl",
            models_dir / f"{slug}.pkl",
        ],
        "scaler": [
            models_dir / f"scaler_{slug}.pkl",
            models_dir / f"{slug}_scaler.pkl",
        ],
    }


@lru_cache(maxsize=64)
def _load_model_and_scaler(crop_name: str):
    models_dir = settings.ml_models_path()
    slug = _slugify_crop(crop_name)
    candidates = _candidate_paths(models_dir, slug)

    model_path = next((p for p in candidates["model"] if p.exists()), None)
    scaler_path = next((p for p in candidates["scaler"] if p.exists()), None)

    if model_path is None or scaler_path is None:
        raise FileNotFoundError(
            "Missing model/scaler for crop. "
            f"Looked for model in: {[str(p) for p in candidates['model']]} and "
            f"scaler in: {[str(p) for p in candidates['scaler']]}"
        )

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    return model, scaler, str(model_path.name), str(scaler_path.name)


@router.post("/predict")
def predict(req: PredictRequest):
    try:
        model, scaler, model_file, scaler_file = _load_model_and_scaler(req.crop_name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {e}")

    # IMPORTANT: feature order must match training: [rainfall, avg_temperature]
    X = np.array([[req.rainfall, req.avg_temperature]], dtype=float)

    try:
        X_scaled = scaler.transform(X)
        y_pred = model.predict(X_scaled)
        pred = float(np.asarray(y_pred).ravel()[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    return {
        "crop_name": req.crop_name,
        "predicted_production": pred,
        "model_file": model_file,
        "scaler_file": scaler_file,
    }

