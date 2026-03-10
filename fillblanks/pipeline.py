from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List

from fillblanks.selection_strategy import DefaultSelectionStrategy, SelectedToken, SelectionStrategy
from fillblanks.sentence_splitter import split_sentences
from fillblanks.tokenizer import extract_tokens


@dataclass(frozen=True)
class PipelineResult:
    selected: List[SelectedToken]
    warnings: List[str]


def select_tokens(
    text: str,
    corpus_words: set[str],
    blanks: int,
    rng: random.Random,
    strategy: SelectionStrategy | None = None,
) -> PipelineResult:
    sentences = split_sentences(text)
    tokens = extract_tokens(text, sentences)
    picker = strategy or DefaultSelectionStrategy()
    selection = picker.select(
        tokens=tokens,
        sentence_count=len(sentences),
        corpus_words=corpus_words,
        blanks=blanks,
        rng=rng,
    )
    return PipelineResult(selected=selection.selected, warnings=selection.warnings)
