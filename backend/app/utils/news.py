"""Public Google News RSS feed fetcher for debate grounding."""

import xml.etree.ElementTree as ET
import urllib.parse
import httpx
from app.utils.logger import get_logger

logger = get_logger(__name__)

async def fetch_latest_news(query: str, max_results: int = 5) -> list[dict[str, str]]:
    """Fetch top articles from Google News RSS feed matching the query."""
    if not query.strip():
        return []
    
    encoded_query = urllib.parse.quote(query.strip())
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                logger.warning("Google News feed returned status %d", response.status_code)
                return []
            
            root = ET.fromstring(response.text)
            items = root.findall(".//item")
            
            results = []
            for item in items[:max_results]:
                title_elem = item.find("title")
                link_elem = item.find("link")
                pub_elem = item.find("pubDate")
                source_elem = item.find("source")
                
                raw_title = title_elem.text if title_elem is not None else ""
                source_name = source_elem.text if source_elem is not None else "News"
                
                title = raw_title
                if raw_title and source_name and raw_title.endswith(f" - {source_name}"):
                    title = raw_title[:-len(f" - {source_name}")].strip()
                elif raw_title and " - " in raw_title:
                    parts = raw_title.rsplit(" - ", 1)
                    title = parts[0].strip()
                    
                results.append({
                    "title": title or raw_title,
                    "link": link_elem.text if link_elem is not None else "",
                    "pub_date": pub_elem.text if pub_elem is not None else "",
                    "source": source_name,
                })
            
            logger.info("Successfully fetched %d news items for query %r", len(results), query)
            return results
            
    except Exception as exc:
        logger.exception("Failed to fetch Google News for query %r: %s", query, exc)
        return []
