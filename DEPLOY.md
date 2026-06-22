# Pusula - Ücretsiz Yayınlama Rehberi

## Seçenek 1: PythonAnywhere (Önerilen - SQLite kalıcı, ücretsiz)

1. **GitHub'a yükle:**
```bash
git init
git add .
git commit -m "Pusula news platform"
# GitHub'da repo oluştur, sonra:
git remote add origin https://github.com/KULLANICI_ADIN/pusula.git
git push -u origin master
```

2. **PythonAnywhere** hesap aç: https://www.pythonanywhere.com

3. **Web tab** → "Add a new web app" → Manual configuration → Python 3.12

4. **Code** → "Go to directory" → `git clone https://github.com/KULLANICI_ADIN/pusula.git`

5. **Virtualenv:** `mkvirtualenv --python=python3.12 pusula ; pip install -r requirements.txt`

6. **WSGI configuration file** içine:
```python
import sys
path = '/home/KULLANICI_ADIN/pusula'
if path not in sys.path:
    sys.path.append(path)
from app import app as application
```

7. **.env** dosyasını PythonAnywhere'de oluştur:
```
GROQ_API_KEY=groq_api_keyinizi_yazin
SECRET_KEY=rastgele_bir_string
SITE_URL=https://KULLANICI_ADIN.pythonanywhere.com
SITE_NAME=Pusula
```

8. **Reload** butonuna bas → Site canlı!

9. **Otomatik haber güncelleme:**
   - Tasks tab → "Add scheduled task"
   - `python /home/KULLANICI_ADIN/pusula/scripts/fetch_news.py`
   - Her gün 06:00

## Seçenek 2: Render (Ücretsiz - ephemeral disk)

1. GitHub'a yükle (yukarıdaki gibi)
2. https://render.com → New Web Service
3. GitHub reposunu bağla
4. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Environment variables: Yukarıdaki .env içeriğini ekle
6. **NOT:** Render'da SQLite dosyası her deploy'da sıfırlanır. Veri kalıcılığı için PostgreSQL'e geçilmesi önerilir.

## Seçenek 3: Railway (Ücretsiz kredi - $5, persistent disk)

1. GitHub'a yükle
2. https://railway.app → New Project → Deploy from GitHub
3. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
4. Railway'de disk persistent olduğu için SQLite çalışır.

## Domain Bağlama (Sonra)

1. Bir domain al (isparkle, namecheap, godaddy)
2. DNS ayarları:
   - PythonAnywhere: CNAME → KULLANICI_ADIN.pythonanywhere.com
   - Render: CNAME → your-app.onrender.com
3. SSL otomatik gelir (Let's Encrypt)

## Hızlı Kontrol
```bash
# Lokalde çalıştır
python app.py
# http://localhost:5000
```

## Admin Paneli
URL: https://SITEN.com/admin/giris
Kullanıcı: admin
Şifre: pusula123
