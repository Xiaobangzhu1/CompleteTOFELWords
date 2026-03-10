import argparse
from fillblanks.cli import _merge_config, main
import random


def _base_args(config_path: str) -> argparse.Namespace:
    return argparse.Namespace(
        input=None,
        corpus=None,
        output=None,
        blanks=None,
        seed=None,
        config=config_path,
        ai_provider=None,
        ai_base_url=None,
        ai_model=None,
        ai_api_key=None,
        env_file=".env",
        topic=None,
        ai_sentence_count=None,
    )


def test_merge_config_reads_input_and_output(tmp_path):
    cfg = tmp_path / "config.txt"
    cfg.write_text("input=a.txt\ncorpus=b.txt\noutput=out\nblanks=8\nseed=11\n", encoding="utf-8")

    args = _base_args(str(cfg))
    merged = _merge_config(args)
    assert merged.input == "a.txt"
    assert merged.corpus == "b.txt"
    assert merged.output == "out"
    assert merged.blanks == 8
    assert merged.seed == 11


def test_merge_config_cli_overrides(tmp_path):
    cfg = tmp_path / "config.txt"
    cfg.write_text("input=a.txt\ncorpus=b.txt\noutput=out\nblanks=8\nseed=11\n", encoding="utf-8")

    args = _base_args(str(cfg))
    args.input = "cli_input.txt"
    args.corpus = "cli_corpus.txt"
    args.output = "cli_out"
    args.blanks = 5
    args.seed = 3
    merged = _merge_config(args)
    assert merged.input == "cli_input.txt"
    assert merged.corpus == "cli_corpus.txt"
    assert merged.output == "cli_out"
    assert merged.blanks == 5
    assert merged.seed == 3


def test_merge_config_env_key_over_env_file(tmp_path, monkeypatch):
    cfg = tmp_path / "config.txt"
    env_file = tmp_path / ".env"
    env_file.write_text("DEEPSEEK_API_KEY=env_file_key\n", encoding="utf-8")
    cfg.write_text("ai_provider=deepseek\n", encoding="utf-8")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "env_key")

    args = _base_args(str(cfg))
    args.env_file = str(env_file)
    merged = _merge_config(args)
    assert merged.ai_provider == "deepseek"
    assert merged.ai_api_key == "env_key"
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)


def test_merge_config_reads_key_from_env_file(tmp_path, monkeypatch):
    cfg = tmp_path / "config.txt"
    env_file = tmp_path / ".env"
    cfg.write_text("ai_provider=deepseek\n", encoding="utf-8")
    env_file.write_text("DEEPSEEK_API_KEY=env_file_key\n", encoding="utf-8")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    args = _base_args(str(cfg))
    args.env_file = str(env_file)
    merged = _merge_config(args)
    assert merged.ai_api_key == "env_file_key"


def test_main_errors_when_missing_input_and_no_config_value(tmp_path, capsys):
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("practice\n", encoding="utf-8")
    cfg = tmp_path / "config.txt"
    cfg.write_text(f"corpus={corpus}\n", encoding="utf-8")

    code = main(["--config", str(cfg), "--corpus", str(corpus), "--blanks", "1"])
    assert code == 1
    captured = capsys.readouterr()
    assert "缺少 --input" in captured.err

def test_ai_topic_selection_not_tied_to_seed(tmp_path, monkeypatch):
    corpus = tmp_path / "corpus.txt"
    corpus.write_text(
        "technology\nchanges\nrapidly\nstudents\nlearn\nmethods\n"
        "teachers\nimprove\nlessons\nschools\nadopt\nplatforms\n"
        "researchers\nreview\nresults\ncommunities\nbenefit\n",
        encoding="utf-8",
    )

    captured: dict[str, bool] = {}

    def fake_choose_topic(topic, rng):
        captured["system_random"] = isinstance(rng, random.SystemRandom)
        return "technology"

    def fake_request(_cfg):
        return (
            "Technology changes rapidly. "
            "Students learn methods. "
            "Teachers improve lessons. "
            "Schools adopt platforms. "
            "Researchers review results. "
            "Communities benefit."
        )

    monkeypatch.setattr("fillblanks.cli.choose_topic", fake_choose_topic)
    monkeypatch.setattr("fillblanks.cli.request_deepseek_text", fake_request)
    monkeypatch.setattr("fillblanks.cli.validate_ai_text", lambda text, sentence_count: None)

    code = main(
        [
            "--ai-provider",
            "deepseek",
            "--ai-api-key",
            "dummy",
            "--corpus",
            str(corpus),
            "--blanks",
            "1",
            "--seed",
            "42",
            "--output",
            str(tmp_path / "out"),
        ]
    )

    assert code == 0
    assert captured.get("system_random") is True
