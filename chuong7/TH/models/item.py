from sqlmodel import Field, SQLModel

class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    price: int = Field(index=True)

class ItemCreate(SQLModel):
    name: str
    price: int

class ItemResponse(SQLModel):
    id: int
    name: str
    price: int