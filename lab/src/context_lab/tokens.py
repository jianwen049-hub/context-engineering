from __future__ import annotations

import re

_CJK = re.compile(r"[\u4e00-\u9fff]")


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    cjk = len(_CJK.findall(text))
    rest = _CJK.sub(" ", text)
    words = [w for w in re.split(r"\s+", rest.strip()) if w]
    return max(1, cjk + int(round(len(words) * 1.3)))


def measure_message(role: str, content: str, framing: int = 4) -> int:
    return estimate_tokens(content) + framing + estimate_tokens(role)
