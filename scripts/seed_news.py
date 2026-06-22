"""Statik haberleri SQLite veritabanina yukler."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.news_db import add_news, get_news_count
from core import news

def seed():
    existing = get_news_count()
    if existing > 0:
        print(f"DB'de zaten {existing} haber var. Seed atlaniyor.")
        return

    static_news = news.get_news(limit=100)
    for n in static_news:
        item = {
            "category": n["category"],
            "title": n["title"],
            "summary": n["summary"],
            "content": n["content"],
            "image": n["image"],
            "source": n.get("source", "Pusula"),
            "source_url": "",
            "date": n.get("date", "2026-01-01"),
            "views": n.get("views", 0),
            "comments": 0,
            "meta_title": n.get("meta_title", n["title"][:60]),
            "meta_description": n.get("meta_description", n["summary"][:160]),
            "keywords": n.get("keywords", []),
            "reading_time": n.get("reading_time", 3),
            "author": n.get("author", "Pusula"),
        }
        add_news(item)
    print(f"{len(static_news)} statik haber DB'ye yuklendi.")

if __name__ == "__main__":
    seed()
