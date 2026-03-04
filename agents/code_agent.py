

from openai import OpenAI
from state import ProjectState
from config import OPENAI_API_KEY, MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM = """
You are a senior Python engineer and AI researcher.
Generate complete, RUNNABLE Python code for the given project.

Requirements:
- All imports at top
- Docstrings on every function/class
- Inline comments explaining key steps
- Use relevant libraries: TensorFlow/Keras, sklearn, numpy, matplotlib, etc.
- Self-contained: no external file dependencies
- Return ONLY raw Python code — no markdown fences, no preamble
"""


def code_node(state: ProjectState) -> ProjectState:
    print("\n╔══   CODE AGENT ══════════════════════════════════╗")
    print(f"║  Generating Python code for: {state['topic']}")
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content":
                    f"Project: {state['topic']}\n"
                    f"Context: {state['research_notes'][:600]}\n\n"
                    "Generate complete working Python code now."},
            ],
            temperature=0.2, max_tokens=1800,
        )
        code = r.choices[0].message.content.strip()
        if code.startswith("```"):
            code = "\n".join(l for l in code.split("\n")
                             if not l.strip().startswith("```")).strip()
        lines = len(code.splitlines())
        print(f"║  {lines} lines generated")
        print("╚══════════════════════════════════════════════════════╝")
        return {**state, "code": code, "current_step": "code_done",
                "messages": state["messages"] + [
                    {"role": "code_agent", "content": f"{lines} lines"}]}
    except Exception as e:
        print(f"║    {e}")
        print("╚══════════════════════════════════════════════════════╝")
        return {**state,
                "code": f"# {state['topic']}\n# Error: {e}\n",
                "current_step": "code_done",
                "errors": state["errors"] + [f"Code: {e}"]}
