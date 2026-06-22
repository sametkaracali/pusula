import json
import re
from datetime import datetime
from .database import get_db


def _row_to_dict(row):
    if row is None:
        return None
    d = dict(row)
    for f in ("keywords", "gallery"):
        if isinstance(d.get(f), str):
            try:
                d[f] = json.loads(d[f])
            except (json.JSONDecodeError, TypeError):
                d[f] = []
    return d


def add_news(item):
    conn = get_db()
    cur = conn.execute("""INSERT INTO news
        (category, title, summary, content, image, gallery, source, source_url, date,
         views, comments, is_breaking, meta_title, meta_description, keywords, reading_time, author)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
        item.get("category"),
        item["title"],
        item.get("summary", ""),
        item.get("content", ""),
        item.get("image", ""),
        json.dumps(item.get("gallery", []), ensure_ascii=False),
        item.get("source", "Pusula"),
        item.get("source_url", ""),
        item.get("date", ""),
        item.get("views", 0),
        item.get("comments", 0),
        item.get("is_breaking", 0),
        item.get("meta_title", item["title"][:60]),
        item.get("meta_description", item.get("summary", "")[:160]),
        json.dumps(item.get("keywords", []), ensure_ascii=False),
        item.get("reading_time", 3),
        item.get("author", "Pusula"),
    ))
    news_id = cur.lastrowid
    conn.commit()
    conn.close()
    _extract_topics(news_id, item["title"], item.get("category", ""))
    return news_id


def update_news(news_id, item):
    conn = get_db()
    fields = ["category", "title", "summary", "content", "image", "gallery", "source",
              "date", "is_breaking", "meta_title", "meta_description", "reading_time", "author"]
    sets = []
    vals = []
    for f in fields:
        if f in item:
            sets.append(f"{f}=?")
            v = item[f]
            if f in ("gallery",) and isinstance(v, (list, tuple)):
                v = json.dumps(v, ensure_ascii=False)
            if f in ("keywords",) and isinstance(v, (list, tuple)):
                v = json.dumps(v, ensure_ascii=False)
            vals.append(v)
    if "keywords" in item and isinstance(item["keywords"], str):
        sets.append("keywords=?")
        vals.append(item["keywords"])
    if sets:
        vals.append(news_id)
        conn.execute(f"UPDATE news SET {', '.join(sets)} WHERE id=?", vals)
        conn.commit()
    conn.close()
    if "title" in item:
        _extract_topics(news_id, item["title"], item.get("category", ""))


def delete_news(news_id):
    conn = get_db()
    conn.execute("DELETE FROM news WHERE id=?", (news_id,))
    conn.execute("DELETE FROM news_topics WHERE news_id=?", (news_id,))
    conn.commit()
    conn.close()


def get_news(category=None, limit=50, offset=0, breaking_only=False):
    conn = get_db()
    if breaking_only:
        rows = conn.execute("SELECT * FROM news WHERE is_breaking=1 ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()
    elif category and category != "tumu":
        rows = conn.execute("SELECT * FROM news WHERE category=? ORDER BY id DESC LIMIT ? OFFSET ?", (category, limit, offset)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM news ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_news_count(category=None):
    conn = get_db()
    if category and category != "tumu":
        row = conn.execute("SELECT COUNT(*) FROM news WHERE category=?", (category,)).fetchone()
    else:
        row = conn.execute("SELECT COUNT(*) FROM news").fetchone()
    conn.close()
    return row[0]


def get_news_by_id(news_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM news WHERE id=?", (news_id,)).fetchone()
    if row:
        conn.execute("UPDATE news SET views=views+1 WHERE id=?", (news_id,))
        conn.commit()
    conn.close()
    return _row_to_dict(row)


def get_trending_news(limit=5):
    conn = get_db()
    rows = conn.execute("SELECT * FROM news ORDER BY views DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_breaking_news(limit=5):
    conn = get_db()
    rows = conn.execute("SELECT * FROM news WHERE is_breaking=1 ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_categories():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT category FROM news WHERE category IS NOT NULL AND category != '' ORDER BY category").fetchall()
    conn.close()
    cats = {r["category"] for r in rows}
    defaults = {"gundem", "ekonomi", "teknoloji", "spor", "dunya", "bilim", "saglik", "sanat", "magazin"}
    return sorted(cats | defaults)


def search_news(query):
    q = f"%{query}%"
    conn = get_db()
    rows = conn.execute("SELECT * FROM news WHERE title LIKE ? OR summary LIKE ? ORDER BY id DESC LIMIT 30", (q, q)).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_videos():
    conn = get_db()
    rows = conn.execute("SELECT * FROM news WHERE video_id != '' AND video_id IS NOT NULL ORDER BY id DESC LIMIT 20").fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_related_news(news_id, category, limit=4):
    conn = get_db()
    rows = conn.execute("SELECT * FROM news WHERE category=? AND id!=? ORDER BY views DESC LIMIT ?", (category, news_id, limit)).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def add_comment(news_id, author, content, parent_id=0):
    conn = get_db()
    conn.execute("INSERT INTO comments (news_id, author, content, parent_id) VALUES (?, ?, ?, ?)", (news_id, author, content, parent_id))
    conn.execute("UPDATE news SET comments=comments+1 WHERE id=?", (news_id,))
    conn.commit()
    conn.close()


def get_comments(news_id):
    conn = get_db()
    rows = conn.execute("SELECT * FROM comments WHERE news_id=? ORDER BY id DESC", (news_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def like_comment(comment_id):
    conn = get_db()
    conn.execute("UPDATE comments SET likes=likes+1 WHERE id=?", (comment_id,))
    conn.commit()
    conn.close()


def add_newsletter(email):
    conn = get_db()
    try:
        conn.execute("INSERT INTO newsletter (email) VALUES (?)", (email,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False


def get_newsletter_subscribers():
    conn = get_db()
    rows = conn.execute("SELECT email, date FROM newsletter WHERE active=1 ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_rss_sources():
    conn = get_db()
    rows = conn.execute("SELECT * FROM rss_sources WHERE active=1 ORDER BY category, id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_rss_sources():
    conn = get_db()
    rows = conn.execute("SELECT * FROM rss_sources ORDER BY category, id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_rss_source(category, url):
    conn = get_db()
    try:
        conn.execute("INSERT INTO rss_sources (category, url) VALUES (?, ?)", (category, url))
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False


def delete_rss_source(source_id):
    conn = get_db()
    conn.execute("DELETE FROM rss_sources WHERE id=?", (source_id,))
    conn.commit()
    conn.close()


def toggle_rss_source(source_id):
    conn = get_db()
    conn.execute("UPDATE rss_sources SET active = CASE WHEN active=1 THEN 0 ELSE 1 END WHERE id=?", (source_id,))
    conn.commit()
    conn.close()


def get_seen_urls():
    conn = get_db()
    rows = conn.execute("SELECT url FROM seen_urls").fetchall()
    conn.close()
    return {r["url"] for r in rows}


def add_seen_url(url):
    conn = get_db()
    conn.execute("INSERT OR IGNORE INTO seen_urls (url) VALUES (?)", (url,))
    conn.commit()
    conn.close()


def add_seen_urls(urls):
    conn = get_db()
    for url in urls:
        conn.execute("INSERT OR IGNORE INTO seen_urls (url) VALUES (?)", (url,))
    conn.commit()
    conn.close()


def get_setting(key, default=None):
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()


def _extract_topics(news_id, title, category):
    conn = get_db()
    words = re.sub(r"[^\w\s]", "", title.lower()).split()
    stop_words = {"bir", "ve", "ile", "bu", "da", "daha", "en", "cok", "icin", "olan", "her", "veya", "ama", "ancak", "gibi", "kadar", "sonra", "once", "uzere", "icin", "daha", "yeni", "oldu", "olacak", "dedi"}
    seen = set()
    for w in words:
        w = w.strip()
        if len(w) > 2 and w not in stop_words and w not in seen:
            seen.add(w)
            conn.execute("INSERT OR IGNORE INTO trending_topics (topic, category) VALUES (?, ?)", (w, category))
            conn.execute("UPDATE trending_topics SET count=count+1, last_seen=date('now') WHERE topic=?", (w,))
            conn.execute("INSERT OR IGNORE INTO news_topics (news_id, topic) VALUES (?, ?)", (news_id, w))
    conn.commit()
    conn.close()


def get_trending_topics(limit=10, category=None):
    conn = get_db()
    if category:
        rows = conn.execute("SELECT topic, count, category FROM trending_topics WHERE category=? ORDER BY count DESC LIMIT ?", (category, limit)).fetchall()
    else:
        rows = conn.execute("SELECT topic, count, category FROM trending_topics ORDER BY count DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_news_by_topic(topic, limit=20):
    conn = get_db()
    rows = conn.execute("""SELECT n.* FROM news n
        JOIN news_topics nt ON n.id=nt.news_id
        WHERE nt.topic=? ORDER BY n.views DESC LIMIT ?""", (topic, limit)).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def log_user_read(session_id, news_id):
    conn = get_db()
    conn.execute("""INSERT INTO user_sessions (session_id, read_news)
        VALUES (?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            read_news = CASE
                WHEN json_valid(read_news) THEN json_insert(read_news, '$[#]', ?)
                ELSE json_array(?)
            END,
            last_seen=datetime('now')""",
        (session_id, json.dumps([news_id], ensure_ascii=False), news_id, news_id))
    conn.commit()
    conn.close()
