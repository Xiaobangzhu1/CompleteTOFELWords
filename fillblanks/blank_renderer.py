from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List

from fillblanks.selection_strategy import SelectedToken


@dataclass(frozen=True)
class RenderedBlank:
    number: int
    token: SelectedToken
    placeholder: str


def _build_placeholder(surface: str, number: int, rng: random.Random) -> str:
    ratio = rng.uniform(0.2, 0.6)
    keep = max(1, math.floor(len(surface) * ratio))
    keep = min(keep, len(surface))
    prefix = surface[:keep]
    missing_count = max(0, len(surface) - keep)
    missing = " ".join("_" for _ in range(missing_count))
    if missing:
        return f"{prefix} {missing} ({number})"
    return f"{prefix} ({number})"


def render_blanks(text: str, selected: List[SelectedToken], rng: random.Random) -> tuple[str, List[RenderedBlank]]:
    ordered = sorted(selected, key=lambda item: item.start)
    rendered: List[RenderedBlank] = []

    for idx, token in enumerate(ordered, start=1):
        placeholder = _build_placeholder(token.surface, idx, rng)
        rendered.append(RenderedBlank(number=idx, token=token, placeholder=placeholder))

    output = text
    for item in sorted(rendered, key=lambda item: item.token.start, reverse=True):
        output = output[: item.token.start] + item.placeholder + output[item.token.end :]

    return output, rendered
