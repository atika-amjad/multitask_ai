from __future__ import annotations


def web_search(query: str, max_results: int = 5) -> list[dict[str, str]]:
    query = query.strip()
    if not query:
        raise ValueError("Search query cannot be empty")

    max_results = max(1, min(max_results, 10))

    try:
        from ddgs import DDGS
    except ImportError as exc:
        raise ImportError(
            "ddgs is required. Install with: pip install ddgs"
        ) from exc

    results: list[dict[str, str]] = []
    for item in DDGS().text(query, max_results=max_results):
        results.append(
            {
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "snippet": item.get("body", ""),
            }
        )
    return results


def format_results(results: list[dict[str, str]]) -> str:
    if not results:
        return "No results found."
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']}\n   {r['url']}\n   {r['snippet']}")
    return "\n\n".join(lines)
