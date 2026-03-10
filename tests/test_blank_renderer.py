import random

from completetofelwords.blank_renderer import render_blanks
from completetofelwords.selection_strategy import SelectedToken


def test_placeholder_prefix_ratio_range():
    token = SelectedToken(
        surface="photosynthesis",
        lower="photosynthesis",
        lemma="photosynthesis",
        start=0,
        end=13,
        sentence_index=0,
    )
    text = "photosynthesis"
    rendered_text, _ = render_blanks(text, [token], random.Random(1))

    # prefix is before the first whitespace and should respect [0.4, 0.6] of token length.
    prefix = rendered_text.split(" ", 1)[0]
    assert len(prefix) >= int(len(token.surface) * 0.4)
    assert len(prefix) <= int(len(token.surface) * 0.6)
