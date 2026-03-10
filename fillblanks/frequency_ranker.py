from functools import lru_cache
from typing import Iterable, List

from wordfreq import word_frequency


@lru_cache(maxsize=8192)
def get_frequency(word: str) -> float:
    # Missing values are treated as very low frequency by returning 0.0.
    value = word_frequency(word, "en")
    if value is None:
        return 0.0
    return float(value)


def weight_from_frequency(freq: float) -> float:
    return 1.0 / (freq + 1.0)


def build_weights(words: Iterable[str]) -> List[float]:
    return [weight_from_frequency(get_frequency(w)) for w in words]
