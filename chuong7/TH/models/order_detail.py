from sqlmodel import Field, SQLModel
from models.item import ItemResponse

class OrderDetail(SQLModel, table=True):
    __tablename__ = 'order_detail' # custom table name

    id: int | None = Field(default=None, primary_key=True)
    order_id: int
    item_id: int
    quantity: int

class OrderDetailCreate(SQLModel):
    order_id: int
    item_id: int
    quantity: int

class OrderDetailResponse(SQLModel):
    id: int
    order_id: int
    item: ItemResponse
    quantity: int