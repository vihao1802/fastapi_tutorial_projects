from sqlmodel import  Session, select
from fastapi.responses import JSONResponse
from time import time
from datetime import datetime
from models.order import Order
import json, hmac, hashlib, urllib.request, urllib.parse

config = {
    "app_id": 2553,
    "key1": "PcY4iZIKFCIdgZvA6ueMcMHHUbRLYjPL",
    "key2": "kLtgPl8HHhfvMuDHPwKfgfsY4Ydm9eIz",
    "endpoint": "https://sb-openapi.zalopay.vn/v2/create"
}

async def handle_zalopay_payment(new_order: Order, session):
    config["endpoint"] = "https://sb-openapi.zalopay.vn/v2/create"

    transID = new_order.id

    app_trans_id = "{}_{}".format(datetime.today().strftime("%y%m%d"), transID)
    order = {
        "app_id": config["app_id"],
        "app_trans_id": app_trans_id, # mã giao dich có định dạng yyMMdd_xxxx
        "app_user": "user123",
        "app_time": int(round(time() * 1000)), # miliseconds
        "embed_data": json.dumps({
            "redirecturl": f"http://localhost:8000/payment/order/{transID}"
        }),
        "item": json.dumps([{}]),
        "amount": new_order.total_amount,
        "description": "Payment for the order #"+str(transID),
        "bank_code": "zalopayapp",
        "callback_url": f"https://robin-pro-reliably.ngrok-free.app/order/{transID}/zalopay-callback"
    }

    # app_id|app_trans_id|app_user|amount|apptime|embed_data|item
    data = "{}|{}|{}|{}|{}|{}|{}".format(
        order["app_id"], order["app_trans_id"], order["app_user"], 
        order["amount"], order["app_time"], order["embed_data"], order["item"]
    )

    new_order.app_trans_id = app_trans_id

    session.add(new_order)
    session.commit()

    order["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()

    response = urllib.request.urlopen(url=config["endpoint"], data=urllib.parse.urlencode(order).encode())
    result = json.loads(response.read())

    print(order)

    return result

async def process_zalopay_callback(payload, order_id, session: Session):
    result = {}

    order = session.exec(select(Order).where(Order.id == order_id)).one_or_none()

    if not order:
        return JSONResponse(content={"return_code": -1, "return_message": "Order not found"})

    try:
        mac = hmac.new(config["key2"].encode(), payload.data.encode(), hashlib.sha256).hexdigest()

        # Kiểm tra callback hợp lệ
        if mac != payload.mac:
            result["return_code"] = -1
            result["return_message"] = "mac not equal"
            order.status = "failed"
        else:
            # Thanh toán thành công, cập nhật trạng thái đơn hàng
            data_json = json.loads(payload.data)
            app_trans_id = data_json["app_trans_id"]

            print(f"Update order's status to 'paid' where app_trans_id = {app_trans_id}")

            order.status = "paid"
            session.add(order)

            result["return_code"] = 1
            result["return_message"] = "success"

        session.commit()

    except Exception as e:
        session.rollback()
        result["return_code"] = 0
        result["error"] = str(e)

    return JSONResponse(content=result)


async def check_zalopay_status_service(app_trans_id: str):
    try:
        config["endpoint"] = "https://sb-openapi.zalopay.vn/v2/query"

        params = {
            "app_id": config["app_id"],
            "app_trans_id": app_trans_id
        }

        data = f"{config['app_id']}|{params['app_trans_id']}|{config['key1']}"  # app_id|app_trans_id|key1
        params["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()

        print("data", data)
        print("params", params)

        response = urllib.request.urlopen(
            url=config["endpoint"], 
            data=urllib.parse.urlencode(params).encode()
        )

        result = json.loads(response.read())
        return result

    except Exception as e:
        raise Exception(f"ZaloPay API error: {str(e)}")