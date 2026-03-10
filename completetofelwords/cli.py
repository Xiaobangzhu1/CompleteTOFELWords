from __future__ import annotations

import argparse
import os
import random
import sys
from pathlib import Path

from completetofelwords.ai_input import (
    AIRequestConfig,
    choose_topic,
    request_deepseek_text,
    validate_ai_text,
)
from completetofelwords.blank_renderer import render_blanks
from completetofelwords.io_utils import (
    read_corpus_words,
    read_env_file,
    read_kv_config,
    read_text,
    resolve_input_path,
    resolve_output_paths,
    wrap_text_lines,
    write_text,
)
from completetofelwords.pipeline import select_tokens


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate TOEFL-style fill-in-the-blank passage.")
    parser.add_argument("--input", required=False, help="Path to the input English passage text file.")
    parser.add_argument("--corpus", required=False, help="Path to TOEFL vocabulary whitelist file.")
    parser.add_argument("--blanks", type=int, default=None, help="Target blank count. Default is 10.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible output.")
    parser.add_argument("--config", default="config.txt", help="Config file path. Default is config.txt")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive prompt mode.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output name prefix. Example: --output out -> out_blanks.txt and out_answers.txt",
    )
    parser.add_argument("--ai-provider", default=None, help="AI provider name. First version supports deepseek.")
    parser.add_argument("--ai-base-url", default=None, help="AI API base URL.")
    parser.add_argument("--ai-model", default=None, help="AI model name.")
    parser.add_argument("--ai-api-key", default=None, help="AI API key (CLI > ENV > .env).")
    parser.add_argument("--env-file", default=".env", help="Environment file path for API keys. Default is .env")
    parser.add_argument("--topic", default=None, help="Topic for AI-generated passage.")
    parser.add_argument("--ai-sentence-count", type=int, default=None, help="AI output sentence count.")
    return parser


