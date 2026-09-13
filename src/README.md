### 安装项目所需的依赖
```shell
pip install -r requirements.txt
```

## 测试
```shell
python3 -m uvicorn app:app --reload --host 0.0.0.0 --port 8080
# 验证 get /health：
curl -i http://localhost:8080/health
#浏览器验证验证 OpenAPI 文档 http://localhost:8080/docs

# 验证 ------ post /tasks 创建 ------
curl -s -X POST http://localhost:8080/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"CREATE","description":"实现 Task API","status":"todo"}' \
  | python3 -m json.tool

curl -i -X POST http://localhost:8080/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":""}'
  
# 验证 ------ put get /tasks{id} 更新 ------
# 先创建一个
curl -s -X POST http://localhost:8080/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"原始标题","description":"原始描述"}' \
  | python3 -m json.tool --no-ensure-ascii

# 查询 
curl -s http://localhost:8080/tasks | python3 -m json.tool --no-ensure-ascii
# 根据id查询
curl -i http://localhost:8080/tasks/168c5d10-3d7d-44e1-900b-eac7865b639f
# 再修改
curl -i -X PUT http://localhost:8080/tasks/168c5d10-3d7d-44e1-900b-eac7865b639f \
  -H "Content-Type: application/json" \
  -d '{"title":"新标题","status":"in_progress"}'

# 删除
curl -i -X DELETE http://localhost:8080/tasks/<id>
# 测试运力:
pytest tests/ -v -s
```

