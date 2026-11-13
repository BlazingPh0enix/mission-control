"""Mod metadata: installed list (CKAN), CKAN-meta index, SpaceDock and GitHub releases."""
import io
import json
import re
import tarfile
import time
from pathlib import Path
from urllib.parse import quote

import httpx

CKAN_META_TARBALL = "https://github.com/KSP-CKAN/CKAN-meta/archive/master.tar.gz"
SPACEDOCK = "https://spacedock.info/api"
HEADERS = {"User-Agent": "kerbal-copilot"}
_cache: dict[str, tuple[float, object]] = {}


def _get_json(url: str, ttl: int = 24 * 3600):
    hit = _cache.get(url)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    resp = httpx.get(url, timeout=20, follow_redirects=True, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    _cache[url] = (time.time(), data)
    return data


def read_installed_ckan(ksp_dir) -> dict[str, str]:
    """identifier -> version from <KSP>/CKAN/installed-<instance>.ckan

    CKAN also keeps dated copies (installed-<instance>-2026-01-31_12-00-00.ckan); the
    undated file is the current one. CKAN leaves out auto-installed dependencies."""
    files = list((Path(ksp_dir) / "CKAN").glob("installed-*.ckan"))
    current = [f for f in files if not re.search(r"-\d{4}-\d{2}-\d{2}_", f.name)]
    if not files:
        return {}
    newest = max(current or files, key=lambda f: f.stat().st_mtime)
    meta = json.loads(newest.read_text(encoding="utf-8-sig"))
    out = {}
    for dep in meta.get("depends") or meta.get("recommends") or []:
        if isinstance(dep, dict) and "name" in dep:
            out[dep["name"]] = dep.get("version") or dep.get("min_version") or ""
    return out


def version_key(version) -> tuple:
    """Sort key for CKAN versions: '1:2.10.0' > '2.9.1' > 'v2.9'. Epoch first, then
    numbers compared as numbers and text as text."""
    text = str(version or "")
    epoch, _, rest = text.rpartition(":") if ":" in text else ("0", "", text)
    parts = re.findall(r"\d+|[A-Za-z]+", rest)
    key = tuple((0, int(p), "") if p.isdigit() else (1, 0, p.lower()) for p in parts)
    return (int(epoch) if epoch.isdigit() else 0, key)


def build_ckan_index(installed: dict[str, str]) -> list[dict]:
    """Download CKAN-meta once and keep metadata for installed mods only."""
    resp = httpx.get(CKAN_META_TARBALL, timeout=180, follow_redirects=True, headers=HEADERS)
    resp.raise_for_status()
    found: dict[str, list[dict]] = {}
    with tarfile.open(fileobj=io.BytesIO(resp.content), mode="r:gz") as tar:
        for member in tar:
            pieces = member.name.split("/")
            if len(pieces) != 3 or not member.name.endswith(".ckan"):
                continue
            if pieces[1] not in installed:
                continue
            fh = tar.extractfile(member)
            if fh is None:
                continue
            try:
                found.setdefault(pieces[1], []).append(json.loads(fh.read().decode("utf-8")))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
    rows = []
    for ident, version in installed.items():
        metas = found.get(ident, [])
        latest = max(metas, key=lambda m: version_key(m.get("version")), default={})
        current = next((m for m in metas if m.get("version") == version), latest)
        res = current.get("resources") or latest.get("resources") or {}
        spacedock = re.search(r"/mod/(\d+)", res.get("spacedock") or "")
        rows.append({
            "identifier": ident,
            "name": current.get("name", ident),
            "version": version,
            "latest": latest.get("version"),
            "installed": 1,
            "abstract": current.get("abstract"),
            "ksp_max": current.get("ksp_version_max") or current.get("ksp_version"),
            "spacedock_id": int(spacedock.group(1)) if spacedock else None,
            "repo": res.get("repository"),
            "homepage": res.get("homepage"),
        })
    return rows


def spacedock_search(query: str) -> list[dict]:
    data = _get_json(f"{SPACEDOCK}/search/mod?query={quote(query)}")
    return [{"id": m.get("id"), "name": m.get("name"), "author": m.get("author"),
             "summary": m.get("short_description"), "downloads": m.get("downloads")}
            for m in (data or [])[:10]]


def spacedock_latest(mod_id: int) -> dict:
    data = _get_json(f"{SPACEDOCK}/mod/{mod_id}/latest")
    return {"version": data.get("friendly_version"), "game_version": data.get("game_version"),
            "changelog": (data.get("changelog") or "")[:1500]}


def github_latest(repo_url: str) -> dict:
    m = re.search(r"github\.com/([^/]+)/([^/#?]+)", repo_url or "")
    if not m:
        return {"error": f"Not a GitHub URL: {repo_url}"}
    owner, repo = m.group(1), m.group(2).removesuffix(".git")
    data = _get_json(f"https://api.github.com/repos/{owner}/{repo}/releases/latest")
    return {"tag": data.get("tag_name"), "name": data.get("name"),
            "published": data.get("published_at"), "url": data.get("html_url"),
            "notes": (data.get("body") or "")[:1500]}


def mod_info(name: str, db) -> dict:
    query = (name or "").lower()
    match = next((m for m in db.mods()
                  if query in (m.get("identifier") or "").lower()
                  or query in (m.get("name") or "").lower()), None)
    info: dict = {"query": name, "installed": match}
    try:
        if match and match.get("spacedock_id"):
            info["spacedock_latest"] = spacedock_latest(match["spacedock_id"])
        elif match and "github.com" in (match.get("repo") or ""):
            info["github_latest"] = github_latest(match["repo"])
        else:
            info["spacedock_search"] = spacedock_search(name)[:5]
    except httpx.HTTPError as exc:
        info["lookup_error"] = str(exc)
    return info
