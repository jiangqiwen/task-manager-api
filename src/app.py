import logging
from fastapi import FastAPI, status, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from models.models import Task, TaskCreate, storage, TaskUpdate


# ---------- 日志配置 ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("task-api")

app = FastAPI(
    title="Task Manager API",
    description="任务管理 RESTful API",
    version="1.0.0",
)
# ---------- 异常处理器：把 422 改成 400 ----------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"输入校验失败: {request.method} {request.url.path} - {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "输入校验失败",
            "errors": exc.errors(),
        },
    )

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"请求: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"响应: {response.status_code} {request.method} {request.url.path}")
    return response

# ---------- /health ----------
@app.get("/health", tags=["健康检查"], summary="健康检查端点")
def health_check():
    return {"status": "healthy"}

# ---------- POST /tasks ----------
@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    tags=["任务"],
    summary="创建新任务",
)
def create_task(data: TaskCreate):
    task = storage.create(data)
    logger.info(f"创建任务成功: {task.id}")
    return task


# ---------- GET /tasks ----------
@app.get(
    "/tasks",
    response_model=list[Task],
    tags=["任务"],
    summary="获取所有任务",
)
def list_tasks():
    tasks = storage.list_all()
    logger.info(f"获取任务列表，共 {len(tasks)} 条")
    return tasks

# ---------- GET /tasks/{id} ----------
@app.get(
    "/tasks/{task_id}",
    response_model=Task,
    tags=["任务"],
    summary="获取单个任务",
)
def get_task(task_id: str):
    task = storage.get(task_id)
    if task is None:
        logger.warning(f"查询失败，任务不存在: {task_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 {task_id} 不存在",
        )
    logger.info(f"查询任务成功: {task_id}")
    return task

# ---------- PUT /tasks/{id} ----------
@app.put(
    "/tasks/{task_id}",
    response_model=Task,
    tags=["任务"],
    summary="更新任务",
)
def update_task(task_id: str, data: TaskUpdate):
    task = storage.update(task_id, data)
    if task is None:
        logger.warning(f"更新失败，任务不存在: {task_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 {task_id} 不存在",
        )
    logger.info(f"更新任务成功: {task_id}")
    return task


# ---------- DELETE /tasks/{id} ----------
@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["任务"],
    summary="删除任务",
)
def delete_task(task_id: str):
    ok = storage.delete(task_id)
    if not ok:
        logger.warning(f"删除失败，任务不存在: {task_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 {task_id} 不存在",
        )
    logger.info(f"删除任务成功: {task_id}")
    return None