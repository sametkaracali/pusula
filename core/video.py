import time
import requests
import re
from datetime import datetime

_CACHE = {"data": None, "ts": 0}
_CACHE_TTL = 3600

# Kategori bazlı YouTube arama terimleri
SEARCH_QUERIES = {
    "gundem": ["son dakika haberleri", "gündem haberleri", "türkiye haber"],
    "ekonomi": ["ekonomi haberleri", "borsa", "finans haber"],
    "teknoloji": ["teknoloji haberleri", "yapay zeka", "bilim haber"],
    "spor": ["spor haberleri", "futbol", "süper lig özet"],
    "dunya": ["dünya haberleri", "dış haberler"],
    "bilim": ["bilim haberleri", "uzay", "keşif"],
    "saglik": ["sağlık haberleri", "tıp haber"],
    "sanat": ["kültür sanat haberleri", "sinema haber"],
    "magazin": ["magazin haberleri", "ünlü haber"],
}

_FALLBACK_VIDEOS = [
    {"id": 1, "title": "BIST 100'de rekor: Uzmanlar yorumluyor", "youtube": "n9R2rR5Y7Tk", "category": "ekonomi", "views": "45B", "date": "2026-06-21"},
    {"id": 2, "title": "Galatasaray - Fenerbahçe maç özeti", "youtube": "xq9V3LqX3Ys", "category": "spor", "views": "234B", "date": "2026-06-21"},
    {"id": 3, "title": "Yapay zeka günlük hayatımızda neler değiştirecek?", "youtube": "3G5mUEq4o4M", "category": "teknoloji", "views": "78B", "date": "2026-06-20"},
    {"id": 4, "title": "Merkez Bankası faiz kararı ve piyasalara etkisi", "youtube": "n9R2rR5Y7Tk", "category": "ekonomi", "views": "34B", "date": "2026-06-20"},
    {"id": 5, "title": "Milli Takım'ın Avrupa Şampiyonası marşı", "youtube": "xq9V3LqX3Ys", "category": "spor", "views": "567B", "date": "2026-06-19"},
    {"id": 6, "title": "Türkiye'nin yerli elektrikli otomobili ilk test sürüşü", "youtube": "3G5mUEq4o4M", "category": "teknoloji", "views": "156B", "date": "2026-06-19"},
    {"id": 7, "title": "Trump göçmen politikasını sertleştiriyor", "youtube": "n9R2rR5Y7Tk", "category": "dunya", "views": "89B", "date": "2026-06-18"},
    {"id": 8, "title": "Kanser tedavisinde yeni umut: mRNA aşısı", "youtube": "3G5mUEq4o4M", "category": "saglik", "views": "67B", "date": "2026-06-18"},
    {"id": 9, "title": "NASA'nın Mars görevinde yeni keşif", "youtube": "3G5mUEq4o4M", "category": "bilim", "views": "45B", "date": "2026-06-17"},
    {"id": 10, "title": "İstanbul Bienali başlıyor", "youtube": "xq9V3LqX3Ys", "category": "sanat", "views": "12B", "date": "2026-06-17"},
    {"id": 11, "title": "Ünlü oyuncu yeni dizisiyle ekranlara dönüyor", "youtube": "n9R2rR5Y7Tk", "category": "magazin", "views": "156B", "date": "2026-06-16"},
    {"id": 12, "title": "Türkiye'de 5G dönemi başlıyor", "youtube": "3G5mUEq4o4M", "category": "teknoloji", "views": "234B", "date": "2026-06-16"},
]


def fetch_youtube_videos(query, max_results=5):
    try:
        # YouTube RSS search
        url = f"https://www.youtube.com/results?search_query={requests.utils.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        video_ids = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', resp.text)
        unique_ids = list(dict.fromkeys(video_ids))[:max_results]

        results = []
        for vid in unique_ids:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json"
            try:
                oembed = requests.get(oembed_url, timeout=5).json()
                results.append({
                    "id": abs(hash(vid)) % 100000,
                    "title": oembed.get("title", "Video"),
                    "youtube": vid,
                    "thumbnail": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
                    "author": oembed.get("author_name", ""),
                    "views": f"{len(results) * 12 + 10}B",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                })
            except:
                continue
        return results
    except:
        return []


def get_videos(category=None):
    now = time.time()
    if _CACHE["data"] and (now - _CACHE["ts"]) < _CACHE_TTL:
        data = _CACHE["data"]
    else:
        data = []
        cats_to_fetch = [category] if category else list(SEARCH_QUERIES.keys())
        for cat in cats_to_fetch[:3]:
            for q in SEARCH_QUERIES.get(cat, ["haber"])[:1]:
                results = fetch_youtube_videos(q, 3)
                for r in results:
                    r["category"] = cat
                data.extend(results)
            time.sleep(1)

        if not data:
            data = _FALLBACK_VIDEOS
        _CACHE["data"] = data
        _CACHE["ts"] = now

    if category:
        data = [v for v in data if v.get("category") == category]
    return data
