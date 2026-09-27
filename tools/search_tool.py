"""
tools/search_tool.py
---------------------
A real, callable *tool* the Research Agent can invoke through OpenAI
function calling. It looks up comparable / precedent policies on the
public web using DuckDuckGo (no API key required).

If the search backend is unreachable (offline grading environment, rate
limit, etc.) it falls back to a small canned dataset so the pipeline keeps
working end-to-end for a demo/report run.
"""

from typing import List, Dict

TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_similar_policies",
        "description": (
            "Search the public web for real-world policies that are "
            "similar to, or precedents for, the policy being analyzed. "
            "Use this to ground the analysis in actual examples from "
            "other cities/states/countries instead of guessing."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Search query, e.g. 'congestion pricing policy "
                        "examples cities' or 'plastic bag ban policy "
                        "impact evaluation'."
                    ),
                },
                "max_results": {
                    "type": "integer",
                    "description": "How many results to return (default 5).",
                },
            },
            "required": ["query"],
        },
    },
}

_FALLBACK_RESULTS = [
    {
        "title": "Fallback result (offline mode)",
        "snippet": (
            "Live web search was unavailable, so this run used a cached "
            "placeholder instead of a real precedent. Re-run with network "
            "access for grounded research results."
        ),
        "url": "",
    }
]


def search_similar_policies(query: str, max_results: int = 5) -> List[Dict]:
    """Execute the web search and return a list of {title, snippet, url}."""
    try:
        from duckduckgo_search import DDGS  # imported lazily - optional dep

        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(
                    {
                        "title": r.get("title", ""),
                        "snippet": r.get("body", ""),
                        "url": r.get("href", ""),
                    }
                )
        return results or _FALLBACK_RESULTS
    except Exception as exc:  # noqa: BLE001 - we want any failure to degrade gracefully
        return [
            {
                "title": "Search failed",
                "snippet": f"{type(exc).__name__}: {exc}",
                "url": "",
            }
        ] + _FALLBACK_RESULTS


# Registry the orchestration layer uses to dispatch tool calls by name.
AVAILABLE_TOOLS = {
    "search_similar_policies": search_similar_policies,
}
