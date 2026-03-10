from functools import lru_cache

try:
    from nltk.stem import PorterStemmer
except Exception:  # pragma: no cover - fallback for environments without nltk
    PorterStemmer = None


_STEMMER = PorterStemmer() if PorterStemmer else None


@lru_cache(maxsize=8192)
def normalize_lemma(word: str) -> str:
    lower = word.lower()
    if not lower:
        return lower
    if _STEMMER is None:
        return lower
    return _STEMMER.stem(lower)
