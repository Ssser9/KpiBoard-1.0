
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..db import get_db
from ..repositories import sum_by_type, sum_by_categories

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def summary(period: str = "30d", db: Session = Depends(get_db), user_id: int = 1):
    now = datetime.utcnow()
    days = 30 if period == "30d" else 7 if period == "7d" else 90
    df = now - timedelta(days=days)
    income, expense = sum_by_type(db, user_id, df, now)
    profit = income - expense
    return {"income": income, "expense": expense, "profit": profit}

@router.get("/categories")
def categories(period: str = "30d", top: int = 10, db: Session = Depends(get_db), user_id: int = 1):
    now = datetime.utcnow()
    days = 30 if period == "30d" else 7 if period == "7d" else 90
    df = now - timedelta(days=days)
    data = sum_by_categories(db, user_id, df, now, top=top)
    return {"period": period, "top": top, "items": data}
