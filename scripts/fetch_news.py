import os, sys, json, html, re, time
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.news_db import add_news, get_news, get_seen_urls, add_seen_urls, get_rss_sources
from core.ai_client import AIClient
from core.seo import seo_fallback
import requests
import feedparser

ai = AIClient()
seen_urls = get_seen_urls()


def _clean_text(text):
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_rss(url, category):
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        feed = feedparser.parse(resp.content)
        if feed.bozo and not feed.entries:
            print(f"  RSS bozo: {url.split('//')[1].split('/')[0]}")
        items = []
        for entry in feed.entries[:15]:
            title = _clean_text(entry.get("title", ""))
            link = (entry.get("link", "") or "").strip()
            desc = _clean_text(entry.get("summary", "") or entry.get("description", "") or "")
            img = ""
            if entry.get("media_content"):
                img = entry["media_content"][0].get("url", "")
            if not img and entry.get("links"):
                for link_tag in entry.links:
                    if link_tag.get("type", "").startswith("image"):
                        img = link_tag.get("href", "")
                        break
            if not img and entry.get("media_thumbnail"):
                img = entry["media_thumbnail"][0].get("url", "")
            if not img and entry.get("enclosures"):
                img = entry["enclosures"][0].get("href", "")
            if not title:
                continue
            items.append({"title": title, "link": link, "desc": desc, "date": entry.get("published", "").strip(), "image": img})
        return items
    except Exception as e:
        print(f"  RSS hata: {url.split('//')[1].split('/')[0]} - {e}")
        return []


def fetch_all():
    global seen_urls
    sources = get_rss_sources()
    if not sources:
        print("Aktif RSS kaynagi bulunamadi. Kaynaklari admin panelinden ekleyin.")
        return

    sources_by_cat = {}
    for s in sources:
        sources_by_cat.setdefault(s["category"], []).append(s["url"])

    total = 0
    ai_calls = 0
    start = time.time()
    existing_urls = get_seen_urls()
    seen_urls.update(existing_urls)

    for category, urls in sources_by_cat.items():
        if total >= 100:
            break
        for feed_url in urls:
            if total >= 100:
                break
            print(f"  {category}: {feed_url.split('//')[1].split('/')[0]}")
            items = parse_rss(feed_url, category)
            for item in items:
                if not item["link"] or item["link"] in seen_urls:
                    continue
                seen_urls.add(item["link"])
                title = item["title"]
                summary = item["desc"][:300] if item["desc"] else title
                content = item["desc"]
                image = item["image"] or f"https://picsum.photos/seed/{abs(hash(title))%10000}/800/400"

                if ai_calls < 20:
                    try:
                        seo = ai.generate_seo_meta(title, summary)
                        if "error" in seo:
                            seo = seo_fallback(title, summary)
                        ai_calls += 1
                        time.sleep(2.5)
                    except:
                        seo = seo_fallback(title, summary)
                else:
                    seo = seo_fallback(title, summary)

                news_item = {
                    "category": category,
                    "title": title,
                    "summary": summary,
                    "content": (summary or title)[:300],
                    "image": image,
                    "source": feed_url.split("//")[1].split("/")[0],
                    "source_url": item["link"],
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "views": 0,
                    "comments": 0,
                    "meta_title": seo.get("meta_title", title[:60]),
                    "meta_description": seo.get("meta_description", summary[:160]),
                    "keywords": seo.get("keywords", []),
                    "reading_time": max(1, len(summary or title) // 200) if (summary or title) else 3,
                }
                add_news(news_item)
                total += 1
                print(f"    + {title[:50]}...")

    add_seen_urls(list(seen_urls - existing_urls))
    elapsed = time.time() - start
    print(f"\nToplam {total} yeni haber eklendi. AI: {ai_calls} cagri. Sure: {elapsed:.0f}s")
    return total


if __name__ == "__main__":
    print(f"RSS taramasi basliyor... {datetime.now().isoformat()}")
    fetch_all()
    print("Tamamlandi.")
