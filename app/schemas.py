from pydantic import BaseModel
from typing import Optional, Any

class UserOut(BaseModel):
    id: int
    email: str
    class Config:
        from_attributes = True

class UserProfileIn(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address_line: Optional[str] = None
    postal_code: Optional[str] = None

class UserProfileOut(UserProfileIn):
    user_id: int

class UserSettingsIn(BaseModel):
    notify_email: Optional[bool] = True
    notify_push: Optional[bool] = True
    spike_pct: Optional[str] = "0.3"
    recurring_delta_pct: Optional[str] = "0.1"
    big_expense_threshold: Optional[str] = "100000"
    low_balance_days: Optional[str] = "7"
    min_tax_reserve_pct: Optional[str] = "0.06"
    preferences: Optional[dict[str, Any]] = {}

class UserSettingsOut(UserSettingsIn):
    user_id: int
