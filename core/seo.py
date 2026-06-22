import json
import re

STOP_WORDS = {"bir", "ve", "ile", "bu", "da", "daha", "en", "çok", "için", "olan", "her",
              "ile", "veya", "ama", "ancak", "gibi", "kadar", "sonra", "önce", "üzere"}

def generate_article_schema(title, description, image, url, date, author="Pusula"):
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": title,
        "description": description[:200],
        "image": image,
        "datePublished": date,
        "author": {"@type": "Person", "name": author},
        "publisher": {"@type": "Organization", "name": "Pusula"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url}
    }, ensure_ascii=False)

def generate_breadcrumb(items):
    elements = []
    for i, item in enumerate(items, 1):
        elements.append({
            "@type": "ListItem",
            "position": i,
            "name": item["name"],
            "item": item["url"]
        })
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": elements
    }, ensure_ascii=False)

def meta_keywords(text):
    words = text.lower().split()
    keywords = []
    for w in words:
        w = w.strip(".,!?\"'()[]{}")
        if len(w) > 2 and w not in STOP_WORDS and not w.isdigit():
            keywords.append(w)
    seen = set()
    result = []
    for k in keywords:
        if k not in seen:
            seen.add(k)
            result.append(k)
    return result[:8]

def seo_fallback(title, summary):
    kw = meta_keywords(title + " " + summary[:200])
    return {
        "meta_title": title[:60],
        "meta_description": summary[:160] if summary else title[:160],
        "keywords": kw,
        "slug": _slugify(title),
        "og_title": title[:60],
        "og_description": summary[:160] if summary else title[:160],
    }

def _slugify(text):
    text = text.lower()
    tr_map = str.maketrans("çğıöşü", "cgiosu")
    text = text.translate(tr_map)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text[:60]
