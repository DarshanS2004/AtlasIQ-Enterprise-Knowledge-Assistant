from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


def _split_csv(raw: str, fallback: list[str]) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()] if raw else fallback


@dataclass(frozen=True)
class AppSettings:
    app_name: str
    app_env: str
    log_level: str
    host: str
    port: int
    llm_provider: str
    enable_langchain_runtime: bool
    openai_api_key: str | None
    openai_chat_model: str
    ollama_base_url: str
    ollama_model: str
    knowledge_dir: Path
    storage_dir: Path
    top_k: int
    chunk_size: int
    chunk_overlap: int
    max_history_messages: int
    cors_origins: list[str]

    @property
    def registry_path(self) -> Path:
        return self.storage_dir / "registry.json"

    @property
    def uploads_dir(self) -> Path:
        return self.storage_dir / "uploads"


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    root = Path.cwd()
    knowledge_dir = Path(os.getenv("KNOWLEDGE_DIR", "data/knowledge"))
    storage_dir = Path(os.getenv("STORAGE_DIR", "storage"))
    return AppSettings(
        app_name=os.getenv("APP_NAME", "AtlasIQ Enterprise Knowledge Assistant"),
        app_env=os.getenv("APP_ENV", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        llm_provider=os.getenv("LLM_PROVIDER", "ollama").strip().lower(),
        enable_langchain_runtime=os.getenv("ENABLE_LANGCHAIN_RUNTIME", "false").lower()
        in {"1", "true", "yes", "on"},
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        knowledge_dir=(root / knowledge_dir).resolve(),
        storage_dir=(root / storage_dir).resolve(),
        top_k=int(os.getenv("TOP_K", "4")),
        chunk_size=int(os.getenv("CHUNK_SIZE", "900")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "120")),
        max_history_messages=int(os.getenv("MAX_HISTORY_MESSAGES", "6")),
        cors_origins=_split_csv(
            os.getenv("CORS_ORIGINS", ""),
            ["http://localhost:8000", "http://127.0.0.1:8000"],
        ),
    )