def _prompt_with_default(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        value = input(f"{prompt}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        print("输入不能为空，请重新输入。")


def _build_interactive_args(args: argparse.Namespace) -> argparse.Namespace:
    default_corpus = args.corpus or "TOFELVob.txt"
    default_blanks = str(args.blanks) if args.blanks is not None else "10"
    print("进入交互模式，请按提示输入。")

    args.input = args.input or _prompt_with_default("请输入英文文本文件路径（--input）")
    args.corpus = args.corpus or _prompt_with_default("请输入托福词表路径（--corpus）", default_corpus)

    blanks_raw = _prompt_with_default("请输入挖空数量（--blanks）", default_blanks)
    try:
        args.blanks = int(blanks_raw)
    except ValueError as exc:
        raise ValueError("--blanks 必须是整数。") from exc

    seed_raw = _prompt_with_default("请输入随机种子（--seed，可留空）", "")
    if seed_raw == "":
        args.seed = None
    else:
        try:
            args.seed = int(seed_raw)
        except ValueError as exc:
            raise ValueError("--seed 必须是整数或留空。") from exc

    output_raw = _prompt_with_default("请输入输出前缀（--output，可留空）", "")
    args.output = output_raw or None
    return args


def _parse_bool(raw: str | None, default: bool = False) -> bool:
    if raw is None:
        return default
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return default


def _is_ai_mode(args: argparse.Namespace) -> bool:
    return bool(args.ai_provider)


def _validate_args(args: argparse.Namespace) -> None:
    if not args.corpus:
        raise ValueError("缺少 --corpus。可使用 --interactive 进入交互模式。")

    if args.blanks < 1:
        raise ValueError("--blanks 必须是大于等于 1 的整数。")

    if _is_ai_mode(args):
        if args.ai_provider.lower() != "deepseek":
            raise ValueError("当前仅支持 --ai-provider deepseek。")
        if not args.ai_api_key:
            raise ValueError("AI 模式缺少 API key。请通过 --ai-api-key、环境变量或 .env 中的 DEEPSEEK_API_KEY 提供。")
        if args.ai_sentence_count < 1:
            raise ValueError("--ai-sentence-count 必须是大于等于 1 的整数。")
    else:
        if not args.input:
            raise ValueError("缺少 --input。可使用 --interactive 进入交互模式。")
        input_path = Path(args.input)
        if not input_path.exists() or not input_path.is_file():
            raise ValueError(f"输入文件不存在或不可读：{args.input}")

    corpus_path = Path(args.corpus)
    if not corpus_path.exists() or not corpus_path.is_file():
        raise ValueError(f"词表文件不存在或不可读：{args.corpus}")


def _build_answers_content(rendered_items) -> str:
    lines = ["# Answers", "# number\toriginal\tlemma\tsentence_index\tspan"]
    for item in rendered_items:
        token = item.token
        lines.append(
            f"{item.number}\t{token.surface}\t{token.lemma}\t{token.sentence_index}\t{token.start}-{token.end}"
        )
    return "\n".join(lines) + "\n"


def _int_or_error(key: str, value: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"配置项 {key} 必须是整数：{value}") from exc


def _merge_config(args: argparse.Namespace) -> argparse.Namespace:
    config = read_kv_config(args.config)
    env_file_values = read_env_file(args.env_file)

    if not args.input:
        args.input = config.get("input")
    if not args.corpus:
        args.corpus = config.get("corpus")
    if args.output is None:
        args.output = config.get("output")

    if args.blanks is None:
        if "blanks" in config and config["blanks"] != "":
            args.blanks = _int_or_error("blanks", config["blanks"])
        else:
            args.blanks = 10

    if args.seed is None and "seed" in config and config["seed"] != "":
        args.seed = _int_or_error("seed", config["seed"])

    ai_enabled = _parse_bool(config.get("ai_enabled"), default=False)
    if not args.ai_provider:
        if "ai_provider" in config and config["ai_provider"]:
            args.ai_provider = config["ai_provider"]
        elif ai_enabled:
            args.ai_provider = "deepseek"

    if args.ai_base_url is None:
        args.ai_base_url = config.get("ai_base_url", "https://api.deepseek.com") or "https://api.deepseek.com"
    if args.ai_model is None:
        args.ai_model = config.get("ai_model", "deepseek-chat") or "deepseek-chat"

    if args.ai_api_key is None:
        args.ai_api_key = os.getenv("DEEPSEEK_API_KEY") or env_file_values.get("DEEPSEEK_API_KEY")

    if args.topic is None:
        args.topic = config.get("ai_topic")

    if args.ai_sentence_count is None:
        if "ai_sentence_count" in config and config["ai_sentence_count"]:
            args.ai_sentence_count = _int_or_error("ai_sentence_count", config["ai_sentence_count"])
        else:
            args.ai_sentence_count = 6

    return args


def _fallback_input_file_path() -> str:
    return _prompt_with_default("AI 调用失败。请输入本地英文文本文件路径以继续")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    arg_count = len(argv) if argv is not None else len(sys.argv) - 1

    try:
        args = _merge_config(args)

        # Auto-enter interactive mode only when explicitly requested.
        if args.interactive:
            args = _build_interactive_args(args)

        # Backward friendly behavior: if user passes no args and config still lacks required keys,
        # switch to interactive prompts instead of failing immediately.
        if arg_count == 0 and (not args.input or not args.corpus):
            args = _build_interactive_args(args)

        _validate_args(args)

        rng = random.Random(args.seed)
        used_ai = _is_ai_mode(args)
        if used_ai:
            topic = choose_topic(args.topic, random.SystemRandom())
            ai_cfg = AIRequestConfig(
                provider=args.ai_provider,
                base_url=args.ai_base_url,
                model=args.ai_model,
                api_key=args.ai_api_key,
                topic=topic,
                sentence_count=args.ai_sentence_count,
            )
            try:
                text = request_deepseek_text(ai_cfg)
                validate_ai_text(
                    text,
                    sentence_count=args.ai_sentence_count,
                )
            except ValueError as exc:
                print(f"[WARN] AI 调用失败，将回退本地文件输入：{exc}", file=sys.stderr)
                fallback_path = _fallback_input_file_path()
                fallback_file = Path(fallback_path)
                if not fallback_file.exists() or not fallback_file.is_file():
                    raise ValueError(f"回退文件不存在或不可读：{fallback_path}")
                text = read_text(fallback_path)
                used_ai = False
        else:
            text = read_text(args.input)

        corpus_words = read_corpus_words(args.corpus)

        result = select_tokens(text=text, corpus_words=corpus_words, blanks=args.blanks, rng=rng)

        if not result.selected:
            raise ValueError("未找到可挖空候选词，请检查输入文本或词表。")

        blank_text, rendered_items = render_blanks(text, result.selected, rng)

        blanks_path, answers_path = resolve_output_paths(args.output)
        input_path = resolve_input_path(args.output)
        write_text(input_path, wrap_text_lines(text, width=80))
        write_text(blanks_path, wrap_text_lines(blank_text, width=80))
        write_text(answers_path, _build_answers_content(rendered_items))

        for warning in result.warnings:
            print(f"[WARN] {warning}", file=sys.stderr)

        print(f"Generated blanks file: {blanks_path}")
        print(f"Generated answers file: {answers_path}")
        print(f"Selected blanks: {len(rendered_items)} / target {args.blanks}")
        return 0
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
