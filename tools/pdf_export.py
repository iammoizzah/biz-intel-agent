"""
Renders the Synthesis Agent's final report into a downloadable PDF.

Uses fpdf2 with a Unicode-capable font so Urdu/Arabic/Hindi text
doesn't just render as boxes -- this matters a lot for the bilingual
requirement, it's the easiest thing to get wrong.
"""

import os
from fpdf import FPDF

# DejaVu Sans covers Latin + a wide Unicode range and ships with most
# Linux distros / fpdf2 installs. For full Urdu/Arabic shaping you'd
# swap in a font like Noto Nastaliq Urdu -- flagged in README as a
# known follow-up rather than solved silently here.
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
]


def _find_font() -> str | None:
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def build_report_pdf(title: str, market_region: str, sections: dict[str, str], output_path: str) -> str:
    """sections: ordered dict-like of {heading: body_text}"""
    pdf = FPDF()
    pdf.add_page()

    font_path = _find_font()
    if font_path:
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", size=16)
    else:
        pdf.set_font("Helvetica", size=16)

    pdf.multi_cell(0, 10, title)
    pdf.set_font_size(10)
    pdf.multi_cell(0, 6, f"Market: {market_region}")
    pdf.ln(4)

    for heading, body in sections.items():
        pdf.set_font_size(13)
        pdf.multi_cell(0, 8, heading)
        pdf.set_font_size(11)
        pdf.multi_cell(0, 6, body)
        pdf.ln(3)

    pdf.output(output_path)
    return output_path
