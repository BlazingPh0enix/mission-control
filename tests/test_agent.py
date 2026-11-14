"""The agent loop with a scripted fake model: no network, no quota."""
import json
from types import SimpleNamespace

import pytest

from kerbal_copilot import agent as agent_module
from kerbal_copilot.agent import Agent, extract_build
from kerbal_copilot.knowledge import KnowledgeBase

GOOD_BUILD = {
    "name": "Tiny hopper", "mission": "suborbital hop",
    "payload": [{"name": "testPod"}],
    "stages": [{"label": "S1", "parts": [{"name": "testTank"}, {"name": "testEngine"}]}],
}


class ToolCall:
    def __init__(self, call_id, name, args):
        self.id = call_id
        self.function = SimpleNamespace(name=name, arguments=json.dumps(args))

    def model_dump(self):
        return {"id": self.id, "type": "function",
                "function": {"name": self.function.name, "arguments": self.function.arguments}}


def reply(content=None, tool_calls=None):
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def final(build: dict) -> str:
    return f"Here's the design.\n\n```json\n{json.dumps(build)}\n```"


@pytest.fixture
def run_with(monkeypatch, parts_db, user_db):
    """Run one agent turn against a list of scripted model replies."""
    def runner(script, prompt="Design something"):
        seen = []

        def fake_chat(messages, tools=None, usage=None, **kwargs):
            seen.append([dict(m) for m in messages])
            usage.add_request()
            return script.pop(0)

        monkeypatch.setattr(agent_module.llm, "chat", fake_chat)
        bot = Agent(parts_db, user_db, KnowledgeBase())
        text, build, report = bot.run(prompt, [])
        return SimpleNamespace(text=text, build=build, report=report, seen=seen, bot=bot)
    return runner


def test_tool_call_then_valid_build(run_with):
    result = run_with([
        reply(tool_calls=[ToolCall("c1", "evaluate_build", {"build": json.dumps(GOOD_BUILD)})]),
        reply(final(GOOD_BUILD)),
    ])
    assert result.build.name == "Tiny hopper"
    assert result.report.launch_twr > 1.2
    tool_msg = result.seen[1][-1]
    assert tool_msg["role"] == "tool" and "dv_vac" in tool_msg["content"]
    assert result.bot.user_db.requests_today() == 2


def test_short_build_gets_one_revision(run_with):
    result = run_with([
        reply(tool_calls=[ToolCall("c1", "mission_budget", {"mission": "mun flyby"})]),
        reply(final(GOOD_BUILD)),
        reply(final(GOOD_BUILD)),  # the "revision" is still short
    ])
    revision_prompt = result.seen[2][-1]["content"]
    assert "Automatic check of your build failed" in revision_prompt
    assert "Still flagged by the checker" in result.text
    assert result.bot.user_db.requests_today() == 3


def test_unknown_tool_and_bad_arguments_go_back_to_model(run_with):
    result = run_with([
        reply(tool_calls=[ToolCall("c1", "launch_kraken", {}),
                          ToolCall("c2", "get_part", {"name": "ghost"})]),
        reply("I need more details: which body?"),
    ])
    tool_msgs = [m for m in result.seen[1] if m["role"] == "tool"]
    assert "Unknown tool" in tool_msgs[0]["content"]
    assert "KeyError" in tool_msgs[1]["content"]
    assert result.build is None and result.report is None


def test_extract_build_handles_missing_and_invalid_json():
    assert extract_build("no json here") == (None, None)
    build, error = extract_build('```json\n{"name": "x"}\n```')
    assert build is None and "invalid" in error


ERNIE_TEXT = """I need a couple more parts before finalizing.<ernie:tool_call>
<invoke name="search_parts"><parameter name="query">liquid fuel engine</parameter>
<parameter name="role">engine</parameter><parameter name="limit">3</parameter></invoke>
<invoke name="get_part"><parameter name="name">testTank</parameter></invoke>
</ernie:tool_call>"""


def test_tool_calls_written_as_text_are_executed(run_with):
    result = run_with([
        reply(ERNIE_TEXT),
        reply(final(GOOD_BUILD)),
    ])
    assert result.build is not None
    sent = result.seen[1]
    assistant = next(m for m in sent if m.get("tool_calls"))
    assert "ernie" not in assistant["content"] and "invoke" not in assistant["content"]
    calls = [tc["function"] for tc in assistant["tool_calls"]]
    assert [c["name"] for c in calls] == ["search_parts", "get_part"]
    assert json.loads(calls[0]["arguments"]) == {"query": "liquid fuel engine",
                                                 "role": "engine", "limit": 3}
    assert [m["role"] for m in sent[-2:]] == ["tool", "tool"]


def test_json_style_text_call_and_plain_text_untouched(run_with):
    text = ('<tool_call>{"name": "mission_budget", '
            '"arguments": {"mission": "mun flyby"}}</tool_call>')
    result = run_with([reply(text), reply("Use about 4,500 m/s.")])
    assert "total_dv" in result.seen[1][-1]["content"]
    assert result.text == "Use about 4,500 m/s."
    plain = run_with([reply("Mention <invoke> in prose, no call.")])
    assert plain.text == "Mention <invoke> in prose, no call."
    ghost = run_with([reply('<tool_call>{"name":"nope","arguments":{}}</tool_call>')])
    assert "nope" in ghost.text  # unknown tool names are not executed
