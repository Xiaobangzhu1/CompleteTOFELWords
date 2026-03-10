import re
from dataclasses import dataclass
from typing import List

from fillblanks.sentence_splitter import SentenceSpan


@dataclass(frozen=True)
class Token:
    surface: str
    lower: str
    start: int
    end: int
    sentence_index: int


_TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


def extract_tokens(text: str, sentence_spans: List[SentenceSpan]) -> List[Token]:
    tokens: List[Token] = []
    for span in sentence_spans:
        segment = text[span.start : span.end]
        for match in _TOKEN_RE.finditer(segment):
            token_start = span.start + match.start()
            token_end = span.start + match.end()
            surface = match.group(0)
            tokens.append(
                Token(
                    surface=surface,
                    lower=surface.lower(),
                    start=token_start,
                    end=token_end,
                    sentence_index=span.index,
                )
            )
    return tokens
