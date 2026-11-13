from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def cache_root():
    from kerbal_copilot.parts.cfg_parser import parse_file

    return parse_file(FIXTURES / "sample_part.cfg")


@pytest.fixture
def parts_db(tmp_path, cache_root):
    """A real parts.db built from the fixture, like ingest does."""
    from kerbal_copilot.parts.db import PartsDB
    from kerbal_copilot.parts.extract import extract

    parts, densities, tech = extract(cache_root)
    mods = [{"identifier": "TestMod", "name": "Test Mod", "version": "1.0", "latest": "1.2",
             "installed": 1, "ksp_max": "1.12"}]
    return PartsDB.build(tmp_path / "parts.db", parts, densities, tech, mods,
                         meta={"parts": len(parts)})


@pytest.fixture
def user_db(tmp_path):
    from kerbal_copilot.storage.user_db import UserDB

    return UserDB(tmp_path / "user.db", remote=False)
