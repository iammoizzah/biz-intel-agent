"""
Document Analyst Agent
=======================
Reads whatever the user uploaded (PDF reports, Excel/CSV ledgers) and
extracts findings relevant to their question. Only activates when the
orchestrator sees uploaded documents in the request.
"""

from config.market_context import MarketContext
from tools.document_parser import parse_document
from utils.llm_client import call_claude

SUBAGENT_MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT_TEMPLATE = """You are a business document analyst. You've been given \
the contents of documents a business owner uploaded (financial reports, sales \
ledgers, inventory sheets, etc.) plus their question.

{market_block}

Extract only what's relevant to their question:
- Concrete numbers (revenue trends, top/bottom performers, cost changes) over vague
  observations
- Call out anomalies or red flags if the data shows them
- If the documents don't actually contain information relevant to the question,
  say that plainly instead of stretching to find a connection
- Output in English; the Synthesis Agent handles translation/formatting
"""


def run_document_analysis(question: str, market: MarketContext, files: list[dict]) -> dict:
    """files: list of {filename, bytes} dicts from the Streamlit uploader."""
    parsed_docs = []
    for f in files:
        try:
            text = parse_document(f["bytes"], f["filename"])
            parsed_docs.append(f"=== {f['filename']} ===\n{text}")
        except Exception as e:
            parsed_docs.append(f"=== {f['filename']} ===\n[Could not parse: {e}]")

    docs_block = "\n\n".join(parsed_docs)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(market_block=market.as_prompt_block())

    resp = call_claude(
        system_prompt,
        f"Business owner's question: {question}\n\nUploaded document contents:\n{docs_block}",
        model=SUBAGENT_MODEL,
        max_tokens=1200,
    )

    return {
        "agent": "document",
        "files_analyzed": [f["filename"] for f in files],
        "summary": resp.text,
    }
