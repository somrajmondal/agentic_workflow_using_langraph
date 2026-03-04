

import os
from dotenv import load_dotenv

load_dotenv()

MODEL          = "gpt-4o-mini"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

if not OPENAI_API_KEY:
    raise EnvironmentError(
        "\n  OPENAI_API_KEY not set!\n"
        "    export OPENAI_API_KEY=sk-...\n"
        "    OR:  echo 'OPENAI_API_KEY=sk-...' > .env\n"
    )

# Output directory — all agents write here
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "project_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Sub-folders (created on demand by each agent)
CHARTS_DIR   = os.path.join(OUTPUT_DIR, "Charts")
IMAGES_DIR   = os.path.join(OUTPUT_DIR, "Images")
CODE_DIR     = os.path.join(OUTPUT_DIR, "Code")
REPORT_DIR   = os.path.join(OUTPUT_DIR, "Report")
