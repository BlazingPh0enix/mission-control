"""Keyword search (SQLite FTS5) over knowledge/*.md, plus the delta-v table parser."""
import re
import sqlite3
import threading
from pathlib import Path

from .config import settings


def _chunks(text: str):
    heading, body = "Intro", []
    for line in text.splitlines():
        if line.startswith("#"):
            if "".join(body).strip():
                yield heading, "\n".join(body).strip()
            heading, body = line.lstrip("#").strip(), []
        else:
            body.append(line)
    if "".join(body).strip():
        yield heading, "\n".join(body).strip()


class KnowledgeBase:
    def __init__(self, folder: Path | None = None):
        self.folder = Path(folder or settings.knowledge_dir)
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.execute("CREATE VIRTUAL TABLE kb USING fts5(file UNINDEXED, heading, body)")
        for md in sorted(self.folder.rglob("*.md")):
            rel = md.relative_to(self.folder).as_posix()
            for heading, body in _chunks(md.read_text(encoding="utf-8")):
                self.conn.execute("INSERT INTO kb VALUES (?, ?, ?)", (rel, heading, body))
        self.conn.commit()

    def search(self, query: str, k: int = 4) -> list[dict]:
        terms = re.findall(r"\w+", query or "")
        if not terms:
            return []
        match = " OR ".join(f'"{t}"' for t in terms)
        with self._lock:
            rows = self.conn.execute(
                "SELECT file, heading, snippet(kb, 2, '[', ']', '...', 40) FROM kb "
                "WHERE kb MATCH ? ORDER BY bm25(kb) LIMIT ?",
                (match, k),
            ).fetchall()
        return [{"file": f, "heading": h, "text": s} for f, h, s in rows]


def load_delta_v(folder: Path | None = None) -> tuple[dict, dict]:
    """Parse the 'Legs' and 'Missions' tables in delta_v_map.md."""
    text = (Path(folder or settings.knowledge_dir) / "delta_v_map.md").read_text(encoding="utf-8")
    legs: dict[str, tuple[str, float]] = {}
    missions: dict[str, list[str]] = {}
    section = ""
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[0]) <= set("-: ") or cells[0] in ("id", "mission"):
            continue
        if section == "legs" and len(cells) >= 3:
            legs[cells[0]] = (cells[1], float(cells[2]))
        elif section == "missions":
            missions[cells[0].lower()] = [c.strip() for c in cells[1].split(",") if c.strip()]
    return legs, missions
