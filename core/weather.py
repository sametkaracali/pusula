import time
import requests
from config import config

_CACHE = {"data": None, "ts": 0}
_CACHE_TTL = 1800

_FALLBACK = {
    "city": "İstanbul",
    "temp": 28,
    "feels_like": 30,
    "humidity": 55,
    "description": "açık",
    "icon": "01d",
    "wind": 12,
    "country": "TR",
}


def get_weather(city="Istanbul"):
    now = time.time()
    if _CACHE["data"] and (now - _CACHE["ts"]) < _CACHE_TTL:
        return _CACHE["data"]

    api_key = config.WEATHER_API_KEY
    if not api_key:
        _CACHE["data"] = _FALLBACK
        _CACHE["ts"] = now
        return _CACHE["data"]

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=tr"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        result = {
            "city": data.get("name", city),
            "temp": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"].capitalize(),
            "icon": data["weather"][0]["icon"],
            "wind": round(data["wind"]["speed"]),
            "country": data["sys"].get("country", ""),
        }
        _CACHE["data"] = result
        _CACHE["ts"] = now
        return result
    except Exception:
        _CACHE["data"] = _FALLBACK
        _CACHE["ts"] = now
        return _CACHE["data"]
