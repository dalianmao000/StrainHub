import pytest
from src.agents.intent_router import IntentRouterAgent

@pytest.fixture
def router():
    return IntentRouterAgent()

@pytest.mark.asyncio
async def test_classify_rnd_intent(router):
    """测试研发意图分类"""
    result = await router.classify("帮我找一下关于鼠李糖乳杆菌的文献")
    assert result["intent"] == "rnd"
    assert result["confidence"] > 0.7

@pytest.mark.asyncio
async def test_classify_qc_intent(router):
    """测试质控意图分类"""
    result = await router.classify("生成今天的质检报告")
    assert result["intent"] == "qc"
    assert result["confidence"] > 0.7

def test_route_to_agent(router):
    """测试路由映射"""
    assert router.route_to_agent("rnd") == "rnd_agent"
    assert router.route_to_agent("qc") == "qc_agent"
    assert router.route_to_agent("unknown") == "fallback"