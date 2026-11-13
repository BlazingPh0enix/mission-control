"""User data: saved builds, profile facts, chat history, request usage, HTTP cache.

Uses a Turso embedded replica when TURSO_* is configured (survives Space restarts),
otherwise a plain local SQLite file.
"""
import datetime as dt
import json
import logging
import sqlite3
import threading
from pathlib import Path

from ..config import settings
from ..models import Build, BuildReport

SCHEMA = (
    ("CREATE TABLE IF NOT EXISTS builds (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, "
     "mission TEXT, build_json TEXT, report_json TEXT, status TEXT DEFAULT 'draft', "
     "outcome TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)"),
    "CREATE TABLE IF NOT EXISTS facts (key TEXT PRIMARY KEY, value TEXT, updated_at TEXT)",
    ("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, "
     "content TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)"),
    "CREATE TABLE IF NOT EXISTS usage (day TEXT PRIMARY KEY, requests INTEGER)",
    "CREATE TABLE IF NOT EXISTS http_cache (key TEXT PRIMARY KEY, body TEXT, expires_at TEXT)",
)
log = logging.getLogger(__name__)


def _now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


class UserDB:
    def __init__(self, path: Path | None = None, remote: bool | None = None):
        self._lock = threading.Lock()
        if remote is None:
            remote = bool(settings.turso_database_url and settings.turso_auth_token)
        self.remote = remote
        if self.remote:
            try:
                import libsql  # the "turso" extra locally; requirements.txt on the Space
            except ImportError:
                log.warning("TURSO_* is set but libsql isn't installed; using a local file. "
                            "Install it with: uv sync --extra dev --extra turso")
                self.remote = False
        # The replica gets its own file: an embedded replica can't reuse a plain SQLite file
        default = "user-replica.db" if self.remote else "user.db"
        target = Path(path) if path else Path(settings.data_dir) / default
        target.parent.mkdir(parents=True, exist_ok=True)
        if self.remote:
            self.conn = libsql.connect(str(target), sync_url=settings.turso_database_url,
                                       auth_token=settings.turso_auth_token)
            self.conn.sync()
        else:
            self.conn = sqlite3.connect(target, check_same_thread=False)
        with self._lock:
            for stmt in SCHEMA:
                self.conn.execute(stmt)
            self.conn.commit()

    def _q(self, sql: str, args=(), write: bool = False) -> list:
        with self._lock:
            rows = self.conn.execute(sql, args).fetchall()
            if write:
                self.conn.commit()
                if self.remote:
                    try:
                        self.conn.sync()
                    except Exception as exc:  # the write already reached Turso; sync is a pull
                        log.warning("Turso sync failed: %s", exc)
            return rows

    # builds ------------------------------------------------------------------
    def save_build(self, build: Build, report: BuildReport | None = None, name=None) -> int:
        rows = self._q(
            "INSERT INTO builds (name, mission, build_json, report_json) VALUES (?,?,?,?) "
            "RETURNING id",
            (name or build.name, build.mission, build.model_dump_json(),
             report.model_dump_json() if report else None),
            write=True,
        )
        return rows[0][0]

    def list_builds(self, limit: int = 20) -> list[dict]:
        rows = self._q("SELECT id, name, mission, status, outcome, report_json, created_at "
                       "FROM builds ORDER BY id DESC LIMIT ?", (limit,))
        out = []
        for build_id, name, mission, status, outcome, report_json, created in rows:
            total = json.loads(report_json)["total_dv_vac"] if report_json else None
            out.append({"id": build_id, "name": name, "mission": mission, "status": status,
                        "outcome": outcome, "total_dv": total, "created_at": created})
        return out

    def load_build(self, build_id: int) -> tuple[Build, BuildReport | None]:
        rows = self._q("SELECT build_json, report_json FROM builds WHERE id = ?", (build_id,))
        if not rows:
            raise KeyError(f"No saved build with id {build_id}")
        build = Build.model_validate_json(rows[0][0])
        report = BuildReport.model_validate_json(rows[0][1]) if rows[0][1] else None
        return build, report

    def set_outcome(self, build_id: int, status: str, outcome: str) -> None:
        self._q("UPDATE builds SET status = ?, outcome = ? WHERE id = ?",
                (status, outcome, build_id), write=True)

    def recent_build_summaries(self, n: int = 5) -> list[str]:
        lines = []
        for b in self.list_builds(n):
            dv = f"{b['total_dv']:,.0f} m/s" if b["total_dv"] else "not evaluated"
            note = f" ({b['outcome']})" if b["outcome"] else ""
            lines.append(f"- #{b['id']} {b['name']} for {b['mission']}: {dv}, {b['status']}{note}")
        return lines

    # facts ---------------------------------------------------------------------
    def set_fact(self, key: str, value: str) -> None:
        self._q("INSERT OR REPLACE INTO facts VALUES (?,?,?)",
                (key, value, _now().isoformat()), write=True)

    def get_facts(self) -> dict[str, str]:
        return {k: v for k, v in self._q("SELECT key, value FROM facts")}

    # chat history ------------------------------------------------------------------
    def add_message(self, role: str, content: str) -> None:
        self._q("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content), write=True)

    # usage (OpenRouter counts days in UTC) --------------------------------------------
    def add_request(self) -> None:
        self._q("INSERT INTO usage (day, requests) VALUES (?, 1) "
                "ON CONFLICT(day) DO UPDATE SET requests = requests + 1",
                (_now().date().isoformat(),), write=True)

    def requests_today(self) -> int:
        rows = self._q("SELECT requests FROM usage WHERE day = ?", (_now().date().isoformat(),))
        return rows[0][0] if rows else 0

    # http cache ------------------------------------------------------------------------
    def cache_get(self, key: str) -> str | None:
        rows = self._q("SELECT body, expires_at FROM http_cache WHERE key = ?", (key,))
        if rows and rows[0][1] > _now().isoformat():
            return rows[0][0]
        return None

    def cache_set(self, key: str, body: str, ttl_hours: int = 24) -> None:
        expires = (_now() + dt.timedelta(hours=ttl_hours)).isoformat()
        self._q("INSERT OR REPLACE INTO http_cache VALUES (?,?,?)", (key, body, expires),
                write=True)

    # backup ------------------------------------------------------------------------------
    def export_json(self) -> dict:
        rows = self._q("SELECT id, name, mission, build_json, report_json, status, outcome, "
                       "created_at FROM builds ORDER BY id")
        cols = ("id", "name", "mission", "build_json", "report_json", "status", "outcome",
                "created_at")
        return {"builds": [dict(zip(cols, r, strict=True)) for r in rows],
                "facts": self.get_facts()}
