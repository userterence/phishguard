from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=190)
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(pattern="^(student|teacher)$")

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class ScanIn(BaseModel):
    url: str = Field(min_length=1, max_length=2048)

class ScanOut(BaseModel):
    id: int
    url: str
    domain: str
    status: str
    category: str
    confidence: Optional[float]
    reasons: List[str]
    created_at: datetime
    class Config: from_attributes = True

class ReportIn(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    category: str = Field(pattern="^(academic|scholarship|account|enrollment)$")
    description: Optional[str] = Field(default=None, max_length=1000)

class ReportReview(BaseModel):
    status: str = Field(pattern="^(verified|rejected|false_positive)$")
    review_note: Optional[str] = None
