"""
Synthesis Agent
================
Takes whatever sub-agents ran and produces the final report: plain
English + the market's local language, with a clear recommendation
and next steps. This is the only agent whose output the user actually
reads directly, so it runs on Sonnet for quality.
"""

from config.market_context import MarketContext
from utils.llm_client import call_claude

SYNTHESIS_MODEL = "claude-sonnet-5"

SYSTEM_PROMPT_TEMPLATE = """You are writing the final report for a small business \
owner who asked a business question. You have findings from one or more specialist \
agents below. Your job is to synthesize -- not just concatenate -- them into one \
clear, actionable report.

{market_block}

Structure the report as:
1. **Direct Answer** -- one or two sentences, no hedging, answer the actual question
2. **Key Findings** -- the concrete evidence behind the answer (cite which agent /
   what source informed each point)
3. **Recommendation** -- specific, prioritized next steps the owner can act on this
   week and this quarter
4. **Risks / What to Watch** -- honest caveats, especially where research was thin

Write the report in {languages}. If more than one language is listed, write the
Direct Answer and Recommendation sections in both (clearly labeled), so the report
is usable either way. Use plain language a non-technical business owner would
understand -- no jargon, no filler.
"""


def run_synthesis(question: str, market: MarketContext, agent_outputs: dict) -> str:
    findings_block = ""
    for agent_name, output in agent_outputs.items():
        findings_block += f"\n--- {agent_name.upper()} AGENT FINDINGS ---\n{output.get('summary', '')}\n"

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        market_block=market.as_prompt_block(),
        languages=" and ".join(market.languages),
    )

    resp = call_claude(
        system_prompt,
        f"Business owner's original question: {question}\n\nAgent findings:\n{findings_block}",
        model=SYNTHESIS_MODEL,
        max_tokens=2500,
        temperature=0.3,
    )
    return resp.text
