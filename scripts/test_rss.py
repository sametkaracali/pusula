"""Test updated RSS feed list"""
import sys, os, requests, feedparser, re, html
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

RSS_FEEDS = {
    "gundem": [
        "https://www.sozcu.com.tr/rss/all.xml",
        "https://www.milliyet.com.tr/rss/rssnew/gundemrss.xml",
        "https://www.hurriyet.com.tr/rss/anasayfa",
        "https://www.sabah.com.tr/rss/anasayfa.xml",
        "https://www.haberturk.com/rss",
    ],
    "ekonomi": [
        "https://www.bloomberght.com/rss",
        "https://www.dunya.com/rss",
        "https://www.hurriyet.com.tr/rss/ekonomi",
    ],
    "teknoloji": [
        "https://www.sozcu.com.tr/feeds-rss-category-bilim-teknoloji",
        "https://www.hurriyet.com.tr/rss/teknoloji",
    ],
    "spor": [
        "https://www.sozcu.com.tr/feeds-rss-category-spor",
        "https://www.hurriyet.com.tr/rss/spor",
    ],
    "dunya": [
        "https://www.sozcu.com.tr/feeds-rss-category-dunya",
        "https://www.hurriyet.com.tr/rss/dunya",
    ],
    "bilim": [
        "https://www.herkesebilimteknoloji.com/rss",
    ],
}

def clean(text):
    if not text: return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()

total_working = 0
total_items = 0
print("RSS Feed Testi\n" + "="*40)
for cat, urls in RSS_FEEDS.items():
    for url in urls:
        name = url.split("//")[1].split("/")[0]
        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            feed = feedparser.parse(resp.content)
            count = len(feed.entries)
            status = "OK" if count > 0 else "HATA"
            if count > 0:
                total_working += 1
                total_items += count
            first = clean(feed.entries[0].get("title", ""))[:50] if feed.entries else ""
            print(f"  [{status}] {cat}: {name} -> {count} item")
            if first:
                print(f"    -> {first}")
        except Exception as e:
            print(f"  [HATA] {cat}: {name} -> {str(e)[:50]}")

print(f"\n{total_working}/{sum(len(v) for v in RSS_FEEDS.values())} feeds calisiyor, toplam {total_items} item")
