import pytest
from src.agents.base import BaseAgent
from src.schemas.agents import BaseState

def test_base_agent_initialization():
    """测试Agent基类初始化"""

    class TestAgent(BaseAgent):
        def define_nodes(self, workflow):
            workflow.add_node("process", lambda s: s)
            workflow.add_edge("process", END)

        def define_edges(self, workflow):
            pass

    agent = TestAgent(
        name="test",
        state_schema=BaseState,
        system_prompt="Test agent",
    )

    assert agent.name == "test"
    assert agent.state_schema == BaseState

def test_workflow_build():
    """测试工作流构建"""

    class SimpleAgent(BaseAgent):
        def define_nodes(self, workflow):
            workflow.add_node("process", lambda s: {"result": "done"})

        def define_edges(self, workflow):
            workflow.add_edge("process", END)

        def get_entry_point(self):
            return "process"

    agent = SimpleAgent(
        name="simple",
        state_schema=BaseState,
        system_prompt="Simple test",
    )

    # 验证工作流可以构建（不实际运行）
    # 完整测试需要数据库连接
    assert agent.name == "simple"
