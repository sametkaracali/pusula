import os
import time
import json
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, Response, redirect, flash
from dotenv import load_dotenv
from config import config as app_config

load_dotenv()

from core.news_db import (
    get_news, get_news_by_id, get_trending_news, get_categories,
    search_news, get_videos, get_news_count,
    add_news, update_news, delete_news, add_comment, get_comments, like_comment,
    add_newsletter, get_newsletter_subscribers,
    get_rss_sources, get_all_rss_sources, add_rss_source, delete_rss_source, toggle_rss_source,
    get_setting, set_setting,
    get_breaking_news, get_trending_topics, get_news_by_topic, get_related_news, log_user_read,
)
from core.finans import get_crypto_prices
from core.spor import get_standings, get_matches, get_live_matches
from core.weather import get_weather
from core.mail import send_newsletter
from core.video import get_videos as get_video_list

app = Flask(__name__)
app.secret_key = app_config.SECRET_KEY
app.config["CATEGORY_INFO"] = app_config.CATEGORY_INFO
app.config["YOUTUBE_VIDEOS"] = app_config.YOUTUBE_VIDEOS

_ratelimit = {}

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "pusula123")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect("/admin/giris")
        return f(*args, **kwargs)
    return decorated


def rl(key, max_req=10, window=60):
    now = time.time()
    if key not in _ratelimit:
        _ratelimit[key] = []
    _ratelimit[key] = [t for t in _ratelimit[key] if now - t < window]
    if len(_ratelimit[key]) >= max_req:
        return False
    _ratelimit[key].append(now)
    return True


@app.context_processor
def inject_globals():
    return {
        "now": datetime.now(),
        "categories": get_categories(),
        "cat_info": app_config.CATEGORY_INFO,
        "crypto_prices": get_crypto_prices(),
        "weather": get_weather(),
        "config": app_config,
        "trending_topics": get_trending_topics(8),
        "breaking_news": get_breaking_news(5),
        "site_title": get_setting("site_title", "Pusula - Son Dakika Haberler"),
        "site_description": get_setting("site_description", "Türkiye'nin son dakika haber platformu"),
    }


@app.route("/")
@app.route("/gundem")
def index():
    kategori = request.args.get("kategori", "tumu")
    sayfa = int(request.args.get("sayfa", 1))
    offset = (sayfa - 1) * 20
    news_list = get_news(kategori if kategori != "tumu" else None, limit=20, offset=offset)
    trending = get_trending_news()
    toplam = get_news_count(kategori if kategori != "tumu" else None)
    return render_template(
        "index.html" if kategori == "tumu" else "kategori.html",
        news=news_list, trending=trending, aktif_kategori=kategori, sayfa=sayfa, toplam=toplam
    )


@app.route("/<kategori>")
def kategori_sayfasi(kategori):
    if kategori not in app_config.CATEGORY_INFO:
        return render_template("404.html"), 404
    sayfa = int(request.args.get("sayfa", 1))
    offset = (sayfa - 1) * 20
    news_list = get_news(kategori, limit=20, offset=offset)
    trending = get_trending_news()
    toplam = get_news_count(kategori)
    return render_template("kategori.html", news=news_list, trending=trending, aktif_kategori=kategori, sayfa=sayfa, toplam=toplam)


@app.route("/haber/<int:news_id>")
def haber_detay(news_id):
    haber = get_news_by_id(news_id)
    if not haber:
        return render_template("404.html"), 404
    session_id = session.get("session_id", request.remote_addr or "anon")
    log_user_read(session_id, news_id)
    trending = get_trending_news()
    ilgili = get_related_news(news_id, haber.get("category", ""), 4)
    ilgili = [h for h in ilgili if h["id"] != haber["id"]][:3]
    yorumlar = get_comments(news_id)
    return render_template("haber.html", haber=haber, trending=trending, ilgili=ilgili, yorumlar=yorumlar)


