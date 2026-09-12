from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GuardrailOutcome:
    allowed: bool
    reason: str | None = None


class PromptGuardrails:
    BLOCK_PATTERNS = (
        "ignore previous instructions",
        "reveal the system prompt",
        "show hidden prompt",
        "print api key",
        "list credentials",
        "bypass safety",
        "export secrets",
    )

    def evaluate(self, question: str) -> GuardrailOutcome:
        lowered = question.lower()
        for pattern in self.BLOCK_PATTERNS:
            if pattern in lowered:
                return GuardrailOutcome(
                    allowed=False,
                    reason="The request was blocked because it resembles prompt injection or secret exfiltration.",
                )
        return GuardrailOutcome(allowed=True)

