"""
Market Analyst Agent
=====================
Distinct from the Research Agent: Research Agent finds current facts
via web search; this agent reasons about market structure, competitive
positioning, and strategy using those facts (and the model's own
domain knowledge of business strategy frameworks), filtered through
the active MarketContext.
"""

from config.market_context import MarketContext
from utils.llm_client import call_claude

SUBAGENT_MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT_TEMPLATE = """You are a market and competitive strategy analyst for \
small/medium businesses.

{market_block}

Given the business owner's question and any research findings supplied, provide:
- A short read on market structure/competitive dynamics relevant to their question
- Concrete risks and opportunities specific to this market (not generic business
  advice that could apply anywhere)
- Where relevant, reference how the regulatory and cultural context above affects
  the decision

Be direct about trade-offs. Don't manufacture false confidence where the research
findings are thin -- flag what would need more validation.
Output in English; the Synthesis Agent handles translation/formatting.
"""


def run_market_analysis(question: str, market: MarketContext, research_findings: str = "") -> dict:
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(market_block=market.as_prompt_block())
    user_msg = f"Business owner's question: {question}"
    if research_findings:
        user_msg += f"\n\nResearch Agent findings so far:\n{research_findings}"

    resp = call_claude(system_prompt, user_msg, model=SUBAGENT_MODEL, max_tokens=1200)

    return {
        "agent": "market",
        "summary": resp.text,
    }
