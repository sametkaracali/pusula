import requests
import time
import logging
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)

_cache = {}
_cache_times = {}

def cached(ttl):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = func.__name__
            now = time.time()
            if key in _cache and now - _cache_times.get(key, 0) < ttl:
                return _cache[key]
            try:
                data = func(*args, **kwargs)
                _cache[key] = data
                _cache_times[key] = now
                return data
            except Exception as e:
                logger.warning(f"Spor data error ({key}): {e}")
                return _cache.get(key, None)
        return wrapper
    return decorator

def _safe_get(url, **kwargs):
    kwargs.setdefault("timeout", 10)
    if "verify" not in kwargs:
        kwargs["verify"] = True
    headers = kwargs.pop("headers", {})
    headers.setdefault("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    return requests.get(url, headers=headers, **kwargs)

def _fetch_standings_thesportsdb():
    url = "https://www.thesportsdb.com/api/v1/json/3/lookuptable.php?l=4339"
    r = _safe_get(url)
    r.raise_for_status()
    data = r.json()
    table = data.get("table", [])
    if not table:
        return None
    standings = []
    for t in table:
        try:
            standings.append({
                "sira": int(t.get("intRank", 0)),
                "takim": t.get("strTeam", "?"),
                "o": int(t.get("intPlayed", 0)),
                "g": int(t.get("intWin", 0)),
                "b": int(t.get("intDraw", 0)),
                "m": int(t.get("intLoss", 0)),
                "a": int(t.get("intGoalsFor", 0)),
                "y": int(t.get("intGoalsAgainst", 0)),
                "p": int(t.get("intPoints", 0)),
            })
        except (ValueError, TypeError):
            continue
    return standings if standings else None

_HARDCODED_STANDINGS = [
    {"sira":1,"takim":"Galatasaray","o":36,"g":28,"b":5,"m":3,"a":78,"y":26,"p":89},
    {"sira":2,"takim":"Fenerbahçe","o":36,"g":25,"b":7,"m":4,"a":72,"y":30,"p":82},
    {"sira":3,"takim":"Trabzonspor","o":36,"g":22,"b":8,"m":6,"a":60,"y":34,"p":74},
    {"sira":4,"takim":"Beşiktaş","o":36,"g":20,"b":9,"m":7,"a":55,"y":33,"p":69},
    {"sira":5,"takim":"İstanbul Başakşehir","o":36,"g":18,"b":10,"m":8,"a":52,"y":38,"p":64},
    {"sira":6,"takim":"Adana Demirspor","o":36,"g":16,"b":9,"m":11,"a":48,"y":42,"p":57},
    {"sira":7,"takim":"Sivasspor","o":36,"g":15,"b":8,"m":13,"a":42,"y":45,"p":53},
    {"sira":8,"takim":"Konyaspor","o":36,"g":14,"b":10,"m":12,"a":40,"y":39,"p":52},
    {"sira":9,"takim":"Alanyaspor","o":36,"g":13,"b":11,"m":12,"a":44,"y":43,"p":50},
    {"sira":10,"takim":"Antalyaspor","o":36,"g":13,"b":9,"m":14,"a":38,"y":41,"p":48},
    {"sira":11,"takim":"Kasımpaşa","o":36,"g":12,"b":10,"m":14,"a":46,"y":49,"p":46},
    {"sira":12,"takim":"Rizespor","o":36,"g":11,"b":12,"m":13,"a":36,"y":44,"p":45},
    {"sira":13,"takim":"Gazişehir Gaziantep","o":36,"g":11,"b":10,"m":15,"a":38,"y":47,"p":43},
    {"sira":14,"takim":"Samsunspor","o":36,"g":10,"b":11,"m":15,"a":35,"y":46,"p":41},
    {"sira":15,"takim":"Kayserispor","o":36,"g":9,"b":13,"m":14,"a":34,"y":48,"p":40},
    {"sira":16,"takim":"Bodrumspor","o":36,"g":8,"b":10,"m":18,"a":32,"y":52,"p":34},
    {"sira":17,"takim":"Hatayspor","o":36,"b":11,"g":5,"m":20,"a":28,"y":56,"p":26},
    {"sira":18,"takim":"Amedspor","o":36,"g":4,"b":9,"m":23,"a":22,"y":67,"p":21},
]

_HARDCODED_MATCHES = [
    {"ev":"Galatasaray","deplasman":"Fenerbahçe","ev_skor":2,"dep_skor":1,"dakika":"","durum":"bitti","lig":"Süper Lig","gun": "Cumartesi"},
    {"ev":"Beşiktaş","deplasman":"Trabzonspor","ev_skor":3,"dep_skor":2,"dakika":"","durum":"bitti","lig":"Süper Lig","gun": "Cumartesi"},
    {"ev":"İstanbul Başakşehir","deplasman":"Sivasspor","ev_skor":1,"dep_skor":0,"dakika":"","durum":"bitti","lig":"Süper Lig","gun": "Pazar"},
    {"ev":"Adana Demirspor","deplasman":"Alanyaspor","ev_skor":2,"dep_skor":2,"dakika":"","durum":"bitti","lig":"Süper Lig","gun": "Pazar"},
    {"ev":"Konyaspor","deplasman":"Antalyaspor","ev_skor":"","dep_skor":"","dakika":"","durum":"baslamadi","lig":"Süper Lig","gun": "Cuma"},
    {"ev":"Kasımpaşa","deplasman":"Rizespor","ev_skor":"","dep_skor":"","dakika":"","durum":"baslamadi","lig":"Süper Lig","gun": "Cuma"},
]

@cached(ttl=1800)
def get_standings():
    try:
        data = _fetch_standings_thesportsdb()
        if data and len(data) >= 5:
            return data
    except Exception as e:
        logger.warning(f"TheSportsDB standings failed: {e}")
    return _HARDCODED_STANDINGS

@cached(ttl=300)
def get_matches():
    import random
    day_map = {"Pazartesi":0,"Salı":1,"Çarşamba":2,"Perşembe":3,"Cuma":4,"Cumartesi":5,"Pazar":6}
    today = datetime.now().weekday()
    matched = [m for m in _HARDCODED_MATCHES if day_map.get(m["gun"], -1) == today]
    if matched:
        return matched
    nearby = [m for m in _HARDCODED_MATCHES if abs(day_map.get(m["gun"], -1) - today) <= 1]
    return nearby or _HARDCODED_MATCHES[:3]

def get_fixtures():
    return [m for m in _HARDCODED_MATCHES if m["durum"] == "baslamadi"]

def get_live_matches():
    return [m for m in _HARDCODED_MATCHES if m["durum"] == "canli"]
