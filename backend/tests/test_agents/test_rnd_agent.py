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

@pytest.mark.asyncio
async def test_detect_data_query(rnd_agent):
    """测试数据查询检测"""
    state = RNDState(
        user_input="分析一下最近的pH数据",
        session_id="test-session",
    )
    result = await rnd_agent._detect_if_data_query(state)
    assert result["is_data_query"] == True

    state2 = RNDState(
        user_input="帮我找一下文献",
        session_id="test-session",
    )
    result2 = await rnd_agent._detect_if_data_query(state2)
    assert result2["is_data_query"] == False

@pytest.mark.asyncio
async def test_rerank_documents(rnd_agent):
    """测试文档重排序"""
    state = RNDState(
        user_input="测试",
        session_id="test-session",
        retrieved_documents=[
            {"source": "doc1", "score": 0.9},
            {"source": "doc2", "score": 0.8},
            {"source": "doc3", "score": 0.7},
        ],
    )
    result = await rnd_agent._rerank_documents(state)
    # Should return top 3 documents
    assert len(result["reranked_documents"]) == 3