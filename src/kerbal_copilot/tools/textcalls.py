"""Recover tool calls that a model wrote as plain text instead of using the tool-call field.

Some free models (ERNIE, Qwen, Hermes-style fine-tunes) do this on some runs:

    <ernie:tool_call><invoke name="search_parts"><parameter name="query">x</parameter></invoke>
    </ernie:tool_call>
    <tool_call>{"name": "search_parts", "arguments": {"query": "x"}}</tool_call>
"""
import itertools
import json
import re
from types import SimpleNamespace

WRAPPER = re.compile(r"<(?P<tag>[\w.:-]*tool_calls?)\b[^>]*>(?P<body>.*?)</(?P=tag)\s*>",
                     re.DOTALL | re.IGNORECASE)
LONE_OPEN = re.compile(r"<[\w.:-]*tool_calls?\b[^>]*>", re.IGNORECASE)
INVOKE = re.compile(r"<invoke\s+name=[\"']?(?P<name>[\w.-]+)[\"']?\s*>(?P<body>.*?)</invoke\s*>",
                    re.DOTALL | re.IGNORECASE)
PARAM = re.compile(
    r"<parameter\s+name=[\"']?(?P<key>[\w.-]+)[\"']?\s*>(?P<value>.*?)</parameter\s*>",
    re.DOTALL | re.IGNORECASE)
_ids = itertools.count(1)


def _make(name: str, args: dict) -> SimpleNamespace:
    call_id = f"text_call_{next(_ids)}"
    function = SimpleNamespace(name=name, arguments=json.dumps(args))
    return SimpleNamespace(
        id=call_id, function=function,
        model_dump=lambda: {"id": call_id, "type": "function",
                            "function": {"name": name, "arguments": function.arguments}},
    )


def _coerce(value: str, schema: dict):
    """Parameter values arrive as text; convert them to what the tool schema declares."""
    value = value.strip()
    kind = schema.get("type")
    try:
        if kind == "integer":
            return int(float(value))
        if kind in ("array", "object", "number", "boolean"):
            return json.loads(value)
    except ValueError:
        pass
    return value


def _json_calls(body: str) -> list[tuple[str, dict]]:
    try:
        data = json.loads(body.strip())
    except ValueError:
        return []
    out = []
    for item in data if isinstance(data, list) else [data]:
        if not isinstance(item, dict):
            continue
        fn = item.get("function") if isinstance(item.get("function"), dict) else item
        args = fn.get("arguments", fn.get("parameters", {}))
        if isinstance(args, str):
            try:
                args = json.loads(args or "{}")
            except ValueError:
                continue
        if fn.get("name") and isinstance(args, dict):
            out.append((fn["name"], args))
    return out


def recover_tool_calls(text: str | None, schemas: list[dict]) -> tuple[list, str]:
    """Return (tool calls, text with the call markup removed). No calls found: ([], text)."""
    if not text or "tool_call" not in text.lower() and "<invoke" not in text.lower():
        return [], text or ""
    props = {s["function"]["name"]: s["function"]["parameters"].get("properties", {})
             for s in schemas}
    found: list[tuple[str, dict]] = []

    def scan(body: str):
        invokes = list(INVOKE.finditer(body))
        for inv in invokes:
            schema = props.get(inv["name"], {})
            args = {p["key"]: _coerce(p["value"], schema.get(p["key"], {}))
                    for p in PARAM.finditer(inv["body"])}
            found.append((inv["name"], args))
        if not invokes:
            found.extend(_json_calls(body))

    for wrapper in WRAPPER.finditer(text):
        scan(wrapper["body"])
    if not found:  # the closing tag may be missing, or invokes may be bare
        scan(text)
    calls = [_make(name, args) for name, args in found if name in props]
    if not calls:
        return [], text
    cleaned = INVOKE.sub("", WRAPPER.sub("", text))
    cleaned = LONE_OPEN.sub("", cleaned)
    cleaned = re.sub(r"</[\w.:-]*tool_calls?\s*>", "", cleaned, flags=re.IGNORECASE)
    return calls, cleaned.strip()
