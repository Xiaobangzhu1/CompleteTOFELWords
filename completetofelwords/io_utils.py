from datetime import datetime
from pathlib import Path
import textwrap
from typing import Tuple


def read_kv_config(path: str) -> dict[str, str]:
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        return {}

    content = read_text(path)
    config: dict[str, str] = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip().lower()
        value = value.strip()
        if key:
            config[key] = value
    return config


def read_env_file(path: str) -> dict[str, str]:
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        return {}

    content = read_text(path)
    env_map: dict[str, str] = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith('"') and value.endswith('"') and len(value) >= 2:
            value = value[1:-1]
        if key:
            env_map[key] = value
    return env_map


def read_text(path: str) -> str:
    file_path = Path(path)
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"文件编码读取失败（请使用 UTF-8）：{path}") from exc


def read_corpus_words(path: str) -> set[str]:
    content = read_text(path)
    words = {line.strip().lower() for line in content.splitlines() if line.strip()}
    if not words:
        raise ValueError("词表文件为空，无法构建候选白名单。")
    return words


def current_date_suffix() -> str:
    return datetime.now().strftime("%Y%m%d%H%M")


def _normalize_output_prefix(output: str | None) -> tuple[str | None, Path]:
    if not output:
        return None, Path(".")

    if output.endswith("/") or output.endswith("\\"):
        directory = Path(output.rstrip("/\\"))
        if str(directory) in {"", "."}:
            return None, Path(".")
        return None, directory

    raw = Path(output)
    parent = raw.parent
    if raw.suffix:
        stem_name = raw.with_suffix("").name
    else:
        stem_name = raw.name

    normalized = stem_name.lstrip("_")
    if not normalized:
        return None, parent
    return normalized, parent


def resolve_output_paths(output: str | None, date_suffix: str | None = None) -> Tuple[Path, Path]:
    suffix = date_suffix or current_date_suffix()
    prefix, parent = _normalize_output_prefix(output)
    if prefix:
        return parent / f"{prefix}_blanks_{suffix}.txt", parent / f"{prefix}_answers_{suffix}.txt"
    return parent / f"blanks_{suffix}.txt", parent / f"answers_{suffix}.txt"


def resolve_input_path(output: str | None, date_suffix: str | None = None) -> Path:
    suffix = date_suffix or current_date_suffix()
    prefix, parent = _normalize_output_prefix(output)
    if prefix:
        return parent / f"{prefix}_input_{suffix}.txt"
    return parent / f"input_{suffix}.txt"


def resolve_ai_input_path(output: str | None, date_suffix: str | None = None) -> Path:
    return resolve_input_path(output, date_suffix)


def wrap_text_lines(content: str, width: int = 80) -> str:
    if width < 1:
        return content

    wrapped_lines: list[str] = []
    for line in content.splitlines():
        if not line.strip():
            wrapped_lines.append("")
            continue
        wrapped_lines.extend(textwrap.wrap(line, width=width, break_long_words=False, break_on_hyphens=False))

    if content.endswith("\n"):
        return "\n".join(wrapped_lines) + "\n"
    return "\n".join(wrapped_lines)


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
