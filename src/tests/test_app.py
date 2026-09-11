import pytest
from fastapi.testclient import TestClient
from app import app
from models.models import storage
import json

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_storage():
    """每个测试用例执行前清空内存存储，避免用例间互相影响"""
    storage._tasks.clear()
    yield
    storage._tasks.clear()


# ---------- /health ----------
def test_health():
    """健康检查返回 200 和 healthy"""
    r = client.get("/health")
    print("\n[POST /tasks] 状态码:", r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}


# ---------- POST /tasks ----------
def test_create_task_success():
    """正常创建任务，返回 201 和完整字段"""
    r = client.post("/tasks", json={
        "title": "写代码",
        "description": "实现 Task API",
        "status": "todo",
    })
    print("\n[POST /tasks] 状态码:", r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
                    
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert data["title"] == "写代码"
    assert data["description"] == "实现 Task API"
    assert data["status"] == "todo"
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_default_values():
    """只传 title，其余字段使用默认值"""
    r = client.post("/tasks", json={"title": "默认测试"})
    print("\n[POST /tasks] 状态码:", r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "todo"
    assert data["description"] == ""


def test_create_task_empty_title():
    """空 title 返回 400"""
    r = client.post("/tasks", json={"title": ""})
    print("\n[POST /tasks] 状态码:", r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    assert r.status_code == 400
    assert "errors" in r.json()

# ---------- GET /tasks{id}  ----------
def test_get_task_success():
    """创建后能查到，返回 200"""
    created = client.post("/tasks", json={"title": "查询测试"}).json()
    r = client.get(f"/tasks/{created['id']}")
    print("\n[GET /tasks{id}] 状态码:", r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]
    assert r.json()["title"] == "查询测试"


def test_get_task_404():
    """不存在的 id 返回 404"""
    r = client.get("/tasks/not-exist")
    print("\n[GET /tasks{id}] 状态码:", r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    assert r.status_code == 404
    assert "不存在" in r.json()["detail"]


# ---------- GET /tasks  ----------
def test_list_tasks_empty():
    r = client.get("/tasks")
    print("\n[GET /tasks] 状态码:", r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    assert r.status_code == 200
    assert r.json() == []

def test_list_tasks_with_data():
    """创建两个任务后，列表返回两条"""
    client.post("/tasks", json={"title": "任务1"})
    client.post("/tasks", json={"title": "任务2"})
    r = client.get("/tasks")
    print("\n[GET /tasks] 状态码:", r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    assert data[0]["title"] == "任务1"
    assert data[1]["title"] == "任务2"

# ---------- DELETE /tasks  ----------
def test_delete_task_success():
    """删除成功返回 204，之后再查返回 404"""
    created = client.post("/tasks", json={"title": "待删除"}).json()
    task_id = created["id"]
    r = client.delete(f"/tasks/{task_id}")
    print("\n[DELETE /tasks{}] 状态码:", r.status_code)
    assert r.status_code == 204
    assert r.content == b""          
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_delete_task_404():
    """删除不存在的 id 返回 404"""
    r = client.delete("/tasks/not-exist")
    print("\n[DELETE /tasks{}] 状态码:", r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    assert r.status_code == 404
    assert "不存在" in r.json()["detail"]