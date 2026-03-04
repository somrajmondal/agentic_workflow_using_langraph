

import json
from openai import OpenAI
from state import ProjectState
from config import OPENAI_API_KEY, MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM = """
You are the manager of an agentic AI project builder.
Given a topic and subject area, decide which capabilities are needed.

CAPABILITY RULES:
  needs_research  → ALWAYS true (every project needs research)
  needs_images    → true if topic benefits from diagrams/photos
                    (science, engineering, biology, geography, history landmarks)
  needs_video     → true if topic has good explanatory YouTube content
                    (science experiments, historical events, how-things-work topics)
  needs_charts    → true if topic involves data, statistics, comparisons,
                    performance metrics, trends, growth, percentages
  needs_code      → true ONLY for CS / AI / algorithms / data science / programming topics
  needs_table     → true if topic compares multiple items, pros/cons, specifications,
                    countries, elements, methods, time periods
  needs_quiz      → ALWAYS true (revision questions help every project)
  needs_timeline  → true if topic is historical, has major milestones, evolution over time
  needs_pdf       → ALWAYS true (PDF is the final submission format)
  needs_mindmap   → true if topic has many sub-branches / sub-concepts to map

Return ONLY valid JSON (no markdown):
{
  "needs_research":  true,
  "needs_images":    true,
  "needs_video":     false,
  "needs_charts":    true,
  "needs_code":      false,
  "needs_table":     true,
  "needs_quiz":      true,
  "needs_timeline":  false,
  "needs_pdf":       true,
  "needs_mindmap":   true,
  "reason": "one line explanation of choices"
}
"""

ICONS = {
    "needs_research": "🔬",
    "needs_images":   "🖼️ ",
    "needs_video":    "🎬",
    "needs_charts":   "📊",
    "needs_code":     "👨‍💻",
    "needs_table":    "📋",
    "needs_quiz":     "🧪",
    "needs_timeline": "⏳",
    "needs_pdf":      "📄",
    "needs_mindmap":  "🧠",
}


def manager_node(state: ProjectState) -> ProjectState:
    print("\n╔══ 🎯  MANAGER ══════════════════════════════════════╗")
    print(f"║  Analysing: {state['topic']!r} ({state['subject_area']})")

    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content":
                    f"Topic: {state['topic']}\n"
                    f"Subject area: {state['subject_area']}\n"
                    f"Tasks: {', '.join(state['tasks'][:4])}"},
            ],
            temperature=0.1, max_tokens=350,
        )
        raw = r.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = "\n".join(l for l in raw.split("\n")
                            if not l.strip().startswith("```")).strip()
        d      = json.loads(raw)
        reason = d.pop("reason", "")

        flags  = {k: bool(d.get(k, True)) for k in ICONS}

        print(f"║  Reason: {reason}")
        print("║  ─────────────────────────────────────────────────")
        for k, icon in ICONS.items():
            status = "✅ RUN " if flags[k] else "⏭️  SKIP"
            print(f"║  {status}  {icon}  {k}")
        print("╚══════════════════════════════════════════════════════╝")

        return {**state, **flags, "current_step": "manager_done",
                "messages": state["messages"] + [
                    {"role": "manager", "content": str(flags)}]}

    except Exception as e:
        print(f"║  ⚠️  Error: {e} — enabling all capabilities")
        print("╚══════════════════════════════════════════════════════╝")
        all_on = {k: True for k in ICONS}
        return {**state, **all_on, "current_step": "manager_done",
                "errors": state["errors"] + [f"Manager: {e}"]}
