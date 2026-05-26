# StrainHub AI Agent Platform

基于LangGraph的多Agent协同平台，支持研发辅助、质控合规、客服支持、设备维护、知识中枢5大业务域的AI智能化。

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 功能模块状态

### 已完成 ✅

| 模块 | 状态 | 描述 |
|:---|:---|:---|
| 项目骨架 | ✅ | Docker Compose编排，Python 3.11 + FastAPI |
| Agent基类 | ✅ | BaseAgent抽象类，统一工作流构建接口 |
| 状态定义 | ✅ | RNDState, QCState, SupportState, MaintState, KnowledgeState |
| Intent Router | ✅ | LLM意图分类 + 关键词fallback |
| R&D Agent | ✅ | 文献检索、数据分析、配方优化工作流 |
| 核心工具 | ✅ | 向量检索(rule_engine)、规则引擎、代码解释器 |
| 顶层编排器 | ✅ | AgentOrchestrator统一调度 |
| FastAPI入口 | ✅ | /chat, /health, /agents, /metrics接口 |
| 测试套件 | ✅ | 8个测试文件，覆盖主要模块 |

### 开发中 🔄

| 模块 | 状态 | 说明 |
|:---|:---|:---|
| QC Agent | ✅ | 质控报告生成、合规校验工作流 |
| Support Agent | ✅ | 多语言客服、知识库问答 |
| Maint. Agent | ✅ | 设备预测性维护、时序数据分析 |
| Knowledge Agent | ✅ | 企业知识中枢、学习推荐 |

### 待开发 📋

| 模块 | 优先级 | 说明 |
|:---|:---|:---|
| PostgreSQL持久化 | P1 | Agent状态、会话管理、审计日志 |
| Milvus向量库集成 | P1 | RAG检索链、生产级部署 |
| Redis缓存层 | P1 | 实时数据、热点结果缓存 |
| 前端界面 | P2 | Vue3多端适配界面 |
| 低代码组件市场 | P2 | 赋能业务部门快速搭建AI应用 |
| 多租户权限体系 | P2 | PostgreSQL RLS、行级安全 |
| 监控告警 | P2 | Prometheus + Grafana |
| CI/CD流水线 | P3 | GitLab CI/CD自动化部署 |

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                     前端呈现层 (待开发)                       │
│  PC/PAD/移动端自适应 │ 低代码画布 │ 数据看板 │ 多语言聊天界面   │
└─────────────────┬───────────────────────────────┬───────────┘
                  │ RESTful API + WebSocket        │
┌─────────────────▼───────────────────────────────▼───────────┐
│                   AI Agent 编排层 (LangGraph)                │
│  Intent Router → 状态机 → Agent调度 → 工具调用 → 结果聚合    │
└───────┬─────────┬─────────┬─────────┬─────────┬─────────────┘
        │         │         │         │         │
┌───────▼──┐ ┌────▼────┐ ┌───▼────┐ ┌──▼─────┐ ┌──▼──────┐
│ R&D Agent│ │ QC Agent│ │Support │ │Maint.  │ │Knowledge│
│   ✅     │ │   ✅    │ │   ✅   │ │   ✅   │ │   ✅   │
└───────┬──┘ └────┬────┘ └───┬────┘ └──┬─────┘ └──┬──────┘
        │         │         │         │         │
┌───────▼─────────▼─────────▼─────────▼─────────▼──────────┐
│                    工具与数据服务层                          │
│ RAG检索链 │ 规则引擎 │ 代码解释器 │ IoT/MES/ERP API │       │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼───────────────────────────────────┐
│                   存储与基础设施层                           │
│ PostgreSQL │ Milvus │ Redis │ InfluxDB                       │
│ Docker Compose / K8s                                       │
└─────────────────────────────────────────────────────────────┘
```

## 快速启动

### 环境要求

- Python 3.11+
- Docker & Docker Compose
- OpenAI API Key（或兼容API）

### 方式一：Docker部署

```bash
# 克隆项目
git clone <repository-url>
cd strainhub-agent

# 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env 填入 OPENAI_API_KEY

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f agent-api

# API访问
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_input": "帮我找一下益生菌相关文献"}'
```

### 方式二：本地开发

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 安装依赖
cd backend
pip install -r requirements.txt

# 启动服务
uvicorn src.main:app --reload --port 8000
```

## API接口

| 接口 | 方法 | 描述 |
|:---|:---|:---|
| `/chat` | POST | 与AI Agent对话 |
| `/health` | GET | 健康检查 |
| `/agents` | GET | 列出所有Agent |
| `/metrics` | GET | Prometheus指标 |
| `/sessions/{user_id}` | GET | 获取用户会话历史 |
| `/session/{session_id}` | GET | 获取特定会话详情 |

## 测试

```bash
# 运行所有测试
pytest backend/tests -v

# 运行特定测试
pytest backend/tests/test_agents/test_rnd_agent.py -v

# 带覆盖率
pytest backend/tests --cov=src --cov-report=html
```

## 项目结构

```
strainhub-agent/
├── backend/
│   ├── src/
│   │   ├── agents/           # Agent定义
│   │   │   ├── base.py       # Agent基类
│   │   │   ├── intent_router.py
│   │   │   ├── rnd_agent.py
│   │   │   ├── qc_agent.py
│   │   │   ├── support_agent.py
│   │   │   ├── maint_agent.py
│   │   │   └── knowledge_agent.py
│   │   ├── schemas/           # 数据模型
│   │   │   └── agents.py
│   │   ├── tools/             # 工具函数
│   │   │   ├── vector_retriever.py
│   │   │   ├── rule_engine.py
│   │   │   └── code_interpreter.py
│   │   ├── workflows/          # 工作流编排
│   │   │   └── orchestrator.py
│   │   ├── config.py          # 配置管理
│   │   └── main.py            # FastAPI入口
│   └── tests/                 # 测试套件
├── frontend/                   # 待开发
├── docker-compose.yml
├── LICENSE
└── README.md
```

## 技术栈

| 层级 | 技术 |
|:---|:---|
| **编排框架** | LangGraph |
| **API框架** | FastAPI + Uvicorn |
| **数据验证** | Pydantic |
| **Agent模型** | OpenAI GPT-4o |
| **向量检索** | Milvus (待集成) |
| **关系数据库** | PostgreSQL (待集成) |
| **缓存** | Redis (待集成) |
| **容器化** | Docker Compose |
| **测试** | pytest + pytest-asyncio |

## 参与贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 联系方式

MIT License