"""Web search (Tavily) and page fetching, cached in the user DB."""
import json

import httpx

from ..config import settings

BLOCKED_HOSTS = ("localhost", "127.0.0.1", "0.0.0.0", "169.254.")


def web_search(query: str, cache=None, max_results: int = 5) -> dict:
    if not settings.tavily_api_key:
        return {"error": "Web search is not configured (TAVILY_API_KEY missing)."}
    lowered = query.lower()
    if "ksp" not in lowered and "kerbal" not in lowered:
        query = f"{query} Kerbal Space Program"
    key = f"search:{query}"
    if cache is not None:
        hit = cache.cache_get(key)
        if hit:
            return json.loads(hit)
    from tavily import TavilyClient

    res = TavilyClient(api_key=settings.tavily_api_key).search(query, max_results=max_results)
    out = {"results": [{"title": r.get("title"), "url": r.get("url"),
                        "snippet": (r.get("content") or "")[:500]}
                       for r in res.get("results", [])]}
    if cache is not None:
        cache.cache_set(key, json.dumps(out), ttl_hours=24)
    return out


def fetch_page(url: str, cache=None, max_chars: int = 6000) -> dict:
    if not url.startswith(("https://", "http://")) or any(h in url for h in BLOCKED_HOSTS):
        return {"error": "Only public http(s) URLs are allowed."}
    key = f"page:{url}"
    if cache is not None:
        hit = cache.cache_get(key)
        if hit:
            return json.loads(hit)
    import trafilatura

    resp = httpx.get(url, timeout=20, follow_redirects=True,
                     headers={"User-Agent": "kerbal-copilot"})
    resp.raise_for_status()
    text = trafilatura.extract(resp.text) or ""
    out = {"url": url, "text": text[:max_chars]}
    if cache is not None:
        cache.cache_set(key, json.dumps(out), ttl_hours=24)
    return out
