"""
Pantun formatter (ABAB rhyme scheme).
Takes a codebook-encoded word sequence and lays it out into 4 lines.
Deterministic algorithm tries to pick breakpoints so that line endings rhyme
A-B-A-B using simple suffix lists from the codebook profile.

This *does not* change token order, preserving perfect invertibility.
It only chooses where to break the sequence into 4 lines.
"""
from __future__ import annotations
from typing import List, Tuple, Dict
import re

def _ends_with_any(word: str, suffixes: List[str]) -> bool:
    return any(word.endswith(suf) for suf in suffixes)

def layout_abab(words: List[str], suffix_a: List[str], suffix_b: List[str]) -> List[str]:
    n = len(words)
    if n == 0:
        return ["", "", "", ""]

    # Ideal chunk sizes (split nearly evenly)
    base = n // 4
    rem = n % 4
    target = [base + (1 if i < rem else 0) for i in range(4)]

    # Simple deterministic search: for each line, allow extending by up to 3 words
    # to satisfy rhyme requirement at the line end.
    lines = []
    idx = 0
    rhyme_targets = [suffix_a, suffix_b, suffix_a, suffix_b]
    for i in range(4):
        want = target[i]
        end = min(n, idx + want)
        # try extending up to +3 tokens to hit rhyme, but never exceed remaining tokens needed.
        best_end = end
        for extra in range(0, 4):
            cand_end = min(n, end + extra)
            if cand_end == 0: break
            last_word = words[cand_end - 1]
            if _ends_with_any(last_word, rhyme_targets[i]):
                best_end = cand_end
                break
        # final fallback: keep end
        line_words = words[idx:best_end]
        if not line_words:
            # must consume at least one word if remaining
            if idx < n:
                line_words = [words[idx]]
                best_end = idx + 1
        lines.append(" ".join(line_words))
        idx = best_end

    # If leftovers remain (rare), append to last line to preserve order.
    if idx < n:
        tail = " ".join(words[idx:])
        lines[-1] = (lines[-1] + " " + tail).strip()

    return lines
