from sqlmodel import Field, SQLModel
from models.item import ItemResponse

class Cart(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    item_id: int
    quantity: int

class CartCreate(SQLModel):
    item_id: int
    quantity: int

class CartResponse(SQLModel):
    id: int
    item: ItemResponse
    quantity: int