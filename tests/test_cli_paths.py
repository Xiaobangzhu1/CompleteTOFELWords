from completetofelwords.io_utils import resolve_output_paths, resolve_input_path, wrap_text_lines


def test_default_output_paths():
    blanks, answers = resolve_output_paths(None, date_suffix="202603101430")
    assert str(blanks) == "blanks_202603101430.txt"
    assert str(answers) == "answers_202603101430.txt"


def test_prefixed_output_paths():
    blanks, answers = resolve_output_paths("out", date_suffix="202603101430")
    assert str(blanks) == "out_blanks_202603101430.txt"
    assert str(answers) == "out_answers_202603101430.txt"


def test_default_input_path():
    assert str(resolve_input_path(None, date_suffix="202603101430")) == "input_202603101430.txt"


def test_prefixed_input_path():
    assert str(resolve_input_path("out", date_suffix="202603101430")) == "out_input_202603101430.txt"


def test_wrap_text_lines_with_fixed_width():
    content = "word " * 30
    wrapped = wrap_text_lines(content.strip(), width=20)
    assert all(len(line) <= 20 for line in wrapped.splitlines())


def test_underscore_only_prefix_is_normalized():
    blanks, answers = resolve_output_paths("_", date_suffix="202603101430")
    assert str(blanks) == "blanks_202603101430.txt"
    assert str(answers) == "answers_202603101430.txt"
    assert str(resolve_input_path("_", date_suffix="202603101430")) == "input_202603101430.txt"


def test_directory_underscore_prefix_is_normalized():
    blanks, answers = resolve_output_paths("ioputs/_", date_suffix="202603101430")
    assert str(blanks) == "ioputs/blanks_202603101430.txt"
    assert str(answers) == "ioputs/answers_202603101430.txt"
    assert str(resolve_input_path("ioputs/_", date_suffix="202603101430")) == "ioputs/input_202603101430.txt"


def test_directory_output_endswith_slash():
    blanks, answers = resolve_output_paths("ioputs/", date_suffix="202603101430")
    assert str(blanks) == "ioputs/blanks_202603101430.txt"
    assert str(answers) == "ioputs/answers_202603101430.txt"
    assert str(resolve_input_path("ioputs/", date_suffix="202603101430")) == "ioputs/input_202603101430.txt"
