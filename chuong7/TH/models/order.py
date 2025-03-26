from sqlmodel import Field, SQLModel
from datetime import datetime
from models.item import Item
from models.order_detail import OrderDetailResponse
from typing import List
from pydantic import BaseModel

class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # default is pending
    status: str = Field(default="pending")
    total_amount: int = Field()
    created_at: datetime = Field(default_factory=datetime.now)

class OrderResponse(SQLModel):
    id: int
    status: str
    total_amount: int
    created_at: datetime
    order_details: List[OrderDetailResponse] = []

# Model lưu callback (nếu cần)
class PaymentCallback(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    app_trans_id: str
    status: str
    raw_data: str  # Lưu dữ liệu callback gốc

# Request Model từ ZaloPay
class CallbackData(BaseModel):
    data: str
    mac: str