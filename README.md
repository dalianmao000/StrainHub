# StrainHub AI Agent Platform

基于LangGraph的多Agent协同平台，支持研发辅助、质控合规、客服支持、设备维护、知识中枢5大业务域。

## 快速启动

```bash
# 复制环境变量模板
cp .env.example .env
# 编辑.env填入API密钥

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f agent-api
```

## 开发

```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

## 测试

```bash
pytest backend/tests -v
```