"""Turn parsed configs into Part objects, resource densities and the tech tree."""
from itertools import pairwise
from pathlib import Path

from ..models import EngineStats, Part
from .cfg_parser import Node, parse_file

ENGINE_MODULES = {"ModuleEngines", "ModuleEnginesFX"}
ROLE_MODULES = {
    "ModuleDecouple": "decoupler",
    "ModuleAnchoredDecouple": "decoupler",
    "ModuleCommand": "command",
    "ModuleParachute": "parachute",
    "ModuleDeployableSolarPanel": "power",
    "ModuleDataTransmitter": "antenna",
    "ModuleScienceExperiment": "science",
    "ModuleRCS": "rcs",
    "ModuleRCSFX": "rcs",
    "ModuleReactionWheel": "reaction_wheel",
    "ModuleWheelBase": "wheel",
    "ModuleDockingNode": "docking",
    "ModuleAblator": "heat_shield",
}
TANK_RESOURCES = {"LiquidFuel", "Oxidizer", "MonoPropellant", "SolidFuel", "XenonGas"}


def _float(value, default: float = 0.0) -> float:
    try:
        return float(str(value).split(",")[0].strip())
    except (TypeError, ValueError):
        return default


def mod_folder(url: str) -> str:
    """'/Squad/Parts/Engine/x.cfg' or 'Squad/Parts/...' -> 'Squad'."""
    return (url or "").strip().strip("/").split("/")[0] or "unknown"


def isp_at(curve: Node | None, pressure: float) -> float:
    """Linear interpolation of an atmosphereCurve (key = pressure_atm isp)."""
    if curve is None:
        return 0.0
    points = []
    for key in curve.get_all("key"):
        bits = key.split()
        if len(bits) >= 2:
            points.append((_float(bits[0]), _float(bits[1])))
    if not points:
        return 0.0
    points.sort()
    if pressure <= points[0][0]:
        return points[0][1]
    for (p0, i0), (p1, i1) in pairwise(points):
        if p0 <= pressure <= p1:
            return i0 + (i1 - i0) * (pressure - p0) / ((p1 - p0) or 1.0)
    return points[-1][1]


def _engine(module: Node) -> EngineStats | None:
    curves = module.children("atmosphereCurve")
    curve = curves[0] if curves else None
    isp_vac = isp_at(curve, 0.0)
    thrust = _float(module.get("maxThrust"))
    if thrust <= 0 or isp_vac <= 0:
        return None
    propellants = {}
    for prop in module.children("PROPELLANT"):
        if prop.get("name"):
            propellants[prop.get("name")] = _float(prop.get("ratio"), 1.0)
    return EngineStats(max_thrust_kn=thrust, isp_vac=isp_vac,
                       isp_asl=max(isp_at(curve, 1.0), 0.0), propellants=propellants)


def part_from_node(node: Node, parent_url: str = "") -> Part | None:
    name = node.get("name")
    if not name:
        return None
    roles: set[str] = set()
    engine = None
    for module in node.children("MODULE"):
        module_name = module.get("name", "")
        if module_name in ENGINE_MODULES and engine is None:
            engine = _engine(module)
            if engine:
                roles.add("engine")
        elif module_name in ROLE_MODULES:
            roles.add(ROLE_MODULES[module_name])
    resources = {}
    for res in node.children("RESOURCE"):
        if res.get("name"):
            resources[res.get("name")] = _float(res.get("maxAmount"))
    # Pods carry a little monopropellant; that doesn't make them tanks
    if not roles & {"engine", "command"} and any(r in TANK_RESOURCES for r in resources):
        roles.add("tank")
    size = (node.get("bulkheadProfiles") or "").split(",")[0].strip() or None
    return Part(
        name=name,
        title=node.get("title", name), # type: ignore
        mod=mod_folder(parent_url),
        category=node.get("category"),
        size=size,
        mass_t=_float(node.get("mass")),
        cost=_float(node.get("cost")),
        tech_required=node.get("TechRequired"),
        description=(node.get("description") or "")[:500],
        roles=sorted(roles),
        resources=resources,
        engine=engine,
    )


def _tech_nodes(tree: Node) -> list[dict]:
    nodes = []
    for rd in tree.children("RDNode"):
        if rd.get("id"):
            nodes.append({
                "id": rd.get("id"),
                "title": rd.get("title", rd.get("id")),
                "cost": int(_float(rd.get("cost"))),
                "parents": [p.get("parentID") for p in rd.children("Parent")
                            if p.get("parentID")],
                "any": (rd.get("anyToUnlock") or "false").lower() == "true",
            })
    return nodes


def _collect(url, node, parts, densities, tech, loc) -> None:
    if node.name == "PART":
        part = part_from_node(node, url)
        if part:
            parts.append(part)
    elif node.name == "RESOURCE_DEFINITION" and node.get("name"):
        densities[node.get("name")] = _float(node.get("density"))
    elif node.name == "TechTree" and not tech:  # like ModuleManager, use the first tree
        tech.extend(_tech_nodes(node))
    elif node.name == "Localization":
        for lang in node.children("en-us"):
            loc.update(dict(lang.values))


def _localize(parts, tech, loc) -> None:
    for part in parts:
        if part.title.startswith("#"):
            part.title = loc.get(part.title, part.title)
        if part.description.startswith("#"):
            part.description = loc.get(part.description, part.description)[:500]
    for node in tech:
        if str(node["title"]).startswith("#"):
            node["title"] = loc.get(node["title"], node["title"])


def _fallbacks(gamedata: Path, parts, tech, loc) -> None:
    """Fill gaps the ConfigCache can leave: localization strings and the tech tree."""
    unresolved = any(p.title.startswith("#") for p in parts)
    if unresolved:
        for cfg in gamedata.rglob("*.cfg"):
            if "locali" in cfg.as_posix().lower():
                for node in parse_file(cfg).children("Localization"):
                    for lang in node.children("en-us"):
                        loc.update(dict(lang.values))
    if not tech:
        mm_tree = gamedata / "ModuleManager.TechTree"
        if mm_tree.exists():
            for node in parse_file(mm_tree).children("TechTree"):
                tech.extend(_tech_nodes(node))


def extract(root: Node, gamedata: Path | None = None):
    """From a parsed ModuleManager.ConfigCache (fully patched)."""
    parts, densities, tech, loc = [], {}, [], {}
    for url_config in root.children("UrlConfig"):
        url = url_config.get("parentUrl", "")
        for node in url_config.nodes:
            _collect(url, node, parts, densities, tech, loc)
    if gamedata is not None:
        _fallbacks(Path(gamedata), parts, tech, loc)
    _localize(parts, tech, loc)
    return parts, densities, tech


def extract_from_gamedata(gamedata: Path):
    """Fallback without a ConfigCache: raw cfgs, ModuleManager patches NOT applied."""
    gamedata = Path(gamedata)
    parts, densities, tech, loc = [], {}, [], {}
    for cfg in gamedata.rglob("*.cfg"):
        url = cfg.relative_to(gamedata).as_posix()
        for node in parse_file(cfg).nodes:
            _collect(url, node, parts, densities, tech, loc)
    _localize(parts, tech, loc)
    return parts, densities, tech
