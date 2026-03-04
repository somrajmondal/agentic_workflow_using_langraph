

import os, json
from openai import OpenAI
from state import ProjectState
from config import OPENAI_API_KEY, MODEL, OUTPUT_DIR

client     = OpenAI(api_key=OPENAI_API_KEY)
REPORT_DIR = os.path.join(OUTPUT_DIR, "Report")

SYSTEM = """
You are an academic historian and fact-checker.
Generate a chronological timeline of 8–12 key events/milestones for the topic.
Include real dates and factually accurate events.

Return ONLY valid JSON array, no markdown:
[
  {"year": "1905", "event": "Description of what happened"},
  {"year": "1920", "event": "Description of what happened"}
]
"""


def _render_timeline(events: list[dict]) -> str:
    """Render timeline as a visual ASCII timeline."""
    lines = ["TIMELINE\n" + "═" * 60]
    for e in events:
        year  = str(e.get("year", "?"))
        event = e.get("event", "")
        lines.append(f"\n  ◆ {year}")
        lines.append(f"  │  {event}")
    lines.append("\n" + "═" * 60)
    return "\n".join(lines)


def timeline_node(state: ProjectState) -> ProjectState:
    print("\n╔══ ⏳  TIMELINE AGENT ════════════════════════════════╗")
    print(f"║  Building timeline for: {state['topic']}")
    os.makedirs(REPORT_DIR, exist_ok=True)

    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content":
                    f"Topic: {state['topic']}\n"
                    f"Research context:\n{state['research_notes'][:600]}"},
            ],
            temperature=0.3, max_tokens=800,
        )
        raw = r.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = "\n".join(l for l in raw.split("\n")
                            if not l.strip().startswith("```")).strip()
        timeline = json.loads(raw)
        print(f"║  {len(timeline)} timeline events")

        # Save as text
        path = os.path.join(REPORT_DIR, "timeline.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"TIMELINE — {state['topic']}\n\n")
            f.write(_render_timeline(timeline))
        print(f"║  → Saved: timeline.txt")

        # Print preview
        for e in timeline[:4]:
            print(f"║    {e['year']} — {e['event'][:50]}")

        print("╚══════════════════════════════════════════════════════╝")
        return {**state, "timeline": timeline, "current_step": "timeline_done",
                "messages": state["messages"] + [
                    {"role": "timeline_agent",
                     "content": f"{len(timeline)} events"}]}

    except Exception as e:
        print(f"║  ⚠️  {e}")
        print("╚══════════════════════════════════════════════════════╝")
        return {**state, "timeline": [], "current_step": "timeline_done",
                "errors": state["errors"] + [f"Timeline: {e}"]}
