#  Karobar AI — Pakistan Business Intelligence Agent

A full multi-agent AI system that researches, analyzes, and delivers actionable business intelligence for Pakistani SMB owners — in English and Urdu.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![Claude](https://img.shields.io/badge/Claude-Haiku-purple?style=flat-square)
![Multi-Agent](https://img.shields.io/badge/Architecture-Multi--Agent-orange?style=flat-square)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?style=flat-square)

> Built for Pakistani business owners — describe your problem in Urdu, English, or both.

---

## The Problem

Pakistani SMB owners (retail shops, textile businesses, restaurants, tech startups) face real business problems every day — falling sales, new competition, expansion decisions, market entry. They have no access to affordable business intelligence or consultants who understand local market dynamics.

## The Solution

A multi-agent AI system that acts like a team of business analysts — researching the Pakistan market, analyzing your documents, and delivering a specific, actionable report in minutes.

---

## Agent Architecture

```
User Input (problem + documents + city + industry)
                    ↓
         ORCHESTRATOR AGENT
    Plans research strategy
                    ↓
    ┌───────────────┬───────────────┐
    ↓               ↓               ↓
RESEARCH        DOCUMENT        MARKET
AGENT           ANALYST         ANALYST
Web search      Reads PDFs/     Pakistan
Pakistan        Excel/CSV       market data
market data     uploaded by     competitor
                user            analysis
    └───────────────┴───────────────┘
                    ↓
         SYNTHESIS AGENT
    Combines all findings into
    structured report + Urdu summary
                    ↓
    PDF + TXT downloadable report
```

---

## Features

- **Multi-agent pipeline** — 5 specialized agents working in sequence
- **Live web search** — real Pakistan market data via DuckDuckGo
- **Document analysis** — upload PDFs, Excel, CSV business files
- **Bilingual output** — full report in English + Urdu summary
- **Pakistan context** — 10 cities, 12 industries, local market knowledge
- **Actionable recommendations** — specific actions with timelines and PKR costs
- **Quick wins** — things you can do this week
- **PDF export** — professional downloadable report
- **Live agent log** — see every agent working in real time

---

## Tech Stack

| Tool                                                             | Role                          |
| ---------------------------------------------------------------- | ----------------------------- |
| [Claude API](https://anthropic.com) (Haiku)                      | All 5 agents                  |
| [DuckDuckGo Search](https://pypi.org/project/duckduckgo-search/) | Live Pakistan market research |
| [PyPDF2](https://pypdf2.readthedocs.io)                          | PDF document extraction       |
| [Pandas](https://pandas.pydata.org)                              | Excel/CSV processing          |
| [fpdf2](https://py-fpdf2.readthedocs.io)                         | PDF report generation         |
| [Streamlit](https://streamlit.io)                                | Web UI                        |

---

## Getting Started

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/karobar-ai.git
cd karobar-ai
```

### 2. Virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install

```bash
pip install -r requirements.txt
```

### 4. API Keys

```bash
cp .env.example .env
```

Add to `.env`:

```
ANTHROPIC_API_KEY=your_key_here
```

Get your key at [console.anthropic.com](https://console.anthropic.com)

### 5. Run

```bash
python -m streamlit run app.py
```

---

## Example Problems to Try

- _"My retail shop in Gulberg is losing customers to online sellers. Sales dropped 30%. Should I go online?"_
- _"میں لاہور میں ریستوران کھولنا چاہتا ہوں — کیا یہ اچھا وقت ہے؟"_
- _"Our textile export business needs new markets beyond Middle East"_
- _"Should I open a second branch in DHA or invest in digital marketing?"_

---

## What I Learned Building This

- Designing multi-agent systems with orchestrator + specialized sub-agents
- Passing context between agents in a pipeline
- Combining RAG (documents) + web search in one system
- Bilingual prompting for Urdu/English output
- Building real-time agent status dashboards in Streamlit
- PDF generation with structured business report formatting
- Designing for a specific user — Pakistani SMB owners

---

## Phase 3 Concepts Demonstrated

- **Multi-agent systems** — 5 agents with distinct roles
- **Tool use** — web search as a tool for research and market agents
- **RAG** — uploaded documents as knowledge base
- **Orchestration** — coordinator agent plans the pipeline
- **Structured output** — JSON synthesis for consistent reports
- **Planning + Reflection** — orchestrator plans, synthesis agent reflects on all findings

## Author

**Moizzah** — [@iammoizzah](https://github.com/iammoizzah)
