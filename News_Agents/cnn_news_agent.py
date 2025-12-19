import argparse
from dataclasses import dataclass
from typing import List, Optional

import feedparser
import requests
from bs4 import BeautifulSoup


# =========================
# Data Model
# =========================
@dataclass
class Article:
    title: str
    url: str
    source: str
    content: Optional[str] = None


# =========================
# Article Fetchers
# =========================
class ArticleFetcher:
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    @staticmethod
    def fetch_html(url: str) -> Optional[str]:
        try:
            resp = requests.get(url, headers=ArticleFetcher.HEADERS, timeout=10)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"[ERROR] Failed to fetch article: {e}")
            return None

    @staticmethod
    def parse_cnn(url: str) -> str:
        html = ArticleFetcher.fetch_html(url)
        if not html:
            return ""

        soup = BeautifulSoup(html, "html.parser")

        paragraphs = soup.select("div[data-component-name='paragraph']")
        if not paragraphs:
            paragraphs = soup.find_all("p")

        return "\n".join(p.get_text(strip=True) for p in paragraphs)


# =========================
# RSS News Scraper
# =========================
class NewsScraper:
    CNN_RSS = "http://rss.cnn.com/rss/edition_world.rss"

    def get_cnn_news(self, limit: int = 3) -> List[Article]:
        feed = feedparser.parse(self.CNN_RSS)
        articles: List[Article] = []

        for entry in feed.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()

            # Filter junk
            if not title or not link:
                continue
            if "video" in title.lower():
                continue
            if "/videos" in link:
                continue

            content = ArticleFetcher.parse_cnn(link)

            articles.append(
                Article(
                    title=title,
                    url=link,
                    source="CNN",
                    content=content,
                )
            )

            if len(articles) >= limit:
                break

        return articles


# =========================
# Output Helper
# =========================
def print_articles(articles: List[Article]) -> None:
    if not articles:
        print("No articles found.")
        return

    for idx, art in enumerate(articles, start=1):
        print(f"\n{idx}. [{art.source}] {art.title}")
        print(f"URL: {art.url}")
        print("\n--- NEWS CONTENT ---")
        print(art.content[:2000] if art.content else "No content extracted.")
        print("\n" + "=" * 90)


# =========================
# CLI
# =========================
def cli() -> None:
    parser = argparse.ArgumentParser(
        description="CNN News Agent"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Number of articles to fetch",
    )

    args = parser.parse_args()
    scraper = NewsScraper()

    print("\n===== CNN NEWS =====")
    print_articles(scraper.get_cnn_news(args.limit))


# =========================
# Entry Point
# =========================
if __name__ == "__main__":
    cli()
