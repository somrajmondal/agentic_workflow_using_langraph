

import os
from state import ProjectState
from config import OUTPUT_DIR

REPORT_DIR = os.path.join(OUTPUT_DIR, "Report")


def _build_pdf(state: ProjectState, path: str):
    """Build a multi-section PDF using reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                     HRFlowable, PageBreak, Table, TableStyle,
                                     Image as RLImage)
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

    doc  = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    DARK_BLUE = colors.HexColor("#1a237e")
    TEAL      = colors.HexColor("#00796b")

    title_style = ParagraphStyle("title", parent=styles["Title"],
        fontSize=22, textColor=DARK_BLUE, spaceAfter=8, alignment=TA_CENTER)
    sub_style   = ParagraphStyle("sub", parent=styles["Normal"],
        fontSize=11, textColor=TEAL, spaceAfter=20, alignment=TA_CENTER)
    h1_style    = ParagraphStyle("h1", parent=styles["Heading1"],
        fontSize=14, textColor=DARK_BLUE, spaceBefore=16, spaceAfter=6)
    h2_style    = ParagraphStyle("h2", parent=styles["Heading2"],
        fontSize=12, textColor=TEAL, spaceBefore=10, spaceAfter=4)
    body_style  = ParagraphStyle("body", parent=styles["Normal"],
        fontSize=10, leading=15, alignment=TA_JUSTIFY, spaceAfter=8)
    code_style  = ParagraphStyle("code", fontName="Courier", fontSize=8,
        leading=12, backColor=colors.HexColor("#f5f5f5"),
        leftIndent=12, spaceAfter=8)
    ref_style   = ParagraphStyle("ref", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#555555"), spaceAfter=4)

    def h(text, style): return Paragraph(text, style)
    def sp(n=1): return Spacer(1, n * 0.4 * cm)
    def hr(): return HRFlowable(width="100%", thickness=0.5,
                                 color=colors.HexColor("#bbbbbb"), spaceAfter=8)

    story = []

    # ── Cover ──────────────────────────────────────────────────
    story += [
        sp(4),
        h(state["topic"], title_style),
        h("Academic Project Report", sub_style),
        h(f"Subject: {state['subject_area'].title()}", sub_style),
        hr(),
        sp(2),
    ]

    # ── Theory ────────────────────────────────────────────────
    story.append(h("Project Report", h1_style))
    story.append(hr())
    for line in state.get("theory", "").split("\n"):
        line = line.strip()
        if not line:
            story.append(sp(0.5))
        elif line.startswith("## "):
            story.append(h(line[3:], h1_style))
        elif line.startswith("### "):
            story.append(h(line[4:], h2_style))
        else:
            story.append(h(line, body_style))

    story.append(PageBreak())

    # ── Research Notes ────────────────────────────────────────
    story.append(h("Research Notes", h1_style))
    story.append(hr())
    for line in state.get("research_notes", "").split("\n"):
        line = line.strip()
        if not line:
            story.append(sp(0.3))
        elif line.startswith("### "):
            story.append(h(line[4:], h2_style))
        elif line.startswith("## "):
            story.append(h(line[3:], h1_style))
        else:
            story.append(h(line, body_style))

    # ── Timeline ─────────────────────────────────────────────
    if state.get("timeline"):
        story.append(PageBreak())
        story.append(h("Timeline", h1_style))
        story.append(hr())
        tl_data = [["Year", "Event"]] + [
            [e.get("year", ""), e.get("event", "")] for e in state["timeline"]
        ]
        tl_table = Table(tl_data, colWidths=[3*cm, 13*cm])
        tl_table.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0), DARK_BLUE),
            ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
            ("FONTSIZE",    (0,0), (-1,0), 10),
            ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1),
             [colors.white, colors.HexColor("#f0f4f8")]),
            ("FONTSIZE",    (0,1), (-1,-1), 9),
            ("VALIGN",      (0,0), (-1,-1), "TOP"),
            ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING",(0,0), (-1,-1), 6),
            ("TOPPADDING",  (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
        ]))
        story.append(tl_table)

    # ── Tables ────────────────────────────────────────────────
    for tbl in state.get("table_data", []):
        story.append(PageBreak())
        story.append(h(tbl.get("title", "Data Table"), h2_style))
        headers = tbl.get("headers", [])
        rows    = tbl.get("rows", [])
        data    = [headers] + rows
        t       = Table(data, repeatRows=1)
        col_w   = [16*cm / len(headers)] * len(headers)
        t       = Table(data, colWidths=col_w, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0), TEAL),
            ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
            ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",    (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS", (0,1), (-1,-1),
             [colors.white, colors.HexColor("#e8f5e9")]),
            ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
            ("LEFTPADDING", (0,0), (-1,-1), 5),
            ("RIGHTPADDING",(0,0), (-1,-1), 5),
            ("TOPPADDING",  (0,0), (-1,-1), 3),
            ("BOTTOMPADDING",(0,0), (-1,-1), 3),
            ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
            ("WORDWRAP",    (0,0), (-1,-1), True),
        ]))
        story.append(t)
        story.append(sp())

    # ── Charts ────────────────────────────────────────────────
    if state.get("chart_paths"):
        story.append(PageBreak())
        story.append(h("Charts & Visualisations", h1_style))
        story.append(hr())
        for cp in state["chart_paths"]:
            if os.path.exists(cp):
                story.append(RLImage(cp, width=15*cm, height=7.5*cm))
                story.append(sp())

    # ── Images ────────────────────────────────────────────────
    if state.get("image_paths"):
        story.append(PageBreak())
        story.append(h("Related Images", h1_style))
        story.append(hr())
        for i, ip in enumerate(state["image_paths"][:4], 1):
            if os.path.exists(ip):
                try:
                    story.append(RLImage(ip, width=12*cm, height=8*cm))
                    story.append(h(f"Figure {i}: {state['topic']} illustration", ref_style))
                    story.append(sp())
                except Exception:
                    pass

    # ── Videos ────────────────────────────────────────────────
    if state.get("video_links"):
        story.append(PageBreak())
        story.append(h("Recommended Videos", h1_style))
        story.append(hr())
        for v in state["video_links"]:
            story.append(h(f"▶ {v['title']}", h2_style))
            story.append(h(f"URL: {v['url']}", ref_style))
            story.append(sp(0.5))

    # ── Code ──────────────────────────────────────────────────
    if state.get("code", "").strip():
        story.append(PageBreak())
        story.append(h("Python Implementation", h1_style))
        story.append(hr())
        for line in state["code"].split("\n")[:80]:   # limit to 80 lines in PDF
            story.append(Paragraph(line.replace(" ", "&nbsp;").replace("<","&lt;"),
                                   code_style))

    # ── Quiz ──────────────────────────────────────────────────
    if state.get("quiz"):
        story.append(PageBreak())
        story.append(h("Revision Quiz", h1_style))
        story.append(hr())
        for i, q in enumerate(state["quiz"], 1):
            story.append(h(f"Q{i}. {q['q']}", h2_style))
            for k, v in q.get("options", {}).items():
                story.append(h(f"&nbsp;&nbsp;&nbsp;{k}) {v}", body_style))
            story.append(h(f"✅ Answer: {q.get('answer','?')} — {q.get('explanation','')}",
                           ref_style))
            story.append(sp())

    # ── Mind Map ──────────────────────────────────────────────
    if state.get("mindmap"):
        story.append(PageBreak())
        story.append(h("Mind Map", h1_style))
        story.append(hr())
        for line in state["mindmap"].split("\n"):
            story.append(Paragraph(
                line.replace(" ", "&nbsp;").replace("<","&lt;"),
                code_style))

    # ── References ────────────────────────────────────────────
    if state.get("references"):
        story.append(PageBreak())
        story.append(h("References", h1_style))
        story.append(hr())
        for ref in state["references"]:
            story.append(h(ref, ref_style))

    doc.build(story)


def pdf_node(state: ProjectState) -> ProjectState:
    print("\n╔══ 📄  PDF AGENT ════════════════════════════════════╗")
    os.makedirs(REPORT_DIR, exist_ok=True)
    path = os.path.join(REPORT_DIR, "project_report.pdf")

    try:
        _build_pdf(state, path)
        size_kb = os.path.getsize(path) // 1024
        print(f"║  → PDF created: project_report.pdf  ({size_kb} KB)")
        print("╚══════════════════════════════════════════════════════╝")
        return {**state, "pdf_path": path, "current_step": "pdf_done",
                "messages": state["messages"] + [
                    {"role": "pdf_agent", "content": f"PDF: {size_kb} KB"}]}
    except ImportError:
        msg = "reportlab not installed — run: pip install reportlab"
        print(f"║  ⚠️  {msg}")
        print("╚══════════════════════════════════════════════════════╝")
        return {**state, "pdf_path": "", "current_step": "pdf_done",
                "errors": state["errors"] + [f"PDF: {msg}"]}
    except Exception as e:
        print(f"║  ⚠️  {e}")
        print("╚══════════════════════════════════════════════════════╝")
        return {**state, "pdf_path": "", "current_step": "pdf_done",
                "errors": state["errors"] + [f"PDF: {e}"]}
