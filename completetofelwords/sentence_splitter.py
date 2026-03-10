import re
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SentenceSpan:
    text: str
    start: int
    end: int
    index: int


_SENTENCE_RE = re.compile(r"[^.!?]+[.!?]?", re.MULTILINE)


def split_sentences(text: str) -> List[SentenceSpan]:
    sentences: List[SentenceSpan] = []
    idx = 0
    for match in _SENTENCE_RE.finditer(text):
        chunk = match.group(0)
        if not chunk.strip():
            continue
        sentences.append(
            SentenceSpan(
                text=chunk,
                start=match.start(),
                end=match.end(),
                index=idx,
            )
        )
        idx += 1
    return sentences
