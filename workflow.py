
from langgraph.graph import StateGraph, END
from state import ProjectState

from agents.planner_agent   import planner_node
from agents.manager_agent   import manager_node
from agents.research_agent  import research_node
from agents.writer_agent    import writer_node
from agents.image_agent     import image_node
from agents.video_agent     import video_node
from agents.chart_agent     import chart_node
from agents.code_agent      import code_node
from agents.table_agent     import table_node
from agents.timeline_agent  import timeline_node
from agents.mindmap_agent   import mindmap_node
from agents.quiz_agent      import quiz_node
from agents.pdf_agent       import pdf_node
from agents.file_agent      import file_node


def _pass(state: ProjectState) -> ProjectState:
    return state


# ── One router per conditional capability ─────────────────────
def _route(flag: str, yes_node: str, no_node: str):
    def router(state: ProjectState) -> str:
        if state.get(flag, False):
            return yes_node
        print(f"  ⏭️  SKIP  {flag.replace('needs_','')}_agent")
        return no_node
    router.__name__ = f"route_{flag}"
    return router


# ── Build the graph ───────────────────────────────────────────
def build_workflow():
    g = StateGraph(ProjectState)

    # ── Fixed nodes ───────────────────────────────────────────
    g.add_node("planner",      planner_node)
    g.add_node("manager",      manager_node)
    g.add_node("research",     research_node)
    g.add_node("writer",       writer_node)

    # ── Conditional capability nodes ──────────────────────────
    g.add_node("image_agent",    image_node)
    g.add_node("video_agent",    video_node)
    g.add_node("chart_agent",    chart_node)
    g.add_node("code_agent",     code_node)
    g.add_node("table_agent",    table_node)
    g.add_node("timeline_agent", timeline_node)
    g.add_node("mindmap_agent",  mindmap_node)
    g.add_node("quiz_agent",     quiz_node)
    g.add_node("pdf_agent",      pdf_node)

    # ── Routing checkpoint nodes (no-ops, just branch points) ─
    for name in ["rt_image","rt_video","rt_chart","rt_code",
                 "rt_table","rt_timeline","rt_mindmap","rt_quiz","rt_pdf"]:
        g.add_node(name, _pass)

    # ── Final node ────────────────────────────────────────────
    g.add_node("file_agent", file_node)

    # ── Fixed edges: planner → manager → research → writer ───
    g.set_entry_point("planner")
    g.add_edge("planner",  "manager")
    g.add_edge("manager",  "research")
    g.add_edge("research", "writer")
    g.add_edge("writer",   "rt_image")   # Enter conditional pipeline

    # ── Conditional chain ─────────────────────────────────────
    # Each checkpoint routes to its agent OR the next checkpoint.
    # After each agent, go to the NEXT checkpoint.

    # 1. Image
    g.add_conditional_edges("rt_image", _route("needs_images","image_agent","rt_video"),
        {"image_agent":"image_agent", "rt_video":"rt_video"})
    g.add_edge("image_agent", "rt_video")

    # 2. Video
    g.add_conditional_edges("rt_video", _route("needs_video","video_agent","rt_chart"),
        {"video_agent":"video_agent", "rt_chart":"rt_chart"})
    g.add_edge("video_agent", "rt_chart")

    # 3. Chart
    g.add_conditional_edges("rt_chart", _route("needs_charts","chart_agent","rt_code"),
        {"chart_agent":"chart_agent", "rt_code":"rt_code"})
    g.add_edge("chart_agent", "rt_code")

    # 4. Code
    g.add_conditional_edges("rt_code", _route("needs_code","code_agent","rt_table"),
        {"code_agent":"code_agent", "rt_table":"rt_table"})
    g.add_edge("code_agent", "rt_table")

    # 5. Table
    g.add_conditional_edges("rt_table", _route("needs_table","table_agent","rt_timeline"),
        {"table_agent":"table_agent", "rt_timeline":"rt_timeline"})
    g.add_edge("table_agent", "rt_timeline")

    # 6. Timeline
    g.add_conditional_edges("rt_timeline", _route("needs_timeline","timeline_agent","rt_mindmap"),
        {"timeline_agent":"timeline_agent", "rt_mindmap":"rt_mindmap"})
    g.add_edge("timeline_agent", "rt_mindmap")

    # 7. Mind Map
    g.add_conditional_edges("rt_mindmap", _route("needs_mindmap","mindmap_agent","rt_quiz"),
        {"mindmap_agent":"mindmap_agent", "rt_quiz":"rt_quiz"})
    g.add_edge("mindmap_agent", "rt_quiz")

    # 8. Quiz
    g.add_conditional_edges("rt_quiz", _route("needs_quiz","quiz_agent","rt_pdf"),
        {"quiz_agent":"quiz_agent", "rt_pdf":"rt_pdf"})
    g.add_edge("quiz_agent", "rt_pdf")

    # 9. PDF
    g.add_conditional_edges("rt_pdf", _route("needs_pdf","pdf_agent","file_agent"),
        {"pdf_agent":"pdf_agent", "file_agent":"file_agent"})
    g.add_edge("pdf_agent", "file_agent")

    # Final
    g.add_edge("file_agent", END)

    return g.compile()
