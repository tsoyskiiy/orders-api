from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from decimal import Decimal

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    full_name: str = Field(min_length=1, max_length=255)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

OrderStatus = Literal["pending", "paid", "shipped", "delivered", "cancelled"]


class OrderCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")


class OrderUpdate(BaseModel):
    quantity: int = Field(default=None, gt=0, description="Quantity must be greater than 0")
    status: OrderStatus = None


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    product_id: int
    quantity: int
    status: str
    created_at: datetime

class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str | None
    description: str | None
    price: Decimal
    stock: int
    created_at: datetime