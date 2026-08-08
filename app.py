import os
import io
import json
import time
import base64
import requests
import anthropic
import pandas as pd
import streamlit as st
from fpdf import FPDF
from dotenv import load_dotenv
from datetime import datetime
from duckduckgo_search import DDGS
import PyPDF2
import unicodedata

load_dotenv()
client = anthropic.Anthropic()

st.set_page_config(
    page_title="Karobar AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body,[class*="css"]{font-family:'Sora',sans-serif;background:#F5F3EF;color:#1A1A1A;}
section[data-testid="stSidebar"]{background:#1A1A1A!important;border-right:1px solid #2A2A2A!important;}
section[data-testid="stSidebar"] *{color:#E0E0E0!important;}
section[data-testid="stSidebar"] .stSelectbox>div>div{background:#2A2A2A!important;border:1px solid #3A3A3A!important;color:#E0E0E0!important;}
section[data-testid="stSidebar"] div[data-testid="stTextInput"] input{background:#2A2A2A!important;border:1px solid #3A3A3A!important;color:#E0E0E0!important;}
section[data-testid="stSidebar"] div[data-testid="stFileUploader"]{background:#2A2A2A!important;border:1px dashed #3A3A3A!important;border-radius:8px!important;}
.hero{background:#1A1A1A;border-radius:16px;padding:2.5rem;margin-bottom:1.5rem;position:relative;overflow:hidden;}
.hero::before{content:'کاروبار';position:absolute;right:-1rem;top:-1rem;font-size:8rem;color:rgba(255,255,255,0.03);font-weight:800;pointer-events:none;}
.hero-eye{font-size:0.65rem;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;color:#C9A84C;margin-bottom:0.5rem;}
.hero h1{font-size:2.6rem;font-weight:800;color:#FFFFFF;line-height:1.1;letter-spacing:-0.03em;}
.hero h1 em{color:#C9A84C;font-style:normal;}
.hero-sub{font-size:0.9rem;color:#666;margin-top:0.4rem;font-weight:300;}
.agent-status{background:#111;border:1px solid #222;border-radius:12px;padding:1rem 1.25rem;margin:1rem 0;font-family:'JetBrains Mono',monospace;font-size:0.75rem;max-height:220px;overflow-y:auto;}
.agent-log{padding:0.2rem 0;line-height:1.6;}
.agent-log.orchestrator{color:#C9A84C;}
.agent-log.research{color:#60A5FA;}
.agent-log.document{color:#34D399;}
.agent-log.market{color:#F472B6;}
.agent-log.synthesis{color:#A78BFA;}
.agent-log.done{color:#FFFFFF;font-weight:600;}
.agent-log.err{color:#F87171;}
.agent-pill{display:inline-flex;align-items:center;gap:0.4rem;padding:0.25rem 0.75rem;border-radius:999px;font-size:0.68rem;font-weight:600;font-family:'JetBrains Mono',monospace;letter-spacing:0.05em;margin:0.2rem;}
.pill-active{background:#C9A84C22;border:1px solid #C9A84C;color:#C9A84C;}
.pill-done{background:#34D39922;border:1px solid #34D399;color:#34D399;}
.pill-idle{background:#2A2A2A22;border:1px solid #3A3A3A;color:#666;}
.section-head{font-family:'JetBrains Mono',monospace;font-size:0.62rem;letter-spacing:0.18em;text-transform:uppercase;color:#888;padding-bottom:0.5rem;border-bottom:1px solid #E0D8CC;margin:1.75rem 0 1rem;}
.report-card{background:#FFFFFF;border:1px solid #E0D8CC;border-radius:12px;padding:1.5rem;margin:0.75rem 0;}
.report-card h3{font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#C9A84C;margin-bottom:0.6rem;}
.report-card p,.report-card li{font-size:0.88rem;color:#444;line-height:1.75;font-weight:300;}
.report-card ul{padding-left:1.25rem;}
.report-card strong{color:#1A1A1A;font-weight:600;}
.insight-grid{display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;margin:0.75rem 0;}
.insight-box{background:#FFFFFF;border:1px solid #E0D8CC;border-radius:10px;padding:1.1rem 1.25rem;}
.insight-box h4{font-size:0.68rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#888;margin-bottom:0.4rem;}
.insight-box p{font-size:0.85rem;color:#444;line-height:1.7;}
.urdu-box{background:#FFFFFF;border:1px solid #E0D8CC;border-right:3px solid #C9A84C;border-radius:10px;padding:1.25rem 1.5rem;direction:rtl;text-align:right;font-size:0.95rem;line-height:2;color:#333;}
.stButton>button{background:#1A1A1A!important;color:#C9A84C!important;border:none!important;border-radius:8px!important;padding:0.7rem 2rem!important;font-family:'Sora',sans-serif!important;font-weight:700!important;font-size:0.88rem!important;width:100%!important;letter-spacing:0.03em!important;}
.stButton>button:hover{background:#2A2A2A!important;}
.stDownloadButton>button{background:transparent!important;color:#1A1A1A!important;border:1.5px solid #1A1A1A!important;border-radius:8px!important;font-family:'Sora',sans-serif!important;font-weight:600!important;width:100%!important;}
div[data-testid="stTextArea"] textarea{background:#FFFFFF!important;border:1.5px solid #E0D8CC!important;border-radius:8px!important;font-family:'Sora',sans-serif!important;}
div[data-testid="stTextArea"] textarea:focus{border-color:#C9A84C!important;}
#MainMenu,footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ── Helpers


def web_search(query: str, n: int = 5) -> str:
    try:
        with DDGS() as d:
            results = list(d.text(query, max_results=n))
        return "\n".join([f"Title: {r.get('title', '')}\nURL: {r.get('href', '')}\nSnippet: {r.get('body', '')}\n" for r in results])
    except Exception as e:
        return f"Search failed: {e}"


def extract_pdf(file) -> str:
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        return "\n\n".join(p.extract_text() or "" for p in reader.pages)[:8000]
    except Exception:
        return ""


def extract_excel(file) -> str:
    try:
        df = pd.read_excel(file)
        return df.to_string(index=False)[:6000]
    except Exception:
        return ""


def extract_csv(file) -> str:
    try:
        df = pd.read_csv(file)
        return df.to_string(index=False)[:6000]
    except Exception:
        return ""


def read_uploaded_files(files) -> str:
    all_content = []
    for f in files:
        name = f.name.lower()
        if name.endswith(".pdf"):
            content = extract_pdf(f)
        elif name.endswith((".xlsx", ".xls")):
            content = extract_excel(f)
        elif name.endswith(".csv"):
            content = extract_csv(f)
        else:
            try:
                content = f.read().decode("utf-8", errors="ignore")[:5000]
            except Exception:
                content = ""
        if content:
            all_content.append(f"[FILE: {f.name}]\n{content}")
    return "\n\n{'='*50}\n\n".join(all_content)


def clean_for_pdf(text: str) -> str:
    text = unicodedata.normalize('NFKD', str(text))
    replacements = {'\u2022': '-', '\u2013': '-', '\u2014': '--', '\u2018': "'", '\u2019': "'",
                    '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u25cf': '-', '\u2043': '-', '\u00b7': '-'}
    for c, r in replacements.items():
        text = text.replace(c, r)
    return text.encode('latin-1', 'ignore').decode('latin-1')

# ── Agent System


def run_agent(name: str, system: str, prompt: str, log_fn, log_type: str, tools=None) -> str:
    log_fn(f"[{name}] Starting...", log_type)
    messages = [{"role": "user", "content": prompt}]

    tool_defs = []
    if tools:
        tool_defs = [{
            "name": "web_search",
            "description": "Search the web for Pakistan-specific business information, market data, regulations, and trends",
            "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
        }]

    for _ in range(5):
        kwargs = dict(model="claude-haiku-4-5", max_tokens=2000,
                      system=system, messages=messages)
        if tool_defs:
            kwargs["tools"] = tool_defs

        response = client.messages.create(**kwargs)

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use" and block.name == "web_search":
                    q = block.input.get("query", "")
                    log_fn(f"[{name}] Searching: {q[:55]}...", log_type)
                    result = web_search(q)
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": block.id, "content": result})
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            for block in response.content:
                if hasattr(block, "text") and block.text.strip():
                    log_fn(f"[{name}] Done ✓", log_type)
                    return block.text.strip()
            break

    return "Agent could not complete analysis."


def orchestrator_agent(problem: str, doc_content: str, city: str, industry: str, log_fn) -> dict:
    log_fn("[ORCHESTRATOR] Planning research strategy...", "orchestrator")

    system = """You are the orchestrator agent for a Pakistani business intelligence system.
Analyze the business problem and create a research plan.
Return ONLY valid JSON with this structure:
{
  "research_queries": ["query1 Pakistan", "query2 Pakistan"],
  "market_queries": ["market query1", "market query2"],
  "key_questions": ["question1", "question2", "question3"],
  "analysis_focus": "what to focus on"
}"""

    prompt = f"""Business problem: {problem}
City: {city}
Industry: {industry}
Has documents: {"Yes — " + str(len(doc_content))[:20] + " chars" if doc_content else "No"}

Create a research plan for this Pakistani business problem."""

    response = client.messages.create(
        model="claude-haiku-4-5", max_tokens=800, system=system,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip().replace(
        "```json", "").replace("```", "").strip()
    try:
        plan = json.loads(raw)
        log_fn(
            f"[ORCHESTRATOR] Plan ready — {len(plan.get('research_queries', []))} research tasks", "orchestrator")
        return plan
    except Exception:
        return {"research_queries": [f"{problem} Pakistan {city}", f"{industry} market Pakistan"],
                "market_queries": [f"{industry} Pakistan market 2024", f"business trends {city} Pakistan"],
                "key_questions": ["What are the main challenges?", "What are market opportunities?"],
                "analysis_focus": problem}


def research_agent(queries: list, city: str, log_fn) -> str:
    log_fn("[RESEARCH AGENT] Starting web research...", "research")
    all_results = []
    for q in queries[:4]:
        log_fn(f"[RESEARCH AGENT] Searching: {q[:55]}", "research")
        result = web_search(f"{q} {city} Pakistan")
        all_results.append(result)
        time.sleep(0.3)

    synthesis_prompt = f"""Synthesize these web search results about a Pakistani business problem.
Focus on: facts, statistics, trends, regulations relevant to Pakistan.

Search Results:
{chr(10).join(all_results[:3])}

Provide a structured research summary with key findings, statistics, and Pakistan-specific insights."""

    return run_agent("RESEARCH", """You are a Pakistan business research specialist.
Extract and synthesize relevant market data, statistics, and insights.
Focus on Pakistan-specific context — local regulations, market conditions, cultural factors.""",
                     synthesis_prompt, log_fn, "research")


def document_agent(doc_content: str, problem: str, log_fn) -> str:
    if not doc_content:
        log_fn("[DOCUMENT AGENT] No documents — skipping", "document")
        return "No documents were uploaded for analysis."

    log_fn("[DOCUMENT AGENT] Analyzing uploaded documents...", "document")
    prompt = f"""Analyze these business documents in context of this problem: {problem}

Documents:
{doc_content[:6000]}

Extract:
- Key financial metrics or performance data
- Business strengths and weaknesses visible in data
- Specific numbers, trends, or patterns
- Anything directly relevant to the business problem"""

    return run_agent("DOCUMENT ANALYST", """You are a business document analyst specializing in Pakistani SMBs.
Extract actionable insights from business documents — financials, reports, data files.
Be specific with numbers and facts from the documents.""",
                     prompt, log_fn, "document")


def market_agent(queries: list, industry: str, city: str, log_fn) -> str:
    log_fn("[MARKET AGENT] Analyzing Pakistan market...", "market")
    all_results = []
    for q in queries[:3]:
        log_fn(f"[MARKET AGENT] Researching: {q[:55]}", "market")
        result = web_search(q)
        all_results.append(result)
        time.sleep(0.3)

    prompt = f"""Analyze the {industry} market in {city}, Pakistan based on these search results:

{chr(10).join(all_results)}

Provide:
- Market size and growth trends in Pakistan
- Key competitors and market leaders
- Consumer behavior and preferences (Pakistani context)
- Regulatory environment
- Opportunities and threats specific to {city}"""

    return run_agent("MARKET ANALYST", f"""You are a Pakistan market research specialist focused on {industry} in {city}.
Provide data-driven market analysis with Pakistan-specific context.
Include local market dynamics, competitor landscape, and consumer insights.""",
                     prompt, log_fn, "market")


def synthesis_agent(problem: str, research: str, documents: str, market: str,
                    city: str, industry: str, log_fn) -> dict:
    log_fn("[SYNTHESIS AGENT] Creating final report...", "synthesis")

    prompt = f"""You are synthesizing a complete business intelligence report for a Pakistani business owner.

BUSINESS PROBLEM: {problem}
CITY: {city} | INDUSTRY: {industry}

RESEARCH FINDINGS:
{research[:2000]}

DOCUMENT ANALYSIS:
{documents[:1500]}

MARKET ANALYSIS:
{market[:2000]}

Create a comprehensive report. Return ONLY valid JSON:
{{
  "executive_summary": "3-4 sentence overview of findings and key recommendation",
  "situation_analysis": "2-3 sentences about current business situation based on all data",
  "key_findings": ["finding 1 with specific detail", "finding 2", "finding 3", "finding 4"],
  "market_opportunities": ["opportunity 1 specific to Pakistan", "opportunity 2", "opportunity 3"],
  "risks": ["risk 1 Pakistan context", "risk 2", "risk 3"],
  "recommendations": [
    {{"action": "specific action", "timeline": "when", "impact": "expected result", "cost": "estimated cost in PKR if relevant"}},
    {{"action": "action 2", "timeline": "when", "impact": "result", "cost": "cost"}},
    {{"action": "action 3", "timeline": "when", "impact": "result", "cost": "cost"}},
    {{"action": "action 4", "timeline": "when", "impact": "result", "cost": "cost"}}
  ],
  "quick_wins": ["something doable this week", "another quick win", "third quick win"],
  "success_metrics": ["metric 1 to track", "metric 2", "metric 3"],
  "urdu_summary": "4-5 sentences in Urdu explaining the main findings and recommendations to the business owner"
}}"""

    response = client.messages.create(
        model="claude-haiku-4-5", max_tokens=3000,
        system="You are a senior business consultant specializing in Pakistani SMBs. Return only valid JSON.",
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip().replace(
        "```json", "").replace("```", "").strip()
    try:
        result = json.loads(raw)
        log_fn("[SYNTHESIS AGENT] Report complete ✓", "synthesis")
        return result
    except Exception:
        log_fn("[SYNTHESIS AGENT] JSON parse error — using raw", "err")
        return {"executive_summary": raw, "key_findings": [], "recommendations": [],
                "market_opportunities": [], "risks": [], "quick_wins": [],
                "success_metrics": [], "urdu_summary": ""}


def generate_pdf_report(problem: str, city: str, industry: str, report: dict) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # Header
    pdf.set_fill_color(26, 26, 26)
    pdf.rect(0, 0, 210, 42, 'F')
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(201, 168, 76)
    pdf.set_xy(20, 10)
    pdf.cell(0, 8, "KAROBAR AI - Business Intelligence Report", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.set_xy(20, 22)
    pdf.multi_cell(0, 5, clean_for_pdf(
        f"Problem: {problem[:80]} | {city} | {industry} | {datetime.now().strftime('%B %d, %Y')}"))
    pdf.ln(15)
    pdf.set_text_color(26, 26, 26)

    def section(title):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(150, 120, 40)
        pdf.multi_cell(0, 7, clean_for_pdf(title))
        pdf.set_text_color(50, 50, 50)
        pdf.set_font("Helvetica", "", 10)
        pdf.ln(1)

    def body(text):
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 5, clean_for_pdf(str(text)))
        pdf.ln(3)

    def bullet(items):
        for item in items:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, clean_for_pdf(f"  - {item}"))
        pdf.ln(2)

    section("EXECUTIVE SUMMARY")
    body(report.get("executive_summary", ""))

    section("SITUATION ANALYSIS")
    body(report.get("situation_analysis", ""))

    section("KEY FINDINGS")
    bullet(report.get("key_findings", []))

    section("MARKET OPPORTUNITIES")
    bullet(report.get("market_opportunities", []))

    section("RISKS TO CONSIDER")
    bullet(report.get("risks", []))

    pdf.add_page()
    section("RECOMMENDATIONS")
    for i, rec in enumerate(report.get("recommendations", []), 1):
        if isinstance(rec, dict):
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 5, clean_for_pdf(
                f"{i}. {rec.get('action', '')}"))
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(100, 100, 100)
            pdf.multi_cell(0, 4, clean_for_pdf(
                f"   Timeline: {rec.get('timeline', '')} | Impact: {rec.get('impact', '')} | Cost: {rec.get('cost', '')}"))
            pdf.set_text_color(50, 50, 50)
            pdf.ln(2)

    section("QUICK WINS (This Week)")
    bullet(report.get("quick_wins", []))

    section("SUCCESS METRICS")
    bullet(report.get("success_metrics", []))

    return bytes(pdf.output())


# ── Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:1.5rem 0 1rem; border-bottom:1px solid #2A2A2A; margin-bottom:1.25rem;">
        <div style="font-size:1.8rem; font-weight:800; color:#FFFFFF; letter-spacing:-0.03em;">
            کاروبار <span style="color:#C9A84C;">AI</span>
        </div>
        <div style="font-size:0.65rem; letter-spacing:0.18em; text-transform:uppercase; color:#444; margin-top:0.3rem;">
            Pakistan Business Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.65rem; letter-spacing:0.15em; text-transform:uppercase; color:#555; margin-bottom:0.5rem;">Business Details</div>', unsafe_allow_html=True)

    city = st.selectbox("City", ["Lahore", "Karachi", "Islamabad", "Faisalabad", "Rawalpindi",
                                 "Multan", "Peshawar", "Quetta", "Sialkot", "Gujranwala", "Other"])
    industry = st.selectbox("Industry", ["Retail / Trade", "Food & Beverage", "Textile & Garments",
                                         "Construction & Real Estate", "Technology / IT", "Agriculture",
                                         "Manufacturing", "Healthcare", "Education", "Transport & Logistics",
                                         "Legal Services", "Financial Services", "Other"])

    st.markdown('<div style="font-size:0.65rem; letter-spacing:0.15em; text-transform:uppercase; color:#555; margin:1rem 0 0.5rem;">Upload Documents (Optional)</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("PDF / Excel / CSV", type=["pdf", "xlsx", "xls", "csv", "txt"],
                                      accept_multiple_files=True, label_visibility="collapsed")
    if uploaded_files:
        st.markdown(
            f'<div style="font-size:0.75rem; color:#34D399; margin-top:0.3rem;">✓ {len(uploaded_files)} file(s) loaded</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem; color:#444; line-height:1.7;">
        <strong style="color:#666;">How it works:</strong><br>
        1. Describe your business problem<br>
        2. Upload relevant documents<br>
        3. Multi-agent system researches and analyzes<br>
        4. Get actionable report in English + Urdu
    </div>
    """, unsafe_allow_html=True)
# MAIN
st.markdown("""
<div class="hero">
    <div class="hero-eye">Multi-Agent · RAG · Web Search · Pakistan Context</div>
    <h1>Karobar <em>AI</em></h1>
    <p class="hero-sub">Describe your business problem. Our agents research, analyze, and deliver a Pakistan-specific intelligence report.</p>
</div>
""", unsafe_allow_html=True)

problem = st.text_area(
    "Business Problem",
    placeholder="e.g. میری دکان میں گاہک کم ہو رہے ہیں — My retail shop in Gulberg is losing customers to online sellers. Sales dropped 30% this year. Should I go online or open another branch?\n\nWrite in Urdu, English, or both...",
    height=130,
    label_visibility="collapsed"
)

run_btn = st.button("Run Analysis →")

if run_btn:
    if not problem.strip():
        st.warning("Please describe your business problem first.")
        st.stop()

    # Agent status display
    st.markdown('<div class="section-head">// Agent Pipeline</div>',
                unsafe_allow_html=True)

    agent_states = {"ORCHESTRATOR": "idle", "RESEARCH": "idle", "DOCUMENT": "idle",
                    "MARKET": "idle", "SYNTHESIS": "idle"}

    status_ph = st.empty()
    log_ph = st.empty()
    log_lines = []

    def update_status(active: str):
        pills = ""
        icons = {"ORCHESTRATOR": "", "RESEARCH": "",
                 "DOCUMENT": "", "MARKET": "", "SYNTHESIS": ""}
        for name, icon in icons.items():
            cls = "pill-active" if name == active else "pill-done" if agent_states.get(
                name) == "done" else "pill-idle"
            pills += f'<span class="agent-pill {cls}">{icon} {name}</span>'
        status_ph.markdown(
            f'<div style="margin:0.5rem 0;">{pills}</div>', unsafe_allow_html=True)

    def log(text: str, kind: str = ""):
        log_lines.append(f'<div class="agent-log {kind}">{text}</div>')
        log_ph.markdown(
            f'<div class="agent-status">{"".join(log_lines[-15:])}</div>', unsafe_allow_html=True)

    # Read uploaded files
    doc_content = ""
    if uploaded_files:
        log("[SYSTEM] Reading uploaded documents...", "document")
        doc_content = read_uploaded_files(uploaded_files)
        log(f"[SYSTEM] Extracted {len(doc_content)} chars from {len(uploaded_files)} file(s)", "document")

    # ORCHESTRATOR
    update_status("ORCHESTRATOR")
    plan = orchestrator_agent(problem, doc_content, city, industry, log)
    agent_states["ORCHESTRATOR"] = "done"
    time.sleep(0.3)

    # RESEARCH
    update_status("RESEARCH")
    research_result = research_agent(
        plan.get("research_queries", [problem]), city, log)
    agent_states["RESEARCH"] = "done"
    time.sleep(0.3)

    # DOCUMENT
    update_status("DOCUMENT")
    doc_result = document_agent(doc_content, problem, log)
    agent_states["DOCUMENT"] = "done"
    time.sleep(0.3)

    # MARKET
    update_status("MARKET")
    market_result = market_agent(
        plan.get("market_queries", [f"{industry} Pakistan"]), industry, city, log)
    agent_states["MARKET"] = "done"
    time.sleep(0.3)

    # SYNTHESIS
    update_status("SYNTHESIS")
    report = synthesis_agent(problem, research_result,
                             doc_result, market_result, city, industry, log)
    agent_states["SYNTHESIS"] = "done"
    update_status("DONE")
    log("[SYSTEM] Analysis complete ✓", "done")

    # ── Report Output
    st.markdown('<div class="section-head">// Intelligence Report</div>',
                unsafe_allow_html=True)

    st.markdown(f"""
    <div class="report-card" style="border-left:3px solid #C9A84C;">
        <h3>Executive Summary</h3>
        <p>{report.get('executive_summary', '')}</p>
        <p style="margin-top:0.5rem; color:#888; font-style:italic; font-size:0.82rem;">
            {report.get('situation_analysis', '')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-head">// Key Findings</div>',
                    unsafe_allow_html=True)
        findings = report.get("key_findings", [])
        f_html = "".join(
            f'<li style="margin:0.4rem 0;">{f}</li>' for f in findings)
        st.markdown(
            f'<div class="report-card"><ul>{f_html}</ul></div>', unsafe_allow_html=True)

        st.markdown(
            '<div class="section-head">// Quick Wins This Week</div>', unsafe_allow_html=True)
        wins = report.get("quick_wins", [])
        w_html = "".join(
            f'<li style="margin:0.4rem 0; color:#34D399;">✓ {w}</li>' for w in wins)
        st.markdown(
            f'<div class="report-card"><ul style="list-style:none; padding:0;">{w_html}</ul></div>', unsafe_allow_html=True)

    with col2:
        st.markdown(
            '<div class="section-head">// Opportunities & Risks</div>', unsafe_allow_html=True)
        opps = report.get("market_opportunities", [])
        risks = report.get("risks", [])
        o_html = "".join(
            f'<li style="margin:0.3rem 0; color:#60A5FA;">↑ {o}</li>' for o in opps)
        r_html = "".join(
            f'<li style="margin:0.3rem 0; color:#F87171;">⚠ {r}</li>' for r in risks)
        st.markdown(
            f'<div class="report-card"><ul style="list-style:none; padding:0;">{o_html}{r_html}</ul></div>', unsafe_allow_html=True)

        st.markdown(
            '<div class="section-head">// Success Metrics</div>', unsafe_allow_html=True)
        metrics = report.get("success_metrics", [])
        m_html = "".join(
            f'<li style="margin:0.3rem 0;"> {m}</li>' for m in metrics)
        st.markdown(
            f'<div class="report-card"><ul style="list-style:none; padding:0;">{m_html}</ul></div>', unsafe_allow_html=True)

    # Recommendations
    st.markdown('<div class="section-head">// Recommendations</div>',
                unsafe_allow_html=True)
    recs = report.get("recommendations", [])
    rec_cols = st.columns(2)
    for i, rec in enumerate(recs[:4]):
        with rec_cols[i % 2]:
            if isinstance(rec, dict):
                st.markdown(f"""
                <div class="report-card">
                    <h3>Action {i+1}</h3>
                    <p><strong>{rec.get('action', '')}</strong></p>
                    <p style="font-size:0.78rem; color:#888; margin-top:0.4rem;">
                        ⏱ {rec.get('timeline', '')} &nbsp;·&nbsp; 💰 {rec.get('cost', '')}
                    </p>
                    <p style="font-size:0.82rem; color:#34D399; margin-top:0.3rem;">
                        → {rec.get('impact', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # Urdu summary
    urdu = report.get("urdu_summary", "")
    if urdu:
        st.markdown('<div class="section-head">// اردو خلاصہ</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<div class="urdu-box">{urdu}</div>', unsafe_allow_html=True)

    # Download
    st.markdown('<div class="section-head">// Export</div>',
                unsafe_allow_html=True)
    dl1, dl2 = st.columns(2)
    with dl1:
        try:
            pdf_bytes = generate_pdf_report(problem, city, industry, report)
            st.download_button("⬇ Download PDF Report", data=pdf_bytes,
                               file_name=f"karobar_ai_{city.lower()}_{datetime.now().strftime('%Y%m%d')}.pdf",
                               mime="application/pdf")
        except Exception as e:
            st.error(f"PDF error: {e}")
    with dl2:
        txt = f"""KAROBAR AI BUSINESS INTELLIGENCE REPORT
{'='*60}
Problem: {problem}
City: {city} | Industry: {industry}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

EXECUTIVE SUMMARY
{report.get('executive_summary', '')}

KEY FINDINGS
{chr(10).join(f'- {f}' for f in report.get('key_findings', []))}

RECOMMENDATIONS
{chr(10).join(f"{i+1}. {r.get('action', '')} | {r.get('timeline', '')} | {r.get('impact', '')}" for i, r in enumerate(report.get('recommendations', []) or []) if isinstance(r, dict))}

QUICK WINS
{chr(10).join(f'- {w}' for w in report.get('quick_wins', []))}

URDU SUMMARY
{report.get('urdu_summary', '')}"""
        st.download_button("⬇ Download TXT Report", data=txt,
                           file_name=f"karobar_ai_{city.lower()}_{datetime.now().strftime('%Y%m%d')}.txt",
                           mime="text/plain")

else:
    st.markdown("""
    <div style="text-align:center; padding:4rem 2rem; background:#FFFFFF;
         border:1.5px dashed #E0D8CC; border-radius:12px; margin-top:0.5rem;">
        <div style="font-size:2.5rem; margin-bottom:0.75rem;"></div>
        <div style="font-size:1.1rem; font-weight:700; color:#1A1A1A; margin-bottom:0.3rem;">
            Describe your business problem above
        </div>
        <div style="font-size:0.85rem; color:#888;">
            Write in Urdu, English, or both — our agents will research and analyze
        </div>
        <div style="margin-top:1.25rem; display:flex; justify-content:center; gap:1rem; flex-wrap:wrap;">
            <span style="font-size:0.75rem; color:#AAA; background:#F5F3EF; padding:0.3rem 0.75rem; border-radius:999px; border:1px solid #E0D8CC;">
                Sales dropping?
            </span>
            <span style="font-size:0.75rem; color:#AAA; background:#F5F3EF; padding:0.3rem 0.75rem; border-radius:999px; border:1px solid #E0D8CC;">
                Should I expand?
            </span>
            <span style="font-size:0.75rem; color:#AAA; background:#F5F3EF; padding:0.3rem 0.75rem; border-radius:999px; border:1px solid #E0D8CC;">
                New market entry?
            </span>
            <span style="font-size:0.75rem; color:#AAA; background:#F5F3EF; padding:0.3rem 0.75rem; border-radius:999px; border:1px solid #E0D8CC;">
                Competitor analysis?
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown('<p style="text-align:center; color:#CCC; font-size:0.72rem; font-family:\'JetBrains Mono\',monospace;">KAROBAR AI · Multi-Agent Pipeline · Pakistan Business Intelligence </p>', unsafe_allow_html=True)
