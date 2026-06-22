import os, json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIClient:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def chat(self, prompt, system=None, model="llama-3.3-70b-versatile", max_tokens=1024):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        try:
            resp = self.client.chat.completions.create(
                model=model, messages=messages, temperature=0.3, max_tokens=max_tokens
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"Hata: {e}"

    def chat_json(self, prompt, system=None, model="llama-3.3-70b-versatile"):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        try:
            resp = self.client.chat.completions.create(
                model=model, messages=messages, temperature=0.2, max_tokens=2000,
                response_format={"type": "json_object"}
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            return {"error": str(e)}

    def analyze_news(self, title, summary):
        prompt = f"""Bu haberi analiz et ve JSON döndür:

BASLIK: {title}
OZET: {summary}

Format:
{{
  "sentiment": "olumlu/olumsuz/nötr",
  "analysis": "kısa analiz (2-3 cümle)",
  "impact": "olası etki",
  "tags": ["etiket1", "etiket2", "etiket3"]
}}"""
        return self.chat_json(prompt)

    def generate_seo_meta(self, title, summary):
        prompt = f"""Bu haber icin SEO meta bilgileri uret:

BASLIK: {title}
OZET: {summary}

JSON formatinda:
{{
  "meta_title": "SEO baslik (maks 60 karakter)",
  "meta_description": "SEO aciklama (maks 160 karakter)",
  "keywords": ["anahtar", "kelime", "listesi"],
  "slug": "url-icin-kisa-ve-aciklayici-baslik",
  "og_title": "sosyal medyada gorunecek baslik",
  "og_description": "sosyal medya aciklamasi"
}}"""
        return self.chat_json(prompt)

    def summarize_news(self, content):
        prompt = f"""Bu haber metnini 2-3 cumleyle ozetle:

{content}"""
        return self.chat(prompt, max_tokens=300)

    def translate_news(self, title, content):
        prompt = f"""Bu Ingilizce haberi Turkce'ye cevir. Sadece ceviriyi ver, aciklama yapma.

BASLIK: {title}
ICERIK: {content}"""
        system = "Sen profesyonel bir cevirmensin. Haber metinlerini Ingilizce'den Turkce'ye ceviriyorsun."
        return self.chat(prompt, system=system, max_tokens=2000)

    def generate_alt_tags(self, title):
        prompt = f"""Bu haber basligi icin bir gorsel alt etiketi (alt text) uret. Sadece 1 cumle:

{title}"""
        return self.chat(prompt, max_tokens=100)
