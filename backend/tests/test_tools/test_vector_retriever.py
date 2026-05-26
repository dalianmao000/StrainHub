import pytest
from src.tools.vector_retriever import vector_retrieve, add_document_to_vector_store

def test_vector_retrieve():
    """测试向量检索（降级模式）"""
    result = vector_retrieve.invoke({
        "query": "测试查询",
        "top_k": 3,
    })
    assert "documents" in result or "query" in result

def test_add_document():
    """测试添加文档"""
    result = add_document_to_vector_store.invoke({
        "text": "测试文本",
        "source": "test",
    })
    assert result["status"] == "success"