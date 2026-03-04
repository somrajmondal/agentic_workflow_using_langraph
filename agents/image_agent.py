import os
import asyncio
import mimetypes
import httpx
from playwright.async_api import async_playwright
from state import ProjectState
from config import OUTPUT_DIR

IMAGES_DIR = os.path.join(OUTPUT_DIR, "Images")
MAX_IMAGES = 5
PAGE_TIMEOUT = 30000

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": UA,
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}


# ----------------------------
# SCROLL FUNCTION (Improved)
# ----------------------------
async def _scroll(page, rounds=5):
    for _ in range(rounds):
        await page.mouse.wheel(0, 3000)
        await asyncio.sleep(1)


# ----------------------------
# GET IMAGE URLS (Improved)
# ----------------------------
async def _get_urls(page) -> list[str]:
    await page.wait_for_selector("img", timeout=10000)

    images = await page.query_selector_all("img")
    urls = set()

    for img in images:
        src = await img.get_attribute("src")
        if not src:
            continue

        if src.startswith("http") and "gstatic" not in src:
            urls.add(src)

        if len(urls) >= MAX_IMAGES:
            break

    return list(urls)


# ----------------------------
# DOWNLOAD IMAGES (Improved)
# ----------------------------
async def _download(urls: list[str]) -> list[str]:
    os.makedirs(IMAGES_DIR, exist_ok=True)
    saved = []

    async with httpx.AsyncClient(
        headers=HEADERS,
        follow_redirects=True,
        timeout=httpx.Timeout(20.0)
    ) as client:

        for i, url in enumerate(urls, 1):
            try:
                response = await client.get(url)

                if response.status_code != 200:
                    continue

                content_type = response.headers.get(
                    "content-type", "image/jpeg"
                ).split(";")[0].strip()

                ext = mimetypes.guess_extension(content_type) or ".jpg"
                file_path = os.path.join(
                    IMAGES_DIR,
                    f"image_{i:02d}{ext}"
                )

                with open(file_path, "wb") as f:
                    f.write(response.content)

                saved.append(file_path)

            except Exception:
                continue

    return saved


# ----------------------------
# MAIN SCRAPER
# ----------------------------
async def _run(query: str) -> list[str]:
    url = (
        "https://www.google.com/search?tbm=isch&safe=active&q="
        + query.replace(" ", "+")
    )

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

        context = await browser.new_context(
            user_agent=UA,
            locale="en-US",
            viewport={"width": 1280, "height": 800},
        )

        page = await context.new_page()

        try:
            await page.goto(url, timeout=PAGE_TIMEOUT)
            await _scroll(page)

            urls = await _get_urls(page)

        finally:
            await browser.close()

    return await _download(urls) if urls else []


# ----------------------------
# SAFE ASYNC EXECUTION
# ----------------------------
def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        return loop.run_until_complete(coro)


# ----------------------------
# IMAGE NODE
# ----------------------------
def image_node(state: ProjectState) -> ProjectState:
    print("\n╔══ 🖼️ IMAGE AGENT ═══════════════════════════════╗")

    noise = {
        "create", "a", "college", "school", "project",
        "on", "with", "and", "the", "generate",
        "make", "write", "report", "about"
    }

    words = [
        w for w in state["topic"].lower().split()
        if w not in noise
    ]

    query = " ".join(words[:5]) + " diagram illustration"

    try:
        paths = run_async(_run(query))

        return {
            **state,
            "image_paths": paths,
            "current_step": "image_done",
            "messages": state["messages"] + [
                {
                    "role": "image_agent",
                    "content": f"{len(paths)} images downloaded"
                }
            ],
        }

    except Exception as e:
        return {
            **state,
            "image_paths": [],
            "current_step": "image_done",
            "errors": state.get("errors", []) + [f"Image Agent: {e}"],
        }