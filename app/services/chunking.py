from __future__ import annotations

from collections.abc import Iterable
import re

from app.core.config import AppSettings


class TextChunker:
    def __init__(self, settings: AppSettings):
        self.settings = settings

    def split(self, text: str) -> list[str]:
        normalized = re.sub(r"\s+\n", "\n", text.strip())
        if not normalized:
            return []

        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.settings.chunk_size,
                chunk_overlap=self.settings.chunk_overlap,
                separators=["\n\n", "\n", ". ", " "],
            )
            chunks = [chunk.strip() for chunk in splitter.split_text(normalized) if chunk.strip()]
            if chunks:
                return chunks
        except ImportError:
            pass

        return self._manual_split(normalized)

    def _manual_split(self, text: str) -> list[str]:
        chunks: list[str] = []
        buffer = ""

        for segment in self._segments(text):
            candidate = f"{buffer} {segment}".strip() if buffer else segment
            if len(candidate) <= self.settings.chunk_size:
                buffer = candidate
                continue

            if buffer:
                chunks.append(buffer)
            overlap = buffer[-self.settings.chunk_overlap :] if buffer else ""
            buffer = f"{overlap} {segment}".strip()

        if buffer:
            chunks.append(buffer)

        return chunks

    @staticmethod
    def _segments(text: str) -> Iterable[str]:
        for piece in re.split(r"\n{2,}|(?<=[.!?])\s+", text):
            cleaned = piece.strip()
            if cleaned:
                yield cleaned

