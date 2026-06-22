import time
import requests

_COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"

_COIN_MAP = {
    "BTC": {"id": "bitcoin", "name": "Bitcoin"},
    "ETH": {"id": "ethereum", "name": "Ethereum"},
    "SOL": {"id": "solana", "name": "Solana"},
    "XRP": {"id": "ripple", "name": "XRP"},
    "DOGE": {"id": "dogecoin", "name": "Dogecoin"},
    "BNB": {"id": "binancecoin", "name": "BNB"},
}

_FALLBACK_KRIPTO = [
    {"symbol": "BTC", "name": "Bitcoin", "price": 65420, "change_24h": 2.15, "volume_24h": 42_500_000_000},
    {"symbol": "ETH", "name": "Ethereum", "price": 3520, "change_24h": 1.80, "volume_24h": 18_200_000_000},
    {"symbol": "SOL", "name": "Solana", "price": 142, "change_24h": -0.65, "volume_24h": 3_800_000_000},
    {"symbol": "XRP", "name": "XRP", "price": 0.52, "change_24h": 3.42, "volume_24h": 1_200_000_000},
    {"symbol": "DOGE", "name": "Dogecoin", "price": 0.12, "change_24h": -1.25, "volume_24h": 650_000_000},
    {"symbol": "BNB", "name": "BNB", "price": 590, "change_24h": 0.95, "volume_24h": 2_100_000_000},
]

_CACHE = {"data": None, "ts": 0}
_CACHE_TTL = 300


def _format_price(price):
    if price >= 1000:
        return f"{price:,.0f}".replace(",", ".")
    if price >= 1:
        return f"{price:,.2f}".replace(",", ".")
    return f"{price:,.4f}".replace(",", ".")


def _format_change(val):
    return f"{val:+.2f}"


def _format_volume(val):
    if val >= 1_000_000_000:
        return f"{val / 1_000_000_000:.2f}B"
    if val >= 1_000_000:
        return f"{val / 1_000_000:.2f}M"
    if val >= 1_000:
        return f"{val / 1_000:.2f}K"
    return str(val)


def get_crypto_prices():
    now = time.time()
    if _CACHE["data"] and (now - _CACHE["ts"]) < _CACHE_TTL:
        return _CACHE["data"]

    coin_ids = ",".join(v["id"] for v in _COIN_MAP.values())
    params = {
        "ids": coin_ids,
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_24hr_vol": "true",
    }

    try:
        resp = requests.get(_COINGECKO_URL, params=params, timeout=10)
        resp.raise_for_status()
        raw = resp.json()
    except Exception:
        _CACHE["data"] = _FALLBACK_KRIPTO
        _CACHE["ts"] = now
        return _CACHE["data"]

    result = []
    for symbol, info in _COIN_MAP.items():
        coin_id = info["id"]
        entry = raw.get(coin_id, {})
        price = entry.get("usd", 0)
        change = entry.get("usd_24h_change", 0)
        volume = entry.get("usd_24h_vol", 0)

        if not price:
            fb = next((c for c in _FALLBACK_KRIPTO if c["symbol"] == symbol), None)
            if fb:
                price = fb["price"]
                change = fb["change_24h"]
                volume = fb["volume_24h"]

        result.append({
            "symbol": symbol,
            "name": info["name"],
            "price": _format_price(price),
            "change_24h": _format_change(change),
            "volume_24h": _format_volume(volume),
            "is_up": change >= 0,
        })

    _CACHE["data"] = result
    _CACHE["ts"] = now
    return result
