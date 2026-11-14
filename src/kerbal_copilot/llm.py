"""OpenRouter client: free-model discovery, fallbacks, daily budget, Groq backup."""
import logging
import time

import httpx
from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError

from .config import settings

log = logging.getLogger(__name__)
OPENROUTER_URL = "https://openrouter.ai/api/v1"
GROQ_URL = "https://api.groq.com/openai/v1"
REFRESH_SECONDS = 6 * 3600


class BudgetExceeded(RuntimeError):
    pass


_clients: dict[str, OpenAI] = {}
_chains: dict[str, tuple[float, list[str]]] = {}


def _client(base_url: str, key: str | None) -> OpenAI:
    if base_url not in _clients:
        _clients[base_url] = OpenAI(
            base_url=base_url,
            api_key=key or "missing",
            default_headers={"X-Title": "Kerbal Copilot"},
            timeout=90,
            max_retries=0,  # we fail over to the next model instead of retrying the same one
        )
    return _clients[base_url]


def discover(kind: str = "tools") -> list[str]:
    """Live free models that support tools (kind='tools') or image input (kind='vision')."""
    preferred = settings.vision_models if kind == "vision" else settings.preferred_models
    try:
        data = httpx.get(f"{OPENROUTER_URL}/models", timeout=20).json()["data"]
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        log.warning("Model discovery failed (%s); using the configured list", exc)
        return [*preferred, "openrouter/free"]
    live = set()
    for model in data:
        model_id = model.get("id", "")
        if not model_id.endswith(":free"):
            continue
        params = model.get("supported_parameters") or []
        inputs = (model.get("architecture") or {}).get("input_modalities") or []
        if kind == "vision" and "image" not in inputs:
            continue
        if kind == "tools" and "tools" not in params:
            continue
        live.add(model_id)
    first = [m for m in preferred if m in live]
    return first + sorted(live - set(first)) + ["openrouter/free"]


def model_chain(kind: str = "tools") -> list[str]:
    stamp, chain = _chains.get(kind, (0.0, []))
    if not chain or time.time() - stamp > REFRESH_SECONDS:
        chain = discover(kind)
        _chains[kind] = (time.time(), chain)
    return chain


def _recent(messages: list[dict], users: int = 2) -> list[dict]:
    """System prompt plus everything from the Nth-last user message (keeps tool pairs intact)."""
    idx = [i for i, m in enumerate(messages) if m.get("role") == "user"]
    start = idx[-users] if len(idx) >= users else (idx[0] if idx else 0)
    head = [messages[0]] if messages and messages[0].get("role") == "system" else []
    return head + messages[max(start, len(head)):]

class EmptyReply(RuntimeError):
    pass

def _attempt(model, messages, extra, kwargs):
    resp = _client(OPENROUTER_URL, settings.openrouter_api_key).chat.completions.create(
        model=model, messages=messages, temperature=0.3,
        max_tokens=settings.max_tokens, **extra, **kwargs,
    )
    msg = resp.choices[0].message if resp.choices else None
    if msg is None or (not msg.content and not msg.tool_calls):
        raise EmptyReply(f"{model}: empty reply")
    return resp


def chat(messages, tools=None, chain=None, usage=None, max_models: int = 4, **kwargs):
    if usage is not None and usage.requests_today() >= settings.daily_request_budget:
        # Free quota is spent: go straight to the paid models instead of stopping
        candidates = []
    else:
        candidates = (chain or model_chain())[:max_models]
    extra = {"tools": tools} if tools else {}
    errors = []
    for model in candidates + settings.paid_models:
        try:
            resp = _attempt(model, messages, extra, kwargs)
            if usage is not None:
                usage.add_request()
            return resp
        except RateLimitError:
            errors.append(f"{model}: rate limited")
        except APIStatusError as exc:
            if exc.status_code == 402:
                raise RuntimeError("OpenRouter returned 402: the credit balance is negative.") from exc
            errors.append(f"{model}: HTTP {exc.status_code}")
        except (APIConnectionError, EmptyReply) as exc:
            errors.append(str(exc))
    if settings.groq_api_key:
        log.warning("OpenRouter failed (%s); trying Groq", "; ".join(errors))
        return _client(GROQ_URL, settings.groq_api_key).chat.completions.create(
            model=settings.groq_model, messages=_recent(messages), temperature=0.3, # type: ignore
            max_tokens=min(settings.max_tokens, 2000), **extra, **kwargs,
        ) # type: ignore
    raise RuntimeError("All models failed: " + "; ".join(errors))


def key_info() -> dict:
    """Remaining credits and limits for the configured OpenRouter key."""
    resp = httpx.get(
        f"{OPENROUTER_URL}/key",
        headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json().get("data", {})
