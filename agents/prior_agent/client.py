from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from openai import APIStatusError, OpenAI


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text().splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        key, value = text.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def env_with_file(root: Path) -> dict[str, str]:
    merged = dict(os.environ)
    merged.update(load_env(root / ".env"))
    return merged


class OpusClient:
    def __init__(self, root: Path, env: dict[str, str] | None = None):
        self.env = env if env is not None else env_with_file(root)
        base = self.env.get("LLM_BASE_URL", "").rstrip("/")
        key = self.env.get("LLM_API_KEY", "")
        if not base or not key:
            raise ValueError("missing_llm_credentials")
        self.model = self.env.get("LLM_MODEL_OPUS", "claude-opus-5.5")
        timeout = float(self.env.get("LLM_TIMEOUT_SECONDS", "300"))
        max_tokens = int(self.env.get("LLM_MAX_OUTPUT_TOKENS", "8192"))
        max_tokens = min(max(max_tokens, 256), 8192)
        token_field = self.env.get("LLM_TOKEN_FIELD", "max_tokens")
        self.max_tokens = max_tokens
        self.token_field = token_field
        self.retries = int(self.env.get("LLM_RETRIES", "6"))
        self.client = OpenAI(base_url=base, api_key=key, timeout=timeout)

    def complete(self, messages: list[dict[str, str]]) -> str:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        kwargs[self.token_field] = self.max_tokens
        last_error: Exception | None = None
        for attempt in range(max(self.retries, 1)):
            try:
                response = self.client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("empty_model_response")
                return content
            except APIStatusError as exc:
                last_error = exc
                if exc.status_code not in {400, 429, 500, 502, 503, 504}:
                    raise
                time.sleep(min(2 ** attempt, 30))
            except Exception as exc:
                last_error = exc
                time.sleep(min(2 ** attempt, 30))
        assert last_error is not None
        raise last_error


def parse_action(text: str) -> dict:
    body = text.strip()
    if body.startswith("```"):
        lines = body.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        body = "\n".join(lines).strip()
    start = body.find("{")
    end = body.rfind("}")
    if start < 0 or end < start:
        raise ValueError("action_json_missing")
    data = json.loads(body[start : end + 1])
    if not isinstance(data, dict):
        raise ValueError("action_not_object")
    return data
