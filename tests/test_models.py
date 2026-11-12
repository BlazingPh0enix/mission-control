import pytest
from pydantic import ValidationError

from kerbal_copilot.models import Build, PartRef


def test_build_json_round_trip():
    build = Build.model_validate({
        "name": "Hopper", "mission": "mun flyby",
        "stages": [{"label": "S1", "parts": [{"name": "liquidEngine2", "qty": 2}]}],
    })
    assert build.body == "Kerbin" and build.stages[0].parts[0].placement == "stack"
    assert Build.model_validate_json(build.model_dump_json()) == build


def test_invalid_part_refs_are_rejected():
    with pytest.raises(ValidationError):
        PartRef(name="x", qty=0)
    with pytest.raises(ValidationError):
        PartRef(name="x", placement="sideways")
