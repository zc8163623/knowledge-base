import asyncio

import uvicorn
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse


app = FastAPI()

#cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 允许所有源
    allow_credentials=True, # 允许客户端传递cookie
    allow_methods=["*"], # get和post都行
    allow_headers=["*"], # 请求头所有信息都行
)

# 封装sse输出结果
task_queues = {}

class QueryRequest(BaseModel):
    query: str
    session_id: str

@app.post("/query")
async def query_by_session(query: QueryRequest, background_tasks: BackgroundTasks):
    query_query = query.query
    session_id = query.session_id
    background_tasks.add_task(long_task, session_id, query_query)
    return {"message": "任务已经开始，请耐心等待", "session_id": session_id}

# 调用工作流的长耗时方法
async def long_task(session_id: str, query: str):
    print(f"开始对{query}问题执行长耗时方法....")
    queue = asyncio.Queue()
    task_queues[session_id] = queue

    for i in range(10):
        await asyncio.sleep(1)
        msg = f"会话id{session_id}这是工作流的第{i}条执行结果\n\n"
        await queue.put(msg)

    await queue.put(None)

@app.get("/stream/{session_id}")
async def stream_by_session(session_id: str):
    print("我来问问，出答案了没？")
    return StreamingResponse(
        event_generator(session_id),
        media_type="text/event-stream"
    )

async def event_generator(session_id: str):
    while session_id not in task_queues:
        await asyncio.sleep(0.1)
    queue = task_queues[session_id]

    while True:
        msg = await queue.get()
        if msg is None:
            break

        yield f"data: {msg}\n\n"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)