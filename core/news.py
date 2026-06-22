import json, os, random
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FALLBACK_FILE = os.path.join(DATA_DIR, "fallback_news.json")

FALLBACK_NEWS = []

# 60 statik haber - 8 kategoride
_cats = ["gundem", "ekonomi", "teknoloji", "spor", "dunya", "bilim", "saglik", "sanat", "magazin"]
_sources = ["TRT Haber", "NTV", "Bloomberg HT", "CNN Türk", "Webtekno", "Sporx", "Fanatik", "Dünya Gazetesi", "BBC Türkçe", "DonanımHaber", "Ekonomim", "NTV Spor", "TRT Spor", "Bilim.org", "Sağlık Haber"]

_news_templates = [
    # GUNDEM
    {"cat": "gundem", "title": "Cumhurbaşkanı yeni ekonomik reform paketini açıkladı", "summary": "Cumhurbaşkanı, enflasyonla mücadele ve büyüme hedefleri doğrultusunda kapsamlı bir ekonomik reform paketini kamuoyuna duyurdu. Pakette vergi indirimleri ve teşvikler yer alıyor."},
    {"cat": "gundem", "title": "TBMM'de yeni yasa teklifi görüşülmeye başlandı", "summary": "Türkiye Büyük Millet Meclisi'nde dijital dönüşümü hızlandıracak yeni bir yasa teklifi üzerinde görüşmeler başladı. Teklif, e-devlet hizmetlerini kapsamlı şekilde düzenliyor."},
    {"cat": "gundem", "title": "İstanbul'da toplu taşımaya yeni zam", "summary": "İstanbul Büyükşehir Belediyesi, toplu taşıma ücretlerine yüzde 15 oranında zam yapıldığını duyurdu. Yeni tarife önümüzdeki haftadan itibaren geçerli olacak."},
    {"cat": "gundem", "title": "Türkiye'de işsizlik oranı düştü", "summary": "TÜİK verilerine göre Türkiye'de işsizlik oranı son 4 yılın en düşük seviyesine gerileyerek yüzde 8,2 oldu. İstihdam artışı hizmet sektöründe yoğunlaştı."},
    {"cat": "gundem", "title": "Yaz tatili için geri sayım başladı: Milyonlar yola çıkıyor", "summary": "Okulların kapanmasına sayılı günler kala milyonlarca vatandaş yaz tatili planları yapmaya başladı. Turizm bölgelerinde rezervasyonlar yüzde 90'a ulaştı."},
    {"cat": "gundem", "title": "Antalya'da turist sayısı rekor kırdı", "summary": "Antalya'ya gelen turist sayısı geçen yıla göre yüzde 25 artışla 6 milyonu aştı. Rus ve Alman turistler ilk sırada yer alıyor."},
    {"cat": "gundem", "title": "Enerji Bakanı'ndan doğalgaz müjdesi", "summary": "Enerji ve Tabii Kaynaklar Bakanı, Karadeniz'de bulunan doğalgaz rezervinin günlük üretiminin 10 milyon metreküpe ulaştığını açıkladı."},
    {"cat": "gundem", "title": "Deprem bölgesinde konut teslimleri sürüyor", "summary": "Çevre ve Şehircilik Bakanlığı, deprem bölgesinde 200 bin konutun teslim edildiğini, yıl sonuna kadar 300 bin konutun daha tamamlanacağını duyurdu."},

    # EKONOMI
    {"cat": "ekonomi", "title": "BIST 100'de tarihi rekor: Endeks 15000 puanı aştı", "summary": "Borsa İstanbul'da BIST 100 endeksi, küresel piyasalardaki olumlu havayla birlikte tarihi bir rekor kırarak 15000 puan seviyesini aştı."},
    {"cat": "ekonomi", "title": "Dolar/TL 46 seviyesinde dengeleniyor", "summary": "Türk Lirası son haftalarda değer kazanırken dolar/TL kuru 46 seviyesinde dengelenme işaretleri gösteriyor."},
    {"cat": "ekonomi", "title": "Merkez Bankası faiz kararını açıkladı", "summary": "TCMB haziran ayı faiz kararını açıkladı. Politika faizi beklentiler dahilinde yüzde 42,5'te sabit tutuldu."},
    {"cat": "ekonomi", "title": "Kripto para piyasasında yükseliş: Bitcoin 85 bin doları gördü", "summary": "Bitcoin ABD'deki olumlu düzenleme haberleriyle birlikte 85 bin dolar seviyesini test etti. Piyasa değeri 3 trilyon dolara yaklaştı."},
    {"cat": "ekonomi", "title": "Enflasyon verileri açıklandı: TÜFE mayısta aylık bazda geriledi", "summary": "TÜİK mayıs ayı enflasyon verilerini açıkladı. Tüketici fiyatları aylık bazda yüzde 2,1 artarken yıllık enflasyon yüzde 35,4 oldu."},
    {"cat": "ekonomi", "title": "Altın fiyatlarında yükseliş: Gram altın 6.200 TL'yi aştı", "summary": "Küresel piyasalardaki belirsizlikler ve jeopolitik riskler altının ons fiyatını yukarı çekerken gram altın 6.200 TL seviyesinin üzerine çıktı."},
    {"cat": "ekonomi", "title": "Türkiye'nin ihracatı mayısta arttı", "summary": "Türkiye İhracatçılar Meclisi verilerine göre mayıs ayı ihracatı geçen yılın aynı dönemine göre yüzde 8 artışla 22,4 milyar dolar oldu."},

    # TEKNOLOJI
    {"cat": "teknoloji", "title": "Apple yapay zeka asistanını Türkiye'de kullanıma açtı", "summary": "Apple'ın yeni yapay zeka asistanı Türkiye'de kullanıma sunuldu. Yerelleştirilmiş Türkçe dil desteğiyle dikkat çekiyor."},
    {"cat": "teknoloji", "title": "Türk girişimcilerden yapay zeka destekli eğitim platformu", "summary": "İki Türk girişimci tarafından geliştirilen yapay zeka destekli eğitim platformu 5 milyon dolar yatırım aldı."},
    {"cat": "teknoloji", "title": "Türkiye'nin ilk yerli elektrikli otomobili haziranda satışta", "summary": "Türkiye'nin yerli elektrikli otomobili haziran ayı itibarıyla satışa sunuluyor. 500 km menzil ve rekabetçi fiyat."},
    {"cat": "teknoloji", "title": "5G ihalesi için tarih belirlendi", "summary": "Bilgi Teknolojileri ve İletişim Kurumu 5G ihalesinin eylül ayında yapılacağını duyurdu. 2027'de ticari kullanıma geçilmesi planlanıyor."},
    {"cat": "teknoloji", "title": "Instagram'dan yeni özellik: Yapay zeka ile görsel düzenleme", "summary": "Instagram kullanıcıların fotoğraflarını yapay zeka yardımıyla düzenlemesine olanak tanıyan yeni bir özellik sunmaya başladı."},
    {"cat": "teknoloji", "title": "Sosyal medya düzenlemesi yasalaştı", "summary": "Sosyal medya platformlarına yönelik yeni düzenleme TBMM'den geçerek yasalaştı. 16 yaş altı kullanıcılar için ebeveyn izni zorunluluğu getirildi."},
    {"cat": "teknoloji", "title": "Google Türkiye'ye yatırım yapacak", "summary": "Google Türkiye'de yapacak. Şirket İstanbul'da kuracağı yapay zeka laboratuvarı için 100 milyon dolar yatırım yapacağını açıkladı."},

    # SPOR
    {"cat": "spor", "title": "Galatasaray'dan şampiyonluk yolunda kritik galibiyet", "summary": "Galatasaray deplasmanda rakibini 3-1 mağlup ederek liderliğini sürdürdü. Şampiyonluk yolunda kritik bir viraj dönüldü."},
    {"cat": "spor", "title": "Fenerbahçe'den transfer bombası: Yıldız oyuncu İstanbul'a geliyor", "summary": "Fenerbahçe Premier Lig'de forma giyen yıldız orta saha oyuncusunu transfer etmek için görüşmelere başladı."},
    {"cat": "spor", "title": "Milli Takım'dan Avrupa Şampiyonası'nda tarihi başarı", "summary": "A Milli Futbol Takımı Avrupa Şampiyonası'nda çeyrek finale yükselerek tarihi bir başarıya imza attı."},
    {"cat": "spor", "title": "Beşiktaş'ta teknik direktör değişikliği", "summary": "Beşiktaş yönetimi teknik direktörle yollarını ayırdı. Yeni teknik direktörle 2 yıllık sözleşme imzalanacağı belirtildi."},
    {"cat": "spor", "title": "Trabzonspor'da flaş gelişme: Yıldız futbolcu takımdan ayrılıyor", "summary": "Trabzonspor'da sezon sonunda sözleşmesi bitecek yıldız futbolcuyla yeni sözleşme imzalanamayacağı açıklandı."},
    {"cat": "spor", "title": "Süper Lig'de şampiyonluk yarışı nefes kesiyor", "summary": "Süper Lig'de bitime 4 hafta kala şampiyonluk yarışı nefes kesiyor. İlk 3 sıradaki takım arasında sadece 4 puan fark var."},
    {"cat": "spor", "title": "Voleybol Milli Takımı'ndan olimpiyat kotası", "summary": "A Milli Voleybol Takımı olimpiyat elemelerini geçerek Paris 2028 olimpiyatlarına katılmaya hak kazandı."},

    # DUNYA
    {"cat": "dunya", "title": "ABD'de faiz kararı merakla bekleniyor", "summary": "ABD Merkez Bankası'nın faiz kararı öncesinde piyasalar temkinli seyrediyor. Analistler faizin sabit kalmasını bekliyor."},
    {"cat": "dunya", "title": "Rusya-Ukrayna savaşında yeni gelişmeler", "summary": "Rusya ve Ukrayna arasındaki savaşta son durum: Taraflar arasında olası bir ateşkes için diplomatik görüşmeler hız kazandı."},
    {"cat": "dunya", "title": "Çin ekonomisinde yavaşlama sinyalleri", "summary": "Çin ekonomisi ikinci çeyrekte beklenenden daha yavaş büyüdü. Emlak sektöründeki sorunlar büyümeyi olumsuz etkiliyor."},
    {"cat": "dunya", "title": "AB'den yapay zeka düzenlemesi: Tarihi yasa yürürlükte", "summary": "Avrupa Birliği'nin yapay zeka düzenlemesi yürürlüğe girdi. Yasa risk bazlı bir sınıflandırma sistemi getiriyor."},
    {"cat": "dunya", "title": "Kuzey Kore'den füze denemesi", "summary": "Kuzey Kore bir kez daha balistik füze denemesi yaptı. Japonya ve Güney Kore açıklamayı kınadı."},
    {"cat": "dunya", "title": "Hindistan nüfusta zirvede: 1.5 milyarı aştı", "summary": "Hindistan resmi verilere göre ülke nüfusu 1.5 milyarı aşarak dünyanın en kalabalık ülkesi olmayı sürdürüyor."},

    # BILIM
    {"cat": "bilim", "title": "NASA Mars'ta su buldu: Yaşamın izleri aranıyor", "summary": "NASA'nın Perseverance aracı Mars'ta antik bir göl yatağında suya dair yeni kanıtlar buldu. Bilim insanları yaşam izlerini araştırıyor."},
    {"cat": "bilim", "title": "Yapay zeka kanser teşhisinde doktorları geçti", "summary": "Yeni bir araştırmaya göre yapay zeka destekli görüntüleme sistemi kanser teşhisinde uzman doktorlardan daha başarılı sonuçlar veriyor."},
    {"cat": "bilim", "title": "Türk bilim insanından çığır açan keşif", "summary": "Türk bilim insanı Prof. Dr. Ayşe Yılmaz ve ekibi, kanser hücrelerini yok eden yeni bir molekül keşfetti."},
    {"cat": "bilim", "title": "Uzay turizmi yeni rekor: 2026'da 500 kişi uzaya gitti", "summary": "Uzay turizmi sektörü 2026'da büyük bir sıçrama yaptı. Yılın ilk yarısında 500'den fazla kişi uzay yolculuğu yaptı."},
    {"cat": "bilim", "title": "Dünyanın en hızlı bilgisayarı Türkiye'ye kuruluyor", "summary": "Türkiye dünyanın en hızlı süper bilgisayarlarından birini kurmak için çalışmalara başladığını duyurdu. Bilgisayar yapay zeka araştırmalarında kullanılacak."},
    {"cat": "bilim", "title": "Klonlama teknolojisinde yeni dönem: İlk primat klonlandı", "summary": "Çinli bilim insanları geliştirdikleri yeni bir teknikle ilk sağlıklı primatı klonlamayı başardı. Etik tartışmalar sürüyor."},
    {"cat": "bilim", "title": "Okyanusların derinliklerinde yeni türler keşfedildi", "summary": "Pasifik Okyanusu'nun 7 bin metre derinliğinde daha önce bilinmeyen 30 yeni canlı türü keşfedildi."},

    # SAGLIK
    {"cat": "saglik", "title": "Kanser tedavisinde devrim: Kişiselleştirilmiş aşı dönemi", "summary": "Bilim insanları kişiselleştirilmiş mRNA kanser aşılarının faz 3 denemelerinde başarılı sonuçlar aldığını duyurdu."},
    {"cat": "saglik", "title": "Sağlık Bakanlığı'ndan yaz uyarısı: Güneş çarpmasına dikkat", "summary": "Sağlık Bakanlığı hava sıcaklıklarının mevsim normallerinin üzerinde seyretmesi nedeniyle vatandaşları güneş çarpmasına karşı uyardı."},
    {"cat": "saglik", "title": "Türkiye'de obezite oranı artıyor: Her 3 kişiden 1'i kilolu", "summary": "Türkiye'de obezite oranı son 10 yılda yüzde 30 arttı. Uzmanlar hareketsiz yaşam ve sağlıksız beslenmeyi neden olarak gösteriyor."},
    {"cat": "saglik", "title": "Sigara bırakma polikliniklerine başvuru sayısı arttı", "summary": "Sağlık Bakanlığı sigara bırakma polikliniklerine başvuru sayısının geçen yıla göre yüzde 40 arttığını açıkladı."},
    {"cat": "saglik", "title": "Yaşlanmayı geciktiren ilaçta çığır açan gelişme", "summary": "ABD'li bilim insanları yaşlanma sürecini yavaşlatan bir ilacın insan deneylerinde başarılı sonuçlar verdiğini duyurdu."},
    {"cat": "saglik", "title": "Akıllı saatler kalp krizini önceden tahmin edebilecek", "summary": "Yeni bir yapay zeka algoritması akıllı saatlerden alınan verilerle kalp krizi riskini 24 saat önceden yüzde 90 doğrulukla tahmin edebiliyor."},

    # SANAT
    {"cat": "sanat", "title": "İstanbul Bienali bu yıl 'Dönüşüm' temasıyla düzenlenecek", "summary": "İstanbul Bienali'nin bu yılki teması 'Dönüşüm' olarak belirlendi. Bienalde 50 ülkeden 100'ün üzerinde sanatçı eserlerini sergileyecek."},
    {"cat": "sanat", "title": "Türk dizi sektörü ihracatta rekor kırdı", "summary": "Türk dizileri 2026'da 180 ülkeye ihraç edilerek 1 milyar dolar gelir elde etti. Güney Amerika ve Orta Doğu en büyük pazarlar."},
    {"cat": "sanat", "title": "Yerli film 'Sonsuzluk' Cannes'da büyük ödül kazandı", "summary": "Yönetmen Mehmet Can'ın filmi 'Sonsuzluk' Cannes Film Festivali'nde Altın Palmiye ödülünü kazandı."},
    {"cat": "sanat", "title": "Zeytinliklerde festival zamanı: Urla Zeytin Festivali başlıyor", "summary": "Urla'da düzenlenecek Zeytin Festivali bu yıl 10. kez kapılarını açıyor. Festivalde konserler söyleşiler ve atölyeler yer alacak."},
    {"cat": "sanat", "title": "Türk ressamın tablosu müzayedede 5 milyon dolara satıldı", "summary": "Ünlü Türk ressamın tablosu Londra'da düzenlenen bir müzayedede 5 milyon dolara alıcı buldu."},
    {"cat": "sanat", "title": "İstanbul Kültür Sanat Vakfı'ndan yeni projeler", "summary": "İKSV 2026 yılı programında 12 yeni projeyi hayata geçireceğini duyurdu. Projeler arasında dijital sanat sergileri de bulunuyor."},

    # MAGAZIN
    {"cat": "magazin", "title": "Ünlü oyuncu çiftten sürpriz boşanma kararı", "summary": "Ünlü oyuncu çift 5 yıllık evliliklerini sürpriz bir şekilde sonlandırma kararı aldı. Çiftten yapılan açıklamada 'anlaşmalı olarak yollarımızı ayırdık' denildi."},
    {"cat": "magazin", "title": "Yerli dizi yıldızı Hollywood yolcusu: Dev yapımla anlaştı", "summary": "Türk dizi ve sinema oyuncusu, büyük bir Hollywood yapımında rol almak için anlaşmaya vardı. Oyuncu önümüzdeki ay Los Angeles'a gidecek."},
    {"cat": "magazin", "title": "Ünlü şarkıcı yıllar sonra sahnede: Dev konser biletleri tükendi", "summary": "Uzun süredir sahnelerden uzak kalan ünlü şarkıcı muhteşem bir dönüş yaptı. Konser biletleri saatler içinde tükendi."},
    {"cat": "magazin", "title": "Met Gala 2026'da Türk tasarımcı rüzgarı", "summary": "Met Gala 2026'da Türk tasarımcıların kreasyonları büyük beğeni topladı. Ünlü oyuncu ve modeller kırmızı halıda Türk tasarımcıların elbiselerini tercih etti."},
    {"cat": "magazin", "title": "Yılın en çok kazanan fenomenleri açıklandı", "summary": "Sosyal medya fenomenlerinin yıllık kazançları açıklandı. İlk 10'da 4 Türk fenomen yer alırken liste başı 50 milyon dolar kazandı."},
    {"cat": "magazin", "title": "Moda haftasında Türk model damgası", "summary": "Paris Moda Haftası'nda podyuma çıkan Türk modeller büyük ilgi gördü. Ünlü modaevleri Türk modellere yoğun ilgi gösteriyor."},
    {"cat": "magazin", "title": "Ünlü sanatçıdan yeni albüm müjdesi", "summary": "Uzun süredir sessizliğini koruyan ünlü sanatçı yeni albümünün haziran sonunda çıkacağını duyurdu. Albümde 12 parça yer alıyor."},
]

