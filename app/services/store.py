from __future__ import annotations

import json
from pathlib import Path

from app.core.config import AppSettings
from app.domain.models import ChunkRecord, ConversationTurn, SourceDocument


class RegistryStore:
    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.settings.storage_dir.mkdir(parents=True, exist_ok=True)
        self.settings.uploads_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_registry()

    def _ensure_registry(self) -> None:
        if self.settings.registry_path.exists():
            return
        self.settings.registry_path.write_text(
            json.dumps({"documents": [], "chunks": [], "sessions": {}}, indent=2),
            encoding="utf-8",
        )

    def load(self) -> dict:
        return json.loads(self.settings.registry_path.read_text(encoding="utf-8-sig"))

    def save(self, payload: dict) -> None:
        self.settings.registry_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def upsert_documents(
        self,
        documents: list[SourceDocument],
        chunks: list[ChunkRecord],
    ) -> tuple[int, int, int]:
        payload = self.load()
        existing_checksums = {item["checksum"] for item in payload["documents"]}
        duplicate_count = 0
        accepted_documents: list[SourceDocument] = []

        for document in documents:
            if document.checksum in existing_checksums:
                duplicate_count += 1
                continue
            accepted_documents.append(document)
            existing_checksums.add(document.checksum)

        accepted_ids = {document.document_id for document in accepted_documents}
        accepted_chunks = [chunk for chunk in chunks if chunk.document_id in accepted_ids]

        payload["documents"].extend(document.to_dict() for document in accepted_documents)
        payload["chunks"].extend(chunk.to_dict() for chunk in accepted_chunks)
        self.save(payload)
        return len(accepted_documents), len(accepted_chunks), duplicate_count

    def list_documents(self) -> list[dict]:
        payload = self.load()
        chunk_counts: dict[str, int] = {}
        for chunk in payload["chunks"]:
            chunk_counts[chunk["document_id"]] = chunk_counts.get(chunk["document_id"], 0) + 1

        records = []
        for document in payload["documents"]:
            records.append(
                {
                    **document,
                    "chunk_count": chunk_counts.get(document["document_id"], 0),
                }
            )
        return records

    def list_chunks(self) -> list[dict]:
        return self.load()["chunks"]

    def append_session_turn(self, session_id: str, turn: ConversationTurn) -> None:
        payload = self.load()
        payload["sessions"].setdefault(session_id, []).append(turn.to_dict())
        self.save(payload)

    def get_session_history(self, session_id: str, limit: int) -> list[ConversationTurn]:
        payload = self.load()
        turns = payload["sessions"].get(session_id, [])[-limit:]
        return [ConversationTurn(**turn) for turn in turns]

    def session_count(self) -> int:
        return len(self.load()["sessions"])
