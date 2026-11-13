import io
import json
import tarfile

from kerbal_copilot.tools import mods


def test_read_installed_ckan(tmp_path):
    (tmp_path / "CKAN").mkdir()
    (tmp_path / "CKAN" / "installed-default.ckan").write_text(json.dumps({
        "kind": "metapackage",
        "depends": [{"name": "ModuleManager", "version": "4.2.3"}, {"name": "MechJeb2"}],
    }))
    assert mods.read_installed_ckan(tmp_path) == {"ModuleManager": "4.2.3", "MechJeb2": ""}
    assert mods.read_installed_ckan(tmp_path / "nowhere") == {}
    # a dated history copy must not win over the current file
    (tmp_path / "CKAN" / "installed-default-2020-01-01_00-00-00.ckan").write_text(
        json.dumps({"depends": [{"name": "OldMod", "version": "0.1"}]}))
    assert "OldMod" not in mods.read_installed_ckan(tmp_path)


def test_version_key_orders_like_ckan():
    versions = ["2.9.1", "2.10.0", "v2.9", "1:0.1", "2.10.0-pre"]
    assert max(versions, key=mods.version_key) == "1:0.1"  # epoch wins
    assert mods.version_key("2.10.0") > mods.version_key("2.9.1")


def _tarball(files: dict[str, dict]) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, meta in files.items():
            data = json.dumps(meta).encode()
            info = tarfile.TarInfo(f"CKAN-meta-master/{name}")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def test_build_ckan_index(monkeypatch):
    blob = _tarball({
        "MechJeb2/MechJeb2-2.9.0.ckan": {"identifier": "MechJeb2", "version": "2.9.0",
                                          "name": "MechJeb 2", "ksp_version_max": "1.12"},
        "MechJeb2/MechJeb2-2.14.1.ckan": {
            "identifier": "MechJeb2", "version": "2.14.1", "name": "MechJeb 2",
            "resources": {"spacedock": "https://spacedock.info/mod/1234/MechJeb2",
                          "repository": "https://github.com/MuMech/MechJeb2"}},
        "Other/Other-1.0.ckan": {"identifier": "Other", "version": "1.0"},
    })

    class Resp:
        content = blob

        def raise_for_status(self):
            pass

    monkeypatch.setattr(mods.httpx, "get", lambda *a, **k: Resp())
    rows = mods.build_ckan_index({"MechJeb2": "2.9.0"})
    assert len(rows) == 1
    row = rows[0]
    assert (row["version"], row["latest"]) == ("2.9.0", "2.14.1")
    assert row["ksp_max"] == "1.12"
    assert row["spacedock_id"] == 1234  # links fall back to the latest release's metadata
    assert row["repo"] == "https://github.com/MuMech/MechJeb2"


def test_mod_info_uses_spacedock_when_known(parts_db, monkeypatch):
    calls = []

    def fake_get_json(url, ttl=0):
        calls.append(url)
        return {"friendly_version": "1.2", "game_version": "1.12.5", "changelog": "fixes"}

    monkeypatch.setattr(mods, "_get_json", fake_get_json)
    parts_db.conn.execute("UPDATE mods SET spacedock_id = 99")
    info = mods.mod_info("testmod", parts_db)
    assert info["installed"]["identifier"] == "TestMod"
    assert info["spacedock_latest"]["version"] == "1.2"
    assert calls == ["https://spacedock.info/api/mod/99/latest"]
