import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None


@app.post("/items")
def creat_item(item: Item):
    print("creat_item后端接口被访问...")
    return item

@app.get("/read_root")
def read_root():
    print("read_root后端接口被访问...")
    print("read_root后端接口被访问...")
    print("read_root后端接口被访问...")
    return {"hello": "world"}

@app.get("/item/{item_id}")
def read_item(item_id: int, a: str):
    print("read_root后端有参数接口被访问...")
    return {"item_id": item_id, "a": a}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000, reload=True)
