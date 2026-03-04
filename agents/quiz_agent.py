

import os, json
from openai import OpenAI
from state import ProjectState
from config import OPENAI_API_KEY, MODEL, OUTPUT_DIR

client     = OpenAI(api_key=OPENAI_API_KEY)
REPORT_DIR = os.path.join(OUTPUT_DIR, "Report")

SYSTEM = """
You are an academic quiz creator.
Generate exactly 5 multiple-choice questions based on the research notes.
Questions should test real understanding, not just memorisation.

Return ONLY valid JSON array, no markdown:
[
  {
    "q": "Question?",
    "options": {"A":"...","B":"...","C":"...","D":"..."},
    "answer": "B",
    "explanation": "Why B is correct."
  }
]
"""


def quiz_node(state: ProjectState) -> ProjectState:
    print("\n╔══ 🧪  QUIZ AGENT ════════════════════════════════════╗")
    os.makedirs(REPORT_DIR, exist_ok=True)
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content":
                    f"Topic: {state['topic']}\n"
                    f"Research:\n{state['research_notes'][:900]}"},
            ],
            temperature=0.5, max_tokens=900,
        )
        raw = r.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = "\n".join(l for l in raw.split("\n")
                            if not l.strip().startswith("```")).strip()
        quiz = json.loads(raw)

        # Save as text
        path = os.path.join(REPORT_DIR, "quiz.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"REVISION QUIZ — {state['topic']}\n{'='*60}\n\n")
            for i, q in enumerate(quiz, 1):
                f.write(f"Q{i}. {q['q']}\n")
                for k, v in q.get("options", {}).items():
                    f.write(f"   {k}) {v}\n")
                f.write(f"   ✅ Answer: {q.get('answer','?')}\n")
                if q.get("explanation"):
                    f.write(f"   💡 {q['explanation']}\n")
                f.write("\n")

        print(f"║  {len(quiz)} questions generated → quiz.txt")
        for i, q in enumerate(quiz, 1):
            print(f"║  Q{i}: {q['q'][:55]}...")
        print("╚══════════════════════════════════════════════════════╝")
        return {**state, "quiz": quiz, "current_step": "quiz_done",
                "messages": state["messages"] + [
                    {"role": "quiz_agent", "content": f"{len(quiz)} MCQs"}]}

    except Exception as e:
        print(f"║  ⚠️  {e}")
        print("╚══════════════════════════════════════════════════════╝")
        return {**state, "quiz": [], "current_step": "quiz_done",
                "errors": state["errors"] + [f"Quiz: {e}"]}
