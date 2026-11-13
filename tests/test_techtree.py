from kerbal_copilot.tools.techtree import tech_path


def test_tech_path_lists_missing_nodes(parts_db):
    result = tech_path(["testEngine", "testDecoupler", "testTank"], parts_db)
    assert {n["id"] for n in result["nodes"]} == {"basicRocketry", "engineering101"}
    assert result["total_science"] == 10
    assert result["part_tech"]["testTank"] == "start"


def test_tech_path_skips_unlocked_and_reports_unknown(parts_db):
    result = tech_path(["testEngine", "ghostPart"], parts_db, unlocked=["basicRocketry"])
    assert result["nodes"] == []
    assert result["unknown_parts"] == ["ghostPart"]
