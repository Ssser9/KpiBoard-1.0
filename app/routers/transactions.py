
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
import pandas as pd
from io import StringIO
from sqlalchemy.orm import Session
from datetime import datetime
from ..db import get_db
from ..models import Transaction
from ..repositories import list_transactions as repo_list

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/import_csv")
async def import_csv(account_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user_id: int = 1):
    # CSV: posted_at, amount, type, [currency, description]
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Нужен CSV файл")
    content = (await file.read()).decode("utf-8")
    df = pd.read_csv(StringIO(content))
    required = {"posted_at", "amount", "type"}
    if not required.issubset(df.columns):
        raise HTTPException(400, f"В CSV должны быть колонки: {', '.join(required)}")
    created = 0
    for _, row in df.iterrows():
        tx = Transaction(
            user_id=user_id,
            account_id=account_id,
            posted_at=datetime.fromisoformat(str(row["posted_at"])),
            amount=float(row["amount"]),
            currency=str(row.get("currency", "RUB")),
            type=str(row["type"]),
            description_raw=str(row.get("description", "")),
            source="csv"
        )
        db.add(tx); created += 1
    db.commit()
    return {"imported": created}

@router.get("")
def list_transactions(
    db: Session = Depends(get_db),
    user_id: int = 1,
    limit: int = 100,
    date_from: str | None = Query(None, description="ISO дата-время"),
    date_to: str | None = Query(None, description="ISO дата-время"),
    category_id: int | None = None,
    search: str | None = None
):
    df = datetime.fromisoformat(date_from) if date_from else None
    dt = datetime.fromisoformat(date_to) if date_to else None
    rows = repo_list(db, user_id, df, dt, category_id, search, limit)
    return {"items": [{
        "id": r.id,
        "posted_at": r.posted_at.isoformat(),
        "amount": float(r.amount),
        "type": r.type,
        "currency": r.currency,
        "category_id": r.category_id,
        "counterparty": r.counterparty,
        "description": r.description_raw
    } for r in rows]}
