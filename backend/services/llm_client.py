"""
Universal LLM client — works with OpenAI, Anthropic, Groq, Google Gemini,
Mistral, Together AI, or any OpenAI-compatible endpoint.

Configure via .env:
  LLM_PROVIDER   = openai | anthropic | groq | google | mistral | together | custom
  LLM_API_KEY    = sk-...
  LLM_MODEL      = (optional — provider default used if omitted)
  LLM_BASE_URL   = (optional — overrides provider default)
  LLM_TIMEOUT    = 60
  LLM_ENABLED    = true

No third-party AI SDK required — uses urllib only.
"""

import json
import logging
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower().strip()
LLM_API_KEY  = os.getenv("LLM_API_KEY",  "").strip()
LLM_MODEL    = os.getenv("LLM_MODEL",    "").strip()
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "").strip()
LLM_TIMEOUT  = int(os.getenv("LLM_TIMEOUT", "60"))
LLM_ENABLED  = os.getenv("LLM_ENABLED", "true").lower() not in ("false", "0", "no")

# ── Provider registry ──────────────────────────────────────────────────────────
# format: "openai" = /v1/chat/completions  |  "anthropic" = /v1/messages
_PROVIDERS: Dict[str, Dict[str, str]] = {
    "openai":    {
        "base_url": "https://api.openai.com/v1",
        "model":    "gpt-4o-mini",
        "format":   "openai",
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com",
        "model":    "claude-haiku-4-5-20251001",
        "format":   "anthropic",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model":    "llama-3.3-70b-versatile",
        "format":   "openai",
    },
    "google": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model":    "gemini-2.0-flash",
        "format":   "openai",
    },
    "mistral": {
        "base_url": "https://api.mistral.ai/v1",
        "model":    "mistral-small-latest",
        "format":   "openai",
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "model":    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "format":   "openai",
    },
}


def _resolve() -> Dict[str, str]:
    """Return the active base_url, model, and wire format."""
    defaults = _PROVIDERS.get(LLM_PROVIDER, _PROVIDERS["openai"])
    return {
        "base_url": LLM_BASE_URL or defaults["base_url"],
        "model":    LLM_MODEL    or defaults["model"],
        "format":   defaults["format"],
    }


# ── Wire formats ───────────────────────────────────────────────────────────────

def _call_openai(messages: List[Dict], as_json: bool, cfg: Dict) -> str:
    payload: Dict[str, Any] = {
        "model":       cfg["model"],
        "messages":    messages,
        "temperature": 0,
    }
    if as_json:
        payload["response_format"] = {"type": "json_object"}

    headers = {
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}",
    }
    url = cfg["base_url"].rstrip("/") + "/chat/completions"
    req = urllib.request.Request(url, json.dumps(payload).encode(), headers)
    with urllib.request.urlopen(req, timeout=LLM_TIMEOUT) as resp:
        data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"]


def _call_anthropic(messages: List[Dict], as_json: bool, cfg: Dict) -> str:
    system = next((m["content"] for m in messages if m["role"] == "system"), None)
    user_msgs = [m for m in messages if m["role"] != "system"]

    if as_json and user_msgs:
        last = user_msgs[-1]
        user_msgs = user_msgs[:-1] + [{
            **last,
            "content": last["content"] + "\n\nRespond with valid JSON only — no markdown fences.",
        }]

    payload: Dict[str, Any] = {
        "model":      cfg["model"],
        "max_tokens": 1024,
        "messages":   user_msgs,
    }
    if system:
        payload["system"] = system

    headers = {
        "Content-Type":      "application/json",
        "x-api-key":         LLM_API_KEY,
        "anthropic-version": "2023-06-01",
    }
    url = cfg["base_url"].rstrip("/") + "/v1/messages"
    req = urllib.request.Request(url, json.dumps(payload).encode(), headers)
    with urllib.request.urlopen(req, timeout=LLM_TIMEOUT) as resp:
        data = json.loads(resp.read())
        return data["content"][0]["text"]


# ── Public API ─────────────────────────────────────────────────────────────────

def chat(messages: List[Dict], as_json: bool = False) -> Optional[str]:
    """
    Send messages to the configured LLM. Returns the text response or None on failure.
    Falls back gracefully — callers should handle None.
    """
    if not LLM_ENABLED:
        logger.debug("LLM disabled (LLM_ENABLED=false)")
        return None
    if not LLM_API_KEY:
        logger.warning("LLM_API_KEY not set — skipping LLM call")
        return None

    cfg = _resolve()
    logger.debug("LLM call: provider=%s model=%s", LLM_PROVIDER, cfg["model"])

    try:
        if cfg["format"] == "anthropic":
            return _call_anthropic(messages, as_json, cfg)
        return _call_openai(messages, as_json, cfg)

    except urllib.error.HTTPError as exc:
        body = exc.read(300).decode(errors="replace")
        logger.warning("LLM HTTP %s: %s", exc.code, body)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        logger.warning("LLM unreachable: %s", exc)
    except Exception as exc:
        logger.warning("LLM call failed: %s", exc)
    return None


def extract_json(messages: List[Dict]) -> Optional[Dict[str, Any]]:
    """
    Call the LLM expecting a JSON response. Returns parsed dict or None.
    Attempts to recover JSON from markdown-fenced or prose responses.
    """
    text = chat(messages, as_json=True)
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
        logger.warning("LLM non-JSON response (first 200 chars): %.200s", text)
        return None
