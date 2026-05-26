from typing import TypedDict, List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

# ==================== 基础状态定义 ====================

class BaseState(TypedDict):
    user_input: str
    session_id: str
    user_id: Optional[str]
    created_at: str

class RouterState(BaseState):
    intent: Literal["rnd", "qc", "support", "maintenance", "knowledge", "unknown"]
    confidence: float
    suggested_agent: str
    context: Dict[str, Any]

class RNDState(BaseState):
    query_embedding: Optional[List[float]]
    retrieved_documents: List[Dict]
    reranked_documents: List[Dict]
    is_data_query: bool
    executed_code: Optional[str]
    analysis_result: Optional[Dict]
    formulation_suggestions: Optional[List[Dict]]
    citations: List[Dict]
    confidence: float
    compliance_issues: List[Dict]
    final_output: Optional[Dict]
    rnd_intent: Optional[str] = None

class QCState(BaseState):
    raw_data: Optional[Dict]
    draft_report: Optional[str]
    compliance_issues: List[Dict]
    human_review_required: bool
    reviewers: List[str]
    final_pdf: Optional[bytes]
    audit_log: Dict

class SupportState(BaseState):
    language: str
    customer_profile: Optional[Dict]
    retrieved_knowledge: List[Dict]
    generated_response: str
    compliance_check: Dict
    transfer_to_human: bool
    session_summary: str

class MaintState(BaseState):
    device_id: str
    sensor_data: Optional[Dict]
    anomaly_score: float
    anomaly_pattern: Optional[str]
    failure_prediction: Optional[Dict]
    recommended_actions: List[Dict]
    work_order: Optional[Dict]
    alert_sent: bool

class KnowledgeState(BaseState):
    user_query: str
    sources: List[str]
    retrieved_chunks: List[Dict]
    answer: str
    citations: List[Dict]
    permission_filter: Dict


# ==================== 数据库模型 ====================

class AgentSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    agent_type: str
    state: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True
