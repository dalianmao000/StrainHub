from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime

from src.workflows.orchestrator import AgentOrchestrator
from src.config import get_settings

settings = get_settings()

app = FastAPI(
    title="StrainHub AI Agent Platform",
    description="基于LangGraph的多Agent协同平台",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_input: str = Field(..., description="用户输入")
    user_id: Optional[str] = Field(None, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID，用于多轮对话")

class ChatResponse(BaseModel):
    session_id: str
    response: str
    agent: str
    metadata: Dict[str, Any]

class SessionHistoryResponse(BaseModel):
    sessions: List[Dict[str, Any]]

orchestrator = AgentOrchestrator()

@app.get("/")
async def root():
    return {"status": "ok", "service": "StrainHub AI Agent Platform"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """聊天接口"""
    session_id = request.session_id or str(uuid.uuid4())

    try:
        result = await orchestrator.process(
            user_input=request.user_input,
            user_id=request.user_id,
        )

        return ChatResponse(
            session_id=session_id,
            response=result.get("final_response", ""),
            agent=result.get("routed_agent", "unknown"),
            metadata={
                "confidence": result.get("agent_outputs", {}).get("confidence", 0),
                "citations": result.get("agent_outputs", {}).get("citations", []),
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{user_id}", response_model=SessionHistoryResponse)
async def get_sessions(user_id: str):
    """获取用户会话历史"""
    return SessionHistoryResponse(sessions=[])

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """获取特定会话详情"""
    return {"session_id": session_id, "state": {}}

@app.get("/agents")
async def list_agents():
    """列出所有可用的Agent"""
    return {
        "agents": [
            {"name": "intent_router", "description": "意图路由器"},
            {"name": "rnd_agent", "description": "研发辅助Agent"},
            {"name": "qc_agent", "description": "质控合规Agent"},
            {"name": "support_agent", "description": "客服支持Agent"},
            {"name": "maint_agent", "description": "设备维护Agent"},
            {"name": "knowledge_agent", "description": "知识中枢Agent"},
        ]
    }

@app.get("/metrics")
async def metrics():
    """Prometheus指标"""
    return {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "average_response_time_ms": 0,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)