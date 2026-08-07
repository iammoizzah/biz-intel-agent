"""
Orchestrator Agent
==================
The entry point. Decides which sub-agents to activate for a given
question, runs them, then hands everything to the Synthesis Agent.

Runs on Sonnet -- this is the one agent that needs real judgment
(routing decisions, not just narrow extraction).
"""

import json
from dataclasses import dataclass, field

from config.market_context import MarketContext
from agents.research_agent import run_research
from agents.document_agent import run_document_analysis
from agents.market_agent import run_market_analysis
from agents.synthesis_agent import run_synthesis
from utils.llm_client import call_claude

ORCHESTRATOR_MODEL = "claude-sonnet-5"

PLAN_PROMPT_TEMPLATE = """You are the orchestrator for a business intelligence \
system. Given a business owner's question, decide which specialist agents are \
needed to answer it well:

- "research": needs current web data (market size, competitor names, pricing,
  regulations, digital payment options, trends)
- "document": the user uploaded documents that should be analyzed (only if
  has_documents is true below)
- "market": needs competitive/strategic reasoning about market structure,
  positioning, or risk

has_documents: {has_documents}

Most questions need "research" and "market" at minimum. Only include "document" if
has_documents is true. Respond with ONLY a JSON array of agent names, e.g.
["research", "market"] or ["research", "document", "market"]. No other text."""


@dataclass
class OrchestrationResult:
    plan: list[str]
    agent_outputs: dict = field(default_factory=dict)
    final_report: str = ""


def plan_agents(question: str, has_documents: bool) -> list[str]:
    system_prompt = PLAN_PROMPT_TEMPLATE.format(has_documents=has_documents)
    resp = call_claude(system_prompt, question, model=ORCHESTRATOR_MODEL, max_tokens=100)
    try:
        agents = json.loads(resp.text.strip())
        valid = {"research", "document", "market"}
        return [a for a in agents if a in valid]
    except (json.JSONDecodeError, TypeError):
        # Fail safe rather than fail loud: a sane default beats a crash
        return ["research", "market"]


def run_pipeline(
    question: str,
    market: MarketContext,
    uploaded_files: list[dict] | None = None,
    progress_callback=None,
) -> OrchestrationResult:
    """progress_callback(str) lets the Streamlit UI show live status."""
    uploaded_files = uploaded_files or []

    def report(msg):
        if progress_callback:
            progress_callback(msg)

    report("Planning which agents to run...")
    plan = plan_agents(question, has_documents=bool(uploaded_files))

    outputs = {}

    if "document" in plan and uploaded_files:
        report("Document Analyst reading uploaded files...")
        outputs["document"] = run_document_analysis(question, market, uploaded_files)

    research_findings = ""
    if "research" in plan:
        report("Research Agent searching the web...")
        outputs["research"] = run_research(question, market)
        research_findings = outputs["research"]["summary"]

    if "market" in plan:
        report("Market Analyst assessing competitive landscape...")
        outputs["market"] = run_market_analysis(question, market, research_findings)

    report("Synthesis Agent writing the final report...")
    final_report = run_synthesis(question, market, outputs)

    return OrchestrationResult(plan=plan, agent_outputs=outputs, final_report=final_report)
