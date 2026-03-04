

import os
from openai import OpenAI
from state import ProjectState
from config import OPENAI_API_KEY, MODEL, OUTPUT_DIR

client     = OpenAI(api_key=OPENAI_API_KEY)
REPORT_DIR = os.path.join(OUTPUT_DIR, "Report")

SYSTEM = """
You are a knowledge cartographer.
Create a detailed ASCII mind map for the given topic.
Show the central topic, 4–6 main branches, and 2–3 sub-points per branch.

Format it like this:

                    ┌─────────────────────┐
                    │    [CENTRAL TOPIC]  │
                    └──────────┬──────────┘
             ┌─────────────────┼─────────────────┐
             │                 │                 │
       [Branch 1]        [Branch 2]        [Branch 3]
       ├─ sub 1a          ├─ sub 2a          ├─ sub 3a
       ├─ sub 1b          ├─ sub 2b          └─ sub 3b
       └─ sub 1c          └─ sub 2c

Use actual content — real sub-topics, real concepts, real facts.
Make it visually clear and informative.
"""


def mindmap_node(state: ProjectState) -> ProjectState:
    print("\n╔══ 🧠  MIND MAP AGENT ════════════════════════════════╗")
    print(f"║  Building mind map for: {state['topic']}")
    os.makedirs(REPORT_DIR, exist_ok=True)

    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content":
                    f"Topic: {state['topic']}\n"
                    f"Subject: {state['subject_area']}\n"
                    f"Key concepts from research:\n{state['research_notes'][:500]}"},
            ],
            temperature=0.4, max_tokens=700,
        )
        mindmap = r.choices[0].message.content.strip()

        # Save
        path = os.path.join(REPORT_DIR, "mindmap.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"MIND MAP — {state['topic']}\n{'='*60}\n\n")
            f.write(mindmap)
        print(f"║  → Saved: mindmap.txt")
        print("╚══════════════════════════════════════════════════════╝")

        return {**state, "mindmap": mindmap, "current_step": "mindmap_done",
                "messages": state["messages"] + [
                    {"role": "mindmap_agent", "content": "mind map created"}]}

    except Exception as e:
        print(f"║  ⚠️  {e}")
        print("╚══════════════════════════════════════════════════════╝")
        return {**state, "mindmap": "", "current_step": "mindmap_done",
                "errors": state["errors"] + [f"Mindmap: {e}"]}
