from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db

router = APIRouter(tags=["crops"])


@router.get("/crops")
def get_crops(db: Session = Depends(get_db)):
    return {"crops": crud.list_crops(db)}

