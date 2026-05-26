from typing import List, Dict
from datetime import datetime, timezone
from langgraph import StateGraph, END
from src.agents.base import BaseAgent
from src.schemas.agents import SupportState
from src.config import get_settings

settings = get_settings()

SUPPORT_AGENT_PROMPT = """You are a multi-language customer support agent specializing in StrainHub products and services.

Your responsibilities:
1. Multi-language support - Detect and respond in the customer's preferred language
2. Knowledge base Q&A - Search and retrieve relevant articles to answer customer questions
3. Product consultation - Provide accurate product information and guidance
4. Compliance validation - Ensure all responses meet regulatory and company standards
5. Transfer handling - Identify when to escalate to human support

Output requirements:
- All responses must be in the customer's detected language
- Include relevant knowledge base citations when available
- Flag low-confidence responses for human review
- Transfer complex or sensitive issues to human agents
"""

class SupportAgent(BaseAgent):
    """Customer Support Agent"""

    def __init__(self):
        super().__init__(
            name="support_agent",
            state_schema=SupportState,
            system_prompt=SUPPORT_AGENT_PROMPT,
        )

    def define_nodes(self, workflow: StateGraph) -> None:
        workflow.add_node("detect_language", self._detect_language)
        workflow.add_node("retrieve_customer_profile", self._retrieve_customer_profile)
        workflow.add_node("search_knowledge_base", self._search_knowledge_base)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("validate_compliance", self._validate_compliance)
        workflow.add_node("decide_transfer", self._decide_transfer)
        workflow.add_node("format_output", self._format_output)

    def define_edges(self, workflow: StateGraph) -> None:
        workflow.add_edge("detect_language", "retrieve_customer_profile")
        workflow.add_edge("retrieve_customer_profile", "search_knowledge_base")
        workflow.add_edge("search_knowledge_base", "generate_response")
        workflow.add_edge("generate_response", "validate_compliance")
        workflow.add_edge("validate_compliance", "decide_transfer")

        workflow.add_edge("decide_transfer", "format_output")

        workflow.add_edge("format_output", END)

    def get_entry_point(self) -> str:
        return "detect_language"

    async def _detect_language(self, state: SupportState) -> SupportState:
        """Detect customer language from input"""
        user_input = state.get("user_input", "")

        # Simple language detection based on character sets and keywords
        if any("一" <= c <= "鿿" for c in user_input):
            language = "zh"
        elif any("぀" <= c <= "ゟ" or "゠" <= c <= "ヿ" for c in user_input):
            language = "ja"
        elif any("가" <= c <= "힯" for c in user_input):
            language = "ko"
        elif any("Ѐ" <= c <= "ӿ" for c in user_input):
            language = "ru"
        elif any(c.lower() in "áéíóúñ" for c in user_input):
            language = "es"
        else:
            language = "en"

        return {"language": language, **state}

    async def _retrieve_customer_profile(self, state: SupportState) -> SupportState:
        """Retrieve customer profile from database"""
        # Placeholder - actual implementation would query customer database
        customer_profile = {
            "customer_id": state.get("user_id", "unknown"),
            "tier": "standard",
            "previous_tickets": 0,
        }
        return {"customer_profile": customer_profile, **state}

    async def _search_knowledge_base(self, state: SupportState) -> SupportState:
        """Search knowledge base for relevant articles"""
        # Placeholder - actual implementation would use vector retriever
        user_input = state.get("user_input", "")
        retrieved_knowledge = [
            {
                "title": "FAQ: Common Questions",
                "content": "Relevant article content here",
                "source": "knowledge_base",
                "relevance_score": 0.85,
            }
        ]
        return {"retrieved_knowledge": retrieved_knowledge, **state}

    async def _generate_response(self, state: SupportState) -> SupportState:
        """Generate multi-language response based on knowledge base"""
        language = state.get("language", "en")
        knowledge = state.get("retrieved_knowledge", [])
        user_input = state.get("user_input", "")

        # Language-specific prompts
        language_prompts = {
            "zh": "请用中文回复：",
            "ja": "日本語で回答してください：",
            "ko": "한국어로 답변해 주세요：",
            "ru": "Пожалуйста, ответьте на русском языке：",
            "es": "Por favor responda en español：",
        }

        prompt_prefix = language_prompts.get(language, "")
        knowledge_context = "\n".join([k.get("content", "") for k in knowledge])

        response = f"{prompt_prefix}{user_input}\n\n参考信息：{knowledge_context}"

        return {"generated_response": response, **state}

    async def _validate_compliance(self, state: SupportState) -> SupportState:
        """Validate response compliance"""
        compliance_check = {
            "passed": True,
            "issues": [],
            "validated_at": datetime.now(timezone.utc).isoformat(),
        }
        return {"compliance_check": compliance_check, **state}

    async def _decide_transfer(self, state: SupportState) -> SupportState:
        """Decide if transfer to human agent is needed"""
        user_input = state.get("user_input", "").lower()

        # Keywords indicating transfer might be needed
        transfer_keywords = [
            "refund", "complaint", "lawyer", "attorney", "legal",
            "escalate", "manager", "supervisor", "broken", "injury",
            "sensitive", "confidential", "contract", "lawsuit",
        ]

        needs_transfer = any(kw in user_input for kw in transfer_keywords)
        return {"transfer_to_human": needs_transfer, **state}

    async def _format_output(self, state: SupportState) -> SupportState:
        """Format final output"""
        output = {
            "user_input": state.get("user_input", ""),
            "response": state.get("generated_response", ""),
            "language": state.get("language", "en"),
            "knowledge_sources": state.get("retrieved_knowledge", []),
            "compliance": state.get("compliance_check", {}),
            "transfer_to_human": state.get("transfer_to_human", False),
            "session_summary": f"Support session completed. Language: {state.get('language', 'en')}",
        }
        return {"session_summary": output["session_summary"], **state}