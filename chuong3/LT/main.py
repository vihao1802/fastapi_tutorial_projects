from fastapi import FastAPI

app = FastAPI()

@app.get("/") 
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.post("/items/")  # Route xử lý POST request tại "/items/"
def create_item(item: dict):
    return {"message": "Item created", "item": item}

@app.get("/items/")
async def read_item(skip: int=10,limit: int=20):
    return {"skip": skip, "limit": limit}

@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

@app.get("/users/{user_id}/items/{item_id}")
def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item