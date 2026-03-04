

import os, asyncio, re
from playwright.async_api import async_playwright
from state import ProjectState
from config import OUTPUT_DIR

PAGE_TIMEOUT = 20_000
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0.0.0 Safari/537.36")


async def _search_youtube(query: str) -> list[dict]:
    """Search YouTube and return top 3 video dicts."""
    url = "https://www.youtube.com/results?search_query=" + query.replace(" ", "+")
    print(f"║  YouTube search: {query!r}")
    videos = []

    async with async_playwright() as pw:
        br   = await pw.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-setuid-sandbox",
                  "--disable-dev-shm-usage"])
        ctx  = await br.new_context(user_agent=UA, locale="en-US",
                                     viewport={"width": 1280, "height": 800})
        page = await ctx.new_page()
        try:
            await page.goto(url, timeout=PAGE_TIMEOUT, wait_until="domcontentloaded")
            await asyncio.sleep(2)

            # Dismiss cookie consent if present
            try:
                btn = page.locator("button:has-text('Accept all'), tp-yt-paper-button:has-text('Accept')")
                if await btn.count() > 0:
                    await btn.first.click(timeout=3000)
                    await asyncio.sleep(1)
            except Exception:
                pass

            # Extract video links and titles
            anchors = await page.query_selector_all("a#video-title")
            for a in anchors[:15]:
                try:
                    title = await a.get_attribute("title") or await a.inner_text()
                    href  = await a.get_attribute("href") or ""
                    if "/watch?v=" in href:
                        vid_id = href.split("v=")[1].split("&")[0]
                        watch  = f"https://www.youtube.com/watch?v={vid_id}"
                        embed  = f"https://www.youtube.com/embed/{vid_id}"
                        thumb  = f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg"
                        videos.append({
                            "title": title.strip(),
                            "url":   watch,
                            "embed": embed,
                            "thumbnail": thumb,
                            "video_id":  vid_id,
                        })
                    if len(videos) >= 3:
                        break
                except Exception:
                    continue

        except Exception as e:
            print(f"║  ⚠️  YouTube page error: {e}")
        finally:
            await br.close()

    return videos


def video_node(state: ProjectState) -> ProjectState:
    print("\n╔══ 🎬  VIDEO AGENT ══════════════════════════════════╗")
    query = state["topic"] + " explained tutorial"

    try:
        videos = asyncio.run(_search_youtube(query))
        print(f"║  {len(videos)} videos found:")
        for v in videos:
            print(f"║    • {v['title'][:55]}")
            print(f"║      {v['url']}")
        print("╚══════════════════════════════════════════════════════╝")

        return {**state, "video_links": videos, "current_step": "video_done",
                "messages": state["messages"] + [
                    {"role": "video_agent",
                     "content": f"{len(videos)} videos: {[v['title'] for v in videos]}"}]}

    except Exception as e:
        print(f"║  ⚠️  {e}")
        print("╚══════════════════════════════════════════════════════╝")
        return {**state, "video_links": [], "current_step": "video_done",
                "errors": state["errors"] + [f"Video: {e}"]}
