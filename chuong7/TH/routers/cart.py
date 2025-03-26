from fastapi import APIRouter, Depends, HTTPException, status
from configs.database import get_session
from models.cart import Cart, CartCreate, CartResponse
from models.order import Order, OrderResponse
from models.item import Item, ItemResponse
from models.order_detail import OrderDetail, OrderDetailCreate
from utils.zalo_pay import handle_zalopay_payment
from sqlmodel import  Session, select, delete

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)

@router.post("/", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(cart: CartCreate, session: Session = Depends(get_session)):
    existing_item = session.get(Item, cart.item_id)

    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if cart.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    
    # Check if item already exists in cart then update quantity
    existing_cart = session.exec(select(Cart).where(Cart.item_id == cart.item_id)).one_or_none()

    if existing_cart:
        existing_cart.quantity += cart.quantity
        session.add(existing_cart)  # Mark for update
        cart_entry = existing_cart
    else:
        cart_entry = Cart.model_validate(cart)  # Properly validate the Pydantic model
        session.add(cart_entry)

    session.commit()
    session.refresh(cart_entry)

    return CartResponse(
        id=cart_entry.id,
        item=ItemResponse(
            id=existing_item.id,
            name=existing_item.name, 
            price=existing_item.price
        ),
        quantity=cart_entry.quantity
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


@router.delete("/{item_id}", response_model=list[CartResponse])
async def remove_cart(item_id: int, session: Session = Depends(get_session)):
    cart_item = session.exec(select(Cart).where(Cart.item_id == item_id)).one_or_none()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    session.delete(cart_item)
    session.commit()

    return await get_all_cart(session)
   
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
        result = await handle_zalopay_payment(new_order)

        # Bước 4: Xóa cart
        session.exec(delete(Cart))

        session.commit()

        return result
    except HTTPException as e: # Re-raise the same HTTPException without modification
        session.rollback()
        raise e 
    except Exception as e: # for unexpected errors
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))