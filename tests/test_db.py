import pytest


def test_search_finds_parts_by_words_and_role(parts_db):
    names = [p["name"] for p in parts_db.search("test engine")]
    assert "testEngine" in names
    engines = parts_db.search("test", role="engine")
    assert [p["name"] for p in engines] == ["testEngine"]
    assert engines[0]["thrust_kn"] == 200


def test_search_by_internal_name_and_odd_characters(parts_db):
    assert parts_db.search("testDecoupler")[0]["name"] == "testDecoupler"
    assert parts_db.search('"T-400" (tank) OR *') != []  # FTS syntax can't break the query


def test_get_and_density(parts_db):
    assert parts_db.get("testTank").mass_t == 0.25
    assert parts_db.density("Oxidizer") == 0.005
    assert parts_db.density("Unobtainium") == 0.0
    with pytest.raises(KeyError):
        parts_db.get("noSuchPart")


def test_tech_mods_meta(parts_db):
    assert parts_db.tech_nodes()["basicRocketry"]["parents"] == ["start"]
    assert parts_db.mods()[0]["identifier"] == "TestMod"
    assert parts_db.meta()["parts"] == "4"
