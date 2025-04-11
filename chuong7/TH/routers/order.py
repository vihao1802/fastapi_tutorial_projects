from fastapi import APIRouter, Depends,  HTTPException
from configs.database import get_session
from models.order import Order, OrderResponse, CallbackData
from models.order_detail import OrderDetail, OrderDetailResponse
from models.item import ItemResponse, Item
from sqlmodel import  Session, select
from services.zalo_pay import process_zalopay_callback, check_zalopay_status_service

router = APIRouter(
    prefix="/order",
    tags=["Order"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=list[Order])
async def get_all(session: Session = Depends(get_session)):
    orders = session.exec(select(Order)).all()
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, session: Session = Depends(get_session)):
    # Lấy thông tin đơn hàng
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Truy vấn OrderDetail và join với Item
    stmt = (
        select(OrderDetail, Item)
        .join(Item, OrderDetail.item_id == Item.id)
        .where(OrderDetail.order_id == order_id)
    )
    
    results = session.exec(stmt).all()

    # Debugging: Kiểm tra dữ liệu lấy được
    print(results)

    # Chuyển đổi kết quả thành danh sách OrderDetailResponse
    order_details = [
        OrderDetailResponse(
            id=od.id,
            order_id=od.order_id,
            quantity=od.quantity,
            item=ItemResponse(
                id=item.id,
                name=item.name,
                price=item.price
            )
        ) for od, item in results
    ]

    return OrderResponse(
        id=order.id,
        status=order.status,
        total_amount=order.total_amount,
        created_at=order.created_at,
        order_details=order_details
    )

@router.post("/{order_id}/zalopay-callback")
async def callback(payload: CallbackData, order_id: str, session: Session = Depends(get_session)):
    return await process_zalopay_callback(payload, order_id, session)

@router.get("/{order_id}/zalopay-status")
async def check_zalopay_status(order_id: int, session: Session = Depends(get_session)):
    try:
        order = session.exec(select(Order).where(Order.id == order_id)).one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        result = await check_zalopay_status_service(order.app_trans_id)

        if result["return_code"] == 1:
            order.status = "paid"
        else:
            order.status = "failed"

        session.add(order) 
        session.commit() # commit changes to the database

        return {"status": "success", "data": result}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))