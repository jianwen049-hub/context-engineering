from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContextBudget:
    model_limit: int = 8192
    output_reserve: int = 1024
    tool_reserve: int = 512
    safety_margin: int = 256

    @property
    def packable_tokens(self) -> int:
        v = self.model_limit - self.output_reserve - self.tool_reserve - self.safety_margin
        return max(0, v)
