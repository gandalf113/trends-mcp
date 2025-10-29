from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP
from trending_server.client import fetch_reddit_popular_topics, fetch_google_trends_rss_struct

mcp = FastMCP("Trends")

@mcp.tool()
async def get_reddit_trending_topics() -> str:
    topics = fetch_reddit_popular_topics()
    return "\n---\n".join(topics)

@mcp.tool()
async def get_google_trending_topics() -> str:
    topics = fetch_google_trends_rss_struct()
    out = []
    for t in topics:
        ft  = f"Topic: {t['topic']}\n"
        ft += f"Published at: {t['publishedAt']}\n"
        ft += f"Approximate traffic: {t['approxTraffic']}\n"
        ft += "Candidates:"
        for c in t["candidates"]:
            ft += "\n\n"
            ft += f"** Article title: {c['title']}\n"
            ft += f"** Article URL: {c['url']}\n"
            ft += f"** Article source: {c['source']}"
        out.append(ft)
    return "\n---\n".join(out)

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
