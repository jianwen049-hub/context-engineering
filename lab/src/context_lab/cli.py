from __future__ import annotations

import argparse
import json

from context_lab.budget import ContextBudget
from context_lab.memory import MemoryStore
from context_lab.packer import PackItem, pack_items


def cmd_pack() -> int:
    budget = ContextBudget(model_limit=1200, output_reserve=200, tool_reserve=100, safety_margin=50)
    mem = MemoryStore()
    mem.ingest_turn("我叫马健文")
    mem.ingest_turn("地址：上海市浦东新区演示路 1 号")
    mem.ingest_turn("我喜欢简洁的答复")

    items = [
        PackItem(100, "system", "你是助手。必须遵守用户偏好。", kind="system"),
        mem.to_pack_item(80),
        PackItem(70, "system", "检索：退款 3-7 个工作日到账。", kind="retrieval"),
        PackItem(40, "user", "你好", kind="history"),
        PackItem(40, "assistant", "您好", kind="history"),
        PackItem(40, "user", "上次那个地址还能用吗？请确认。", kind="history"),
        PackItem(10, "assistant", "（很旧的闲聊）今天天气不错" * 20, kind="history"),
    ]
    items = [i for i in items if i is not None]
    result = pack_items(items, budget)
    print(json.dumps(
        {
            "packable": budget.packable_tokens,
            "used_tokens": result.used_tokens,
            "messages": result.messages,
            "dropped": result.dropped,
            "memory": mem.summary_text(),
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="context_lab")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pack")
    args = p.parse_args(argv)
    if args.cmd == "pack":
        return cmd_pack()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
