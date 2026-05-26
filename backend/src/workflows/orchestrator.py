from typing import Literal, Dict, Any
from langgraph import StateGraph, END
from src.schemas.agents import BaseState
from src.agents.intent_router import IntentRouterAgent
from src.agents.rnd_agent import RNDAgent
from src.config import get_settings

settings = get_settings()

class OrchestratorState(BaseState):
    routed_agent: Literal["rnd", "qc", "support", "maint", "knowledge", "fallback"]
    agent_outputs: Dict[str, Any]
    final_response: str

class AgentOrchestrator:
    """顶层Agent编排器"""

    def __init__(self):
        self.router = IntentRouterAgent()
        self.agents = {
            "rnd": RNDAgent(),
        }

    async def route(self, user_input: str, session_id: str) -> str:
        """路由用户输入到对应Agent"""
        classification = await self.router.classify(user_input)
        return classification["intent"]

    async def execute_agent(self, agent_name: str, state: Dict) -> Dict:
        """执行指定Agent"""
        if agent_name not in self.agents:
            return {"error": f"Agent {agent_name} not found"}

        agent = self.agents[agent_name]
        result = await agent.invoke(state)
        return result

    async def process(self, user_input: str, user_id: str = None) -> Dict[str, Any]:
        """处理用户请求的完整流程"""
        import uuid

        session_id = str(uuid.uuid4())
        state = {
            "user_input": user_input,
            "session_id": session_id,
            "user_id": user_id,
        }

        # Step 1: 路由
        routed_agent = await self.route(user_input, session_id)
        state["routed_agent"] = routed_agent

        # Step 2: 执行对应Agent
        if routed_agent in self.agents:
            agent_output = await self.execute_agent(routed_agent, state)
            state["agent_outputs"] = {routed_agent: agent_output}
            state["final_response"] = self._format_response(agent_output)
        else:
            state["agent_outputs"] = {}
            state["final_response"] = "抱歉，我无法处理您的请求。请尝试重新描述您的问题。"

        return state

    def _format_response(self, output: Dict) -> str:
        """格式化Agent响应为用户友好格式"""
        if not output:
            return "处理完成，无结果返回。"

        if isinstance(output, dict):
            if "final_output" in output:
                return str(output["final_output"])
            return str(output)

        return str(output)


def build_orchestrator_workflow():
    """构建编排工作流（LangGraph方式）"""
    workflow = StateGraph(OrchestratorState)

    async def _route_node(state: OrchestratorState) -> OrchestratorState:
        router = IntentRouterAgent()
        classification = await router.classify(state["user_input"])
        return {"routed_agent": classification["intent"], **state}

    async def _rnd_agent_node(state: OrchestratorState) -> OrchestratorState:
        agent = RNDAgent()
        output = await agent.invoke(state)
        return {"agent_outputs": {"rnd": output}, **state}

    async def _aggregate_node(state: OrchestratorState) -> OrchestratorState:
        orchestrator = AgentOrchestrator()
        response = orchestrator._format_response(state.get("agent_outputs", {}))
        return {"final_response": response, **state}

    # 添加节点
    workflow.add_node("route", _route_node)
    workflow.add_node("rnd_agent", _rnd_agent_node)
    workflow.add_node("aggregate", _aggregate_node)

    # 添加边
    workflow.add_edge("route", "rnd_agent")
    workflow.add_edge("rnd_agent", "aggregate")
    workflow.add_edge("aggregate", END)

    workflow.set_entry_point("route")
    return workflow.compile()