@app.route("/finans")
def finans():
    bist_data = {"xu100": "14.734,5", "xu030": "17.019,86", "xbank": "18.994,46", "xusin": "18.190,19", "xutek": "50.417,30"}
    hisseler = [
        {"sembol": "AKBNK", "ad": "Akbank", "fiyat": "78,50", "degisim": "+1.2"},
        {"sembol": "GARAN", "ad": "Garanti BBVA", "fiyat": "142,30", "degisim": "+0.8"},
        {"sembol": "THYAO", "ad": "Türk Hava Yolları", "fiyat": "312,50", "degisim": "+2.1"},
        {"sembol": "ASELS", "ad": "Aselsan", "fiyat": "89,40", "degisim": "-0.5"},
        {"sembol": "EREGL", "ad": "Ereğli Demir Çelik", "fiyat": "56,20", "degisim": "+0.3"},
        {"sembol": "KCHOL", "ad": "Koç Holding", "fiyat": "245,60", "degisim": "+1.5"},
        {"sembol": "SAHOL", "ad": "Sabancı Holding", "fiyat": "178,90", "degisim": "-0.2"},
        {"sembol": "TUPRS", "ad": "Tüpraş", "fiyat": "167,30", "degisim": "+0.7"},
        {"sembol": "BIMAS", "ad": "BİM Mağazalar", "fiyat": "523,00", "degisim": "+0.4"},
        {"sembol": "SISE", "ad": "Şişe Cam", "fiyat": "45,80", "degisim": "-1.1"},
    ]
    doviz = {"USD": "46,48", "EUR": "53,36", "GBP": "61,59", "CHF": "51,20", "GA": "6.205,50", "ONS": "2.358"}
    return render_template("finans.html", bist=bist_data, hisseler=hisseler, doviz=doviz, kripto=get_crypto_prices())


@app.route("/kaydedilenler")
def kaydedilenler():
    return render_template("kaydedilenler.html")


@app.route("/iletisim")
def iletisim():
    return render_template("iletisim.html")


@app.route("/gizlilik")
def gizlilik():
    return render_template("gizlilik.html")


@app.route("/spor")
def spor():
    return render_template("spor.html", maclar=get_matches(), puan_durumu=get_standings(), canli_mac=get_live_matches())


@app.route("/video")
def video():
    kategori = request.args.get("kategori", "")
    videolar = get_video_list(kategori if kategori else None)
    featured = videolar[0] if videolar else None
    return render_template("video.html", videolar=videolar, featured=featured, aktif_kategori=kategori)


@app.route("/ara")
def ara():
    q = request.args.get("q", "").strip()
    return render_template("ara.html", query=q, sonuclar=search_news(q) if q else [])


@app.route("/trend/<topic>")
def trend_topic(topic):
    news_list = get_news_by_topic(topic)
    trending = get_trending_news()
    return render_template("ara.html", query=f"#{topic}", sonuclar=news_list, trending=trending)


# ----- API -----

@app.route("/api/load-more")
def api_load_more():
    kategori = request.args.get("kategori", "tumu")
    sayfa = int(request.args.get("sayfa", 2))
    offset = (sayfa - 1) * 20
    news_list = get_news(kategori if kategori != "tumu" else None, limit=20, offset=offset)
    toplam = get_news_count(kategori if kategori != "tumu" else None)
    has_more = (offset + 20) < toplam
    html = ""
    for h in news_list:
        html += f"""<div class="col-md-6 news-item">
        <article class="news-card h-100" onclick="window.location='/haber/{h['id']}'" role="link" tabindex="0" onkeydown="if(event.key==='Enter'||event.key===' ')window.location='/haber/{h['id']}'">
            <div class="news-image rounded-0 lazy-bg" data-src="{h['image']}" style="background-color:#e9ecef;">
                <span class="category-badge category-{h['category']}">{h.get('category', '').upper()}</span>
            </div>
            <div class="card-body d-flex flex-column">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <small class="text-muted"><i class="bi bi-calendar3"></i> {h.get('date', '')}</small>
                    <small class="text-muted"><i class="bi bi-eye"></i> {h.get('views', 0)}</small>
                </div>
                <h5 class="fw-bold">{h['title']}</h5>
                <p class="text-muted small flex-grow-1">{h['summary'][:120]}...</p>
                <div class="d-flex justify-content-between align-items-center mt-auto">
                    <small class="text-muted"><i class="bi bi-building"></i> {h.get('source', 'Pusula')}</small>
                </div>
            </div>
        </article></div>"""
    return jsonify({"html": html, "hasMore": has_more})


