from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    openai_api_key: str
    postgresql_url: str = "postgresql://agent:agent@localhost:5432/agent_db"
    milvus_url: str = "localhost:19530"
    redis_url: str = "redis://localhost:6379"
    influxdb_url: str = "http://localhost:8086"

    # 模型配置
    gpt_model: str = "gpt-4o"
    embedding_model: str = "bge-m3"

    # RAG配置
    vector_top_k: int = 5
    rerank_top_k: int = 3

    # 安全配置
    confidence_threshold: float = 0.7
    min_citations: int = 2

    class Config:
        env_file = ".env"
        extra = "allow"

@lru_cache
def get_settings() -> Settings:
    return Settings()
