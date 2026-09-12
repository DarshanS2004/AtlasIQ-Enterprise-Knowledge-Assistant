from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str


class OverviewResponse(BaseModel):
    app_name: str
    runtime_mode: Literal["deterministic", "openai", "ollama"]
    document_count: int
    chunk_count: int
    sessions_tracked: int
    top_k: int
    llm_enabled: bool


class DocumentView(BaseModel):
    document_id: str
    title: str
    source_path: str
    department: str
    tags: list[str]
    checksum: str
    chunk_count: int
    created_at: str


class IngestManualRequest(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    body: str = Field(min_length=20, max_length=20000)
    department: str = Field(default="general", min_length=2, max_length=60)
    tags: list[str] = Field(default_factory=list)


class IngestResponse(BaseModel):
    accepted_documents: int
    created_chunks: int
    duplicate_documents: int
    runtime_mode: str
    indexed_titles: list[str]


class ChatRequest(BaseModel):
    question: str = Field(min_length=4, max_length=2000)
    session_id: str = Field(default="default")
    audience: str = Field(default="operations")
    department: str | None = None
    tags: list[str] = Field(default_factory=list)


class CitationView(BaseModel):
    title: str
    source_path: str
    chunk_id: str
    excerpt: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    confidence: str
    retrieval_strategy: str
    session_id: str
    citations: list[CitationView]
    blocked: bool = False
    block_reason: str | None = None
    runtime_note: str | None = None
