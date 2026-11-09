#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from context_lab.budget import ContextBudget
from context_lab.cli import cmd_pack
from context_lab.packer import PackItem, pack_items
from context_lab.memory import MemoryStore


def main() -> int:
    b = ContextBudget()
    assert b.packable_tokens < b.model_limit
    items = [
        PackItem(100, "system", "must keep", kind="system"),
        PackItem(1, "user", "drop me " * 200, kind="history"),
    ]
    r = pack_items(items, ContextBudget(model_limit=200, output_reserve=20, tool_reserve=20, safety_margin=10))
    assert r.messages[0]["content"] == "must keep"
    mem = MemoryStore()
    mem.ingest_turn("地址：演示路 1 号")
    assert "演示路" in mem.summary_text()
    assert cmd_pack() == 0
    # run unit tests
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        return 1
    print("smoke_check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
