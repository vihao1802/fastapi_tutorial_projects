from fastapi import APIRouter, Depends, HTTPException, status
from configs.database import get_session
from models.cart import Cart, CartResponse
from models.order import Order
from models.item import Item, ItemResponse
from models.order_detail import OrderDetail
from services.zalo_pay import handle_zalopay_payment
from sqlmodel import  Session, select

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)

@router.get("/", response_model=list[CartResponse])
async def get_all_cart(session: Session = Depends(get_session)):
    carts = session.exec(select(Cart)).all()
    
    results = []

    for c in carts:
        item = session.get(Item, c.item_id)

        if not item:
            raise HTTPException(status_code=404, detail=f"Item with id {c.item_id} not found")
        
        results.append(CartResponse(
            id=c.id,
            item=ItemResponse(id=item.id, name=item.name, price=item.price),
            quantity=c.quantity
        ))

    return results
   
@router.post("/checkout", response_model=dict, status_code=status.HTTP_200_OK)
async def checkout_cart(session: Session = Depends(get_session)):

    # check if cart is empty in database
    cart_items = session.exec(select(Cart)).all()
    if len(cart_items) == 0:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    #  total amount
    total_amount = 0
    for c in cart_items:
        item = session.get(Item, c.item_id)
        total_amount += item.price * c.quantity

    try:
        # Bước 1: Tạo order
        new_order = Order(total_amount=total_amount)  
        session.add(new_order)
        session.commit()  
        session.refresh(new_order)

        # Bước 2: Tạo order_detail 
        for item in cart_items:
            order_detail = OrderDetail(
                order_id=new_order.id,
                item_id=item.item_id,
                quantity=item.quantity
            )
            session.add(order_detail)
        
        # Bước 3: Kết nối với API ZaloPay
        result = await handle_zalopay_payment(new_order, session)

        # Bước 4: Xóa cart
        # session.exec(delete(Cart))

        session.commit()

        return result
    except HTTPException as e: # Re-raise the same HTTPException without modification
        session.rollback()
        raise e 
    except Exception as e: # for unexpected errors
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))