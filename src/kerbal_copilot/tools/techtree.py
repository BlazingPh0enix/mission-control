"""Which tech nodes (and how much science) a set of parts needs."""


def tech_path(part_names: list[str], db, unlocked=()) -> dict:
    nodes = db.tech_nodes()
    done = set(unlocked) | {"start"}
    memo: dict[str, float] = {}

    def chain_cost(node_id: str, stack: frozenset = frozenset()) -> float:
        """Rough cost to reach a node; only used to pick the cheapest parent."""
        if node_id in done or node_id not in nodes:
            return 0.0
        if node_id in memo:
            return memo[node_id]
        if node_id in stack:
            return float("inf")
        node = nodes[node_id]
        costs = [chain_cost(p, stack | {node_id}) for p in node["parents"] if p in nodes]
        if not costs:
            extra = 0.0
        elif node["any"]:
            extra = min(costs)
        else:
            extra = sum(costs)
        memo[node_id] = node["cost"] + extra
        return memo[node_id]

    needed: dict[str, dict] = {}

    def require(node_id: str) -> None:
        if node_id in done or node_id in needed or node_id not in nodes:
            return
        node = nodes[node_id]
        needed[node_id] = node
        parents = [p for p in node["parents"] if p in nodes]
        if not parents:
            return
        if node["any"]:
            require(min(parents, key=chain_cost))
        else:
            for parent in parents:
                require(parent)

    unknown, by_part = [], {}
    for name in part_names:
        try:
            tech = db.get(name).tech_required
        except KeyError:
            unknown.append(name)
            continue
        by_part[name] = tech
        if tech:
            require(tech)

    ordered = sorted(needed.items(), key=lambda kv: kv[1]["cost"])
    return {
        "nodes": [{"id": k, "title": v["title"], "cost": v["cost"]} for k, v in ordered],
        "total_science": sum(v["cost"] for v in needed.values()),
        "part_tech": by_part,
        "unknown_parts": unknown,
    }
