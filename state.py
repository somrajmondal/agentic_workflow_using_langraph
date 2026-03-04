

from typing import TypedDict, List, Optional


class ProjectState(TypedDict):

    # ── INPUT ─────────────────────────────────────────────────
    user_prompt:        str           # Raw user input
    topic:              str           # Cleaned topic name
    subject_area:       str           # science / cs / history / etc.
    tasks:              List[str]     # Planner sub-task list

    # ── MANAGER CAPABILITY FLAGS ──────────────────────────────
    # Set by manager_node. Each flag = one conditional branch.
    needs_research:     bool          # Web search / deep research
    needs_images:       bool          # Download images from Google
    needs_video:        bool          # Embed YouTube video links
    needs_charts:       bool          # Generate data charts (matplotlib)
    needs_code:         bool          # Generate Python code
    needs_table:        bool          # Build a comparison/data table
    needs_quiz:         bool          # Generate MCQ quiz
    needs_timeline:     bool          # Build historical timeline
    needs_pdf:          bool          # Export report as PDF
    needs_mindmap:      bool          # Generate ASCII mind map

    # ── AGENT OUTPUTS ─────────────────────────────────────────
    research_notes:     str
    references:         List[str]
    theory:             str           # Full written report
    code:               str           # Python source code
    chart_paths:        List[str]     # PNG file paths
    image_paths:        List[str]     # Downloaded image file paths
    video_links:        List[dict]    # [{"title":..., "url":..., "embed":...}]
    table_data:         List[dict]    # [{"header": [...], "rows": [[...]]}]
    quiz:               List[dict]    # [{"q":..., "options":..., "answer":...}]
    timeline:           List[dict]    # [{"year":..., "event":...}]
    mindmap:            str           # ASCII mind map text
    pdf_path:           str           # Final PDF file path
    zip_path:           str           # Final ZIP file path

    # ── SYSTEM ────────────────────────────────────────────────
    messages:           List[dict]
    current_step:       str
    errors:             List[str]
