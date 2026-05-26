from typing import Literal
from langchain_openai import ChatOpenAI
from src.schemas.agents import RouterState
from src.config import get_settings

settings = get_settings()

INTENT_ROUTER_PROMPT = """你是一个意图路由器，负责识别用户输入的意图并路由到相应的专业Agent。

支持的意图类型：
- rnd: 研发相关（文献检索、实验数据分析、配方优化、工艺参数查询）
- qc: 质控相关（报告生成、合规校验、版本对比）
- support: 客服相关（产品咨询、技术支持、使用指导）
- maintenance: 设备维护相关（故障预警、维护工单、备件查询）
- knowledge: 知识管理相关（企业知识问答、学习推荐、培训资料查询）
- unknown: 无法识别的意图

分析用户输入，返回意图分类和置信度（0-1）。

示例：
输入: "帮我找一下关于鼠李糖乳杆菌的文献"
输出: {"intent": "rnd", "confidence": 0.95, "reason": "明确的文献检索需求"}

输入: "这台发酵罐昨天报警了什么"
输出: {"intent": "maintenance", "confidence": 0.88, "reason": "设备故障查询"}
"""

class IntentRouterAgent:
    """意图路由Agent"""

    def __init__(self):
        self.llm = ChatOpenAI(model=settings.gpt_model)
        self.prompt = INTENT_ROUTER_PROMPT

    async def classify(self, user_input: str) -> dict:
        """对用户输入进行意图分类"""
        response = await self.llm.ainvoke(
            f"{self.prompt}\n\n输入: {user_input}\n输出:"
        )

        content = response.content
        return self._parse_response(content)

    def _parse_response(self, content: str) -> dict:
        """解析LLM响应"""
        import json
        import re

        json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        content_lower = content.lower()

        if any(k in content_lower for k in ["文献", "专利", "检索", "实验数据", "配方"]):
            return {"intent": "rnd", "confidence": 0.8}
        elif any(k in content_lower for k in ["报告", "合规", "校验", "检测"]):
            return {"intent": "qc", "confidence": 0.8}
        elif any(k in content_lower for k in ["咨询", "支持", "使用", "帮助"]):
            return {"intent": "support", "confidence": 0.8}
        elif any(k in content_lower for k in ["设备", "维护", "故障", "预警"]):
            return {"intent": "maintenance", "confidence": 0.8}
        elif any(k in content_lower for k in ["知识", "培训", "学习", "文档"]):
            return {"intent": "knowledge", "confidence": 0.8}

        return {"intent": "unknown", "confidence": 0.5}

    def route_to_agent(self, intent: str) -> str:
        """根据意图路由到对应Agent"""
        routing = {
            "rnd": "rnd_agent",
            "qc": "qc_agent",
            "support": "support_agent",
            "maintenance": "maint_agent",
            "knowledge": "knowledge_agent",
            "unknown": "fallback",
        }
        return routing.get(intent, "fallback")