# biz-intel-agent

# Business Intelligence Agent

A multi-agent system that answers SMB owners' business questions with
grounded, localized, actionable reports — bilingual by default.


## Why this exists

Generic "ask an AI about your business" tools give generic answers. This
system is grounded in an actual market: it pulls current web data from
trusted local sources, reads your own business documents, reasons about
local competitive/regulatory context, and writes the final report in the
market's language(s) — not just English.

Ships pre-configured for **Pakistan**, with **India** and **UAE** included
to prove the architecture generalizes. Adding a new market is one config
entry — see `config/market_context.py`.

## Architecture

User question (+ optional documents)
│
▼
┌─────────────────┐
│ ORCHESTRATOR │ Sonnet — decides which agents to run
└────────┬─────────┘
│
┌────────┼────────┬─────────────┐
▼ ▼ ▼ │
┌───────┐┌────────┐┌──────────┐ │
│Research││Document││ Market │ │ Haiku — narrow, parallel tasks
│ Agent ││ Agent ││ Analyst │ │
└───┬───┘└───┬────┘└────┬─────┘ │
└────────┴──────────┘ │
▼ │
┌───────────────┐ │
│ SYNTHESIS │ Sonnet — writes the bilingual report
└───────┬────────┘
▼
Markdown report + downloadable PDF


- **Orchestrator** (`agents/orchestrator.py`) — plans which sub-agents a
  question actually needs (not every question needs document analysis).
- **Research Agent** — generates targeted search queries, runs them via
  DuckDuckGo, prioritizes the active market's trusted domains.
- **Document Analyst** — parses uploaded PDF/Excel/CSV and extracts
  what's relevant to the question.
- **Market Analyst** — reasons about competitive structure, risk, and
  strategy, filtered through the market's regulatory/cultural context.
- **Synthesis Agent** — combines everything into one report: direct
  answer, key findings, prioritized recommendations, risks — in the
  market's language(s).

## The market context layer

Nothing region-specific is hardcoded into agent logic. Every agent
receives a `MarketContext` (region, languages, currency, trusted
domains, regulatory notes, cultural notes) which gets rendered into its
system prompt. This is what lets the same codebase serve Pakistan,
India, or any market you configure — see `config/market_context.py`.

## Setup

```bash
git clone <your-repo-url>
cd biz-intel-agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your ANTHROPIC_API_KEY
streamlit run app.py
```

## Stack

- Claude API — Sonnet 5 (orchestrator, synthesis), Haiku 4.5 (sub-agents)
- DuckDuckGo search (no API key required)
- pypdf + pandas/openpyxl for document parsing
- Streamlit UI, fpdf2 for PDF export

## Known follow-ups (being upfront about scope)

- Urdu/Arabic PDF rendering uses DejaVu Sans; proper Nastaliq shaping
  needs a dedicated font (Noto Nastaliq Urdu) — noted in
  `tools/pdf_export.py`.
- No persistent vector DB — documents are read fully in-context per
  session, which is fine at SMB-document scale but wouldn't scale to a
  large document corpus.
- No conversation memory across sessions yet (each question is
  stateless end-to-end).

## Deployment

Free-tier deployable on Streamlit Community Cloud: connect this repo,
set `ANTHROPIC_API_KEY` in the app's secrets, done.

