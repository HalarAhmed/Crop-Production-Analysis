from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes.crops import router as crops_router
from .routes.historical import router as historical_router
from .routes.predict import router as predict_router

app = FastAPI(
    title="Agri Crop Analysis & Prediction API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(crops_router)
app.include_router(historical_router)
app.include_router(predict_router)


@app.get("/health")
def health():
    return {"status": "ok"}


def run():
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )


if __name__ == "__main__":
    run()

