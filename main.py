
import asyncio
from workflow import build_workflow
from state import ProjectState



async def main():

    prompt = input("📝 Enter your project topic:\n> ").strip()
    if not prompt:
        prompt = "Solar Energy"

    print(f"\n🚀 Starting workflow for: {prompt!r}\n{'═'*60}")

    app = build_workflow()

    initial: ProjectState = {
        "user_prompt":    prompt,
        "topic":          "",
        "subject_area":   "",
        "tasks":          [],
        # Manager flags (all default True; manager will override)
        "needs_research":  True,
        "needs_images":    True,
        "needs_video":     True,
        "needs_charts":    True,
        "needs_code":      True,
        "needs_table":     True,
        "needs_quiz":      True,
        "needs_timeline":  True,
        "needs_pdf":       True,
        "needs_mindmap":   True,
        # Agent outputs
        "research_notes":  "",
        "references":      [],
        "theory":          "",
        "code":            "",
        "chart_paths":     [],
        "image_paths":     [],
        "video_links":     [],
        "table_data":      [],
        "quiz":            [],
        "timeline":        [],
        "mindmap":         "",
        "pdf_path":        "",
        "zip_path":        "",
        # System
        "messages":        [],
        "current_step":    "start",
        "errors":          [],
    }

    final = initial
    async for step in app.astream(initial):
        for node_name, state in step.items():
            final = state

    # ── Final summary ────────────────────────────────────────
    print(f"\n{'═'*60}")
    print("  🎉  PROJECT COMPLETE!")
    print(f"{'═'*60}")
    print(f"  Topic      : {final.get('topic', prompt)}")
    print(f"  Subject    : {final.get('subject_area', '—')}")
    print(f"  Charts     : {len(final.get('chart_paths', []))} PNG files")
    print(f"  Images     : {len(final.get('image_paths', []))} downloaded")
    print(f"  Videos     : {len(final.get('video_links', []))} YouTube links")
    print(f"  Timeline   : {len(final.get('timeline', []))} events")
    print(f"  Tables     : {len(final.get('table_data', []))} tables")
    print(f"  Quiz       : {len(final.get('quiz', []))} MCQ questions")
    print(f"  Mind Map   : {'✅' if final.get('mindmap') else '—'}")
    print(f"  Code       : {'✅' if final.get('code','').strip() else '—'}")
    print(f"  PDF        : {final.get('pdf_path', '—')}")
    print(f"  📦 ZIP     : {final.get('zip_path', '—')}")

    if final.get("errors"):
        print(f"\n  ⚠️  {len(final['errors'])} warning(s):")
        for e in final["errors"]:
            print(f"     • {e}")

    print(f"{'═'*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
