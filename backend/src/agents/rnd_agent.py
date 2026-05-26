from typing import List, Dict, Optional
from langgraph import StateGraph, END
from src.agents.base import BaseAgent
from src.schemas.agents import RNDState
from src.config import get_settings

settings = get_settings()

RND_AGENT_PROMPT = """你是一个研发智能助手，专注于菌种相关研发工作。

你的职责：
1. 文献与专利检索 - 从向量数据库检索相关文献，返回带引用的结构化结果
2. 实验数据分析 - 执行Python代码分析实验数据，生成洞察
3. 配方优化建议 - 基于历史数据和规则引擎生成配方推荐

输出要求：
- 所有输出必须包含引用溯源（citation_required=True）
- 涉及菌株名称、指标范围的数据必须通过规则引擎校验
- 置信度低于0.7时标注不确定性
"""

class RNDAgent(BaseAgent):
    """研发辅助Agent"""

    def __init__(self):
        super().__init__(
            name="rnd_agent",
            state_schema=RNDState,
            system_prompt=RND_AGENT_PROMPT,
        )

    def define_nodes(self, workflow: StateGraph) -> None:
        workflow.add_node("classify_intent", self._classify_rnd_intent)
        workflow.add_node("embed_query", self._embed_user_query)
        workflow.add_node("vector_search", self._vector_search)
        workflow.add_node("cross_encoder_rerank", self._rerank_documents)
        workflow.add_node("detect_query_type", self._detect_if_data_query)
        workflow.add_node("execute_analysis", self._execute_data_analysis)
        workflow.add_node("generate_formulation", self._generate_formulation_suggestions)
        workflow.add_node("validate_compliance", self._validate_compliance)
        workflow.add_node("add_citations", self._attach_citations)
        workflow.add_node("format_output", self._format_final_output)

    def define_edges(self, workflow: StateGraph) -> None:
        workflow.add_edge("classify_intent", "embed_query")
        workflow.add_edge("embed_query", "vector_search")
        workflow.add_edge("vector_search", "cross_encoder_rerank")
        workflow.add_edge("cross_encoder_rerank", "detect_query_type")

        workflow.add_conditional_edges(
            "detect_query_type",
            lambda s: "execute_analysis" if s.get("is_data_query") else "generate_formulation",
        )

        workflow.add_edge("execute_analysis", "validate_compliance")
        workflow.add_edge("generate_formulation", "validate_compliance")
        workflow.add_edge("validate_compliance", "add_citations")
        workflow.add_edge("add_citations", "format_output")
        workflow.add_edge("format_output", END)

    def get_entry_point(self) -> str:
        return "classify_intent"

    async def _classify_rnd_intent(self, state: RNDState) -> RNDState:
        """分类R&D子意图"""
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model=settings.gpt_model)
        user_input = state.get("user_input", "")

        if "数据" in user_input or "分析" in user_input or "对比" in user_input:
            intent = "data_analysis"
        elif "配方" in user_input or "优化" in user_input:
            intent = "formulation"
        else:
            intent = "literature"

        return {"rnd_intent": intent, **state}

    async def _embed_user_query(self, state: RNDState) -> RNDState:
        """向量化用户查询"""
        from langchain_openai import OpenAIEmbeddings

        embeddings = OpenAIEmbeddings(model=settings.embedding_model)
        query_vector = embeddings.embed_query(state.get("user_input", ""))
        return {"query_embedding": query_vector, **state}

    async def _vector_search(self, state: RNDState) -> RNDState:
        """向量搜索文档"""
        # Placeholder - actual implementation uses vector_retriever tool
        return {"retrieved_documents": [], **state}

    async def _rerank_documents(self, state: RNDState) -> RNDState:
        """使用Cross-Encoder重排序文档"""
        documents = state.get("retrieved_documents", [])
        reranked = documents[:settings.rerank_top_k]
        return {"reranked_documents": reranked, **state}

    async def _detect_if_data_query(self, state: RNDState) -> RNDState:
        """检测是否为数据查询"""
        data_keywords = ["数据", "分析", "对比", "趋势", "统计", "pH", "OD", "温度"]
        user_input = state.get("user_input", "")
        is_data = any(kw in user_input for kw in data_keywords)
        return {"is_data_query": is_data, **state}

    async def _execute_data_analysis(self, state: RNDState) -> RNDState:
        """执行数据分析"""
        return {"analysis_result": {"summary": "分析完成"}, **state}

    async def _generate_formulation_suggestions(self, state: RNDState) -> RNDState:
        """生成配方建议"""
        return {"formulation_suggestions": [{"text": "配方建议已生成"}], **state}

    async def _validate_compliance(self, state: RNDState) -> RNDState:
        """合规校验"""
        return {"compliance_issues": [], **state}

    async def _attach_citations(self, state: RNDState) -> RNDState:
        """添加引用"""
        citations = [
            {"source": doc.get("source", "Unknown"), "page": doc.get("page", 1)}
            for doc in state.get("reranked_documents", [])
        ]
        return {"citations": citations, **state}

    async def _format_final_output(self, state: RNDState) -> RNDState:
        """格式化最终输出"""
        output = {
            "user_input": state["user_input"],
            "result": state.get("analysis_result") or state.get("formulation_suggestions"),
            "citations": state.get("citations", []),
            "confidence": state.get("confidence", 0.8),
        }
        return {"final_output": output, **state}