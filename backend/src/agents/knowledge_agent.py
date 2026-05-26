from typing import List, Dict, Optional
from langgraph import StateGraph, END
from src.agents.base import BaseAgent
from src.schemas.agents import KnowledgeState
from src.config import get_settings

settings = get_settings()

KNOWLEDGE_AGENT_PROMPT = """你是一个企业知识库智能助手，专注于知识检索和学习推荐。

你的职责：
1. 企业知识库检索 - 从向量数据库检索相关知识片段，返回带引用的结构化结果
2. 学习资料推荐 - 基于用户查询推荐相关培训材料和学习资源
3. 知识问答 - 基于检索到的内容生成准确的回答

输出要求：
- 所有输出必须包含引用溯源（citation_required=True）
- 涉及权限的知识需要根据permission_filter进行过滤
- 无法找到答案时明确标注"未找到相关知识"
"""


class KnowledgeAgent(BaseAgent):
    """企业知识库Agent"""

    def __init__(self):
        super().__init__(
            name="knowledge_agent",
            state_schema=KnowledgeState,
            system_prompt=KNOWLEDGE_AGENT_PROMPT,
        )

    def define_nodes(self, workflow: StateGraph) -> None:
        workflow.add_node("parse_query", self._parse_query)
        workflow.add_node("retrieve_chunks", self._retrieve_chunks)
        workflow.add_node("synthesize_answer", self._synthesize_answer)
        workflow.add_node("add_citations", self._add_citations)
        workflow.add_node("format_output", self._format_output)

    def define_edges(self, workflow: StateGraph) -> None:
        workflow.add_edge("parse_query", "retrieve_chunks")
        workflow.add_edge("retrieve_chunks", "synthesize_answer")
        workflow.add_edge("synthesize_answer", "add_citations")
        workflow.add_edge("add_citations", "format_output")
        workflow.add_edge("format_output", END)

    def get_entry_point(self) -> str:
        return "parse_query"

    async def _parse_query(self, state: KnowledgeState) -> KnowledgeState:
        """解析用户查询，提取检索关键词和权限过滤条件"""
        user_query = state.get("user_query", "")

        # Extract key search terms from user query
        keywords = []
        if len(user_query) > 0:
            keywords = user_query.split()

        return {
            "user_query": user_query,
            "sources": keywords,
            "permission_filter": state.get("permission_filter", {}),
            **state,
        }

    async def _retrieve_chunks(self, state: KnowledgeState) -> KnowledgeState:
        """从向量存储中检索相关知识片段"""
        # Placeholder - actual implementation uses vector_retriever tool
        # This would connect to Milvus or similar vector database
        retrieved_chunks = [
            {
                "content": "知识库内容占位符",
                "source": "enterprise_kb",
                "relevance_score": 0.85,
            }
        ]

        return {
            "retrieved_chunks": retrieved_chunks,
            **state,
        }

    async def _synthesize_answer(self, state: KnowledgeState) -> KnowledgeState:
        """基于检索到的片段合成答案"""
        retrieved_chunks = state.get("retrieved_chunks", [])
        user_query = state.get("user_query", "")

        if not retrieved_chunks:
            answer = "未找到与您查询相关的知识内容。"
        else:
            # Placeholder synthesis - actual implementation would use RAG
            chunks_text = "\n".join([c.get("content", "") for c in retrieved_chunks])
            answer = f"根据检索到的知识内容，关于'{user_query}'的回答如下：\n{chunks_text}"

        return {"answer": answer, **state}

    async def _add_citations(self, state: KnowledgeState) -> KnowledgeState:
        """为答案添加来源引用"""
        retrieved_chunks = state.get("retrieved_chunks", [])
        citations = [
            {
                "source": chunk.get("source", "Unknown"),
                "content_snippet": chunk.get("content", "")[:100],
                "relevance_score": chunk.get("relevance_score", 0.0),
            }
            for chunk in retrieved_chunks
        ]

        return {"citations": citations, **state}

    async def _format_output(self, state: KnowledgeState) -> KnowledgeState:
        """格式化最终输出"""
        output = {
            "user_query": state.get("user_query", ""),
            "answer": state.get("answer", ""),
            "citations": state.get("citations", []),
            "retrieved_chunks": state.get("retrieved_chunks", []),
            "permission_filter": state.get("permission_filter", {}),
        }

        return {"final_output": output, **state}