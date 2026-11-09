from __future__ import annotations

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from context_lab.budget import ContextBudget
from context_lab.memory import MemoryStore
from context_lab.packer import PackItem, pack_items


class TestPacker(unittest.TestCase):
    def test_system_kept(self):
        b = ContextBudget(model_limit=500, output_reserve=50, tool_reserve=50, safety_margin=20)
        items = [
            PackItem(100, "system", "SYS", kind="system"),
            PackItem(10, "user", "x" * 400, kind="history"),
            PackItem(90, "user", "current question", kind="history"),
        ]
        r = pack_items(items, b)
        roles_contents = [(m["role"], m["content"]) for m in r.messages]
        self.assertIn(("system", "SYS"), roles_contents)
        self.assertTrue(r.used_tokens <= b.packable_tokens)

    def test_memory_slot(self):
        mem = MemoryStore()
        mem.ingest_turn("我叫Evans")
        mem.ingest_turn("我喜欢安静")
        self.assertIn("Evans", mem.summary_text())
        self.assertIn("安静", mem.summary_text())
        item = mem.to_pack_item()
        self.assertIsNotNone(item)
        assert item is not None
        self.assertEqual(item.kind, "memory")


if __name__ == "__main__":
    unittest.main()
