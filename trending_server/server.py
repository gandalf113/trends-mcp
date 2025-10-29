from datetime import datetime
from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.routing import Mount
from mcp.server.fastmcp import FastMCP
from trending_server.client import fetch_reddit_popular_topics, fetch_google_trends_rss_struct
from trending_server.utils import generate_trending_news_pdf, S3Uploader

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


@mcp.tool()
async def create_trending_news_pdf(
    asOf: str,
    trending: list[dict]
) -> str:
    """
    Generate a PDF from trending news data and upload it to S3-compatible storage.

    Args:
        asOf: ISO-8601 timestamp for when the trending data is valid
        trending: List of trending news items, each containing:
            - title: Headline or title of the trending story
            - summary: Short summary or description of the story
            - category: One of ENTERTAINMENT, BUSINESS, POLITICS, or SPORTS
            - audience: Target audience or region (e.g. 'Virginia', 'US')
            - items: List of source URLs for the story

    Returns:
        str: The CDN URL (if configured) or direct storage URL of the uploaded PDF
    """
    # Construct the data dictionary matching the schema
    data = {
        "asOf": asOf,
        "trending": trending
    }

    # Generate PDF
    pdf_buffer = generate_trending_news_pdf(data)

    # Upload to storage
    uploader = S3Uploader()
    url = uploader.upload_pdf(
        pdf_data=pdf_buffer,
        metadata={
            'asOf': asOf,
            'trending_count': str(len(trending))
        }
    )

    return f"PDF successfully created and uploaded: {url}"


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
