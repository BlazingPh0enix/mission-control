"""Chat loop: tool calling, automatic build evaluation, one self-correction round."""
import json
import re
from pathlib import Path

from pydantic import ValidationError

from . import llm
from .config import settings
from .knowledge import KnowledgeBase
from .models import Build, BuildReport
from .parts.db import PartsDB, ensure_parts_db
from .storage.user_db import UserDB
from .tools import delta_v
from .tools.registry import make_tools, tool_schemas
from .tools.textcalls import recover_tool_calls

PROMPT_PATH = Path(__file__).parent / "prompts" / "system.md"
JSON_BLOCK = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)


def extract_build(text: str) -> tuple[Build | None, str | None]:
    blocks = JSON_BLOCK.findall(text or "")
    if not blocks:
        return None, None
    try:
        return Build.model_validate_json(blocks[-1]), None
    except ValidationError as exc:
        return None, f"The build JSON is invalid: {exc.errors()[:3]}"


def _trim(history, keep: int = 10) -> list[dict]:
    out = []
    for msg in history or []:
        if not isinstance(msg, dict) or msg.get("role") not in ("user", "assistant"):
            continue
        content = msg.get("content")
        if isinstance(content, list):
            content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
        if isinstance(content, str) and content:
            out.append({"role": msg["role"], "content": content})
    return out[-keep:]


class Agent:
    def __init__(self, db: PartsDB, user_db: UserDB, kb: KnowledgeBase):
        self.db, self.user_db, self.kb = db, user_db, kb
        self.last_budget: float | None = None
        self.schemas = tool_schemas(web_enabled=bool(settings.tavily_api_key))
        self.tools = make_tools(self)
        self.prompt_template = PROMPT_PATH.read_text(encoding="utf-8")

    @classmethod
    def from_env(cls) -> "Agent":
        return cls(PartsDB(ensure_parts_db()), UserDB(), KnowledgeBase())

    def system_prompt(self) -> str:
        facts = self.user_db.get_facts()
        fact_lines = "\n".join(f"- {k}: {v}" for k, v in facts.items() if v) or "- (none yet)"
        builds = "\n".join(self.user_db.recent_build_summaries()) or "- (none yet)"
        schema = json.dumps(Build.model_json_schema(), separators=(",", ":"))
        return (self.prompt_template
                .replace("{profile_facts}", fact_lines)
                .replace("{recent_build_summaries}", builds)
                .replace("{build_json_schema}", schema))

    def quota_text(self) -> str:
        used = self.user_db.requests_today()
        return f"Model requests today (UTC): {used} / {settings.daily_request_budget}"

    def _call(self, tool_call) -> str:
        fn = self.tools.get(tool_call.function.name)
        if fn is None:
            return json.dumps({"error": f"Unknown tool: {tool_call.function.name}"})
        try:
            result = fn(**json.loads(tool_call.function.arguments or "{}"))
        except Exception as exc:  # every failure goes back to the model so it can self-correct
            result = {"error": f"{type(exc).__name__}: {exc}"}
        return json.dumps(result, default=str)[:8000]

    def _loop(self, messages: list[dict], steps: int) -> str:
        for _ in range(steps):
            msg = llm.chat(messages, tools=self.schemas, usage=self.user_db).choices[0].message
            tool_calls, content = msg.tool_calls, msg.content or ""
            if not tool_calls:  # some free models write the call as text instead
                tool_calls, content = recover_tool_calls(content, self.schemas)
            if not tool_calls:
                messages.append({"role": "assistant", "content": content})
                return content
            messages.append({
                "role": "assistant",
                "content": content,
                "tool_calls": [tc.model_dump() for tc in tool_calls],
            })
            for tc in tool_calls:
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": self._call(tc)})
        final = llm.chat(
            messages + [{"role": "user", "content": "Give your final answer now."}],
            tools=self.schemas, tool_choice="none", usage=self.user_db,
        ).choices[0].message
        return recover_tool_calls(final.content, self.schemas)[1]  # drop any call markup

    def _check(self, text: str):
        build, error = extract_build(text)
        if error:
            return None, None, [error]
        if build is None:
            return None, None, []
        try:
            report = delta_v.evaluate(build, self.db)
        except (KeyError, ValueError, ZeroDivisionError) as exc:
            return build, None, [str(exc)]
        return build, report, delta_v.check_build(build, report, self.last_budget)

    def run(self, user_msg: str, history) -> tuple[str, Build | None, BuildReport | None]:
        self.last_budget = None
        messages = [
            {"role": "system", "content": self.system_prompt()},
            *_trim(history),
            {"role": "user", "content": user_msg},
        ]
        text = self._loop(messages, settings.max_agent_steps)
        build, report, problems = self._check(text)
        if problems:
            messages.append({"role": "user", "content": (
                "Automatic check of your build failed:\n- " + "\n- ".join(problems)
                + "\nFix the build and output the corrected ```json block."
            )})
            text2 = self._loop(messages, 2)
            build2, report2, problems2 = self._check(text2)
            if build2 is not None:
                text, build, report = text2, build2, report2
                if problems2:
                    text += "\n\n> Still flagged by the checker: " + "; ".join(problems2)
            else:
                text += "\n\n> Checker: " + "; ".join(problems)
        self.user_db.add_message("user", user_msg)
        self.user_db.add_message("assistant", text)
        return text, build, report

    def save_current(self, state, name=None) -> int | None:
        if not state:
            return None
        build = Build.model_validate(state["build"])
        report = BuildReport.model_validate(state["report"]) if state.get("report") else None
        return self.user_db.save_build(build, report, name)
