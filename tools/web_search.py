"""
Web search tool used by the Research Agent.

Uses DuckDuckGo (no API key needed) and re-ranks results so that a
market's trusted_domains (from MarketContext) surface first — this is
one of the main places region-awareness actually lives in the code.
"""

from duckduckgo_search import DDGS


def search_web(query: str, trusted_domains: list[str] | None = None, max_results: int = 8) -> list[dict]:
    """Returns a list of {title, href, body} dicts, trusted-domain
    results first."""
    trusted_domains = trusted_domains or []

    with DDGS() as ddgs:
        raw_results = list(ddgs.text(query, max_results=max_results * 2))

    def is_trusted(r: dict) -> bool:
        return any(domain in r.get("href", "") for domain in trusted_domains)

    trusted = [r for r in raw_results if is_trusted(r)]
    other = [r for r in raw_results if not is_trusted(r)]

    return (trusted + other)[:max_results]


def search_multi(queries: list[str], trusted_domains: list[str] | None = None, per_query: int = 5) -> dict[str, list[dict]]:
    """Run several queries (e.g. one per sub-question the orchestrator
    generated) and return them keyed by query."""
    return {q: search_web(q, trusted_domains, per_query) for q in queries}
