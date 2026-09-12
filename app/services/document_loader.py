from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from app.domain.models import SourceDocument

SUPPORTED_EXTENSIONS = {".txt", ".md", ".json", ".csv"}


class DocumentLoader:
    def load_directory(self, knowledge_dir: Path) -> list[SourceDocument]:
        documents: list[SourceDocument] = []
        if not knowledge_dir.exists():
            return documents

        for path in sorted(knowledge_dir.rglob("*")):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                documents.append(self.load_path(path))
        return documents

    def load_path(self, path: Path) -> SourceDocument:
        body = self._read_text(path)
        checksum = hashlib.sha256(body.encode("utf-8")).hexdigest()
        department = path.parent.name.replace("_", " ").lower()
        title = path.stem.replace("_", " ").replace("-", " ").title()
        tags = [department, path.suffix.lstrip(".").lower()]
        return SourceDocument(
            document_id=f"doc-{checksum[:12]}",
            title=title,
            source_path=str(path.as_posix()),
            body=body,
            department=department,
            tags=tags,
            checksum=checksum,
        )

    def load_inline(
        self,
        *,
        title: str,
        body: str,
        department: str,
        tags: list[str],
        source_path: str,
    ) -> SourceDocument:
        checksum = hashlib.sha256(body.encode("utf-8")).hexdigest()
        return SourceDocument(
            document_id=f"doc-{checksum[:12]}",
            title=title,
            source_path=source_path,
            body=body,
            department=department.lower(),
            tags=[tag.lower() for tag in tags],
            checksum=checksum,
        )

    def _read_text(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix in {".txt", ".md"}:
            return path.read_text(encoding="utf-8")
        if suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            return self._normalize_json(payload)
        if suffix == ".csv":
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                rows = []
                for index, row in enumerate(reader, start=1):
                    cells = ", ".join(f"{key}={value}" for key, value in row.items())
                    rows.append(f"Row {index}: {cells}")
                return "\n".join(rows)
        raise ValueError(f"Unsupported file extension: {suffix}")

    def _normalize_json(self, payload: object) -> str:
        if isinstance(payload, dict):
            return "\n".join(f"{key}: {value}" for key, value in payload.items())
        if isinstance(payload, list):
            rows = []
            for index, item in enumerate(payload, start=1):
                if isinstance(item, dict):
                    text = ", ".join(f"{key}={value}" for key, value in item.items())
                else:
                    text = str(item)
                rows.append(f"Record {index}: {text}")
            return "\n".join(rows)
        return str(payload)

