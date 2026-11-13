from kerbal_copilot.parts.extract import extract, mod_folder


def test_extract_engine_part(cache_root):
    parts, densities, _tech = extract(cache_root)
    engine = next(p for p in parts if p.name == "testEngine")
    assert engine.title == "Test Engine"  # resolved from the Localization node
    assert engine.mod == "TestMod"  # leading slash in parentUrl is handled
    assert engine.size == "size1"
    assert "engine" in engine.roles
    assert engine.engine.isp_vac == 300
    assert engine.engine.isp_asl == 250
    assert densities["LiquidFuel"] == 0.005


def test_roles_for_tank_pod_and_decoupler(cache_root):
    parts = {p.name: p for p in extract(cache_root)[0]}
    assert parts["testTank"].roles == ["tank"]
    assert parts["testTank"].resources == {"LiquidFuel": 180, "Oxidizer": 220}
    assert parts["testPod"].roles == ["command"]  # monopropellant doesn't make it a tank
    assert parts["testDecoupler"].roles == ["decoupler"]


def test_tech_tree(cache_root):
    tech = {t["id"]: t for t in extract(cache_root)[2]}
    assert tech["generalRocketry"]["parents"] == ["basicRocketry", "engineering101"]
    assert tech["generalRocketry"]["any"] is True
    assert tech["basicRocketry"]["any"] is False


def test_mod_folder():
    assert mod_folder("/Squad/Parts/Engine/x.cfg") == "Squad"
    assert mod_folder("ReStock/Parts/y") == "ReStock"
    assert mod_folder("") == "unknown"
