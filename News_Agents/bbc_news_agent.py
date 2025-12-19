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
    def parse_bbc(url: str) -> str:
        html = ArticleFetcher.fetch_html(url)
        if not html:
            return ""

        soup = BeautifulSoup(html, "html.parser")
        article = soup.find("article")
        if not article:
            return ""

        paragraphs = article.find_all("p")
        return "\n".join(p.get_text(strip=True) for p in paragraphs)


# =========================
# RSS News Scraper
# =========================
class NewsScraper:
    BBC_RSS = "https://feeds.bbci.co.uk/news/rss.xml"

    def get_bbc_news(self, limit: int = 5):
        feed = feedparser.parse(self.BBC_RSS)
        articles = []

        for entry in feed.entries[:limit]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = entry.get("summary", "").strip()

            articles.append(
                Article(
                    title=title,
                    url=link,
                    source="BBC",
                    content=summary,
                )
            )

        return articles


# =========================
# Output Helper
# =========================
def print_articles(articles: List[Article]) -> None:
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
        description="BBC News Agent"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of articles to fetch",
    )

    args = parser.parse_args()
    scraper = NewsScraper()

    print("\n===== BBC NEWS =====")
    print_articles(scraper.get_bbc_news(args.limit))


# =========================
# Entry Point
# =========================
if __name__ == "__main__":
    cli()
