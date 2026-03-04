

import os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from openai import OpenAI
from state import ProjectState
from config import OPENAI_API_KEY, MODEL, OUTPUT_DIR

client    = OpenAI(api_key=OPENAI_API_KEY)
CHART_DIR = os.path.join(OUTPUT_DIR, "Charts")

DARK = {"bg":"#0d1117","ax":"#111520","grid":"#1e2133","text":"#e8eaf6",
        "muted":"#5c6080",
        "palette":["#00f5c4","#7b5cf0","#f0a500","#ff4f6d","#00b4ff",
                   "#a8ff78","#ff6b6b","#ffd93d"]}

PLAN_SYSTEM = """
You are a data visualisation expert for student projects.
Given a topic and research notes, design 2–3 meaningful charts.

Allowed chart_types: bar, line, pie, horizontal_bar

Each chart must have real, plausible data (not fake random numbers).
Use actual statistics or reasonable estimates from the research notes.

Return ONLY valid JSON array, no markdown:
[
  {
    "title": "Chart title",
    "chart_type": "bar",
    "labels": ["A","B","C","D"],
    "values": [30, 45, 20, 60],
    "xlabel": "X label",
    "ylabel": "Y label",
    "note": "Data source note"
  }
]
"""


def _style(ax):
    ax.set_facecolor(DARK["ax"])
    for s in ax.spines.values():
        s.set_edgecolor(DARK["grid"])
    ax.tick_params(colors=DARK["muted"], labelsize=9)


def _render(chart: dict, path: str):
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=DARK["bg"])
    _style(ax)
    colors = DARK["palette"]
    ct     = chart.get("chart_type", "bar").lower()
    labels = chart["labels"]
    values = chart["values"]
    n      = min(len(labels), len(values))
    labels, values = labels[:n], values[:n]

    if ct in ("bar", "horizontal_bar"):
        if ct == "horizontal_bar":
            bars = ax.barh(labels, values, color=colors[:n], edgecolor=DARK["grid"])
            for bar, val in zip(bars, values):
                ax.text(bar.get_width() + max(values)*0.01, bar.get_y() + bar.get_height()/2,
                        str(round(val,1)), va="center", color=DARK["text"], fontsize=8)
            ax.set_xlabel(chart.get("ylabel",""), color=DARK["muted"], fontsize=10)
            ax.grid(axis="x", color=DARK["grid"], linewidth=0.6)
        else:
            bars = ax.bar(labels, values, color=colors[:n], width=0.55, edgecolor=DARK["grid"])
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01,
                        str(round(val,1)), ha="center", color=DARK["text"], fontsize=8)
            ax.set_xlabel(chart.get("xlabel",""), color=DARK["muted"], fontsize=10)
            ax.set_ylabel(chart.get("ylabel",""), color=DARK["muted"], fontsize=10)
            ax.grid(axis="y", color=DARK["grid"], linewidth=0.6)
            plt.xticks(rotation=20, ha="right")

    elif ct == "line":
        x = list(range(n))
        ax.plot(x, values, color=DARK["palette"][0], linewidth=2.2,
                marker="o", markersize=5, markerfacecolor=DARK["palette"][1])
        ax.fill_between(x, values, alpha=0.08, color=DARK["palette"][0])
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=20, ha="right", color=DARK["muted"], fontsize=8)
        ax.set_xlabel(chart.get("xlabel",""), color=DARK["muted"], fontsize=10)
        ax.set_ylabel(chart.get("ylabel",""), color=DARK["muted"], fontsize=10)
        ax.grid(color=DARK["grid"], linewidth=0.6)

    elif ct == "pie":
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, colors=colors[:n],
            autopct="%1.1f%%", startangle=140,
            textprops={"color": DARK["text"], "fontsize": 9})
        for at in autotexts:
            at.set_color(DARK["bg"]); at.set_fontsize(8)
        ax.set_facecolor(DARK["ax"])

    note = chart.get("note", "")
    ax.set_title(chart["title"], color=DARK["text"], fontsize=13, fontweight="bold", pad=14)
    if note:
        fig.text(0.5, -0.02, f"Note: {note}", ha="center",
                 color=DARK["muted"], fontsize=8, style="italic")

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=DARK["bg"])
    plt.close(fig)
    print(f"║  → Saved: {os.path.basename(path)}")


def chart_node(state: ProjectState) -> ProjectState:
    print("\n╔══ 📊  CHART AGENT ══════════════════════════════════╗")
    os.makedirs(CHART_DIR, exist_ok=True)
    chart_paths = []

    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": PLAN_SYSTEM},
                {"role": "user", "content":
                    f"Topic: {state['topic']}\n\n"
                    f"Research notes excerpt:\n{state['research_notes'][:800]}"},
            ],
            temperature=0.3, max_tokens=900,
        )
        raw = r.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = "\n".join(l for l in raw.split("\n")
                            if not l.strip().startswith("```")).strip()
        charts = json.loads(raw)
        print(f"║  GPT-4o-mini planned {len(charts)} charts")

        for i, chart in enumerate(charts, 1):
            path = os.path.join(CHART_DIR, f"chart_{i:02d}_{chart['chart_type']}.png")
            _render(chart, path)
            chart_paths.append(path)

    except Exception as e:
        print(f"║   GPT planning failed ({e}), using fallback chart")
        fallback = {
            "title": f"Key Aspects of {state['topic']}",
            "chart_type": "bar",
            "labels": ["Importance","Adoption","Research","Applications","Growth"],
            "values": [85, 72, 90, 78, 88],
            "xlabel": "Aspect", "ylabel": "Score (%)", "note": "Illustrative values"
        }
        try:
            path = os.path.join(CHART_DIR, "chart_01_bar.png")
            _render(fallback, path)
            chart_paths.append(path)
        except Exception as e2:
            print(f"║    Fallback also failed: {e2}")

    print(f"║  {len(chart_paths)} charts total")
    print("╚══════════════════════════════════════════════════════╝")
    return {**state, "chart_paths": chart_paths, "current_step": "chart_done",
            "messages": state["messages"] + [
                {"role": "chart_agent", "content": f"{len(chart_paths)} charts"}]}
