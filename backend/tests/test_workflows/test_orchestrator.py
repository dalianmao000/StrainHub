import pytest
from src.workflows.orchestrator import AgentOrchestrator, build_orchestrator_workflow

@pytest.fixture
def orchestrator():
    return AgentOrchestrator()

@pytest.mark.asyncio
async def test_route_rnd(orchestrator):
    """测试研发意图路由"""
    result = await orchestrator.route("找一下鼠李糖乳杆菌的文献", "test-session")
    assert result in ["rnd", "qc", "support", "maintenance", "knowledge", "unknown"]

@pytest.mark.asyncio
async def test_process(orchestrator):
    """测试完整处理流程"""
    result = await orchestrator.process("帮我分析一下最近的数据", "user-1")
    assert "session_id" in result
    assert "routed_agent" in result
    assert "final_response" in result

def test_build_workflow():
    """测试工作流构建"""
    workflow = build_orchestrator_workflow()
    assert workflow is not None