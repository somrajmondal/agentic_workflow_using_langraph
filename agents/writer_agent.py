

from openai import OpenAI
from state import ProjectState
from config import OPENAI_API_KEY, MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM = """
You are an expert academic writer.
Using the research notes provided, write a complete project report.

Sections (use ## headings):
## Abstract
## 1. Introduction
## 2. Background & History
## 3. Core Concepts
## 4. Applications & Use Cases
## 5. Advantages & Limitations
## 6. Future Scope
## 7. Conclusion

Rules:
- Minimum 900 words, full paragraphs 
- Academic tone, clear for undergraduate level
- Base content only on the provided research notes
"""


def writer_node(state: ProjectState) -> ProjectState:
    print("\n╔══ ✍️   WRITER ═══════════════════════════════════════╗")
    print(f"║  Writing report for: {state['topic']}")
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content":
                    f"Topic: {state['topic']}\n\n"
                    f"Research Notes:\n{state['research_notes']}\n\n"
                    "Write the complete academic report now."},
            ],
            temperature=0.6, max_tokens=2000,
        )
        theory = r.choices[0].message.content.strip()
        wc = len(theory.split())
        print(f"║  {wc} words written")
        print("╚══════════════════════════════════════════════════════╝")
        return {**state, "theory": theory, "current_step": "writer_done",
                "messages": state["messages"] + [
                    {"role": "writer", "content": f"{wc} words"}]}
    except Exception as e:
        print(f"║  ⚠️  {e}")
        print("╚══════════════════════════════════════════════════════╝")
        return {**state,
                "theory": f"# {state['topic']}\n\n{state['research_notes']}",
                "current_step": "writer_done",
                "errors": state["errors"] + [f"Writer: {e}"]}
