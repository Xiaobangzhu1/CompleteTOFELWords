from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Sequence
from urllib import error, request


_DEFAULT_TOPICS: Sequence[str] = (
    "technology",
    "education",
    "environment",
    "health",
    "culture",
    "science",
)


@dataclass(frozen=True)
class AIRequestConfig:
    provider: str
    base_url: str
    model: str
    api_key: str
    topic: str
    sentence_count: int
    timeout_seconds: float = 30.0


def choose_topic(user_topic: str | None, rng) -> str:
    if user_topic and user_topic.strip():
        return user_topic.strip()
    return rng.choice(list(_DEFAULT_TOPICS))


def build_prompt(topic: str, sentence_count: int) -> str:
    return (
        "Write an English passage for TOEFL reading practice. "
        f"Topic: {topic}. "
        f"The passage must contain exactly {sentence_count} sentences. "
        "Use a general-to-specific structure: the first sentence gives an overall introduction, "
        "and the remaining sentences provide specific supporting details. "
        "Use complete sentences ending with '.', '!' or '?'. "
        "Return plain text only, with no title and no bullet points."
    )


def request_deepseek_text(cfg: AIRequestConfig) -> str:
    endpoint = cfg.base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": cfg.model,
        "messages": [
            {
                "role": "system",
                "content": "You generate TOEFL-level English passages following strict format constraints.",
            },
            {
                "role": "user",
                "content": build_prompt(
                    topic=cfg.topic,
                    sentence_count=cfg.sentence_count,
                ),
            },
        ],
        "temperature": 0.7,
    }

    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cfg.api_key}",
    }
    req = request.Request(endpoint, data=data, headers=headers, method="POST")

    try:
        with request.urlopen(req, timeout=cfg.timeout_seconds) as resp:
            body = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ValueError(f"DeepSeek API 请求失败：HTTP {exc.code}，{detail}") from exc
    except error.URLError as exc:
        raise ValueError(f"DeepSeek API 连接失败：{exc.reason}") from exc
    except TimeoutError as exc:
        raise ValueError("DeepSeek API 请求超时。") from exc

    try:
        result = json.loads(body)
        text = result["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        raise ValueError("DeepSeek API 返回格式无法解析。") from exc

    if not text:
        raise ValueError("DeepSeek API 返回为空文本。")
    return text


def validate_ai_text(text: str, sentence_count: int) -> None:
    if any(ord(ch) > 127 for ch in text):
        raise ValueError("AI 返回文本包含非英文字符，未通过英文约束。")

    sentence_matches = re.findall(r"[^.!?]+[.!?]", text)
    if len(sentence_matches) != sentence_count:
        raise ValueError(f"AI 返回句数不符合要求：期望 {sentence_count} 句，实际 {len(sentence_matches)} 句。")
