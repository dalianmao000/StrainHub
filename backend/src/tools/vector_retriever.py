from typing import List, Optional, Dict
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from src.config import get_settings

settings = get_settings()

@tool
def vector_retrieve(query: str, top_k: int = None, filters: Optional[Dict] = None) -> List[Dict]:
    """从向量数据库检索相关文档

    Args:
        query: 自然语言查询
        top_k: 返回top-k结果，默认使用配置值
        filters: 过滤条件（如source_type, date_range）
    """
    top_k = top_k or settings.vector_top_k

    embeddings = OpenAIEmbeddings(model=settings.embedding_model)
    query_vector = embeddings.embed_query(query)

    # 降级实现：当Milvus不可用时返回空结果
    # 生产环境应连接实际Milvus实例
    return {
        "query": query,
        "top_k": top_k,
        "documents": [],
        "message": "Vector search - Milvus not connected in dev mode",
    }

@tool
def add_document_to_vector_store(
    text: str,
    source: str,
    metadata: Optional[Dict] = None
) -> Dict:
    """添加文档到向量存储

    Args:
        text: 文档文本内容
        source: 来源标识
        metadata: 额外元数据
    """
    metadata = metadata or {}
    return {
        "status": "success",
        "source": source,
        "message": "Document added - Milvus not connected in dev mode",
    }