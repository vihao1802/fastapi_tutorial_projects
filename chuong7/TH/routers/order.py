from fastapi import APIRouter, Depends,  HTTPException
from fastapi.responses import JSONResponse
from configs.database import get_session
from models.order import Order, OrderResponse, PaymentCallback, CallbackData
from models.order_detail import OrderDetail, OrderDetailResponse
from models.item import ItemResponse, Item
from sqlmodel import  Session, select
from utils.zalo_pay import handle_zalopay_callback
import json, hmac, hashlib, urllib.request, urllib.parse

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


config = {
    'key2': 'kLtgPl8HHhfvMuDHPwKfgfsY4Ydm9eIz'
}


""" @router.post("/{order_id}/zalopay-callback",)
async def callback(request: Request, order_id: int):
    return handle_zalopay_callback(request=request,order_id=order_id) """

@router.post("/{order_id}/zalopay-callback")
async def callback(payload: CallbackData, order_id: str, session: Session = Depends(get_session)):
    result = {}

    order = session.exec(select(Order).where(Order.id == order_id)).one_or_none()

    try:
        mac = hmac.new(config["key2"].encode(), payload.data.encode(), hashlib.sha256).hexdigest()

        # Kiểm tra callback hợp lệ (đến từ ZaloPay server)
        if mac != payload.mac:
            result["return_code"] = -1
            result["return_message"] = "mac not equal"
            order.status = "failed"

        else:
            # Thanh toán thành công, cập nhật trạng thái đơn hàng
            data_json = json.loads(payload.data)
            app_trans_id = data_json["app_trans_id"]

            print(f"update order's status = success where app_trans_id = {app_trans_id}")

            order.status = "paid"
            session.add(order)

            # Lưu callback vào DB
            new_callback = PaymentCallback(
                app_trans_id=app_trans_id,
                status="success",
                raw_data=payload.data
            )
            session.add(new_callback)

            result["return_code"] = 1
            result["return_message"] = "success"

        session.commit()

    except Exception as e:
        result["return_code"] = 0  # ZaloPay server sẽ callback lại (tối đa 3 lần)
        result["error"] = str(e)

    return JSONResponse(content=result)