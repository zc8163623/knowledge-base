import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

@app.get("/api/data")
def get_data():
    print("请求后端接口服务")
    return {"message": "这是后端数据", "status": "success"}

#cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 允许所有源
    allow_credentials=True, # 允许客户端传递cookie
    allow_methods=["*"], # get和post都行
    allow_headers=["*"], # 请求头所有信息都行
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
