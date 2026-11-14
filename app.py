"""Gradio entry point (Hugging Face Space, Render, or local)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import gradio as gr  # noqa: E402

from kerbal_copilot.config import settings  # noqa: E402
from kerbal_copilot.models import Build, BuildReport  # noqa: E402
from kerbal_copilot.tools.diagram import render_state  # noqa: E402
from kerbal_copilot.ui import tables  # noqa: E402
from kerbal_copilot.ui.theme import CSS, make_theme  # noqa: E402

try:  # ZeroGPU refuses to start without at least one @spaces.GPU function
    import spaces

    @spaces.GPU(duration=1)
    def _zerogpu_placeholder():
        return None
except ImportError:  # not on ZeroGPU (laptop, Render, your PC)
    pass

MISSIONS = [
    "low kerbin orbit",
    "mun flyby",
    "mun orbit",
    "mun landing and return",
    "minmus orbit",
    "minmus landing and return",
]
ROLES = ["", "engine", "tank", "command", "decoupler", "parachute", "power", "antenna",
         "science", "rcs", "docking", "heat_shield"]


def build_app(agent) -> gr.Blocks:
    def respond(message, history, state):
        history = history or []
        if not (message or "").strip():
            return history, "", state, gr.update(), gr.update(), gr.update(), agent.quota_text()
        try:
            reply, build, report = agent.run(message, history)
        except Exception as exc:  # show the problem in the chat instead of a red error toast
            reply, build, report = f"Something went wrong: {exc}", None, None
        history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": reply},
        ]
        if build is not None:
            state = {"build": build.model_dump(),
                     "report": report.model_dump() if report else None}
        return (history, "", state, render_state(state, agent.db), tables.summary_md(state),
                tables.stage_rows(state), agent.quota_text())

    def save_build(state, name):
        if not state:
            return "Nothing to save yet.", gr.update()
        build = Build.model_validate(state["build"])
        report = BuildReport.model_validate(state["report"]) if state.get("report") else None
        build_id = agent.user_db.save_build(build, report, (name or "").strip() or None)
        return f"Saved as build #{build_id}.", tables.build_rows(agent.user_db.list_builds())

    def load_build(build_id):
        if build_id is None:
            return None, "<p>Enter a build id from the table first.</p>", "", []
        try:
            build, report = agent.user_db.load_build(int(build_id))
        except (KeyError, ValueError) as exc:
            return None, f"<p>{exc}</p>", "", []
        state = {"build": build.model_dump(), "report": report.model_dump() if report else None}
        return (state, render_state(state, agent.db), tables.summary_md(state),
                tables.stage_rows(state))

    def save_outcome(build_id, status, outcome):
        if build_id is not None:
            agent.user_db.set_outcome(int(build_id), status, outcome or "")
        return tables.build_rows(agent.user_db.list_builds())

    def save_profile(game_mode, unlocked, prefs):
        agent.user_db.set_fact("game_mode", game_mode or "")
        agent.user_db.set_fact("unlocked_tech", unlocked or "")
        agent.user_db.set_fact("preferences", prefs or "")
        return "Profile saved."

    def search_parts(query, role):
        return tables.part_rows(agent.db.search(query or "", role=role or None, limit=25))

    facts = agent.user_db.get_facts()

    with gr.Blocks(title="Kerbal Copilot") as demo:
        state = gr.State(None)
        gr.Markdown("# Kerbal Copilot\nDesign rockets that fit your tech tree, mods and "
                    "delta-v budget.", elem_id="header")
        with gr.Row(equal_height=False):
            with gr.Column(scale=3):
                chat = gr.Chatbot(height=560, show_label=False, elem_id="chat")
                with gr.Row():
                    box = gr.Textbox(placeholder="Design a Mun lander for career mode with "
                                                 "mid-tier tech", show_label=False,
                                     container=False, scale=6, elem_id="composer")
                    send = gr.Button("Send", variant="primary", scale=1, min_width=90)
                mission = gr.Dropdown(MISSIONS, label="Quick start: pick a mission", value=None)
                quota = gr.Markdown(agent.quota_text(), elem_id="quota")
            with gr.Column(scale=2, elem_id="side"):
                with gr.Tab("Current build"):
                    diagram = gr.HTML()
                    summary = gr.Markdown()
                    stages = gr.Dataframe(headers=tables.STAGE_HEADERS, interactive=False)
                    with gr.Row():
                        build_name = gr.Textbox(label="Save as", scale=3)
                        save_btn = gr.Button("Save build", scale=1)
                    save_msg = gr.Markdown()
                with gr.Tab("Saved builds"):
                    saved = gr.Dataframe(headers=tables.BUILD_HEADERS, interactive=False,
                                         value=tables.build_rows(agent.user_db.list_builds()))
                    with gr.Row():
                        build_id = gr.Number(label="Build id", precision=0)
                        status = gr.Dropdown(["draft", "flown", "retired"], value="flown",
                                             label="Status")
                    outcome = gr.Textbox(label="Outcome notes",
                                         placeholder="Reached Mun orbit with 150 m/s spare")
                    with gr.Row():
                        load_btn = gr.Button("Load into viewer")
                        outcome_btn = gr.Button("Save outcome")
                with gr.Tab("Parts"):
                    part_q = gr.Textbox(label="Search parts", placeholder="2.5m vacuum engine")
                    part_role = gr.Dropdown(ROLES, value="", label="Role")
                    part_results = gr.Dataframe(headers=tables.PART_HEADERS, interactive=False)
                with gr.Tab("Mods"):
                    gr.Dataframe(headers=tables.MOD_HEADERS, interactive=False,
                                 value=tables.mod_rows(agent.db.mods()))
                with gr.Tab("Profile"):
                    game_mode = gr.Dropdown(["career", "science", "sandbox"],
                                            value=facts.get("game_mode") or "career",
                                            label="Game mode")
                    unlocked = gr.Textbox(value=facts.get("unlocked_tech", ""),
                                          label="Unlocked tech node ids (comma-separated)")
                    prefs = gr.Textbox(value=facts.get("preferences", ""), label="Preferences",
                                       lines=3)
                    profile_btn = gr.Button("Save profile")
                    profile_msg = gr.Markdown()

        outputs = [chat, box, state, diagram, summary, stages, quota]
        box.submit(respond, [box, chat, state], outputs, api_name="chat")
        send.click(respond, [box, chat, state], outputs)
        mission.change(lambda m: f"Design a rocket for: {m}." if m else "", mission, box)
        save_btn.click(save_build, [state, build_name], [save_msg, saved])
        load_btn.click(load_build, build_id, [state, diagram, summary, stages])
        outcome_btn.click(save_outcome, [build_id, status, outcome], saved)
        part_q.submit(search_parts, [part_q, part_role], part_results)
        profile_btn.click(save_profile, [game_mode, unlocked, prefs], profile_msg)
    return demo


def error_app(message: str) -> gr.Blocks:
    """Shown instead of the real UI when startup fails, so the Space explains itself."""
    with gr.Blocks(title="Kerbal Copilot") as demo:
        gr.Markdown(f"## Kerbal Copilot couldn't start\n\n{message}\n\n"
                    "Check the Space secrets (HF_TOKEN, HF_DATA_REPO) and the logs.")
    return demo


def create_demo() -> gr.Blocks:
    from kerbal_copilot.agent import Agent

    try:
        agent = Agent.from_env()
    except Exception as exc:
        return error_app(str(exc))
    return build_app(agent)


demo = create_demo()

if __name__ == "__main__":
    auth = None
    if settings.app_username and settings.app_password:
        auth = (settings.app_username, settings.app_password)
    demo.queue(default_concurrency_limit=2).launch(
        auth=auth,
        theme=make_theme(),
        css=CSS,
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", "7860")),
    )
