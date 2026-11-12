import json
import re
import sqlite3
from pathlib import Path

from ..models import Part

SCHEMA = """
CREATE TABLE parts (
    name TEXT PRIMARY KEY,
    title TEXT,
    mod TEXT,
    category TEXT,
    size TEXT,
    mass_t REAL,
    cost REAL,
    tech_required TEXT,
    roles TEXT,
    data TEXT
);
CREATE VIRTUAL TABLE parts_fts USING fts5(name UNINDEXED, title, mod, roles, description);
CREATE TABLE resources (name TEXT PRIMARY KEY, density REAL);
CREATE TABLE tech_nodes (id TEXT PRIMARY KEY, title TEXT, cost INTEGER, parents TEXT,
                         any_parent INTEGER);
CREATE TABLE mods (
  identifier TEXT PRIMARY KEY, name TEXT, version TEXT, latest TEXT, installed INTEGER,
  abstract TEXT, ksp_max TEXT, spacedock_id INTEGER, repo TEXT, homepage TEXT
);
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
"""
MOD_COLUMNS = ("identifier", "name", "version", "latest", "installed", "abstract", "ksp_max", "spacedock_id", "repo", "homepage")

class PartsDB:
    def __init__(self, path):
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._parts: dict[str, Part] = {}
        self._densities: dict[str, float] | None = None

    @classmethod
    def build(cls, path, parts, densities, tech, mods=(), meta=None) -> "PartsDB":
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            path.unlink()
        db = cls(path)
        c = db.conn
        c.executescript(SCHEMA)
        seen = set()
        for p in parts:
            if p.name in seen:
                continue
            seen.add(p.name)
            roles = "," + ",".join(p.roles) + ","
            c.execute("INSERT INTO parts VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (p.name, p.title, p.mod, p.category, p.size, p.mass_t, p.cost,
                       p.tech_required, roles, p.model_dump_json()))
            c.execute("INSERT INTO parts_fts VALUES (?,?,?,?,?)",
                      (p.name, p.title, p.mod, " ".join(p.roles), p.description))
        c.executemany("INSERT OR REPLACE INTO resources VALUES (?,?)", list(densities.items()))
        for t in tech:
            c.execute("INSERT OR REPLACE INTO tech_nodes VALUES (?,?,?,?,?)",
                      (t["id"], t["title"], t["cost"], json.dumps(t["parents"]),
                       int(t.get("any", False))))
        for m in mods:
            c.execute("INSERT OR REPLACE INTO mods VALUES (?,?,?,?,?,?,?,?,?,?)",
                      tuple(m.get(k) for k in MOD_COLUMNS))
        for key, value in (meta or {}).items():
            c.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", (key, str(value)))
        c.commit()
        return db

    def get(self, name: str) -> Part:
        if name not in self._parts:
            row = self.conn.execute("SELECT data FROM parts WHERE name = ?", (name,)).fetchone()
            if row is None:
                raise KeyError(f"Unknown part '{name}'. Use search_parts to find valid names.")
            self._parts[name] = Part.model_validate_json(row["data"])
        return self._parts[name]

    def density(self, resource: str) -> float:
        if self._densities is None:
            rows = self.conn.execute("SELECT name, density FROM resources")
            self._densities = {r["name"]: r["density"] for r in rows}
        return self._densities.get(resource, 0.0)

    def search(self, query: str = "", role=None, size=None, mod=None, limit: int = 10):
        terms = re.findall(r"\w+", query or "")
        args: list = []
        if terms:
            sql = ("SELECT p.* FROM parts_fts f JOIN parts p ON p.name = f.name "
                   "WHERE parts_fts MATCH ?")
            args.append(" OR ".join(f'"{t}"' for t in terms))
            order = " ORDER BY bm25(parts_fts)"
        else:
            sql = "SELECT p.* FROM parts p WHERE 1=1"
            order = " ORDER BY p.mod, p.name"
        if role:
            sql += " AND p.roles LIKE ?"
            args.append(f"%,{role},%")
        if size:
            sql += " AND p.size = ?"
            args.append(size)
        if mod:
            sql += " AND p.mod LIKE ?"
            args.append(f"%{mod}%")
        sql += order + " LIMIT ?"
        args.append(int(limit))
        return [self._summary(r) for r in self.conn.execute(sql, args)]

    @staticmethod
    def _summary(row) -> dict:
        p = Part.model_validate_json(row["data"])
        out = {"name": p.name, "title": p.title, "mod": p.mod, "size": p.size,
               "mass_t": p.mass_t, "cost": p.cost, "tech": p.tech_required, "roles": p.roles}
        if p.engine:
            out["thrust_kn"] = p.engine.max_thrust_kn
            out["isp_vac"] = round(p.engine.isp_vac)
            out["isp_asl"] = round(p.engine.isp_asl)
        if p.resources:
            out["resources"] = {k: v for k, v in p.resources.items() if v}
        return out

    def tech_nodes(self) -> dict[str, dict]:
        rows = self.conn.execute("SELECT id, title, cost, parents, any_parent FROM tech_nodes")
        return {r["id"]: {"title": r["title"], "cost": r["cost"],
                          "parents": json.loads(r["parents"]), "any": bool(r["any_parent"])}
                for r in rows}

    def mods(self) -> list[dict]:
        return [dict(r) for r in self.conn.execute("SELECT * FROM mods ORDER BY identifier")]

    def meta(self) -> dict:
        return {r["key"]: r["value"] for r in self.conn.execute("SELECT * FROM meta")}