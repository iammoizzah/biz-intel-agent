"""
Research Agent
==============
Given a business question and the active MarketContext, generates
targeted search queries, runs them, and produces a grounded summary
with source attribution. Runs on Haiku -- this is a narrow, well-scoped
task and doesn't need Sonnet-level reasoning.
"""

from config.market_context import MarketContext
from tools.web_search import search_multi
from utils.llm_client import call_claude

SUBAGENT_MODEL = "claude-haiku-4-5-20251001"

QUERY_GEN_PROMPT = """You are a research query planner for a business intelligence \
system. Given a business owner's question, generate 3-4 specific, high-signal web \
search queries that would surface real, current data (market size, competitor names, \
pricing, regulations, trends). Prefer specific over generic.

Output ONLY the queries, one per line, no numbering, no extra text."""

SUMMARIZE_PROMPT_TEMPLATE = """You are a market research analyst. Summarize the \
search results below into a factual briefing for the business owner's question.

{market_block}

Rules:
- Only state what's supported by the search results. If results are thin or unclear
  on something, say so plainly rather than filling gaps with assumptions.
- Note the source (domain) next to each claim.
- Keep it to tight bullet points, not prose paragraphs.
- Output in English; the Synthesis Agent will handle translation/bilingual formatting.
"""


def generate_queries(question: str) -> list[str]:
    resp = call_claude(QUERY_GEN_PROMPT, question, model=SUBAGENT_MODEL, max_tokens=200)
    return [line.strip() for line in resp.text.strip().split("\n") if line.strip()]


def run_research(question: str, market: MarketContext) -> dict:
    queries = generate_queries(question)
    results = search_multi(queries, trusted_domains=market.trusted_domains, per_query=5)

    # Flatten results into a compact context block for the summarizer
    results_block = ""
    for query, hits in results.items():
        results_block += f"\nQuery: {query}\n"
        for hit in hits:
            results_block += f"- [{hit.get('href', '')}] {hit.get('title', '')}: {hit.get('body', '')[:300]}\n"

    system_prompt = SUMMARIZE_PROMPT_TEMPLATE.format(market_block=market.as_prompt_block())
    summary = call_claude(
        system_prompt,
        f"Business owner's question: {question}\n\nSearch results:\n{results_block}",
        model=SUBAGENT_MODEL,
        max_tokens=1200,
    )

    return {
        "agent": "research",
        "queries_used": queries,
        "raw_results": results,
        "summary": summary.text,
    }
