"""
Business Intelligence Agent -- Streamlit UI

Run with: streamlit run app.py
"""

import os
import streamlit as st

from config.market_context import MARKETS, DEFAULT_MARKET, get_market
from agents.orchestrator import run_pipeline
from tools.pdf_export import build_report_pdf

st.set_page_config(page_title="Business Intelligence Agent",
                   layout="wide")

# --- Sidebar: market + about ---
with st.sidebar:
    st.title(" BI Agent")
    st.caption("Multi-agent business intelligence, localized to your market.")

    market_name = st.selectbox("Market", list(
        MARKETS.keys()), index=list(MARKETS.keys()).index(DEFAULT_MARKET))
    market = get_market(market_name)

    st.divider()
    st.markdown("**How it works**")
    st.markdown(
        "1. An Orchestrator plans which specialist agents your question needs\n"
        "2. Research, Document, and Market agents run (in parallel where possible)\n"
        "3. A Synthesis agent writes one clear, actionable report"
    )
    st.divider()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.warning("ANTHROPIC_API_KEY not set -- see .env.example", icon="⚠️")

# --- Main ---
st.title("Business Intelligence Agent")
st.caption(
    f"Currently configured for: **{market.region}** ({', '.join(market.languages).upper()})")

question = st.text_area(
    "Describe your business problem or question",
    placeholder="e.g. Should I open a second branch in Gulberg? / کیا مجھے گلبرگ میں دوسری شاخ کھولنی چاہیے؟",
    height=100,
)

uploaded = st.file_uploader(
    "Optional: upload business documents (PDF, Excel, CSV)",
    type=["pdf", "xlsx", "xls", "csv"],
    accept_multiple_files=True,
)

run_clicked = st.button("Analyze", type="primary",
                        disabled=not question.strip())

if run_clicked:
    files = [{"filename": f.name, "bytes": f.getvalue()}
             for f in (uploaded or [])]

    status_box = st.empty()

    def progress(msg: str):
        status_box.info(msg)

    with st.spinner("Running agents..."):
        try:
            result = run_pipeline(question, market, files,
                                  progress_callback=progress)
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

    status_box.empty()
    st.success(f"Agents used: {', '.join(result.plan)}")

    st.markdown("## Report")
    st.markdown(result.final_report)

    with st.expander("See individual agent findings"):
        for name, output in result.agent_outputs.items():
            st.markdown(f"**{name.title()} Agent**")
            st.markdown(output.get("summary", ""))
            st.divider()

    # PDF export
    os.makedirs("outputs", exist_ok=True)
    pdf_path = os.path.join("outputs", "report.pdf")
    try:
        build_report_pdf(
            title=f"Business Intelligence Report -- {market.region}",
            market_region=market.region,
            sections={"Question": question, "Report": result.final_report},
            output_path=pdf_path,
        )
        with open(pdf_path, "rb") as f:
            st.download_button(
                "Download PDF report", f, file_name="business_report.pdf", mime="application/pdf")
    except Exception as e:
        st.warning(f"Report generated, but PDF export failed: {e}")
