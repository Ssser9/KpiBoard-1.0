# Вверху файла
from sqlalchemy import select, func, and_, or_, case  # <- добавили case
# остальное без изменений

from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_
from datetime import datetime
from .models import Transaction, Category

def sum_by_type(db: Session, user_id: int, date_from: datetime, date_to: datetime):
    income_q = func.coalesce(func.sum(func.case((Transaction.type == 'credit', Transaction.amount), else_=0)), 0)
    expense_q = func.coalesce(func.sum(func.case((Transaction.type == 'debit', Transaction.amount), else_=0)), 0)
    q = select(income_q.label("income"), expense_q.label("expense")).where(
        and_(Transaction.user_id==user_id, Transaction.posted_at>=date_from, Transaction.posted_at<date_to)
    )
    row = db.execute(q).first()
    income = float(row.income or 0)
    expense = float(row.expense or 0)
    return income, abs(expense)

def list_transactions(db: Session, user_id: int, date_from: datetime | None = None, date_to: datetime | None = None,
                      category_id: int | None = None, search: str | None = None, limit: int = 100):
    cond = [Transaction.user_id == user_id]
    if date_from:
        cond.append(Transaction.posted_at >= date_from)
    if date_to:
        cond.append(Transaction.posted_at < date_to)
    if category_id:
        cond.append(Transaction.category_id == category_id)
    if search:
        like = f"%{search}%"
        cond.append(or_(Transaction.description_raw.ilike(like), Transaction.counterparty.ilike(like)))
    q = (select(Transaction).where(and_(*cond))
         .order_by(Transaction.posted_at.desc())
         .limit(limit))
    rows = db.execute(q).scalars().all()
    return rows

# ЗАМЕНИ эту функцию на новую
def sum_by_categories(db: Session, user_id: int, date_from: datetime, date_to: datetime, top: int = 10):
    from .models import Transaction, Category

    expense_case = case((Transaction.type == 'debit', Transaction.amount), else_=0)
    income_case  = case((Transaction.type == 'credit', Transaction.amount), else_=0)

    q = (
        select(
            Category.id.label("category_id"),
            func.coalesce(Category.name, "Без категории").label("category_name"),
            func.coalesce(func.sum(expense_case), 0).label("expense"),
            func.coalesce(func.sum(income_case), 0).label("income"),
        )
        .select_from(Transaction)
        .join(Category, Transaction.category_id == Category.id, isouter=True)
        .where(
            and_(
                Transaction.user_id == user_id,
                Transaction.posted_at >= date_from,
                Transaction.posted_at < date_to,
            )
        )
        .group_by(Category.id, Category.name)
        .order_by(func.coalesce(func.sum(expense_case), 0).desc())
        .limit(top)
    )

    items = []
    for row in db.execute(q):
        items.append({
            "category_id": row.category_id,
            "category_name": row.category_name or "Без категории",
            "expense": float(abs(row.expense or 0)),
            "income": float(row.income or 0),
        })
    return items

