from completetofelwords.pipeline import select_tokens


def test_sentence_restriction_prefers_middle_sentences():
    text = (
        "Apple begins here. "
        "Practice grows quickly in class. "
        "Students practice hard daily. "
        "London appears later. "
        "Final sentence ends."
    )
    corpus = {"practice", "grows", "quickly", "students", "hard", "daily"}

    result = select_tokens(text=text, corpus_words=corpus, blanks=2, rng=__import__("random").Random(7))

    assert len(result.selected) == 2
    for token in result.selected:
        assert token.sentence_index in {1, 2}


def test_short_text_triggers_warning_and_fallback():
    text = "Practice works. Students practice. Practice improves."
    corpus = {"practice", "works", "students", "improves"}

    result = select_tokens(text=text, corpus_words=corpus, blanks=2, rng=__import__("random").Random(3))

    assert len(result.selected) == 2
    assert any("句子数量不足" in msg for msg in result.warnings)


def test_no_false_relax_warning_when_middle_sentences_are_enough():
    text = (
        "S1 apple. "
        "S2 practice grows fast. "
        "S3 students practice daily. "
        "S4 local culture rises. "
        "S5 final note. "
        "S6 end."
    )
    corpus = {
        "practice",
        "grows",
        "fast",
        "students",
        "daily",
        "local",
        "culture",
        "rises",
        "apple",
        "final",
        "note",
        "end",
    }

    result = select_tokens(text=text, corpus_words=corpus, blanks=2, rng=__import__("random").Random(1))

    assert len(result.selected) == 2
    assert all(token.sentence_index in {1, 2, 3} for token in result.selected)
    assert not any("放宽：句段限制" in msg for msg in result.warnings)
