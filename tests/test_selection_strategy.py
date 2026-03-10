import random

from fillblanks.pipeline import select_tokens
from fillblanks.selection_strategy import SelectedToken, SelectionResult


class FixedStrategy:
    def select(self, *, tokens, sentence_count, corpus_words, blanks, rng):
        selected = []
        for token in tokens[:blanks]:
            selected.append(
                SelectedToken(
                    surface=token.surface,
                    lower=token.lower,
                    lemma=token.lower,
                    start=token.start,
                    end=token.end,
                    sentence_index=token.sentence_index,
                )
            )
        return SelectionResult(selected=selected, warnings=["custom strategy"]) 


def test_pipeline_accepts_custom_strategy():
    text = "Practice grows. Skills improve quickly."
    corpus = {"practice", "grows", "skills", "improve", "quickly"}

    result = select_tokens(
        text=text,
        corpus_words=corpus,
        blanks=1,
        rng=random.Random(1),
        strategy=FixedStrategy(),
    )

    assert len(result.selected) == 1
    assert result.warnings == ["custom strategy"]


def test_default_strategy_picks_three_high_frequency_first(monkeypatch):
    text = (
        "Apple starts here. "
        "We discuss alpha beta gamma delta epsilon. "
        "Zeta eta theta iota kappa. "
        "Lambda mu nu xi omicron. "
        "Tail sentence one. "
        "Tail sentence two."
    )
    corpus = {
        "alpha",
        "beta",
        "gamma",
        "delta",
        "epsilon",
        "zeta",
        "eta",
        "theta",
        "iota",
        "kappa",
        "lambda",
        "mu",
        "nu",
        "xi",
        "omicron",
        "tail",
        "sentence",
        "one",
        "two",
    }

    high_freq = {"alpha": 10.0, "beta": 9.0, "gamma": 8.0}

    def fake_frequency(word: str) -> float:
        return high_freq.get(word, 0.1)

    monkeypatch.setattr("fillblanks.selection_strategy.get_frequency", fake_frequency)

    result = select_tokens(text=text, corpus_words=corpus, blanks=5, rng=random.Random(7))
    lowers = {token.lower for token in result.selected}
    assert {"alpha", "beta", "gamma"}.issubset(lowers)
