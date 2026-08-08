import os
import io
import json
import time
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
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,600&family=Inter:wght@300;400;500;600&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body,[class*="css"]{
    font-family:'Inter',sans-serif;
    background:#FAFAF8!important;
    color:#1C1C1C!important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"]{
    background:#1C1C1C!important;
    border-right:none!important;
}
section[data-testid="stSidebar"] *{color:#E8E8E8!important;}
section[data-testid="stSidebar"] .stSelectbox>div>div{
    background:#2A2A2A!important;border:1px solid #383838!important;
    color:#E8E8E8!important;border-radius:8px!important;
}
section[data-testid="stSidebar"] div[data-testid="stFileUploader"]{
    background:#2A2A2A!important;border:1.5px dashed #383838!important;border-radius:8px!important;
}

/* ── Hero ── */
.hero{
    background:#1C1C1C;
    border-radius:20px;
    padding:3rem 3rem 2.5rem;
    margin-bottom:2rem;
    position:relative;
    overflow:hidden;
}
.hero::after{
    content:'';
    position:absolute;
    top:0;right:0;bottom:0;
    width:40%;
    background:linear-gradient(135deg,transparent,rgba(212,175,55,0.08));
    pointer-events:none;
}
.hero-tag{
    font-size:0.62rem;font-weight:600;
    letter-spacing:0.22em;text-transform:uppercase;
    color:#B8943F;margin-bottom:0.75rem;
}
.hero h1{
    font-family:'Fraunces',serif;
    font-size:3.2rem;font-weight:700;
    color:#FFFFFF;line-height:1.05;
    letter-spacing:-0.02em;margin-bottom:0.5rem;
}
.hero h1 em{color:#D4AF37;font-style:italic;}
.hero-sub{font-size:0.95rem;color:#666;font-weight:300;max-width:520px;line-height:1.6;}
.hero-badges{display:flex;gap:0.5rem;margin-top:1.25rem;flex-wrap:wrap;}
.hero-badge{
    font-size:0.68rem;font-weight:500;letter-spacing:0.06em;
    color:#888;background:rgba(255,255,255,0.06);
    border:1px solid rgba(255,255,255,0.1);
    border-radius:999px;padding:0.3rem 0.85rem;
}

/* ── Input area ── */
.input-wrap{
    background:#FFFFFF;border:1.5px solid #E8E4DC;
    border-radius:16px;padding:1.75rem;margin-bottom:1.5rem;
}
.input-label{
    font-size:0.62rem;font-weight:600;letter-spacing:0.18em;
    text-transform:uppercase;color:#AAA;margin-bottom:0.6rem;
}

/* ── Agent pipeline ── */
.pipeline-wrap{
    background:#FFFFFF;border:1.5px solid #E8E4DC;
    border-radius:16px;padding:1.5rem;margin:1.25rem 0;
}
.pipeline-title{
    font-size:0.62rem;font-weight:600;letter-spacing:0.18em;
    text-transform:uppercase;color:#AAA;margin-bottom:1rem;
}
.agent-pills{display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.75rem;}
.agent-pill{
    display:inline-flex;align-items:center;gap:0.35rem;
    padding:0.3rem 0.8rem;border-radius:999px;
    font-size:0.68rem;font-weight:600;
    font-family:'Inter',monospace;letter-spacing:0.04em;
    transition:all 0.2s;
}
.pill-idle{background:#F5F5F5;border:1px solid #E0E0E0;color:#BBB;}
.pill-active{background:#FFF8E7;border:1px solid #D4AF37;color:#B8943F;}
.pill-done{background:#F0FFF4;border:1px solid #86EFAC;color:#16A34A;}
.agent-log-box{
    background:#F8F6F2;border-radius:10px;
    padding:0.85rem 1rem;font-family:'Inter',monospace;
    font-size:0.72rem;max-height:180px;overflow-y:auto;
    border:1px solid #F0EBE0;
}
.log-line{padding:0.12rem 0;line-height:1.5;color:#888;}
.log-line.orchestrator{color:#B8943F;}
.log-line.research{color:#2563EB;}
.log-line.document{color:#059669;}
.log-line.market{color:#7C3AED;}
.log-line.synthesis{color:#DC2626;}
.log-line.done{color:#1C1C1C;font-weight:600;}
.log-line.err{color:#EF4444;}

/* ── Section labels ── */
.sec-label{
    font-size:0.6rem;font-weight:700;letter-spacing:0.2em;
    text-transform:uppercase;color:#C0B090;
    padding-bottom:0.6rem;border-bottom:1.5px solid #F0EAD8;
    margin:2rem 0 1rem;
}

/* ── Cards ── */
.card{
    background:#FFFFFF;border:1.5px solid #E8E4DC;
    border-radius:14px;padding:1.4rem 1.6rem;margin:0.6rem 0;
}
.card-label{
    font-size:0.6rem;font-weight:700;letter-spacing:0.16em;
    text-transform:uppercase;color:#C0B090;margin-bottom:0.6rem;
}
.card p,.card li{font-size:0.88rem;color:#444;line-height:1.75;font-weight:300;}
.card ul{padding-left:1.25rem;}
.card strong{color:#1C1C1C;font-weight:600;}
.exec-card{
    background:#1C1C1C;border-radius:14px;
    padding:1.75rem 2rem;margin:0.75rem 0;
}
.exec-card p{font-size:0.92rem;color:#C8C8C8;line-height:1.8;font-weight:300;}
.exec-card p em{color:#D4AF37;font-style:normal;font-weight:500;}

/* ── Rec cards ── */
.rec-card{
    background:#FFFFFF;border:1.5px solid #E8E4DC;
    border-radius:14px;padding:1.25rem 1.4rem;
    border-top:3px solid #D4AF37;
}
.rec-num{
    font-family:'Fraunces',serif;font-size:1.6rem;
    font-weight:700;color:#E8E4DC;float:right;line-height:1;
}
.rec-action{font-size:0.92rem;font-weight:600;color:#1C1C1C;margin-bottom:0.4rem;}
.rec-meta{font-size:0.75rem;color:#AAA;margin-bottom:0.3rem;}
.rec-impact{font-size:0.82rem;color:#059669;font-weight:500;}

/* ── Quick win ── */
.win-item{
    display:flex;align-items:flex-start;gap:0.75rem;
    padding:0.6rem 0;border-bottom:1px solid #F0EAD8;
}
.win-check{
    width:18px;height:18px;border-radius:50%;
    background:#F0FFF4;border:1.5px solid #86EFAC;
    display:flex;align-items:center;justify-content:center;
    font-size:0.65rem;color:#16A34A;flex-shrink:0;margin-top:0.1rem;
}
.win-text{font-size:0.85rem;color:#444;line-height:1.55;}

/* ── Urdu ── */
.urdu-wrap{
    background:#FEFCE8;border:1.5px solid #FDE68A;
    border-radius:14px;padding:1.5rem 1.75rem;
    direction:rtl;text-align:right;
}
.urdu-label{
    font-size:0.6rem;font-weight:700;letter-spacing:0.16em;
    text-transform:uppercase;color:#92400E;margin-bottom:0.6rem;
    direction:ltr;text-align:left;
}
.urdu-text{font-size:1rem;color:#1C1C1C;line-height:2.1;}

/* ── Streamlit overrides ── */
div[data-testid="stTextArea"] textarea{
    background:#FFFFFF!important;
    border:1.5px solid #E8E4DC!important;
    border-radius:10px!important;
    color:#1C1C1C!important;
    font-family:'Inter',sans-serif!important;
    font-size:0.92rem!important;
    line-height:1.65!important;
}
div[data-testid="stTextArea"] textarea:focus{
    border-color:#D4AF37!important;
    box-shadow:0 0 0 3px rgba(212,175,55,0.12)!important;
}
div[data-testid="stTextArea"] textarea::placeholder{color:#BBB!important;}
.stButton>button{
    background:#1C1C1C!important;color:#D4AF37!important;
    border:none!important;border-radius:10px!important;
    padding:0.75rem 2rem!important;
    font-family:'Inter',sans-serif!important;
    font-weight:600!important;font-size:0.9rem!important;
    width:100%!important;letter-spacing:0.04em!important;
}
.stButton>button:hover{background:#2A2A2A!important;}
.stDownloadButton>button{
    background:transparent!important;color:#1C1C1C!important;
    border:1.5px solid #E8E4DC!important;border-radius:10px!important;
    font-family:'Inter',sans-serif!important;font-weight:600!important;
    font-size:0.85rem!important;width:100%!important;
}
.stDownloadButton>button:hover{border-color:#1C1C1C!important;}
#MainMenu,footer,header{visibility:hidden;}
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
    return "\n\n".join(all_content)


def clean_for_pdf(text: str) -> str:
    text = unicodedata.normalize('NFKD', str(text))
    for c, r in {'\u2022': '-', '\u2013': '-', '\u2014': '--', '\u2018': "'", '\u2019': "'",
                 '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u25cf': '-'}.items():
        text = text.replace(c, r)
    return text.encode('latin-1', 'ignore').decode('latin-1')

# ── Agents


def run_agent(name, system, prompt, log_fn, log_type, use_tools=False) -> str:
    messages = [{"role": "user", "content": prompt}]
    tools = [{
        "name": "web_search",
        "description": "Search the web for Pakistan-specific business, market, and regulatory information",
        "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
    }] if use_tools else []

    for _ in range(5):
        kwargs = dict(model="claude-haiku-4-5", max_tokens=2000,
                      system=system, messages=messages)
        if tools:
            kwargs["tools"] = tools
        response = client.messages.create(**kwargs)

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use" and block.name == "web_search":
                    q = block.input.get("query", "")
                    log_fn(f"[{name}] → {q[:60]}", log_type)
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": block.id, "content": web_search(q)})
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            for block in response.content:
                if hasattr(block, "text") and block.text.strip():
                    log_fn(f"[{name}] Complete ✓", "done")
                    return block.text.strip()
            break
    return "Analysis unavailable."


def orchestrator_agent(problem, doc_content, city, industry, log_fn) -> dict:
    log_fn("[ORCHESTRATOR] Analyzing problem and planning pipeline...", "orchestrator")
    system = """You are the orchestrator of a Pakistani business intelligence system.
Return ONLY valid JSON — no markdown, no explanation:
{"research_queries":["q1 Pakistan","q2"],"market_queries":["m1","m2"],"key_questions":["kq1","kq2"]}"""
    response = client.messages.create(
        model="claude-haiku-4-5", max_tokens=600, system=system,
        messages=[
            {"role": "user", "content": f"Problem: {problem}\nCity: {city}\nIndustry: {industry}"}]
    )
    raw = response.content[0].text.strip().replace(
        "```json", "").replace("```", "").strip()
    try:
        plan = json.loads(raw)
        log_fn(
            f"[ORCHESTRATOR] {len(plan.get('research_queries', []))} research tasks queued", "orchestrator")
        return plan
    except Exception:
        return {"research_queries": [f"{problem} Pakistan {city}", f"{industry} trends Pakistan 2024"],
                "market_queries": [f"{industry} market {city} Pakistan", f"competition {industry} Pakistan"],
                "key_questions": ["Main challenges?", "Market opportunities?"]}


def research_agent(queries, city, log_fn) -> str:
    log_fn("[RESEARCH AGENT] Searching Pakistan market data...", "research")
    results = []
    for q in queries[:3]:
        log_fn(f"[RESEARCH AGENT] → {q[:60]}", "research")
        results.append(web_search(f"{q} Pakistan {city}"))
        time.sleep(0.3)
    return run_agent("RESEARCH",
                     "You are a Pakistan business research specialist. Synthesize search results into structured findings with Pakistan-specific context, statistics, and actionable data.",
                     f"Synthesize these search results for a Pakistani business problem:\n\n{'---'.join(results[:3])}",
                     log_fn, "research")


def document_agent(doc_content, problem, log_fn) -> str:
    if not doc_content:
        log_fn("[DOCUMENT AGENT] No documents uploaded — skipping", "document")
        return "No documents uploaded."
    log_fn("[DOCUMENT AGENT] Analyzing business documents...", "document")
    return run_agent("DOCUMENT",
                     "You are a business document analyst for Pakistani SMBs. Extract specific numbers, trends, and insights from the documents that relate to the business problem.",
                     f"Problem: {problem}\n\nDocuments:\n{doc_content[:6000]}",
                     log_fn, "document")


def market_agent(queries, industry, city, log_fn) -> str:
    log_fn("[MARKET AGENT] Analyzing Pakistan market landscape...", "market")
    results = []
    for q in queries[:3]:
        log_fn(f"[MARKET AGENT] → {q[:60]}", "market")
        results.append(web_search(q))
        time.sleep(0.3)
    return run_agent("MARKET",
                     f"You are a Pakistan market analyst specializing in {industry} in {city}. Provide data-driven market analysis with local context — competitors, consumer behavior, regulations, opportunities.",
                     f"Analyze {industry} market in {city}, Pakistan:\n\n{'---'.join(results)}",
                     log_fn, "market")


def synthesis_agent(problem, research, documents, market, city, industry, log_fn) -> dict:
    log_fn("[SYNTHESIS AGENT] Generating intelligence report...", "synthesis")
    prompt = f"""Create a business intelligence report for a Pakistani {industry} business in {city}.

Problem: {problem}
Research: {research[:1800]}
Documents: {documents[:1200]}
Market: {market[:1800]}

Return ONLY valid JSON:
{{
  "executive_summary": "3-4 sentence overview and key recommendation",
  "situation_analysis": "2-3 sentences about the current situation",
  "key_findings": ["specific finding with data", "finding 2", "finding 3", "finding 4"],
  "market_opportunities": ["opportunity 1 Pakistan specific", "opportunity 2", "opportunity 3"],
  "risks": ["risk 1", "risk 2", "risk 3"],
  "recommendations": [
    {{"action":"specific action","timeline":"timeframe","impact":"expected result","cost":"PKR estimate"}},
    {{"action":"action 2","timeline":"timeframe","impact":"result","cost":"cost"}},
    {{"action":"action 3","timeline":"timeframe","impact":"result","cost":"cost"}},
    {{"action":"action 4","timeline":"timeframe","impact":"result","cost":"cost"}}
  ],
  "quick_wins": ["doable this week 1","doable this week 2","doable this week 3"],
  "success_metrics": ["metric 1 to track","metric 2","metric 3"],
  "urdu_summary": "4-5 sentences in Urdu for the business owner"
}}"""
    response = client.messages.create(
        model="claude-haiku-4-5", max_tokens=3000,
        system="Senior business consultant for Pakistani SMBs. Return only valid JSON.",
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip().replace(
        "```json", "").replace("```", "").strip()
    try:
        result = json.loads(raw)
        log_fn("[SYNTHESIS AGENT] Report ready ✓", "synthesis")
        return result
    except Exception:
        return {"executive_summary": raw, "key_findings": [], "recommendations": [],
                "market_opportunities": [], "risks": [], "quick_wins": [], "success_metrics": [], "urdu_summary": ""}


def generate_pdf(problem, city, industry, report) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(22, 22, 22)
    pdf.set_fill_color(28, 28, 28)
    pdf.rect(0, 0, 210, 44, 'F')
    pdf.set_font("Helvetica", "B", 17)
    pdf.set_text_color(212, 175, 55)
    pdf.set_xy(22, 11)
    pdf.cell(0, 8, "KAROBAR AI — Business Intelligence Report", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.set_xy(22, 23)
    pdf.multi_cell(0, 5, clean_for_pdf(
        f"{city} | {industry} | {datetime.now().strftime('%B %d, %Y')}"))
    pdf.ln(16)
    pdf.set_text_color(28, 28, 28)

    def sec(t):
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(160, 130, 40)
        pdf.multi_cell(0, 6, clean_for_pdf(t))
        pdf.set_text_color(50, 50, 50)
        pdf.set_font("Helvetica", "", 10)
        pdf.ln(1)

    def body(t):
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 5, clean_for_pdf(str(t)))
        pdf.ln(3)

    def bullets(items):
        for item in items:
            pdf.set_font("Helvetica", "", 10)
            words = str(item).split()
            chunks, chunk = [], []
            for w in words:
                chunk.append(w)
                if len(' '.join(chunk)) > 150:
                    chunks.append(' '.join(chunk))
                    chunk = []
            if chunk:
                chunks.append(' '.join(chunk))
            for c in chunks:
                pdf.multi_cell(0, 5, clean_for_pdf(f"  - {c}"))
        pdf.ln(2)

    sec("EXECUTIVE SUMMARY")
    body(report.get("executive_summary", ""))
    sec("SITUATION ANALYSIS")
    body(report.get("situation_analysis", ""))
    sec("KEY FINDINGS")
    bullets(report.get("key_findings", []))
    sec("MARKET OPPORTUNITIES")
    bullets(report.get("market_opportunities", []))
    sec("RISKS")
    bullets(report.get("risks", []))
    pdf.add_page()
    sec("RECOMMENDATIONS")
    for i, rec in enumerate(report.get("recommendations", []), 1):
        if isinstance(rec, dict):
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 5, clean_for_pdf(
                f"{i}. {rec.get('action', '')}"))
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(120, 120, 120)
            pdf.multi_cell(0, 4, clean_for_pdf(
                f"   Timeline: {rec.get('timeline', '')} | Cost: {rec.get('cost', '')} | Impact: {rec.get('impact', '')}"))
            pdf.set_text_color(50, 50, 50)
            pdf.ln(3)
    sec("QUICK WINS")
    bullets(report.get("quick_wins", []))
    sec("SUCCESS METRICS")
    bullets(report.get("success_metrics", []))
    return bytes(pdf.output())


# ── Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1.75rem 0 1.25rem;border-bottom:1px solid #2A2A2A;margin-bottom:1.25rem;">
        <div style="font-family:'Fraunces',serif;font-size:1.9rem;font-weight:700;color:#FFFFFF;letter-spacing:-0.02em;">
            Karobar <span style="color:#D4AF37;">AI</span>
        </div>
        <div style="font-size:0.6rem;letter-spacing:0.2em;text-transform:uppercase;color:#555;margin-top:0.3rem;">
            Pakistan Business Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;color:#555;margin-bottom:0.5rem;">Your Business</div>', unsafe_allow_html=True)

    city = st.selectbox("City", ["Lahore", "Karachi", "Islamabad", "Faisalabad", "Rawalpindi",
                                 "Multan", "Peshawar", "Quetta", "Sialkot", "Gujranwala", "Other"],
                        label_visibility="collapsed")
    industry = st.selectbox("Industry", ["Retail / Trade", "Food & Beverage", "Textile & Garments",
                                         "Construction & Real Estate", "Technology / IT", "Agriculture",
                                         "Manufacturing", "Healthcare", "Education",
                                         "Transport & Logistics", "Financial Services", "Other"],
                            label_visibility="collapsed")

    st.markdown('<div style="font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;color:#555;margin:1.25rem 0 0.5rem;">Documents</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload files", type=["pdf", "xlsx", "xls", "csv", "txt"],
                                      accept_multiple_files=True, label_visibility="collapsed")
    if uploaded_files:
        for f in uploaded_files:
            st.markdown(
                f'<div style="font-size:0.72rem;color:#4ADE80;padding:0.15rem 0;">✓ {f.name}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem;color:#555;line-height:1.8;">
        <div style="color:#888;font-weight:600;margin-bottom:0.4rem;font-size:0.65rem;letter-spacing:0.1em;text-transform:uppercase;">How It Works</div>
        <div>① Describe your problem</div>
        <div>② Upload any business docs</div>
        <div>③ 5 agents research & analyze</div>
        <div>④ Get English + Urdu report</div>
    </div>
    """, unsafe_allow_html=True)

# ── Hero
st.markdown(f"""
<div class="hero">
    <div class="hero-tag">Multi-Agent · Web Search · RAG · {city} · {industry}</div>
    <h1>Karobar <em>AI</em></h1>
    <p class="hero-sub">Describe your business problem in Urdu or English. Five specialized agents research the Pakistan market and deliver an actionable intelligence report.</p>
    <div class="hero-badges">
        <span class="hero-badge"> Orchestrator</span>
        <span class="hero-badge"> Research Agent</span>
        <span class="hero-badge"> Document Analyst</span>
        <span class="hero-badge"> Market Analyst</span>
        <span class="hero-badge"> Synthesis Agent</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input
st.markdown('<div class="input-wrap">', unsafe_allow_html=True)
st.markdown('<div class="input-label">Describe Your Business Problem</div>',
            unsafe_allow_html=True)

problem = st.text_area(
    "problem",
    placeholder="e.g. میری دکان میں گاہک کم ہو رہے ہیں — My retail shop in Gulberg is losing customers to online competitors. Sales dropped 30% this year. Should I start selling online or open a new branch?\n\nYou can write in Urdu, English, or both.",
    height=140,
    label_visibility="collapsed",
    key="business_problem"
)

run_btn = st.button("Run Analysis →")
st.markdown('</div>', unsafe_allow_html=True)

# ── Pipeline
if run_btn:
    if not problem.strip():
        st.warning("Please describe your business problem above.")
        st.stop()

    st.markdown('<div class="pipeline-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="pipeline-title">// Agent Pipeline</div>',
                unsafe_allow_html=True)

    agent_states = {k: "idle" for k in [
        "ORCHESTRATOR", "RESEARCH", "DOCUMENT", "MARKET", "SYNTHESIS"]}
    icons = {"ORCHESTRATOR": "", "RESEARCH": "",
             "DOCUMENT": "", "MARKET": "", "SYNTHESIS": ""}

    pills_ph = st.empty()
    log_ph = st.empty()
    log_lines = []

    def update_pills(active=""):
        html = '<div class="agent-pills">'
        for name, icon in icons.items():
            if name == active:
                cls = "pill-active"
            elif agent_states[name] == "done":
                cls = "pill-done"
            else:
                cls = "pill-idle"
            html += f'<span class="agent-pill {cls}">{icon} {name}</span>'
        html += '</div>'
        pills_ph.markdown(html, unsafe_allow_html=True)

    def log(text, kind=""):
        log_lines.append(f'<div class="log-line {kind}">{text}</div>')
        log_ph.markdown(
            f'<div class="agent-log-box">{"".join(log_lines[-12:])}</div>',
            unsafe_allow_html=True
        )

    update_pills()

    # Read docs
    doc_content = ""
    if uploaded_files:
        log("[SYSTEM] Reading uploaded documents...", "document")
        doc_content = read_uploaded_files(uploaded_files)
        log(f"[SYSTEM] {len(doc_content)} chars extracted from {len(uploaded_files)} file(s)", "document")

    # Run pipeline
    update_pills("ORCHESTRATOR")
    plan = orchestrator_agent(problem, doc_content, city, industry, log)
    agent_states["ORCHESTRATOR"] = "done"

    update_pills("RESEARCH")
    research_result = research_agent(
        plan.get("research_queries", [problem]), city, log)
    agent_states["RESEARCH"] = "done"

    update_pills("DOCUMENT")
    doc_result = document_agent(doc_content, problem, log)
    agent_states["DOCUMENT"] = "done"

    update_pills("MARKET")
    market_result = market_agent(
        plan.get("market_queries", [f"{industry} Pakistan"]), industry, city, log)
    agent_states["MARKET"] = "done"

    update_pills("SYNTHESIS")
    report = synthesis_agent(problem, research_result,
                             doc_result, market_result, city, industry, log)
    agent_states["SYNTHESIS"] = "done"
    update_pills()
    log("[SYSTEM] Analysis complete — report ready below ↓", "done")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Report
    st.markdown('<div class="sec-label">Intelligence Report</div>',
                unsafe_allow_html=True)

    # Executive summary
    st.markdown(f"""
    <div class="exec-card">
        <div style="font-size:0.6rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#666;margin-bottom:0.75rem;">Executive Summary</div>
        <p>{report.get('executive_summary', '')}</p>
        <p style="margin-top:0.75rem;color:#888;font-size:0.82rem;">{report.get('situation_analysis', '')}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="sec-label">Key Findings</div>',
                    unsafe_allow_html=True)
        findings = report.get("key_findings", [])
        f_items = "".join(
            f'<li style="margin:0.45rem 0;">{f}</li>' for f in findings)
        st.markdown(
            f'<div class="card"><ul>{f_items}</ul></div>', unsafe_allow_html=True)

        st.markdown(
            '<div class="sec-label">Quick Wins — This Week</div>', unsafe_allow_html=True)
        wins_html = ""
        for w in report.get("quick_wins", []):
            wins_html += f'<div class="win-item"><div class="win-check">✓</div><div class="win-text">{w}</div></div>'
        st.markdown(
            f'<div class="card">{wins_html}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="sec-label">Opportunities</div>',
                    unsafe_allow_html=True)
        opps = report.get("market_opportunities", [])
        o_items = "".join(
            f'<li style="margin:0.4rem 0;color:#059669;">↑ {o}</li>' for o in opps)
        st.markdown(
            f'<div class="card"><ul style="list-style:none;padding:0;">{o_items}</ul></div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-label">Risks</div>',
                    unsafe_allow_html=True)
        risks = report.get("risks", [])
        r_items = "".join(
            f'<li style="margin:0.4rem 0;color:#DC2626;">⚠ {r}</li>' for r in risks)
        st.markdown(
            f'<div class="card"><ul style="list-style:none;padding:0;">{r_items}</ul></div>', unsafe_allow_html=True)

    # Recommendations
    st.markdown('<div class="sec-label">Recommendations</div>',
                unsafe_allow_html=True)
    recs = report.get("recommendations", [])
    rec_cols = st.columns(2)
    for i, rec in enumerate(recs[:4]):
        with rec_cols[i % 2]:
            if isinstance(rec, dict):
                st.markdown(f"""
                <div class="rec-card">
                    <div class="rec-num">0{i+1}</div>
                    <div class="rec-action">{rec.get('action', '')}</div>
                    <div class="rec-meta">⏱ {rec.get('timeline', '')} &nbsp;·&nbsp; 💰 {rec.get('cost', '')}</div>
                    <div class="rec-impact">→ {rec.get('impact', '')}</div>
                </div>
                """, unsafe_allow_html=True)

    # Metrics
    st.markdown('<div class="sec-label">Success Metrics</div>',
                unsafe_allow_html=True)
    metrics = report.get("success_metrics", [])
    m_cols = st.columns(3)
    for i, m in enumerate(metrics[:3]):
        with m_cols[i]:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:1.4rem;margin-bottom:0.3rem;"></div>
                <div style="font-size:0.82rem;color:#444;font-weight:300;line-height:1.5;">{m}</div>
            </div>
            """, unsafe_allow_html=True)

    # Urdu
    urdu = report.get("urdu_summary", "")
    if urdu:
        st.markdown('<div class="sec-label">اردو خلاصہ</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div class="urdu-wrap">
            <div class="urdu-label">Urdu Summary for Business Owner</div>
            <div class="urdu-text">{urdu}</div>
        </div>
        """, unsafe_allow_html=True)

    # Download
    st.markdown('<div class="sec-label">Export Report</div>',
                unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    with d1:
        try:
            pdf_bytes = generate_pdf(problem, city, industry, report)
            st.download_button("⬇ Download PDF Report", data=pdf_bytes,
                               file_name=f"karobar_ai_{city.lower()}_{datetime.now().strftime('%Y%m%d')}.pdf",
                               mime="application/pdf")
        except Exception as e:
            st.error(f"PDF error: {e}")
    with d2:
        txt = f"""KAROBAR AI REPORT — {city} | {industry}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

PROBLEM
{problem}

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
    <div style="text-align:center;padding:4.5rem 2rem;background:#FFFFFF;
         border:1.5px dashed #E8E4DC;border-radius:16px;margin-top:0.5rem;">
        <div style="font-family:'Fraunces',serif;font-size:2.5rem;color:#E8E4DC;margin-bottom:0.75rem;">
            کاروبار
        </div>
        <div style="font-size:1rem;font-weight:600;color:#1C1C1C;margin-bottom:0.3rem;">
            Describe your business problem above
        </div>
        <div style="font-size:0.85rem;color:#AAA;margin-bottom:1.5rem;">
            Write in Urdu, English, or both
        </div>
        <div style="display:flex;justify-content:center;gap:0.75rem;flex-wrap:wrap;">
            <span style="font-size:0.75rem;color:#AAA;background:#FAFAF8;padding:0.35rem 0.85rem;border-radius:999px;border:1px solid #E8E4DC;">Sales dropping?</span>
            <span style="font-size:0.75rem;color:#AAA;background:#FAFAF8;padding:0.35rem 0.85rem;border-radius:999px;border:1px solid #E8E4DC;">Should I expand?</span>
            <span style="font-size:0.75rem;color:#AAA;background:#FAFAF8;padding:0.35rem 0.85rem;border-radius:999px;border:1px solid #E8E4DC;">New market entry?</span>
            <span style="font-size:0.75rem;color:#AAA;background:#FAFAF8;padding:0.35rem 0.85rem;border-radius:999px;border:1px solid #E8E4DC;">Competitor analysis?</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<p style="text-align:center;color:#CCC;font-size:0.68rem;letter-spacing:0.1em;">
    KAROBAR AI · MULTI-AGENT PIPELINE · PAKISTAN BUSINESS INTELLIGENCE ·
</p>
""", unsafe_allow_html=True)
