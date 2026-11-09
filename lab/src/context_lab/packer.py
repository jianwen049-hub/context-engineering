from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from context_lab.budget import ContextBudget
from context_lab.tokens import measure_message


@dataclass(order=True)
class PackItem:
    priority: int
    role: str = field(compare=False)
    content: str = field(compare=False)
    kind: str = field(default="history", compare=False)

    def tokens(self) -> int:
        return measure_message(self.role, self.content)


@dataclass
class PackResult:
    messages: list[dict[str, str]]
    used_tokens: int
    dropped: list[dict[str, Any]]


def pack_items(items: list[PackItem], budget: ContextBudget) -> PackResult:
    packable = budget.packable_tokens
    # sort by priority desc; stable for ties by original order via enumerate
    indexed = sorted(enumerate(items), key=lambda ic: (-ic[1].priority, ic[0]))
    chosen: list[tuple[int, PackItem]] = []
    used = 0
    dropped: list[dict[str, Any]] = []

    for idx, item in indexed:
        need = item.tokens()
        if item.kind == "system" and need > packable:
            raise ValueError("system message exceeds packable budget")
        if used + need <= packable:
            chosen.append((idx, item))
            used += need
        else:
            dropped.append({"kind": item.kind, "priority": item.priority, "tokens": need})

    # restore chronological / original order among chosen
    chosen.sort(key=lambda ic: ic[0])
    messages = [{"role": it.role, "content": it.content, "kind": it.kind} for _, it in chosen]
    # API messages usually don't include kind — strip for "messages_for_model"
    return PackResult(
        messages=[{"role": m["role"], "content": m["content"]} for m in messages],
        used_tokens=used,
        dropped=dropped,
    )
