from kerbal_copilot.knowledge import KnowledgeBase, load_delta_v

# Surface-to-surface totals printed on the community delta-v map (v1.7.3)
MAP_TOTALS = {
    "keostationary orbit": 4515, "mun landing": 5120, "minmus landing": 4660,
    "moho landing": 8360, "eve landing": 13800, "gilly landing": 5000, "duna landing": 6520,
    "ike landing": 5280, "dres landing": 6670, "jool descent": 22250, "laythe landing": 10190,
    "vall landing": 7800, "tylo landing": 9190, "bop landing": 6810, "pol landing": 6570,
    "eeloo landing": 7460,
}


def test_delta_v_tables_parse():
    legs, missions = load_delta_v()
    assert legs["kerbin_ascent"][1] == 3400
    assert missions["mun flyby"] == ["kerbin_ascent", "mun_transfer"]


def test_every_mission_uses_known_legs():
    legs, missions = load_delta_v()
    unknown = {m: [leg for leg in ls if leg not in legs] for m, ls in missions.items()}
    assert {m: ls for m, ls in unknown.items() if ls} == {}


def test_landing_missions_match_the_map_totals():
    legs, missions = load_delta_v()
    totals = {m: sum(legs[leg][1] for leg in missions[m]) for m in MAP_TOTALS}
    assert totals == MAP_TOTALS


def test_knowledge_search():
    hits = KnowledgeBase().search("gravity turn")
    assert hits and hits[0]["file"] == "ascent.md"
    assert KnowledgeBase().search("!!!") == []
