import requests
import logging
from datetime import timezone
from dateutil import parser as dtparse
from bs4 import BeautifulSoup

from trending_server.client.constants import DEFAULT_USER_AGENT

logger = logging.getLogger(__name__)

def fetch_google_trends_rss_struct(geo="US", timeout=15):
    url = f"https://trends.google.com/trending/rss?geo={geo}"
    try:
        r = requests.get(url, headers=DEFAULT_USER_AGENT, timeout=timeout)
        r.raise_for_status()
        xml_text = r.text
    except Exception as e:
        logger.exception(f"[google] RSS fetch error", e)
        return []

    try:
        # Use lxml's XML parser explicitly
        soup = BeautifulSoup(xml_text, "lxml-xml")

        items = []
        for it in soup.find_all("item"):
            # topic
            title_tag = it.find("title")
            topic = title_tag.get_text(strip=True) if title_tag else ""

            # publication date -> ISO UTC
            pub_iso = None
            pub_tag = it.find("pubDate")
            if pub_tag:
                pub_text = pub_tag.get_text(strip=True)
                if pub_text:
                    try:
                        dt = dtparse.parse(pub_text)
                        # make sure it's aware before converting to UTC
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        else:
                            dt = dt.astimezone(timezone.utc)
                        pub_iso = dt.isoformat()
                    except Exception:
                        pass

            # approx traffic
            approx_tag = it.find("ht:approx_traffic")
            approx = approx_tag.get_text(strip=True) if approx_tag else ""

            # news items (candidates)
            candidates = []
            for ni in it.find_all("ht:news_item"):
                t_tag = ni.find("ht:news_item_title")
                u_tag = ni.find("ht:news_item_url")
                s_tag = ni.find("ht:news_item_source")

                title = t_tag.get_text(strip=True) if t_tag else ""
                url = u_tag.get_text(strip=True) if u_tag else ""
                source = s_tag.get_text(strip=True) if s_tag else ""

                if url:
                    candidates.append({"title": title, "url": url, "source": source})

            items.append({
                "topic": topic,
                "publishedAt": pub_iso,
                "approxTraffic": approx,
                "candidates": candidates,
            })

        logger.info(f"[google] RSS struct items={len(items)} geo={geo}")
        return items

    except Exception as e:
        logger.exception(f"[google] RSS parse error", e)
        return []
