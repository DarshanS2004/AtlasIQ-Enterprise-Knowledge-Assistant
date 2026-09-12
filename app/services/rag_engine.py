from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
import hashlib
import logging
from math import sqrt
from pathlib import Path
import re

from fastapi import UploadFile

from app.core.config import AppSettings
from app.domain.models import ChunkRecord, Citation, ConversationTurn, SourceDocument
from app.services.chunking import TextChunker
from app.services.document_loader import DocumentLoader
from app.services.guardrails import PromptGuardrails
from app.services.llm_runtime import LLMRuntime
from app.services.store import RegistryStore

logger = logging.getLogger(__name__)


class EnterpriseKnowledgeEngine:
    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.loader = DocumentLoader()
        self.chunker = TextChunker(settings)
        self.guardrails = PromptGuardrails()
        self.llm_runtime = LLMRuntime(settings)
        self.store = RegistryStore(settings)

    def bootstrap_seed_knowledge(self, force: bool = False) -> dict:
        if not force and self.store.list_documents():
            return {
                "accepted_documents": 0,
                "created_chunks": 0,
                "duplicate_documents": 0,
                "runtime_mode": self.runtime_mode,
                "indexed_titles": [],
            }

        documents = self.loader.load_directory(self.settings.knowledge_dir)
        return self._ingest_documents(documents)

    def ingest_manual_document(
        self,
        *,
        title: str,
        body: str,
        department: str,
        tags: list[str],
    ) -> dict:
        document = self.loader.load_inline(
            title=title,
            body=body,
            department=department,
            tags=tags,
            source_path=f"manual://{self._slugify(title)}",
        )
        return self._ingest_documents([document])

    async def ingest_uploaded_files(self, files: list[UploadFile]) -> dict:
        documents: list[SourceDocument] = []
        for upload in files:
            suffix = Path(upload.filename or "").suffix.lower()
            destination = self.settings.uploads_dir / (upload.filename or "upload.txt")
            content = await upload.read()
            destination.write_bytes(content)
            if suffix not in {".txt", ".md", ".json", ".csv"}:
                logger.info("Skipping unsupported upload: %s", upload.filename)
                continue
            documents.append(self.loader.load_path(destination))
        return self._ingest_documents(documents)

    def list_documents(self) -> list[dict]:
        return self.store.list_documents()

    def get_overview(self) -> dict:
        documents = self.store.list_documents()
        chunk_count = len(self.store.list_chunks())
        return {
            "app_name": self.settings.app_name,
            "runtime_mode": self.runtime_mode,
            "document_count": len(documents),
            "chunk_count": chunk_count,
            "sessions_tracked": self.store.session_count(),
            "top_k": self.settings.top_k,
            "llm_enabled": self.llm_runtime.is_available(),
        }

    def answer_question(
        self,
        *,
        question: str,
        session_id: str,
        audience: str,
        department: str | None = None,
        tags: list[str] | None = None,
    ) -> dict:
        retrieval_strategy = self.runtime_mode
        runtime_note = None
        guardrail = self.guardrails.evaluate(question)
        if not guardrail.allowed:
            return {
                "answer": "I can help with knowledge retrieval, but I can’t process that request.",
                "confidence": "blocked",
                "retrieval_strategy": retrieval_strategy,
                "session_id": session_id,
                "citations": [],
                "blocked": True,
                "block_reason": guardrail.reason,
                "runtime_note": None,
            }

        citations = self._retrieve(question, department=department, tags=tags or [])
        history = self.store.get_session_history(session_id, self.settings.max_history_messages)

        if not citations:
            answer = (
                "I couldn’t find grounded evidence in the indexed knowledge base for that question. "
                "Try seeding the demo data, uploading a source document, or narrowing the scope."
            )
            confidence = "low"
        elif self.llm_runtime.is_available():
            try:
                answer = self.llm_runtime.answer(
                    question=question,
                    audience=audience,
                    citations=citations,
                    history=history,
                )
                confidence = self._confidence_label(citations)
            except Exception:  # pragma: no cover
                logger.exception("LLM answer generation failed")
                answer = self._deterministic_answer(
                    question=question,
                    citations=citations,
                    audience=audience,
                )
                confidence = "medium" if citations else "low"
                retrieval_strategy = "deterministic"
                runtime_note = (
                    f"{self.settings.llm_provider.capitalize()} runtime failed for this request, so the assistant "
                    "used the built-in grounded fallback instead. Check the provider setup, model name, "
                    "and local/runtime connectivity if you want full LLM answers."
                )
        else:
            answer = self._deterministic_answer(question=question, citations=citations, audience=audience)
            confidence = self._confidence_label(citations)

        self.store.append_session_turn(session_id, ConversationTurn(role="user", content=question))
        self.store.append_session_turn(session_id, ConversationTurn(role="assistant", content=answer))

        return {
            "answer": answer,
            "confidence": confidence,
            "retrieval_strategy": retrieval_strategy,
            "session_id": session_id,
            "citations": [citation.to_dict() for citation in citations],
            "blocked": False,
            "block_reason": None,
            "runtime_note": runtime_note,
        }

    @property
    def runtime_mode(self) -> str:
        return self.llm_runtime.provider_label()

    def _ingest_documents(self, documents: list[SourceDocument]) -> dict:
        chunks = [chunk for document in documents for chunk in self._chunk_document(document)]
        accepted_count, chunk_count, duplicate_count = self.store.upsert_documents(documents, chunks)
        indexed_titles = [document.title for document in documents][:accepted_count]
        return {
            "accepted_documents": accepted_count,
            "created_chunks": chunk_count,
            "duplicate_documents": duplicate_count,
            "runtime_mode": self.runtime_mode,
            "indexed_titles": indexed_titles,
        }

    def _chunk_document(self, document: SourceDocument) -> Iterable[ChunkRecord]:
        for index, chunk_text in enumerate(self.chunker.split(document.body), start=1):
            checksum = hashlib.sha256(f"{document.document_id}:{index}:{chunk_text}".encode("utf-8")).hexdigest()
            yield ChunkRecord(
                chunk_id=f"chunk-{checksum[:12]}",
                document_id=document.document_id,
                title=document.title,
                source_path=document.source_path,
                department=document.department,
                tags=document.tags,
                text=chunk_text,
                chunk_index=index,
                checksum=checksum,
            )

    def _retrieve(
        self,
        question: str,
        *,
        department: str | None,
        tags: list[str],
    ) -> list[Citation]:
        raw_chunks = self.store.list_chunks()
        if department:
            raw_chunks = [chunk for chunk in raw_chunks if chunk["department"] == department.lower()]
        if tags:
            tag_set = {tag.lower() for tag in tags}
            raw_chunks = [
                chunk
                for chunk in raw_chunks
                if tag_set.intersection({tag.lower() for tag in chunk.get("tags", [])})
            ]

        if not raw_chunks:
            return []

        query_vector = self._hashed_embedding(question)
        query_tokens = Counter(self._tokenize(question))
        scored = []
        for chunk in raw_chunks:
            dense_score = self._cosine_similarity(query_vector, self._hashed_embedding(chunk["text"]))
            lexical_score = self._lexical_overlap(query_tokens, Counter(self._tokenize(chunk["text"])))
            score = round((dense_score * 0.72) + (lexical_score * 0.28), 4)
            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        citations = []
        for score, chunk in scored[: self.settings.top_k]:
            excerpt = chunk["text"][:320].strip()
            citations.append(
                Citation(
                    title=chunk["title"],
                    source_path=chunk["source_path"],
                    chunk_id=chunk["chunk_id"],
                    excerpt=excerpt,
                    score=score,
                )
            )
        return citations

    def _deterministic_answer(
        self,
        *,
        question: str,
        citations: list[Citation],
        audience: str,
    ) -> str:
        evidence = "\n".join(
            f"- {citation.title}: {self._clean_excerpt(citation.excerpt)}"
            for citation in citations[:3]
        )
        return (
            f"For the {audience} audience, the strongest grounded answer to '{question}' is supported by the indexed knowledge base below.\n\n"
            f"Evidence summary:\n{evidence}\n\n"
            "Operational next step: use the cited documents as the source of truth, and if this needs a policy-grade response, "
            "validate the latest version of the referenced source before acting."
        )

    def _confidence_label(self, citations: list[Citation]) -> str:
        if not citations:
            return "low"
        average = sum(citation.score for citation in citations) / len(citations)
        if average >= 0.55:
            return "high"
        if average >= 0.28:
            return "medium"
        return "low"

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"[a-zA-Z0-9]{2,}", text.lower())

    def _hashed_embedding(self, text: str, dimensions: int = 256) -> list[float]:
        vector = [0.0] * dimensions
        for token in self._tokenize(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:2], "big") % dimensions
            sign = 1.0 if digest[2] % 2 == 0 else -1.0
            vector[index] += sign
        return vector

    @staticmethod
    def _cosine_similarity(left: list[float], right: list[float]) -> float:
        numerator = sum(a * b for a, b in zip(left, right, strict=False))
        left_norm = sqrt(sum(value * value for value in left))
        right_norm = sqrt(sum(value * value for value in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)

    @staticmethod
    def _lexical_overlap(query_tokens: Counter[str], chunk_tokens: Counter[str]) -> float:
        if not query_tokens or not chunk_tokens:
            return 0.0
        intersection = sum(min(count, chunk_tokens[token]) for token, count in query_tokens.items())
        denominator = max(sum(query_tokens.values()), 1)
        return intersection / denominator

    @staticmethod
    def _slugify(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

    @staticmethod
    def _clean_excerpt(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()
