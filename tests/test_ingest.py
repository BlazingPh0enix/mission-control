"""End-to-end ingest on a fake KSP folder (no network, no upload)."""
import json
import shutil
import sys
from pathlib import Path

from kerbal_copilot import cli
from kerbal_copilot.parts.db import PartsDB

FIXTURES = Path(__file__).parent / "fixtures"


def test_ingest_builds_parts_db(tmp_path, monkeypatch, capsys):
    ksp = tmp_path / "Kerbal Space Program"
    (ksp / "GameData").mkdir(parents=True)
    shutil.copy(FIXTURES / "sample_part.cfg", ksp / "GameData" / "ModuleManager.ConfigCache")
    (ksp / "CKAN").mkdir()
    (ksp / "CKAN" / "installed-default.ckan").write_text(json.dumps(
        {"depends": [{"name": "TestMod", "version": "1.0"}]}))
    out = tmp_path / "parts.db"

    monkeypatch.setattr(sys, "argv", ["kerbal-copilot", "ingest", "--ksp", str(ksp),
                                      "--out", str(out), "--no-ckan"])
    cli.main()

    assert "4 parts" in capsys.readouterr().out
    db = PartsDB(out)
    assert db.get("testEngine").title == "Test Engine"
    assert db.mods()[0]["identifier"] == "TestMod"
    assert len(db.tech_nodes()) == 4
