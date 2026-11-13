import pytest

from kerbal_copilot.models import Build, BuildReport, PartRef, Stage

BUILD = Build(name="Hopper", mission="low kerbin orbit",
              stages=[Stage(label="S1", parts=[PartRef(name="testEngine")])])
REPORT = BuildReport(stages=[], total_dv_vac=3550.0, launch_twr=1.4)


def test_save_list_load_and_outcome(user_db):
    build_id = user_db.save_build(BUILD, REPORT)
    assert user_db.list_builds()[0]["total_dv"] == 3550.0
    loaded, report = user_db.load_build(build_id)
    assert loaded == BUILD and report == REPORT
    user_db.set_outcome(build_id, "flown", "Orbit with 120 m/s spare")
    assert "Orbit with 120 m/s spare" in user_db.recent_build_summaries()[0]
    with pytest.raises(KeyError):
        user_db.load_build(999)


def test_facts_usage_cache_and_export(user_db):
    user_db.set_fact("game_mode", "career")
    assert user_db.get_facts() == {"game_mode": "career"}
    assert user_db.requests_today() == 0
    user_db.add_request()
    user_db.add_request()
    assert user_db.requests_today() == 2
    user_db.cache_set("k", "v", ttl_hours=1)
    assert user_db.cache_get("k") == "v"
    user_db.cache_set("old", "v", ttl_hours=-1)
    assert user_db.cache_get("old") is None
    user_db.save_build(BUILD, None, name="Unevaluated")
    exported = user_db.export_json()
    assert exported["builds"][0]["name"] == "Unevaluated"
    assert exported["facts"]["game_mode"] == "career"
