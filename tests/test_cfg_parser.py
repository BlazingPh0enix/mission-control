from kerbal_copilot.parts.cfg_parser import parse

SAMPLE = """
// comment
PART
{
    name = testTank
    mass = 0.25 // dry mass
    RESOURCE
    {
        name = LiquidFuel
        maxAmount = 180
    }
    MODULE { name = ModuleDecouple }
}
"""


def test_nested_nodes_and_comments():
    part = parse(SAMPLE).children("PART")[0]
    assert part.get("name") == "testTank"
    assert part.get("mass") == "0.25"
    assert part.children("RESOURCE")[0].get("maxAmount") == "180"


def test_one_line_node():
    part = parse(SAMPLE).children("PART")[0]
    assert part.children("MODULE")[0].get("name") == "ModuleDecouple"


def test_duplicate_keys():
    node = parse("C { key = 0 300\n key = 1 250 }").children("C")[0]
    assert node.get_all("key") == ["0 300", "1 250"]
