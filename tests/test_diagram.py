from kerbal_copilot.models import Build, PartRef, Stage
from kerbal_copilot.tools.delta_v import evaluate
from kerbal_copilot.tools.diagram import render_state, render_svg
from kerbal_copilot.ui import tables

BUILD = Build(
    name="Test hopper", mission="mun flyby",
    payload=[PartRef(name="testPod")],
    stages=[
        Stage(label="Boosters", fires_with_next=True,
              parts=[PartRef(name="testTank", qty=2, placement="radial"),
                     PartRef(name="testEngine", qty=2, placement="radial")]),
        Stage(label="Core", parts=[PartRef(name="testDecoupler"), PartRef(name="testTank"),
                                   PartRef(name="testEngine")]),
    ],
)


def test_render_svg_draws_every_stage(parts_db):
    report = evaluate(BUILD, parts_db)
    svg = render_svg(BUILD, report, parts_db)
    assert svg.startswith("<svg") and svg.endswith("</svg>")
    assert "Boosters + Core" in svg  # boosters drawn beside the core
    assert "Payload" in svg
    assert "<polygon" in svg  # pod triangle / engine trapezoid


def test_render_state_never_raises(parts_db):
    bad = BUILD.model_copy(update={"payload": [PartRef(name="ghost")]})
    html = render_state({"build": bad.model_dump(), "report": None}, parts_db)
    assert "Can't draw" in html
    assert render_state(None, parts_db) == ""


def test_tables_from_state(parts_db):
    report = evaluate(BUILD, parts_db)
    state = {"build": BUILD.model_dump(), "report": report.model_dump()}
    rows = tables.stage_rows(state)
    assert [r[0] for r in rows] == ["Boosters", "Core"]
    assert "Launch TWR" in tables.summary_md(state)
    assert tables.stage_rows(None) == [] and tables.summary_md(None) == ""
