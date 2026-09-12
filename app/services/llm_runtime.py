from __future__ import annotations

import json
from textwrap import dedent
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import AppSettings
from app.domain.models import Citation, ConversationTurn


class LLMRuntime:
    def __init__(self, settings: AppSettings):
        self.settings = settings

    def is_available(self) -> bool:
        provider = self.settings.llm_provider
        if provider == "ollama":
            return bool(self.settings.ollama_base_url and self.settings.ollama_model)
        if provider == "openai":
            if not self.settings.enable_langchain_runtime or not self.settings.openai_api_key:
                return False
            try:
                import langchain  # noqa: F401
                import langchain_openai  # noqa: F401
            except ImportError:
                return False
            return True
        return False

    def provider_label(self) -> str:
        return self.settings.llm_provider if self.is_available() else "deterministic"

    def answer(
        self,
        *,
        question: str,
        audience: str,
        citations: list[Citation],
        history: list[ConversationTurn],
    ) -> str:
        if self.settings.llm_provider == "ollama":
            return self._answer_with_ollama(
                question=question,
                audience=audience,
                citations=citations,
                history=history,
            )
        if self.settings.llm_provider == "openai":
            return self._answer_with_openai(
                question=question,
                audience=audience,
                citations=citations,
                history=history,
            )
        raise RuntimeError(f"Unsupported LLM provider: {self.settings.llm_provider}")

    def _answer_with_openai(
        self,
        *,
        question: str,
        audience: str,
        citations: list[Citation],
        history: list[ConversationTurn],
    ) -> str:
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            api_key=self.settings.openai_api_key,
            model=self.settings.openai_chat_model,
            temperature=0.1,
        )
        context = "\n\n".join(
            f"[{index}] {citation.title}\nSource: {citation.source_path}\nExcerpt: {citation.excerpt}"
            for index, citation in enumerate(citations, start=1)
        )
        messages = [
            SystemMessage(
                content=dedent(
                    """
                    You are AtlasIQ, an enterprise knowledge assistant.
                    Answer only from the provided retrieval context.
                    If the evidence is thin or incomplete, say so clearly.
                    Keep the response crisp, actionable, and suitable for an enterprise audience.
                    """
                ).strip()
            )
        ]

        for turn in history[-self.settings.max_history_messages :]:
            if turn.role == "user":
                messages.append(HumanMessage(content=turn.content))
            else:
                messages.append(AIMessage(content=turn.content))

        messages.append(
            HumanMessage(
                content=dedent(
                    f"""
                    Audience: {audience}
                    User question: {question}

                    Retrieval context:
                    {context}

                    Produce an answer with three short parts:
                    1. Direct answer
                    2. What the evidence says
                    3. Operational next step
                    """
                ).strip()
            )
        )
        response = llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)

    def _answer_with_ollama(
        self,
        *,
        question: str,
        audience: str,
        citations: list[Citation],
        history: list[ConversationTurn],
    ) -> str:
        context = "\n\n".join(
            f"[{index}] {citation.title}\nSource: {citation.source_path}\nExcerpt: {citation.excerpt}"
            for index, citation in enumerate(citations, start=1)
        )

        messages = [
            {
                "role": "system",
                "content": dedent(
                    """
                    You are AtlasIQ, an enterprise knowledge assistant.
                    Answer only from the provided retrieval context.
                    If the evidence is incomplete, say so clearly.
                    Keep the response concise, operational, and suitable for enterprise use.
                    """
                ).strip(),
            }
        ]

        for turn in history[-self.settings.max_history_messages :]:
            messages.append({"role": turn.role, "content": turn.content})

        messages.append(
            {
                "role": "user",
                "content": dedent(
                    f"""
                    Audience: {audience}
                    User question: {question}

                    Retrieval context:
                    {context}

                    Produce an answer with three short parts:
                    1. Direct answer
                    2. What the evidence says
                    3. Operational next step
                    """
                ).strip(),
            }
        )

        payload = json.dumps(
            {
                "model": self.settings.ollama_model,
                "messages": messages,
                "stream": False,
            }
        ).encode("utf-8")
        request = Request(
            url=f"{self.settings.ollama_base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=120) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:  # pragma: no cover
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Ollama returned HTTP {exc.code}: {detail}") from exc
        except URLError as exc:  # pragma: no cover
            raise RuntimeError(
                "Could not reach Ollama. Make sure Ollama is installed and running on localhost:11434."
            ) from exc

        return body.get("message", {}).get("content", "").strip()

