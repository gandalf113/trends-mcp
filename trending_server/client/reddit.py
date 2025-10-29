import feedparser
import re


def fetch_reddit_popular_topics(limit=10):
    url = "https://www.reddit.com/discover.rss"
    topics = []
    d = feedparser.parse(url, request_headers={"Accept-Languge": "en-US"})
    for e in d.entries[:limit * 2]:
        t = (e.get("title") or "").strip()
        t = re.sub(r'\s*\[[^\]]+\]\s*', ' ', t).strip()
        if t and 2 <= len(t.split()) <= 12 and len(t) <= 140:
            if t not in topics:
                topics.append(t)
        if len(topics) >= limit:
            break
    return topics[:limit]
