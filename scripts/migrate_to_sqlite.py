"""JSON dosyalarındaki mevcut verileri SQLite'e taşır."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.database import init_db
from core.news_db import add_news, add_seen_urls

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def migrate():
    init_db()

    # news.json
    news_file = os.path.join(DATA_DIR, "news.json")
    if os.path.exists(news_file):
        with open(news_file, "r", encoding="utf-8") as f:
            items = json.load(f)
        count = 0
        for item in reversed(items):
            try:
                add_news(item)
                count += 1
            except Exception as e:
                print(f"  Hata (id={item.get('id')}): {e}")
        print(f"  {count} haber SQLite'e taşındı.")

    # seen_urls.json
    seen_file = os.path.join(DATA_DIR, "seen_urls.json")
    if os.path.exists(seen_file):
        with open(seen_file, "r", encoding="utf-8") as f:
            urls = json.load(f)
        add_seen_urls(urls)
        print(f"  {len(urls)} URL geçmişi taşındı.")

    # fallback_news.json'u da ekle (eğer hiç haber yoksa)
    from core.news_db import get_news_count
    if get_news_count() == 0:
        fallback_file = os.path.join(DATA_DIR, "fallback_news.json")
        if os.path.exists(fallback_file):
            with open(fallback_file, "r", encoding="utf-8") as f:
                fallback = json.load(f)
            for item in reversed(fallback):
                add_news(item)
            print(f"  {len(fallback)} fallback haber eklendi.")

    print("Migration tamamlandı.")

if __name__ == "__main__":
    migrate()
