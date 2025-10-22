from typing import Dict, Any, List
from .config import make_tavily


def search_ai_news(state: Dict[str, Any]) -> Dict[str, Any]:
    tavily = make_tavily()
    queries: List[str] = state.get("queries") or [
        "AI business impact 2024", "AI productivity tools", "AI job market trends", 
        "AI startup funding", "AI enterprise adoption", "AI career opportunities",
        "AI automation success stories", "AI industry disruption", "AI skills demand"
    ]

    aggregated: List[Dict[str, Any]] = []
    for q in queries:
        res = tavily.search(query=q, search_depth="advanced", include_answer=False, max_results=8)
        for item in res.get("results", []):
            aggregated.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "content": item.get("content"),
                "score": item.get("score", 0),
                "source_query": q,
            })

    # Deduplicate by URL while keeping best score
    by_url: Dict[str, Dict[str, Any]] = {}
    for r in aggregated:
        url = r.get("url")
        if not url:
            continue
        prev = by_url.get(url)
        if prev is None or (r.get("score", 0) > prev.get("score", 0)):
            by_url[url] = r

    # Sort by score descending
    deduped = sorted(by_url.values(), key=lambda x: x.get("score", 0), reverse=True)

    return {
        **state,
        "results": deduped
    }
