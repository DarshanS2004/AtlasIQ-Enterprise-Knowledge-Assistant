from fastapi import APIRouter, Depends, File, UploadFile

from app.api.dependencies import get_engine
from app.api.schemas import (
    ChatRequest,
    ChatResponse,
    DocumentView,
    IngestManualRequest,
    IngestResponse,
    OverviewResponse,
)
from app.services.rag_engine import EnterpriseKnowledgeEngine

router = APIRouter(prefix="/api/v1", tags=["knowledge"])


@router.get("/overview", response_model=OverviewResponse)
def get_overview(engine: EnterpriseKnowledgeEngine = Depends(get_engine)) -> OverviewResponse:
    return OverviewResponse(**engine.get_overview())


@router.get("/documents", response_model=list[DocumentView])
def list_documents(engine: EnterpriseKnowledgeEngine = Depends(get_engine)) -> list[DocumentView]:
    return [DocumentView(**record) for record in engine.list_documents()]


@router.post("/ingest/seed", response_model=IngestResponse)
def ingest_seed(engine: EnterpriseKnowledgeEngine = Depends(get_engine)) -> IngestResponse:
    return IngestResponse(**engine.bootstrap_seed_knowledge(force=False))


@router.post("/ingest/manual", response_model=IngestResponse)
def ingest_manual(
    payload: IngestManualRequest,
    engine: EnterpriseKnowledgeEngine = Depends(get_engine),
) -> IngestResponse:
    result = engine.ingest_manual_document(
        title=payload.title,
        body=payload.body,
        department=payload.department,
        tags=payload.tags,
    )
    return IngestResponse(**result)


@router.post("/ingest/files", response_model=IngestResponse)
async def ingest_files(
    files: list[UploadFile] = File(...),
    engine: EnterpriseKnowledgeEngine = Depends(get_engine),
) -> IngestResponse:
    result = await engine.ingest_uploaded_files(files)
    return IngestResponse(**result)


@router.post("/chat/query", response_model=ChatResponse)
def chat_query(
    payload: ChatRequest,
    engine: EnterpriseKnowledgeEngine = Depends(get_engine),
) -> ChatResponse:
    result = engine.answer_question(
        question=payload.question,
        session_id=payload.session_id,
        audience=payload.audience,
        department=payload.department,
        tags=payload.tags,
    )
    return ChatResponse(**result)

