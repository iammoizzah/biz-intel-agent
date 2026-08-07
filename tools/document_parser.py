"""
Document parsing tool used by the Document Analyst agent.

Handles the three formats SMB owners actually upload: PDF reports,
Excel sheets (sales ledgers, inventory), and CSV exports.
Everything is normalized to plain text + a structured summary so it
can be dropped straight into a prompt (RAG-lite: no vector DB needed
at this scale — a business's own documents fit in-context).
"""

import io
import pandas as pd
from pypdf import PdfReader


def parse_pdf(file_bytes: bytes, max_chars: int = 15000) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = []
    for i, page in enumerate(reader.pages):
        text_parts.append(f"--- Page {i + 1} ---\n{page.extract_text() or ''}")
    full_text = "\n".join(text_parts)
    return full_text[:max_chars]


def parse_tabular(file_bytes: bytes, filename: str, max_rows: int = 200) -> str:
    """Handles .csv and .xlsx. Returns a text summary + a preview table
    the model can reason over — full dumps of large sheets blow the
    context window and don't help the model anyway."""
    if filename.lower().endswith(".csv"):
        df = pd.read_csv(io.BytesIO(file_bytes))
    else:
        df = pd.read_excel(io.BytesIO(file_bytes))

    summary_lines = [
        f"Rows: {len(df)}, Columns: {list(df.columns)}",
        "",
        "Column summarystats:",
        df.describe(include="all").to_string(),
        "",
        f"Preview (first {min(max_rows, len(df))} rows):",
        df.head(max_rows).to_string(),
    ]
    return "\n".join(summary_lines)


def parse_document(file_bytes: bytes, filename: str) -> str:
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        return parse_pdf(file_bytes)
    elif ext in ("csv", "xlsx", "xls"):
        return parse_tabular(file_bytes, filename)
    else:
        try:
            return file_bytes.decode("utf-8")[:15000]
        except UnicodeDecodeError:
            return f"[Unsupported file type: {ext}]"
