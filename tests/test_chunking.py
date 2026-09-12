import unittest

from app.core.config import AppSettings
from app.services.chunking import TextChunker


class TextChunkerTests(unittest.TestCase):
    def test_manual_split_creates_multiple_chunks_for_large_input(self) -> None:
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
            knowledge_dir=__import__("pathlib").Path("."),
            storage_dir=__import__("pathlib").Path("."),
            top_k=4,
            chunk_size=90,
            chunk_overlap=20,
            max_history_messages=6,
            cors_origins=["http://localhost:8000"],
        )
        chunker = TextChunker(settings)
        text = " ".join(
            [
                "AtlasIQ keeps enterprise knowledge available for incident response and onboarding."
                for _ in range(8)
            ]
        )

        chunks = chunker._manual_split(text)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) > 0 for chunk in chunks))


if __name__ == "__main__":
    unittest.main()
