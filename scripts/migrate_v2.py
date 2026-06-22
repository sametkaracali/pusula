import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.database import get_db

conn = get_db()

# gallery ve is_breaking kolonlarini ekle
for col, typ in [("gallery", "TEXT DEFAULT '[]'"), ("is_breaking", "INTEGER DEFAULT 0")]:
    try:
        conn.execute(f"ALTER TABLE news ADD COLUMN {col} {typ}")
        conn.commit()
        print(f"  + {col} kolonu eklendi")
    except Exception:
        print(f"  ~ {col} zaten var")

# trending_topics tablosu
conn.executescript("""
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
    CREATE TABLE IF NOT EXISTS user_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        read_news TEXT DEFAULT '[]',
        interests TEXT DEFAULT '{}',
        last_seen TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS push_subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        endpoint TEXT UNIQUE NOT NULL,
        p256dh TEXT,
        auth TEXT,
        date TEXT DEFAULT (date('now'))
    );
""")
conn.commit()

# Mevcut haberlerde galeri yoksa, icerikten goruntu cikar
rows = conn.execute("SELECT id, content, image FROM news WHERE gallery IS NULL OR gallery = '[]'").fetchall()
updated = 0
for row in rows:
    images = []
    if row["image"]:
        images.append({"url": row["image"], "caption": ""})
    conn.execute("UPDATE news SET gallery=? WHERE id=?", (json.dumps(images, ensure_ascii=False), row["id"]))
    updated += 1
conn.commit()
print(f"  {updated} habere galeri eklendi")

conn.close()
print("Migration v2 tamamlandi!")