@app.route("/api/load-saved", methods=["POST"])
def api_load_saved():
    ids = request.json.get("ids", [])
    if not ids:
        return jsonify({"news": []})
    all_news = get_news(limit=5000)
    nmap = {str(n["id"]): n for n in all_news}
    return jsonify({"news": [nmap[i] for i in ids if i in nmap]})


@app.route("/api/refresh-news")
def api_refresh_news():
    ip = request.remote_addr or "unknown"
    if not rl(f"refresh:{ip}", 1, 120):
        return jsonify({"success": False, "error": "2 dakika bekleyin."}), 429
    try:
        from scripts.fetch_news import fetch_all
        return jsonify({"success": True, "output": str(fetch_all())[-500:]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/yorum-ekle/<int:news_id>", methods=["POST"])
def yorum_ekle(news_id):
    ip = request.remote_addr or "unknown"
    if not rl(f"yorum:{ip}", 5, 30):
        return jsonify({"error": "Çok hızlısınız."}), 429
    data = request.json
    content = (data.get("yorum", "") or data.get("content", "")).strip()
    if not content:
        return jsonify({"error": "Boş yorum"}), 400
    if len(content) > 1000:
        return jsonify({"error": "Maks 1000 karakter"}), 400
    parent_id = int(data.get("parent_id", 0))
    add_comment(news_id, data.get("author", "Anonim"), content, parent_id)
    return jsonify({"success": True, "yorumlar": get_comments(news_id)})


@app.route("/api/yorumlar/<int:news_id>")
def yorumlari_getir(news_id):
    return jsonify(get_comments(news_id))


@app.route("/api/yorum-begen/<int:comment_id>", methods=["POST"])
def api_yorum_begen(comment_id):
    like_comment(comment_id)
    return jsonify({"success": True})


@app.route("/api/newsletter", methods=["GET", "POST"])
def api_newsletter():
    if request.method == "GET":
        return render_template("abonelik_iptal.html")
    data = request.json
    email = (data.get("email", "")).strip()
    if not email or "@" not in email:
        return jsonify({"success": False, "error": "Geçerli e-posta girin."})
    if add_newsletter(email):
        return jsonify({"success": True, "message": "Abone oldunuz!"})
    return jsonify({"success": False, "error": "Zaten abonesiniz."})


@app.route("/api/weather")
def api_weather():
    return jsonify(get_weather(request.args.get("city", "Istanbul")))


@app.route("/api/trending-topics")
def api_trending_topics():
    return jsonify(get_trending_topics(15))


@app.route("/api/yapay-zeka-ozet/<int:news_id>")
def api_ai_summary(news_id):
    haber = get_news_by_id(news_id)
    if not haber:
        return jsonify({"error": "Bulunamadı"}), 404
    try:
        from core.ai_client import AIClient
        summary = AIClient().summarize_news(haber.get("content", haber.get("summary", "")))
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/api/push-subscribe", methods=["POST"])
def api_push_subscribe():
    data = request.json
    conn = get_db()
    conn.execute("INSERT OR IGNORE INTO push_subscriptions (endpoint, p256dh, auth) VALUES (?, ?, ?)",
                 (data.get("endpoint"), data.get("p256dh"), data.get("auth")))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ----- SEO -----

@app.route("/sitemap.xml")
def sitemap():
    news_list = get_news(limit=5000)
    today = datetime.now().strftime("%Y-%m-%d")
    pages = [{"loc": f"{app_config.SITE_URL}/", "priority": "1.0", "lastmod": today}]
    for cat in app_config.CATEGORY_INFO:
        pages.append({"loc": f"{app_config.SITE_URL}/{cat}", "priority": "0.8", "lastmod": today})
    for route in ("finans", "spor", "video"):
        pages.append({"loc": f"{app_config.SITE_URL}/{route}", "priority": "0.7", "lastmod": today})
    for h in news_list:
        pages.append({"loc": f"{app_config.SITE_URL}/haber/{h['id']}", "priority": "0.6", "lastmod": h.get("date", today)})
    return Response(render_template("sitemap.xml", pages=pages), mimetype="application/xml")


@app.route("/favicon.ico")
def favicon():
    ico = os.path.join(app.static_folder, "favicon.ico")
    if os.path.exists(ico):
        return Response(open(ico, "rb").read(), mimetype="image/x-icon")
    return "", 204


@app.route("/robots.txt")
def robots():
    return Response(f"User-agent: *\nAllow: /\nSitemap: {app_config.SITE_URL}/sitemap.xml", mimetype="text/plain")


@app.route("/feed.xml")
def rss_feed():
    return Response(render_template("feed.xml", news=get_news(limit=30), now=datetime.now()), mimetype="application/xml")


# ----- Admin Panel -----

@app.route("/admin/giris", methods=["GET", "POST"])
def admin_giris():
    if request.method == "POST":
        if request.form.get("username") == ADMIN_USER and request.form.get("password") == ADMIN_PASS:
            session["admin_logged_in"] = True
            return redirect("/admin")
        flash("Hatalı giriş", "danger")
    return render_template("admin/giris.html")


@app.route("/admin/cikis")
def admin_cikis():
    session.pop("admin_logged_in", None)
    return redirect("/admin/giris")


@app.route("/admin")
@login_required
def admin_index():
    all_news = get_news(limit=5000)
    stats = {
        "total_news": get_news_count(),
        "total_views": sum(n.get("views", 0) for n in all_news),
        "total_comments": sum(n.get("comments", 0) for n in all_news),
        "total_subscribers": len(get_newsletter_subscribers()),
    }
    return render_template("admin/index.html", stats=stats, trending=get_trending_news(10), sources=get_rss_sources())


@app.route("/admin/haberler")
@login_required
def admin_haberler():
    sayfa = int(request.args.get("sayfa", 1))
    return render_template("admin/haberler.html", haberler=get_news(limit=50, offset=(sayfa-1)*50), toplam=get_news_count(), sayfa=sayfa)


@app.route("/admin/haber-ekle", methods=["GET", "POST"])
@login_required
def admin_haber_ekle():
    if request.method == "POST":
        gallery = []
        for i in range(10):
            url = request.form.get(f"gallery_url_{i}", "")
            cap = request.form.get(f"gallery_cap_{i}", "")
            if url:
                gallery.append({"url": url, "caption": cap})
        item = {
            "category": request.form["category"],
            "title": request.form["title"],
            "summary": request.form.get("summary", ""),
            "content": request.form.get("content", ""),
            "image": request.form.get("image", f"https://picsum.photos/seed/{abs(hash(request.form['title']))%10000}/800/400"),
            "gallery": gallery,
            "source": request.form.get("source", "Pusula"),
            "author": request.form.get("author", "Pusula"),
            "is_breaking": int(request.form.get("is_breaking", "0")),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "meta_title": request.form["title"][:60],
            "meta_description": (request.form.get("summary", "") or request.form["title"])[:160],
        }
        add_news(item)
        flash("Haber eklendi!", "success")
        return redirect("/admin/haberler")
    return render_template("admin/haber_ekle.html")


@app.route("/admin/haber-duzenle/<int:news_id>", methods=["GET", "POST"])
@login_required
def admin_haber_duzenle(news_id):
    haber = get_news_by_id(news_id)
    if not haber:
        flash("Haber bulunamadı", "danger")
        return redirect("/admin/haberler")
    if request.method == "POST":
        gallery = []
        for i in range(10):
            url = request.form.get(f"gallery_url_{i}", "")
            cap = request.form.get(f"gallery_cap_{i}", "")
            if url:
                gallery.append({"url": url, "caption": cap})
        update_news(news_id, {
            "category": request.form["category"],
            "title": request.form["title"],
            "summary": request.form.get("summary", ""),
            "content": request.form.get("content", ""),
            "image": request.form.get("image", ""),
            "gallery": gallery,
            "source": request.form.get("source", "Pusula"),
            "author": request.form.get("author", "Pusula"),
            "is_breaking": int(request.form.get("is_breaking", "0")),
            "meta_title": request.form["title"][:60],
            "meta_description": (request.form.get("summary", "") or request.form["title"])[:160],
        })
        flash("Haber güncellendi!", "success")
        return redirect("/admin/haberler")
    return render_template("admin/haber_duzenle.html", haber=haber)


@app.route("/admin/haber-sil/<int:news_id>", methods=["POST"])
@login_required
def admin_haber_sil(news_id):
    delete_news(news_id)
    flash("Haber silindi!", "success")
    return redirect("/admin/haberler")


@app.route("/admin/kaynaklar", methods=["GET", "POST"])
@login_required
def admin_kaynaklar():
    if request.method == "POST":
        add_rss_source(request.form["category"], request.form["url"])
        flash("Kaynak eklendi!", "success")
        return redirect("/admin/kaynaklar")
    return render_template("admin/kaynaklar.html", sources=get_all_rss_sources())


@app.route("/admin/kaynak-toggle/<int:source_id>")
@login_required
def admin_kaynak_toggle(source_id):
    toggle_rss_source(source_id)
    return redirect("/admin/kaynaklar")


@app.route("/admin/kaynak-sil/<int:source_id>", methods=["POST"])
@login_required
def admin_kaynak_sil(source_id):
    delete_rss_source(source_id)
    flash("Kaynak silindi!", "success")
    return redirect("/admin/kaynaklar")


@app.route("/admin/newsletter")
@login_required
def admin_newsletter():
    return render_template("admin/newsletter.html", subscribers=get_newsletter_subscribers())


@app.route("/admin/ayarlar", methods=["GET", "POST"])
@login_required
def admin_ayarlar():
    if request.method == "POST":
        for k in ("site_title", "site_description"):
            if request.form.get(k):
                set_setting(k, request.form[k])
        flash("Ayarlar kaydedildi!", "success")
        return redirect("/admin/ayarlar")
    return render_template("admin/ayarlar.html",
                           site_title=get_setting("site_title", "Pusula"),
                           site_description=get_setting("site_description", ""))


@app.route("/admin/breaking")
@login_required
def admin_breaking():
    return render_template("admin/breaking.html", breaking=get_breaking_news(20), news=get_news(limit=20))


@app.route("/admin/breaking-ekle/<int:news_id>")
@login_required
def admin_breaking_ekle(news_id):
    update_news(news_id, {"is_breaking": 1})
    flash("Breaking habere eklendi!", "success")
    return redirect("/admin/breaking")


@app.route("/admin/breaking-cikar/<int:news_id>")
@login_required
def admin_breaking_cikar(news_id):
    update_news(news_id, {"is_breaking": 0})
    return redirect("/admin/breaking")


@app.route("/abonelik-iptal")
def abonelik_iptal():
    return render_template("abonelik_iptal.html")


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    from core.database import init_db
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app_config.DEBUG)
