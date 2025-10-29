import re
import feedparser

def fetch_reddit_popular_topics(limit=10):
    topics = []
    url = "https://www.reddit.com/discover.rss"
    d = feedparser.parse(url, request_headers={"Accept-Languge": "en-US"})
    for e in d.entries[:limit * 2]:
        title = (e.get("title") or "").strip()
        title = re.sub(r'\s*\[[^\]]+\]\s*', ' ', title).strip()
        summary = (e.get("summary" or "")).strip()
        links = [i.get("href") for i in (e.get("links") or [])]
        published = e.get("published_parsed")

        topics.append({
            "title": title,
            "summary": summary,
            "links": links,
            "publishDate": published
        })

        if len(topics) >= limit:
            break

    return topics