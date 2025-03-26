from sqlmodel import  Session, select
from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from time import time
from datetime import datetime
from models.order import Order
from configs.database import get_session
import json, hmac, hashlib, urllib.request, urllib.parse

async def handle_zalopay_payment(new_order: Order):
    config = {
        "app_id": 2553,
        "key1": "PcY4iZIKFCIdgZvA6ueMcMHHUbRLYjPL",
        "key2": "kLtgPl8HHhfvMuDHPwKfgfsY4Ydm9eIz",
        "endpoint": "https://sb-openapi.zalopay.vn/v2/create"
    }
    # transID = random.randrange(1000000)
    transID = new_order.id

    # print(random.randrange(1000000))

    order = {
        "app_id": config["app_id"],
        "app_trans_id": "{:%y%m%d}_{}".format(datetime.today(), transID), # mã giao dich có định dạng yyMMdd_xxxx
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

    order["mac"] = hmac.new(config['key1'].encode(), data.encode(), hashlib.sha256).hexdigest()

    response = urllib.request.urlopen(url=config["endpoint"], data=urllib.parse.urlencode(order).encode())
    result = json.loads(response.read())

    print(order)

    return result

async def handle_zalopay_callback(request: Request, order_id: int, session: Session = Depends(get_session)):
    config = {
        'key2': 'kLtgPl8HHhfvMuDHPwKfgfsY4Ydm9eIz'
    }
    result = {}

    order = session.exec(select(Order).where(Order.id == order_id)).one_or_none()

    try:
        cbdata = await request.json()
        mac = hmac.new(config['key2'].encode(), cbdata['data'].encode(), hashlib.sha256).hexdigest()

        # kiểm tra callback hợp lệ (đến từ ZaloPay server)
        if mac != cbdata['mac']:
            # callback không hợp lệ
            result['return_code'] = -1
            result['return_message'] = 'mac not equal'
            order.status = "failed"
        else:
            # thanh toán thành công, merchant cập nhật trạng thái cho đơn hàng
            dataJson = json.loads(cbdata['data'])
            print("update order's status = success where app_trans_id = " + dataJson['app_trans_id'])

            result['return_code'] = 1
            result['return_message'] = 'success'

            order.status = "paid"

        session.commit()
        session.refresh(order)

    except Exception as e:
        result['return_code'] = 0 # ZaloPay server sẽ callback lại (tối đa 3 lần)
        result['e'] = str(e)

    # thông báo kết quả cho ZaloPay server
    return JSONResponse(content=result)