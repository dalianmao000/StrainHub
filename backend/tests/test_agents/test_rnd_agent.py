import pytest
from src.agents.rnd_agent import RNDAgent
from src.schemas.agents import RNDState

@pytest.fixture
def rnd_agent():
    return RNDAgent()

@pytest.mark.asyncio
async def test_rnd_agent_initialization(rnd_agent):
    """测试R&D Agent初始化"""
    assert rnd_agent.name == "rnd_agent"
    assert rnd_agent.state_schema == RNDState

@pytest.mark.asyncio
async def test_classify_intent(rnd_agent):
    """测试意图分类"""
    state = RNDState(
        user_input="帮我找一下鼠李糖乳杆菌的文献",
        session_id="test-session",
    )
    result = await rnd_agent._classify_rnd_intent(state)
    assert result["rnd_intent"] == "literature"

def test_workflow_builds(rnd_agent):
    """测试工作流可以构建"""
    workflow = rnd_agent.build_workflow()
    assert workflow is not None