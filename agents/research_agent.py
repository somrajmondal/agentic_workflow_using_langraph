

from openai import OpenAI
from state import ProjectState
from config import OPENAI_API_KEY, MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM = """
You are an expert academic researcher.
Write comprehensive research notes covering ALL of:

### Background & History
### Core Concepts & Principles
### Key Facts & Statistics (include real numbers)
### Real-World Applications
### Advantages & Limitations
### Current Trends & Future Scope

Then a REFERENCES section with 6 credible sources.

Format:
## RESEARCH NOTES
### [section]
...

## REFERENCES
1. Author (Year). Title. Publisher/URL.
"""


def research_node(state: ProjectState) -> ProjectState:
    print("\n╔══ 🔬  RESEARCH ═════════════════════════════════════╗")
    print(f"║  Topic: {state['topic']}")
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content":
                    f"Topic: {state['topic']}\n"
                    f"Subject: {state['subject_area']}\n"
                    f"Tasks: {', '.join(state['tasks'][:5])}"},
            ],
            temperature=0.4, max_tokens=2000,
        )
        full = r.choices[0].message.content.strip()

        if "## REFERENCES" in full:
            parts = full.split("## REFERENCES")
            notes = parts[0].replace("## RESEARCH NOTES", "").strip()
            refs  = [l.strip() for l in parts[1].split("\n")
                     if l.strip() and l.strip()[0].isdigit()]
        else:
            notes, refs = full, []

        print(f"║  {len(notes.split())} words  |  {len(refs)} references")
        print("╚══════════════════════════════════════════════════════╝")
        return {**state, "research_notes": notes, "references": refs,
                "current_step": "research_done",
                "messages": state["messages"] + [
                    {"role": "research",
                     "content": f"{len(notes.split())} words, {len(refs)} refs"}]}
    except Exception as e:
        print(f"║  ⚠️  {e}")
        print("╚══════════════════════════════════════════════════════╝")
        return {**state,
                "research_notes": f"Research on {state['topic']}. Error: {e}",
                "references": [],
                "current_step": "research_done",
                "errors": state["errors"] + [f"Research: {e}"]}
