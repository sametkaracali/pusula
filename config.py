import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32).hex())
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/pusula.db")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY", "")
    MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN", "")
    MAIL_FROM = os.getenv("MAIL_FROM", "Pusula <noreply@pusula.com>")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    SITE_URL = os.getenv("SITE_URL", "http://localhost:5000")
    SITE_NAME = os.getenv("SITE_NAME", "Pusula")

    CATEGORY_INFO = {
        "gundem": {"name": "Gündem", "icon": "bi-newspaper", "desc": "Türkiye ve dünyadan son dakika gündem haberleri"},
        "ekonomi": {"name": "Ekonomi", "icon": "bi-graph-up-arrow", "desc": "Borsa, döviz, enflasyon ve finans haberleri"},
        "teknoloji": {"name": "Teknoloji", "icon": "bi-cpu", "desc": "Yapay zeka, sosyal medya, yazılım ve donanım haberleri"},
        "spor": {"name": "Spor", "icon": "bi-trophy", "desc": "Futbol, basketbol, voleybol ve tüm spor haberleri"},
        "dunya": {"name": "Dünya", "icon": "bi-globe2", "desc": "Dünya gündemi, uluslararası ilişkiler ve küresel haberler"},
        "bilim": {"name": "Bilim", "icon": "bi-rocket-takeoff", "desc": "Uzay, genetik, yapay zeka ve bilim dünyasından haberler"},
        "saglik": {"name": "Sağlık", "icon": "bi-heart-pulse", "desc": "Sağlık, hastalıklar, tedavi yöntemleri ve sağlıklı yaşam haberleri"},
        "sanat": {"name": "Kültür-Sanat", "icon": "bi-palette", "desc": "Sinema, müzik, tiyatro, sergi ve sanat haberleri"},
        "magazin": {"name": "Magazin", "icon": "bi-star", "desc": "Ünlü haberleri, moda, dedikodu ve eğlence dünyasından son dakika magazin haberleri"},
    }

    YOUTUBE_VIDEOS = [
        {"id": 1, "title": "BIST 100'de rekor: Uzmanlar yorumluyor", "youtube": "n9R2rR5Y7Tk", "category": "ekonomi", "views": "45B", "date": "2026-06-21"},
        {"id": 2, "title": "Galatasaray - Fenerbahçe maç özeti", "youtube": "xq9V3LqX3Ys", "category": "spor", "views": "234B", "date": "2026-06-21"},
        {"id": 3, "title": "Yapay zeka günlük hayatımızda neler değiştirecek?", "youtube": "3G5mUEq4o4M", "category": "teknoloji", "views": "78B", "date": "2026-06-20"},
        {"id": 4, "title": "Merkez Bankası faiz kararı ve piyasalara etkisi", "youtube": "n9R2rR5Y7Tk", "category": "ekonomi", "views": "34B", "date": "2026-06-20"},
        {"id": 5, "title": "Milli Takım'ın Avrupa Şampiyonası marşı", "youtube": "xq9V3LqX3Ys", "category": "spor", "views": "567B", "date": "2026-06-19"},
        {"id": 6, "title": "Türkiye'nin yerli elektrikli otomobili ilk test sürüşü", "youtube": "3G5mUEq4o4M", "category": "teknoloji", "views": "156B", "date": "2026-06-19"},
    ]


config = Config()
