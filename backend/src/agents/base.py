from abc import ABC, abstractmethod
from typing import Type, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from src.schemas.agents import BaseState
from src.config import get_settings

settings = get_settings()

class BaseAgent(ABC):
    """所有Agent的基类"""

    def __init__(
        self,
        name: str,
        state_schema: Type[BaseState],
        system_prompt: str,
    ):
        self.name = name
        self.state_schema = state_schema
        self.system_prompt = system_prompt

    @abstractmethod
    def define_nodes(self, workflow: StateGraph) -> None:
        """定义工作流节点"""
        pass

    @abstractmethod
    def define_edges(self, workflow: StateGraph) -> None:
        """定义工作流边"""
        pass

    def build_workflow(self) -> StateGraph:
        """构建并编译工作流"""
        workflow = StateGraph(self.state_schema)
        self.define_nodes(workflow)
        self.define_edges(workflow)
        workflow.set_entry_point(self.get_entry_point())
        return workflow.compile()

    def get_entry_point(self) -> str:
        """获取入口节点名称"""
        return "process"

    async def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """执行Agent"""
        compiled = self.build_workflow()
        result = await compiled.ainvoke(state)
        return result

    async def stream(self, state: Dict[str, Any]):
        """流式执行Agent"""
        compiled = self.build_workflow()
        async for event in compiled.astream(state, stream_mode="updates"):
            yield event
