# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime

from ..db import get_db
from ..models import User, UserProfile, UserSettings
from ..schemas import (
    UserOut, UserProfileIn, UserProfileOut,
    UserSettingsIn, UserSettingsOut
)
from ..security import decode_token, hash_password

router = APIRouter(prefix="/users", tags=["users"])


# ---------- helpers ----------
def get_current_user_id(authorization: str = Header(None)) -> int:
    """
    Берём user_id из JWT 'Authorization: Bearer <token>'
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "missing bearer token")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(401, "invalid token")
    return int(payload["sub"])


# ---------- регистрация (MVP) ----------
@router.post("", response_model=UserOut)
def create_user(email: str, password: str = "changeme", db: Session = Depends(get_db)):
    """
    Простейшее создание пользователя (для локальных тестов).
    Пароль хэшируем.
    """
    exists = db.query(User).filter(User.email == email).first()
    if exists:
        raise HTTPException(400, "email already exists")
    u = User(email=email, hashed_password=hash_password(password))
    db.add(u); db.flush()
    db.add(UserProfile(user_id=u.id))
    db.add(UserSettings(user_id=u.id))
    db.commit(); db.refresh(u)
    return u


# ---------- ручки "моего" пользователя (для фронта) ----------
@router.get("/me", response_model=UserOut)
def me(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "user not found")
    return u


@router.get("/me/profile", response_model=UserProfileOut)
def me_profile(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    p = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not p:
        raise HTTPException(404, "profile not found")
    return UserProfileOut(
        user_id=user_id,
        first_name=p.first_name, last_name=p.last_name, phone=p.phone,
        company_name=p.company_name, inn=p.inn, kpp=p.kpp, country=p.country,
        city=p.city, address_line=p.address_line, postal_code=p.postal_code
    )


@router.put("/me/profile", response_model=UserProfileOut)
def me_profile_update(
    data: UserProfileIn,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    p = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not p:
        p = UserProfile(user_id=user_id)
        db.add(p)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    p.updated_at = datetime.utcnow()
    db.commit()
    return UserProfileOut(user_id=user_id, **data.model_dump(exclude_unset=False))


@router.get("/me/settings", response_model=UserSettingsOut)
def me_settings(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    s = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not s:
        raise HTTPException(404, "settings not found")
    payload = {
        "notify_email": s.notify_email, "notify_push": s.notify_push,
        "spike_pct": s.spike_pct, "recurring_delta_pct": s.recurring_delta_pct,
        "big_expense_threshold": s.big_expense_threshold,
        "low_balance_days": s.low_balance_days,
        "min_tax_reserve_pct": s.min_tax_reserve_pct,
        "preferences": s.preferences or {},
    }
    return UserSettingsOut(user_id=user_id, **payload)


@router.put("/me/settings", response_model=UserSettingsOut)
def me_settings_update(
    data: UserSettingsIn,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    s = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not s:
        s = UserSettings(user_id=user_id)
        db.add(s)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    s.updated_at = datetime.utcnow()
    db.commit()
    return UserSettingsOut(user_id=user_id, **data.model_dump(exclude_unset=False))


# ---------- админские ручки "по ID" (чтобы НЕ конфликтовали с /me) ----------
@router.get("/by-id/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "user not found")
    return u


@router.get("/by-id/{user_id}/profile", response_model=UserProfileOut)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    p = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not p:
        raise HTTPException(404, "profile not found")
    return UserProfileOut(
        user_id=user_id,
        first_name=p.first_name, last_name=p.last_name, phone=p.phone,
        company_name=p.company_name, inn=p.inn, kpp=p.kpp, country=p.country,
        city=p.city, address_line=p.address_line, postal_code=p.postal_code
    )


@router.put("/by-id/{user_id}/profile", response_model=UserProfileOut)
def update_profile(user_id: int, data: UserProfileIn, db: Session = Depends(get_db)):
    p = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not p:
        p = UserProfile(user_id=user_id)
        db.add(p)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    p.updated_at = datetime.utcnow()
    db.commit()
    return UserProfileOut(user_id=user_id, **data.model_dump(exclude_unset=False))


@router.get("/by-id/{user_id}/settings", response_model=UserSettingsOut)
def get_settings(user_id: int, db: Session = Depends(get_db)):
    s = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not s:
        raise HTTPException(404, "settings not found")
    payload = {
        "notify_email": s.notify_email, "notify_push": s.notify_push,
        "spike_pct": s.spike_pct, "recurring_delta_pct": s.recurring_delta_pct,
        "big_expense_threshold": s.big_expense_threshold,
        "low_balance_days": s.low_balance_days,
        "min_tax_reserve_pct": s.min_tax_reserve_pct,
        "preferences": s.preferences or {},
    }
    return UserSettingsOut(user_id=user_id, **payload)


@router.put("/by-id/{user_id}/settings", response_model=UserSettingsOut)
def update_settings(user_id: int, data: UserSettingsIn, db: Session = Depends(get_db)):
    s = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not s:
        s = UserSettings(user_id=user_id)
        db.add(s)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    s.updated_at = datetime.utcnow()
    db.commit()
    return UserSettingsOut(user_id=user_id, **data.model_dump(exclude_unset=False))
