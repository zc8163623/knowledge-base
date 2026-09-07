import time

import uvicorn
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

def write_log1(email: str, content: str):
    while True:
        print(f"正在给{email}发送信息，str...")
        time.sleep(1)


@app.get("/send-task/{email}")
async def send_task(email: str, background_tasks: BackgroundTasks):
    print("开始执行任务...")
    background_tasks.add_task(write_log1, email, "hello")
    # time.sleep(5)
    # print("任务执行完毕...")
    return {"massage": "任务执行完成"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)