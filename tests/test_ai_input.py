from completetofelwords.ai_input import validate_ai_text


def test_validate_ai_text_ok():
    text = (
        "Technology changes quickly. "
        "Digital tools improve classroom access. "
        "Teachers can track student progress more precisely. "
        "Students review lessons with interactive platforms. "
        "Schools also reduce delays in feedback cycles. "
        "As a result, learning outcomes become more consistent."
    )
    validate_ai_text(text, sentence_count=6)


def test_validate_ai_text_sentence_mismatch():
    text = "One sentence only."
    try:
        validate_ai_text(text, sentence_count=6)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "句数" in str(exc)
