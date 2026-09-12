from functools import lru_cache

from app.core.config import AppSettings, get_settings
from app.services.rag_engine import EnterpriseKnowledgeEngine


@lru_cache(maxsize=1)
def get_engine() -> EnterpriseKnowledgeEngine:
    settings: AppSettings = get_settings()
    return EnterpriseKnowledgeEngine(settings)

