import json
import logging
from dataclasses import dataclass
from urllib.request import Request, urlopen
from urllib.error import URLError

from shared.taxonomy import SQLI_TYPES, VALID_DB, VALID_TYPES


logger = logging.getLogger("llm_client")


@dataclass
class ClassifyResult:
    sqli_type: str
    db_engine: str
    confidence: float
    reasoning: str


LLM_CONFIGS = {
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        "auth_header": "x-goog-api-key",
    },
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "auth_header": "Authorization",
    },
}

DEFAULT_TAXONOMY = [t.name for t in SQLI_TYPES]
DEFAULT_DB = list(VALID_DB)


def _build_prompt(payload: str) -> str:
    return (
        f"Classify this SQL injection payload: {json.dumps(payload)}\n\n"
        f"Taxonomy: {json.dumps(DEFAULT_TAXONOMY)}\n"
        f"DB engines: {json.dumps(DEFAULT_DB)}\n\n"
        f"Return JSON with keys: sqli_type, db_engine, confidence (0.0-1.0), reasoning (>=30 chars)"
    )


def classify_via_llm(payload: str, provider: str = "gemini",
                     api_key: str = "", api_url: str = "") -> ClassifyResult | None:
    if not api_key:
        logger.warning("No API key provided for %s, skipping LLM fallback", provider)
        return None

    try:
        url = api_url or LLM_CONFIGS.get(provider, {}).get("url", "")
        if not url:
            logger.error("Unknown provider: %s", provider)
            return None

        headers = {
            "Content-Type": "application/json",
        }
        auth_header = LLM_CONFIGS.get(provider, {}).get("auth_header", "Authorization")
        headers[auth_header] = api_key

        body = json.dumps({
            "contents": [{"parts": [{"text": _build_prompt(payload)}]}]
        }).encode("utf-8")

        req = Request(url, data=body, headers=headers, method="POST")
        with urlopen(req, timeout=30) as resp:
            response_data = json.loads(resp.read().decode("utf-8"))

        return _parse_llm_response(response_data, provider)

    except URLError as e:
        logger.error("LLM API error: %s", e)
        return None
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error("LLM response parse error: %s", e)
        return None


def _parse_llm_response(data: dict, provider: str) -> ClassifyResult | None:
    try:
        if provider == "gemini":
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        elif provider == "openai":
            text = data["choices"][0]["message"]["content"]
        else:
            text = str(data)

        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        text = text.strip()

        result = json.loads(text)
        sqli_type = result.get("sqli_type", "unknown")
        db_engine = result.get("db_engine", "unknown")
        confidence = float(result.get("confidence", 0.5))
        reasoning = result.get("reasoning", "")

        if sqli_type not in VALID_TYPES:
            sqli_type = "unknown"
        if db_engine not in VALID_DB:
            db_engine = "unknown"
        confidence = max(0.0, min(1.0, confidence))
        if len(reasoning) < 10:
            reasoning = f"LLM classified as {sqli_type} on {db_engine}"

        return ClassifyResult(sqli_type, db_engine, confidence, reasoning)

    except (KeyError, IndexError, json.JSONDecodeError, ValueError) as e:
        logger.error("Failed to parse LLM response: %s", e)
        return None
