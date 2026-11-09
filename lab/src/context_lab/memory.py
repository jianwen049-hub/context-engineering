from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from context_lab.packer import PackItem

_ADDR = re.compile(r"地址[=:：]\s*(.+)$")
_PREF = re.compile(r"我(更)?喜欢\s*(.+)$")
_NAME = re.compile(r"我叫\s*([\w\u4e00-\u9fff]{2,12})")


@dataclass
class MemoryStore:
    slots: dict[str, str] = field(default_factory=dict)
    updated_at: dict[str, str] = field(default_factory=dict)

    def _touch(self, key: str, value: str) -> None:
        self.slots[key] = value.strip()
        self.updated_at[key] = datetime.now(timezone.utc).isoformat()

    def ingest_turn(self, text: str) -> None:
        if m := _ADDR.search(text):
            self._touch("address", m.group(1))
        if m := _PREF.search(text):
            self._touch("preference", m.group(2))
        if m := _NAME.search(text):
            self._touch("name", m.group(1))

    def summary_text(self) -> str:
        if not self.slots:
            return ""
        parts = [f"{k}={v}" for k, v in sorted(self.slots.items())]
        return "长期记忆：" + "；".join(parts)

    def to_pack_item(self, priority: int = 80) -> PackItem | None:
        text = self.summary_text()
        if not text:
            return None
        return PackItem(priority=priority, role="system", content=text, kind="memory")
