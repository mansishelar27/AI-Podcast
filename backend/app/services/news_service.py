"""
Automated financial / stock market news fetcher.
Aggregates from multiple RSS feeds (India-focused and global) and returns
unified items for the homepage news column.
"""
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any, Optional

import httpx

from app.core.logger import logger

# RSS feeds: stock market and major financial news (India + global)
FINANCIAL_RSS_FEEDS = [
    {"url": "https://economictimes.indiatimes.com/rss.cms", "source": "Economic Times"},
    {"url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms", "source": "ET Markets"},
    {"url": "https://www.moneycontrol.com/rss/latestnews.xml", "source": "MoneyControl"},
    {"url": "https://www.business-standard.com/rss/home_page_top_stories.rss", "source": "Business Standard"},
]

# Namespaces commonly used in RSS
RSS_NS = {"dc": "http://purl.org/dc/elements/1.1/", "content": "http://purl.org/rss/1.0/modules/content/"}


def _parse_rss_item(item_el, source: str) -> Optional[Dict[str, Any]]:
    """Extract title, link, published, snippet from an <item> element."""
    try:
        title_el = item_el.find("title")
        link_el = item_el.find("link")
        if title_el is None or title_el.text is None or not title_el.text.strip():
            return None
        title = title_el.text.strip()
        link = link_el.text.strip() if link_el is not None and link_el.text else ""

        # Try pubDate first, then dc:date
        pub_date = None
        pub_el = item_el.find("pubDate") or item_el.find("dc:date", RSS_NS)
        if pub_el is not None and pub_el.text:
            try:
                pub_date = pub_el.text.strip()
            except Exception:
                pass

        desc_el = item_el.find("description") or item_el.find("content:encoded", RSS_NS)
        snippet = ""
        if desc_el is not None and desc_el.text:
            raw = desc_el.text.strip()
            # Strip HTML tags for snippet
            snippet = re.sub(r"<[^>]+>", " ", raw).strip()
            snippet = snippet[:200] + "..." if len(snippet) > 200 else snippet

        return {
            "title": title,
            "link": link,
            "published": pub_date,
            "snippet": snippet,
            "source": source,
        }
    except Exception as e:
        logger.debug("Parse RSS item failed: %s", e)
        return None


async def _fetch_and_parse_feed(url: str, source: str, timeout: float = 10.0) -> List[Dict[str, Any]]:
    """Fetch one RSS feed and return list of items."""
    items = []
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
    except Exception as e:
        logger.warning("Failed to fetch RSS %s: %s", url, e)
        return items

    # Handle both RSS 2.0 and channel/item structure
    channel = root.find("channel")
    if channel is None:
        channel = root
    for item_el in channel.findall("item"):
        parsed = _parse_rss_item(item_el, source)
        if parsed:
            items.append(parsed)
    return items


async def get_financial_news(limit: int = 25) -> List[Dict[str, Any]]:
    """
    Fetch and aggregate financial/stock market news from configured RSS feeds.
    Returns a single list sorted by published date (newest first), deduplicated by title.
    """
    all_items: List[Dict[str, Any]] = []
    seen_titles: set = set()

    for feed in FINANCIAL_RSS_FEEDS:
        try:
            items = await _fetch_and_parse_feed(feed["url"], feed["source"])
            for it in items:
                key = (it["title"].lower()[:80] if it["title"] else "")
                if key and key not in seen_titles:
                    seen_titles.add(key)
                    all_items.append(it)
        except Exception as e:
            logger.warning("Feed %s failed: %s", feed.get("url"), e)

    # Sort by published date if available (newest first); items without date go last
    def sort_key(x):
        s = (x.get("published") or "")
        if not s:
            return datetime.min
        s = s.strip()[:30]
        for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d %b %Y"):
            try:
                return datetime.strptime(s[:25], fmt)
            except (ValueError, TypeError):
                continue
        return datetime.min

    all_items.sort(key=sort_key, reverse=True)
    return all_items[:limit]
