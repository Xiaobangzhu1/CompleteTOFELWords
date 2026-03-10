from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, List, Protocol

from completetofelwords.frequency_ranker import get_frequency
from completetofelwords.lemmatizer import normalize_lemma
from completetofelwords.tokenizer import Token


@dataclass(frozen=True)
class SelectedToken:
    surface: str
    lower: str
    lemma: str
    start: int
    end: int
    sentence_index: int


@dataclass(frozen=True)
class RuleState:
    allow_all_sentences: bool = False
    allow_proper_nouns: bool = False
    allow_duplicate_lemmas: bool = False


@dataclass(frozen=True)
class SelectionResult:
    selected: List[SelectedToken]
    warnings: List[str]


class SelectionStrategy(Protocol):
    def select(
        self,
        *,
        tokens: List[Token],
        sentence_count: int,
        corpus_words: set[str],
        blanks: int,
        rng: random.Random,
    ) -> SelectionResult:
        ...


def _is_proper_noun(token: Token) -> bool:
    return bool(token.surface and token.surface[0].isupper())


def _uniform_sample_without_replacement(
    candidates: List[SelectedToken],
    count: int,
    rng: random.Random,
) -> List[SelectedToken]:
    if count <= 0 or not candidates:
        return []
    k = min(count, len(candidates))
    return rng.sample(candidates, k)


def _allowed_sentence_indices(sentence_count: int, allow_all: bool) -> set[int]:
    if allow_all:
        return set(range(sentence_count))
    if sentence_count < 4:
        return set()
    return set(range(1, sentence_count - 2))


def _build_candidates(
    tokens: Iterable[Token],
    corpus_words: set[str],
    sentence_count: int,
    state: RuleState,
    used_positions: set[tuple[int, int]],
    used_lemmas: set[str],
) -> List[SelectedToken]:
    allowed_sentences = _allowed_sentence_indices(sentence_count, state.allow_all_sentences)

    candidates: List[SelectedToken] = []
    seen_lemmas_in_pool: set[str] = set()
    for token in tokens:
        if (token.start, token.end) in used_positions:
            continue
        if len(token.lower) < 2:
            continue
        if token.lower not in corpus_words:
            continue
        if allowed_sentences and token.sentence_index not in allowed_sentences:
            continue
        if not state.allow_all_sentences and not allowed_sentences:
            continue
        if not state.allow_proper_nouns and _is_proper_noun(token):
            continue

        lemma = normalize_lemma(token.lower)
        if not state.allow_duplicate_lemmas:
            if lemma in used_lemmas or lemma in seen_lemmas_in_pool:
                continue
            seen_lemmas_in_pool.add(lemma)

        candidates.append(
            SelectedToken(
                surface=token.surface,
                lower=token.lower,
                lemma=lemma,
                start=token.start,
                end=token.end,
                sentence_index=token.sentence_index,
            )
        )
    return candidates


class DefaultSelectionStrategy:
    """Default strategy: uniform random sampling with staged fallback rules."""

    def select(
        self,
        *,
        tokens: List[Token],
        sentence_count: int,
        corpus_words: set[str],
        blanks: int,
        rng: random.Random,
    ) -> SelectionResult:
        warnings: List[str] = []
        if sentence_count < 4:
            warnings.append("句子数量不足，已自动放宽句段限制以继续生成。")

        selected: List[SelectedToken] = []
        used_positions: set[tuple[int, int]] = set()
        used_lemmas: set[str] = set()

        states = [
            RuleState(allow_all_sentences=False, allow_proper_nouns=False, allow_duplicate_lemmas=False),
            RuleState(allow_all_sentences=True, allow_proper_nouns=False, allow_duplicate_lemmas=False),
            RuleState(allow_all_sentences=True, allow_proper_nouns=True, allow_duplicate_lemmas=False),
            RuleState(allow_all_sentences=True, allow_proper_nouns=True, allow_duplicate_lemmas=True),
        ]

        strict_candidates = _build_candidates(
            tokens=tokens,
            corpus_words=corpus_words,
            sentence_count=sentence_count,
            state=states[0],
            used_positions=used_positions,
            used_lemmas=used_lemmas,
        )
        if strict_candidates:
            ranked = sorted(
                strict_candidates,
                key=lambda item: (get_frequency(item.lower), -item.start),
                reverse=True,
            )
            fixed_count = min(3, blanks, len(ranked))
            for item in ranked[:fixed_count]:
                selected.append(item)
                used_positions.add((item.start, item.end))
                used_lemmas.add(item.lemma)

        for stage_index, state in enumerate(states):
            need = blanks - len(selected)
            if need <= 0:
                break

            if stage_index == 1:
                warnings.append("候选不足，已放宽：句段限制。")
            elif stage_index == 2:
                warnings.append("候选不足，已放宽：专有名词限制。")
            elif stage_index == 3:
                warnings.append("候选不足，已放宽：词元唯一性限制。")

            candidates = _build_candidates(
                tokens=tokens,
                corpus_words=corpus_words,
                sentence_count=sentence_count,
                state=state,
                used_positions=used_positions,
                used_lemmas=used_lemmas,
            )
            if not candidates:
                continue

            sampled = _uniform_sample_without_replacement(candidates, need, rng)

            for item in sampled:
                selected.append(item)
                used_positions.add((item.start, item.end))
                if not state.allow_duplicate_lemmas:
                    used_lemmas.add(item.lemma)

        selected = sorted(selected, key=lambda x: x.start)
        return SelectionResult(selected=selected[:blanks], warnings=warnings)
