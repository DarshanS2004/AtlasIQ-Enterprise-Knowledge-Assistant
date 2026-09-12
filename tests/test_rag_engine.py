import tempfile
import unittest
from pathlib import Path

from app.core.config import AppSettings
from app.services.rag_engine import EnterpriseKnowledgeEngine


class EnterpriseKnowledgeEngineTests(unittest.TestCase):
    def test_seed_ingestion_and_grounded_answer(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            knowledge_dir = temp_path / "knowledge"
            knowledge_dir.mkdir(parents=True, exist_ok=True)
            storage_dir = temp_path / "storage"
            storage_dir.mkdir(parents=True, exist_ok=True)

            (knowledge_dir / "incident_response.md").write_text(
                "# Incident Policy\nP1 incidents require initial customer acknowledgment within 15 minutes.",
                encoding="utf-8",
            )

            settings = AppSettings(
                app_name="test",
                app_env="test",
                log_level="INFO",
                host="127.0.0.1",
                port=8000,
                llm_provider="ollama",
                enable_langchain_runtime=False,
                openai_api_key=None,
                openai_chat_model="gpt-4o-mini",
                ollama_base_url="http://localhost:11434",
                ollama_model="llama3.2",
                knowledge_dir=knowledge_dir,
                storage_dir=storage_dir,
                top_k=3,
                chunk_size=120,
                chunk_overlap=20,
                max_history_messages=4,
                cors_origins=["http://localhost:8000"],
            )

            engine = EnterpriseKnowledgeEngine(settings)
            ingest_result = engine.bootstrap_seed_knowledge()
            answer = engine.answer_question(
                question="What is the P1 acknowledgment expectation?",
                session_id="test-session",
                audience="operations",
            )

            self.assertEqual(ingest_result["accepted_documents"], 1)
            self.assertGreaterEqual(ingest_result["created_chunks"], 1)
            self.assertIn("15 minutes", answer["answer"])
            self.assertTrue(answer["citations"])
            self.assertFalse(answer["blocked"])


if __name__ == "__main__":
    unittest.main()
