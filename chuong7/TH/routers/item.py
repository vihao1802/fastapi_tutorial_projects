from fastapi import APIRouter, Depends, HTTPException, status
from configs.database import get_session
from models.item import Item, ItemCreate
from sqlmodel import  Session, select

router = APIRouter(
    prefix="/item",
    tags=["Item"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate, session: Session = Depends(get_session)):
    try:
        new_item = Item(**item.dict())
        session.add(new_item)
        session.commit()
        session.refresh(new_item)
        return new_item
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[Item])
async def get_all_items(session: Session = Depends(get_session)):
    items = session.exec(select(Item)).all()
    return items

""" @router.delete("/{item_id}", response_model=list[Item])
async def remove_item(item_id: int, session: Session = Depends(get_session)):
    cart_item = session.exec(select(Cart).where(Cart.item_id == item_id)).one()

    if cart_item:
        raise HTTPException(status_code=400, detail="Item is in cart")

    try:
        item = session.exec(select(Item).where(Item.id == item_id)).one()
        session.delete(item)
        session.commit()
        return session.exec(select(Item)).all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) """