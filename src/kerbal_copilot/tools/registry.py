"""Tool schemas (OpenAI function-calling format) and the dispatch table."""
import json

from ..models import Build
from . import delta_v, mods, techtree, web

STR = {"type": "string"}
# Builds travel as JSON strings: some providers (Gemini/Gemma) reject bare "object" schemas
BUILD_ARG = {"type": "string",
             "description": "Build as a JSON string (schema in the system prompt)"}
ROLES = ["engine", "tank", "command", "decoupler", "parachute", "power", "antenna", "science",
         "rcs", "reaction_wheel", "wheel", "docking", "heat_shield"]


def _fn(name: str, description: str, properties: dict, required=()) -> dict:
    return {"type": "function", "function": {
        "name": name,
        "description": description,
        "parameters": {"type": "object", "properties": properties, "required": list(required)},
    }}


def tool_schemas(web_enabled: bool) -> list[dict]:
    tools = [
        _fn("search_parts", "Search installed parts (stock and modded). Returns internal names "
            "and key stats.",
            {"query": STR, "role": {"type": "string", "enum": ROLES}, "size": STR, "mod": STR,
             "limit": {"type": "integer"}}, ["query"]),
        _fn("get_part", "Full stats for one part by internal name.", {"name": STR}, ["name"]),
        _fn("evaluate_build", "Per-stage delta-v, TWR and burn time for a build.",
            {"build": BUILD_ARG}, ["build"]),
        _fn("mission_budget", "Delta-v required for a mission. Names are '<body> flyby', "
            "'<body> orbit', '<body> landing' or '<body> landing and return' (e.g. 'duna "
            "landing and return'); Eve, Duna and Laythe also have 'aerobraked' versions such "
            "as 'duna aerobraked landing'. Also: 'low kerbin orbit', 'keostationary orbit', "
            "'kerbin escape', 'mun orbit and return', 'minmus orbit and return', "
            "'jool capture', 'jool descent', 'kerbol low orbit'.",
            {"mission": STR}, ["mission"]),
        _fn("search_knowledge", "Search local notes: ascent tips, tech advice, mod notes.",
            {"query": STR}, ["query"]),
        _fn("mod_info", "Installed version, latest release and links for a mod.",
            {"name": STR}, ["name"]),
        _fn("tech_path", "Tech nodes and science needed to unlock the given parts.",
            {"parts": {"type": "array", "items": STR}}, ["parts"]),
        _fn("builds", "List, load or save the player's builds.",
            {"action": {"type": "string", "enum": ["list", "load", "save"]},
             "build_id": {"type": "integer"}, "name": STR, "build": BUILD_ARG},
            ["action"]),
    ]
    if web_enabled:
        tools += [
            _fn("web_search", "Search the web for recent KSP or mod information.",
                {"query": STR}, ["query"]),
            _fn("fetch_page", "Read the text of a web page found by web_search.",
                {"url": STR}, ["url"]),
        ]
    return tools


def parse_build(build) -> Build:
    """Accept a JSON string or an already-decoded object from the model."""
    if isinstance(build, str):
        build = json.loads(build)
    return Build.model_validate(build)


def make_tools(agent) -> dict:
    db, udb, kb = agent.db, agent.user_db, agent.kb

    def search_parts(query, role=None, size=None, mod=None, limit=10):
        return db.search(query, role=role, size=size, mod=mod, limit=min(int(limit), 20))

    def get_part(name):
        return db.get(name).model_dump(exclude={"description"})

    def evaluate_build(build):
        return delta_v.evaluate(parse_build(build), db).model_dump()

    def mission_budget(mission):
        result = delta_v.mission_budget(mission)
        agent.last_budget = result.get("total_dv")
        return result

    def search_knowledge(query):
        return kb.search(query)

    def mod_info(name):
        return mods.mod_info(name, db)

    def tech_path(parts):
        facts = udb.get_facts()
        unlocked = [t.strip() for t in facts.get("unlocked_tech", "").split(",") if t.strip()]
        return techtree.tech_path(parts, db, unlocked)

    def builds(action, build_id=None, name=None, build=None):
        if action == "list":
            return udb.list_builds()
        if action == "load" and build_id is not None:
            loaded, report = udb.load_build(int(build_id))
            return {"build": loaded.model_dump(), "report": report.model_dump() if report else None}
        if action == "save" and build:
            parsed = parse_build(build)
            return {"saved_id": udb.save_build(parsed, delta_v.evaluate(parsed, db), name)}
        return {"error": "Use action list, load (with build_id) or save (with build)."}

    table = {f.__name__: f for f in (search_parts, get_part, evaluate_build, mission_budget,
                                     search_knowledge, mod_info, tech_path, builds)}
    table["web_search"] = lambda query: web.web_search(query, cache=udb)
    table["fetch_page"] = lambda url: web.fetch_page(url, cache=udb)
    return table
