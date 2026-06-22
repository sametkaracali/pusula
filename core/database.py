import sqlite3
import os
from config import config

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DB_PATH = os.path.join(DB_DIR, "pusula.db")


def get_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            title TEXT NOT NULL,
            summary TEXT DEFAULT '',
            content TEXT DEFAULT '',
            image TEXT DEFAULT '',
            gallery TEXT DEFAULT '[]',
            source TEXT DEFAULT 'Pusula',
            source_url TEXT DEFAULT '',
            date TEXT DEFAULT (date('now')),
            views INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            is_breaking INTEGER DEFAULT 0,
            meta_title TEXT DEFAULT '',
            meta_description TEXT DEFAULT '',
            keywords TEXT DEFAULT '[]',
            reading_time INTEGER DEFAULT 3,
            author TEXT DEFAULT 'Pusula',
            video_id TEXT DEFAULT '',
            date_created TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_id INTEGER NOT NULL,
            author TEXT DEFAULT 'Anonim',
            content TEXT NOT NULL,
            date TEXT DEFAULT (datetime('now')),
            likes INTEGER DEFAULT 0,
            dislikes INTEGER DEFAULT 0,
            parent_id INTEGER DEFAULT 0,
            FOREIGN KEY (news_id) REFERENCES news(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS newsletter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            date TEXT DEFAULT (date('now')),
            active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS rss_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            active INTEGER DEFAULT 1,
            date_added TEXT DEFAULT (date('now'))
        );

        CREATE TABLE IF NOT EXISTS seen_urls (
            url TEXT PRIMARY KEY
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS trending_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT UNIQUE NOT NULL,
            count INTEGER DEFAULT 1,
            category TEXT DEFAULT '',
            last_seen TEXT DEFAULT (date('now'))
        );

        CREATE TABLE IF NOT EXISTS news_topics (
            news_id INTEGER,
            topic TEXT,
            PRIMARY KEY (news_id, topic)
        );

        CREATE TABLE IF NOT EXISTS push_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT UNIQUE NOT NULL,
            p256dh TEXT,
            auth TEXT,
            date TEXT DEFAULT (date('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_news_category ON news(category);
        CREATE INDEX IF NOT EXISTS idx_news_date ON news(date);
        CREATE INDEX IF NOT EXISTS idx_news_views ON news(views);
        CREATE INDEX IF NOT EXISTS idx_news_breaking ON news(is_breaking);
        CREATE INDEX IF NOT EXISTS idx_comments_news_id ON comments(news_id);
        CREATE INDEX IF NOT EXISTS idx_trending_last_seen ON trending_topics(last_seen);
    """)
    conn.commit()
    conn.close()


def seed_default_sources():
    conn = get_db()
    existing = conn.execute("SELECT COUNT(*) FROM rss_sources").fetchone()[0]
    if existing > 0:
        conn.close()
        return
    default_sources = {
        "gundem": ["https://www.sozcu.com.tr/rss/all.xml", "https://www.milliyet.com.tr/rss/rssnew/gundemrss.xml", "https://www.hurriyet.com.tr/rss/anasayfa", "https://www.sabah.com.tr/rss/anasayfa.xml", "https://www.haberturk.com/rss"],
        "ekonomi": ["https://www.bloomberght.com/rss", "https://www.dunya.com/rss", "https://www.hurriyet.com.tr/rss/ekonomi"],
        "teknoloji": ["https://www.sozcu.com.tr/feeds-rss-category-bilim-teknoloji", "https://www.hurriyet.com.tr/rss/teknoloji"],
        "spor": ["https://www.sozcu.com.tr/feeds-rss-category-spor", "https://www.hurriyet.com.tr/rss/spor"],
        "dunya": ["https://www.sozcu.com.tr/feeds-rss-category-dunya", "https://www.hurriyet.com.tr/rss/dunya"],
        "bilim": ["https://www.herkesebilimteknoloji.com/rss"],
    }
    for cat, urls in default_sources.items():
        for url in urls:
            conn.execute("INSERT OR IGNORE INTO rss_sources (category, url) VALUES (?, ?)", (cat, url))
    conn.commit()
    conn.close()


init_db()
seed_default_sources()
