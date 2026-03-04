

import os, json
from openai import OpenAI
from state import ProjectState
from config import OPENAI_API_KEY, MODEL, OUTPUT_DIR

client     = OpenAI(api_key=OPENAI_API_KEY)
REPORT_DIR = os.path.join(OUTPUT_DIR, "Report")

SYSTEM = """
You are an academic data analyst.
Generate 1–2 meaningful comparison or data tables for the given topic.
Tables should add real value — comparisons, specs, statistics, pros/cons, timelines, etc.

Return ONLY valid JSON array, no markdown:
[
  {
    "title": "Table title",
    "headers": ["Column1", "Column2", "Column3"],
    "rows": [
      ["row1col1", "row1col2", "row1col3"],
      ["row2col1", "row2col2", "row2col3"]
    ],
    "note": "Optional source note"
  }
]
"""


def _format_table(table: dict) -> str:
    """Render a table dict as a nicely aligned ASCII table string."""
    headers = table["headers"]
    rows    = table["rows"]
    all_rows = [headers] + [[str(c) for c in r] for r in rows]
    widths   = [max(len(str(row[i])) for row in all_rows)
                for i in range(len(headers))]

    def _row(r):
        return "│ " + " │ ".join(str(c).ljust(w) for c, w in zip(r, widths)) + " │"

    sep   = "├─" + "─┼─".join("─" * w for w in widths) + "─┤"
    top   = "┌─" + "─┬─".join("─" * w for w in widths) + "─┐"
    bot   = "└─" + "─┴─".join("─" * w for w in widths) + "─┘"

    lines = [top, _row(headers), sep]
    for r in rows:
        # Pad row to match header count
        r = list(r) + [""] * (len(headers) - len(r))
        lines.append(_row(r))
    lines.append(bot)
    if table.get("note"):
        lines.append(f"Note: {table['note']}")
    return "\n".join(lines)


def table_node(state: ProjectState) -> ProjectState:
    print("\n╔══ 📋  TABLE AGENT ══════════════════════════════════╗")
    print(f"║  Building tables for: {state['topic']}")
    os.makedirs(REPORT_DIR, exist_ok=True)

    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content":
                    f"Topic: {state['topic']}\n"
                    f"Subject: {state['subject_area']}\n"
                    f"Research context:\n{state['research_notes'][:700]}"},
            ],
            temperature=0.3, max_tokens=1000,
        )
        raw = r.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = "\n".join(l for l in raw.split("\n")
                            if not l.strip().startswith("```")).strip()
        tables = json.loads(raw)
        print(f"║  {len(tables)} tables generated")

        # Save as formatted text file
        txt_path = os.path.join(REPORT_DIR, "tables.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"DATA TABLES — {state['topic']}\n{'='*60}\n\n")
            for t in tables:
                f.write(f"\n{t['title']}\n")
                f.write(_format_table(t))
                f.write("\n\n")
            print(f"║  → Saved: tables.txt")

        print("╚══════════════════════════════════════════════════════╝")
        return {**state, "table_data": tables, "current_step": "table_done",
                "messages": state["messages"] + [
                    {"role": "table_agent", "content": f"{len(tables)} tables"}]}

    except Exception as e:
        print(f"║  ⚠️  {e}")
        print("╚══════════════════════════════════════════════════════╝")
        return {**state, "table_data": [], "current_step": "table_done",
                "errors": state["errors"] + [f"Table: {e}"]}
