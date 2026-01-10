import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set

import app.config as config


def crawl_site(
    start_url: str,
    max_pages: int | None = None,
) -> List[Dict[str, str]]:
    """
    Crawl a website starting from start_url and extract readable text.

    Args:
        start_url (str): Entry URL
        max_pages (int | None): Override max pages limit

    Returns:
        List[Dict[str, str]]: [{ "url": str, "text": str }]
    """

    if not start_url:
        return []

    visited: Set[str] = set()
    queue: List[str] = [start_url]
    pages: List[Dict[str, str]] = []

    parsed_start = urlparse(start_url)
    domain = parsed_start.netloc

    page_limit = max_pages or config.CRAWL_MAX_PAGES

    headers = {
        "User-Agent": config.CRAWL_USER_AGENT
    }

    while queue and len(visited) < page_limit:
        url = queue.pop(0)
        url = url.split("#")[0].rstrip("/")

        if url in visited:
            continue

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=config.CRAWL_TIMEOUT,
            )

            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                continue

        except requests.RequestException:
            continue

        visited.add(url)

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract readable paragraph text
        text = " ".join(
            p.get_text(strip=True)
            for p in soup.find_all("p")
        )
        if len(text) > 200_000:
            text = text[:200_000]

        if text:
            pages.append({
                "url": url,
                "text": text,
            })

        # Discover internal links
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a["href"])
            parsed_link = urlparse(link)

            if (
                parsed_link.scheme in ("http", "https")
                and parsed_link.netloc == domain
                and link not in visited
            ):
                queue.append(link)

    return pages
