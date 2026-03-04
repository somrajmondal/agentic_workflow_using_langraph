

import json
from openai import OpenAI
from state import ProjectState
from config import OPENAI_API_KEY, MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM = """
You are a senior academic project planner.
From the student's request extract:
  1. topic       — clean short name, e.g. "Solar Energy", "World War 2", "CNN"
  2. subject_area — one of: [science, cs, history, geography, biology,
                              physics, chemistry, math, economics, general]
  3. tasks        — 6–8 ordered sub-tasks to complete the project

Return ONLY valid JSON, no markdown fences:
{
  "topic": "...",
  "subject_area": "...",
  "tasks": ["task1", ...]
}
"""


def planner_node(state: ProjectState) -> ProjectState:
    print("\n╔══ 🗂️  PLANNER ══════════════════════════════════════╗")
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user",   "content": state["user_prompt"]},
            ],
            temperature=0.2, max_tokens=500,
        )
        raw = r.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = "\n".join(l for l in raw.split("\n")
                            if not l.strip().startswith("```")).strip()
        d = json.loads(raw)
        topic        = d.get("topic", state["user_prompt"][:50])
        subject_area = d.get("subject_area", "general")
        tasks        = d.get("tasks", [])

        print(f"║  Topic   : {topic}")
        print(f"║  Subject : {subject_area}")
        for i, t in enumerate(tasks, 1):
            print(f"║  Task {i}  : {t}")
        print("╚══════════════════════════════════════════════════════╝")

        return {**state, "topic": topic, "subject_area": subject_area,
                "tasks": tasks, "current_step": "planner_done"}

    except Exception as e:
        print(f"║  ⚠️  Error: {e}")
        print("╚══════════════════════════════════════════════════════╝")
        return {**state,
                "topic": state["user_prompt"][:60],
                "subject_area": "general",
                "tasks": ["Research topic", "Write theory", "Build report"],
                "current_step": "planner_done",
                "errors": state["errors"] + [f"Planner: {e}"]}
