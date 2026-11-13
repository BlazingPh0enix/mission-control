import math

import pytest

from kerbal_copilot.models import Build, EngineStats, Part, PartRef, Stage
from kerbal_copilot.tools.delta_v import G0, check_build, evaluate, mission_budget

DENSITY = {"LiquidFuel": 0.005, "Oxidizer": 0.005, "SolidFuel": 0.0075}
LIQUID = EngineStats(max_thrust_kn=200, isp_vac=300, isp_asl=250,
                     propellants={"LiquidFuel": 0.9, "Oxidizer": 1.1})
SOLID = EngineStats(max_thrust_kn=250, isp_vac=210, isp_asl=180, propellants={"SolidFuel": 1})
PARTS = {
    "pod": Part(name="pod", mass_t=0.8, roles=["command"]),
    "tank": Part(name="tank", mass_t=0.25, roles=["tank"],
                 resources={"LiquidFuel": 180, "Oxidizer": 220}),
    "engine": Part(name="engine", mass_t=1.5, roles=["engine"], engine=LIQUID),
    "srb": Part(name="srb", mass_t=1.0, roles=["engine"], resources={"SolidFuel": 400},
                engine=SOLID),
}


class FakeDB:
    def get(self, name):
        return PARTS[name]

    def density(self, resource):
        return DENSITY.get(resource, 0.0)


def test_single_stage_matches_rocket_equation():
    build = Build(name="t", mission="test", payload=[PartRef(name="pod")],
                  stages=[Stage(label="S1", parts=[PartRef(name="tank"), PartRef(name="engine")])])
    report = evaluate(build, FakeDB())
    m0, m1 = 0.8 + 0.25 + 2.0 + 1.5, 0.8 + 0.25 + 1.5
    assert report.stages[0].dv_vac == pytest.approx(300 * G0 * math.log(m0 / m1), abs=0.5)
    assert report.launch_twr == pytest.approx(200 * 250 / 300 / (m0 * 9.81), abs=0.01)


def test_side_boosters_burn_with_core():
    build = Build(name="t", mission="test", payload=[PartRef(name="pod")], stages=[
        Stage(label="Boosters", fires_with_next=True,
              parts=[PartRef(name="srb", qty=2, placement="radial")]),
        Stage(label="Core", parts=[PartRef(name="tank"), PartRef(name="engine")]),
    ])
    report = evaluate(build, FakeDB())
    booster_mdot = 2 * 250 / (210 * G0)
    assert report.stages[0].burn_time_s == pytest.approx(6.0 / booster_mdot, abs=0.2)
    full_core_burn = 2.0 / (200 / (300 * G0))
    assert report.stages[1].burn_time_s < full_core_burn  # core drained during booster phase


def test_unknown_part_raises():
    build = Build(name="t", mission="test", stages=[Stage(label="S1", parts=[PartRef(name="x")])])
    with pytest.raises(KeyError):
        evaluate(build, FakeDB())


def test_mission_budget_sums_legs_and_matches_fuzzy_names():
    budget = mission_budget("mun landing and return")
    assert budget["total_dv"] == 3400 + 860 + 280 + 580 + 580 + 280
    assert budget["with_margin_dv"] == round(budget["total_dv"] * 1.1)
    assert mission_budget("munn orbit")["mission"] == "mun orbit"
    assert "error" in mission_budget("journey to the centre of jool")


def test_check_build_flags_low_twr_and_short_delta_v():
    build = Build(name="t", mission="test", payload=[PartRef(name="pod")],
                  stages=[Stage(label="S1", parts=[PartRef(name="tank"), PartRef(name="engine")])])
    report = evaluate(build, FakeDB())
    assert check_build(build, report) == []
    problems = check_build(build, report.model_copy(update={"launch_twr": 0.9}), 9999)
    assert any("TWR" in p for p in problems) and any("delta-v" in p for p in problems)
