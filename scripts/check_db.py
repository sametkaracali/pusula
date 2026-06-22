"""Check DB state"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.news_db import get_news_count, get_news

count = get_news_count()
print(f"DB haber sayisi: {count}")
if count > 0:
    first = get_news(limit=1)[0]
    print(f"Ilk haber: {first['id']} - {first['title'][:40]}")
    print(f"Kategori: {first.get('category')}")
else:
    print("DB bos!")