def _init_fallback():
    if os.path.exists(FALLBACK_FILE):
        return
    os.makedirs(DATA_DIR, exist_ok=True)
    news_list = []
    for i, t in enumerate(_news_templates):
        cat = t["cat"]
        idx = (i % 100) + 1
        news_list.append({
            "id": i + 1,
            "category": cat,
            "title": t["title"],
            "summary": t["summary"],
            "content": t["summary"][:300],
            "image": f"https://picsum.photos/seed/static{idx}/800/400",
            "source": random.choice(_sources),
            "date": "2026-06-" + f"{min(i % 28 + 1, 28):02d}",
            "views": random.randint(1000, 90000),
            "comments": random.randint(0, 1000),
            "meta_title": t["title"][:60],
            "meta_description": t["summary"][:160],
            "keywords": [cat.capitalize(), "Türkiye", "Gündem", "Haber"],
            "slug": t["title"].lower().replace(" ", "-")[:50],
            "reading_time": random.randint(2, 6),
            "author": random.choice(["Ali Demir", "Ayşe Yılmaz", "Mehmet Can", "Zeynep Kaya", "Can Özmen"]),
        })
    with open(FALLBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)

def get_news(category=None, limit=50, offset=0):
    _init_fallback()
    with open(FALLBACK_FILE, "r", encoding="utf-8") as f:
        news = json.load(f)
    if category and category != "tumu":
        news = [n for n in news if n.get("category") == category]
    news.sort(key=lambda x: x.get("id", 0), reverse=True)
    return news[offset:offset+limit]

def get_news_count(category=None):
    _init_fallback()
    with open(FALLBACK_FILE, "r", encoding="utf-8") as f:
        news = json.load(f)
    if category and category != "tumu":
        news = [n for n in news if n.get("category") == category]
    return len(news)

def get_news_by_id(news_id):
    _init_fallback()
    with open(FALLBACK_FILE, "r", encoding="utf-8") as f:
        news = json.load(f)
    for n in news:
        if n["id"] == news_id:
            return n
    return None

def get_trending_news(limit=5):
    _init_fallback()
    with open(FALLBACK_FILE, "r", encoding="utf-8") as f:
        news = json.load(f)
    return sorted(news, key=lambda x: x.get("views", 0), reverse=True)[:limit]

def get_categories():
    return ["gundem", "ekonomi", "teknoloji", "spor", "dunya", "bilim", "saglik", "sanat", "magazin"]

def search_news(query):
    _init_fallback()
    query = query.lower()
    with open(FALLBACK_FILE, "r", encoding="utf-8") as f:
        news = json.load(f)
    return [n for n in news if query in n.get("title","").lower() or query in n.get("summary","").lower()][:30]

def get_videos():
    return []
