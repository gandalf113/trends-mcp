from datetime import datetime
from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP
from trending_server.client import fetch_reddit_popular_topics, fetch_google_trends_rss_struct

mcp = FastMCP("Trends")


@mcp.tool()
async def get_reddit_trending_topics(limit: int = 10) -> str:
    topics = fetch_reddit_popular_topics(limit)
    formatted = []
    for t in topics:
        # format date here
        pretty_date = "Unknown date"
        if t["publishDate"]:
            dt = datetime(*t["publishDate"][:6])
            pretty_date = dt.strftime("%b %d, %Y %I:%M %p")  # e.g. Oct 29, 2025 11:39 AM

        links = "\n".join([f"- {link}" for link in t["links"]]) if t["links"] else "No links"
        formatted.append(
            f"**{t['title']}**\n"
            f"_{pretty_date}_\n\n"
            f"{t['summary']}\n\n"
            f"{links}"
        )
    return "\n\n---\n\n".join(formatted)


@mcp.tool()
async def get_google_trending_topics(limit: int = 10) -> str:
    topics = fetch_google_trends_rss_struct()[:limit]
    out = []

    for t in topics:
        # Pretty date
        pretty_date = "Unknown date"
        if t.get("publishedAt"):
            try:
                dt = datetime(*t["publishedAt"][:6])  # assuming struct_time
                pretty_date = dt.strftime("%b %d, %Y %I:%M %p")
            except Exception:
                pretty_date = str(t["publishedAt"])

        # Format candidates
        candidates_fmt = []
        for c in t.get("candidates", []):
            candidates_fmt.append(
                f"- **{c['title']}** ({c['source']})\n  {c['url']}"
            )
        candidates_str = "\n".join(candidates_fmt) if candidates_fmt else "No articles found"

        ft = (
            f"### {t['topic'].title()}\n"
            f"**Published at:** {pretty_date}\n"
            f"**Approximate traffic:** {t['approxTraffic']}\n\n"
            f"**Articles:**\n{candidates_str}"
        )
        out.append(ft)

    return "\n\n---\n\n".join(out)

@asynccontextmanager
async def lifespan(app):
    async with mcp.session_manager.run():
        yield


app = Starlette(
    lifespan=lifespan,
    routes=[
        # streamable HTTP endpoint at /mcp
        Mount("/", app=mcp.streamable_http_app()),
    ],
)
