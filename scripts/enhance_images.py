"""Tüm haberlere kategorilerine uygun, kaliteli görseller ekler."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.database import get_db
from core.news_db import update_news

# Kategori bazlı gorsel temalari - her kategori icin 20+ farkli seed
CATEGORY_IMAGES = {
    "gundem": [
        "turkey-flag-parliament", "istanbul-bosphorus-night", "ankara-government", "turkish-flag-sky",
        "grand-bazaar-istanbul", "turkish-coffee", "istanbul-skyline", "blue-mosque",
        "izmir-coast", "ankara-castle", "istanbul-bridge", "turkish-tea-garden",
        "antalya-beach", "cappadocia-balloons", "pamukkale-travertine", "trabzon-sumela",
        "turkish-river", "istanbul-tram", "ankara-mountain", "turkey-nature",
    ],
    "ekonomi": [
        "stock-market-chart", "bitcoin-crypto", "money-growth", "business-meeting",
        "dollar-euro-exchange", "stock-exchange", "gold-bars", "financial-graph",
        "investment-chart", "market-analysis", "bank-building", "economic-growth",
        "trading-dashboard", "crypto-wallet", "bull-bear-market", "profit-graph",
        "global-economy", "finance-data", "money-flow", "investor-strategy",
    ],
    "teknoloji": [
        "artificial-intelligence", "robot-hand-tech", "circuit-board", "cyber-security",
        "vr-headset-future", "smartphone-tech", "coding-screen", "data-center",
        "ai-chip-brain", "space-tech", "digital-transformation", "5g-network",
        "future-city-tech", "quantum-computing", "tech-startup", "innovation-lab",
        "machine-learning", "cloud-computing", "robot-automation", "smart-devices",
    ],
    "spor": [
        "football-stadium", "basketball-game", "soccer-ball-grass", "olympic-stadium",
        "tennis-match", "volleyball-action", "marathon-running", "swimming-race",
        "f1-race-car", "boxing-ring", "wrestling-match", "gym-fitness",
        "mountain-biking", "skiing-snow", "surfing-wave", "athletics-track",
        "golf-course", "champions-trophy", "sports-team", "winner-podium",
    ],
    "dunya": [
        "earth-globe-night", "world-map", "united-nations", "global-network",
        "paris-eiffel", "new-york-skyline", "london-bridge", "tokyo-night",
        "dubai-city", "beijing-temple", "moscow-kremlin", "rio-christ-statue",
        "sydney-opera", "berlin-gate", "rome-colosseum", "africa-savanna",
        "antarctica-ice", "pacific-ocean", "amazon-forest", "himalaya-mountain",
    ],
    "bilim": [
        "nasa-space", "microscope-lab", "dna-helix", "scientist-research",
        "telescope-stars", "mars-planet", "laboratory-experiment", "atom-particle",
        "space-shuttle", "molecular-structure", "brain-neuroscience", "satellite-orbit",
        "climate-change", "fossil-dinosaur", "deep-sea-explore", "solar-system",
        "genetic-research", "quantum-physics", "cancer-research", "vaccine-lab",
    ],
    "saglik": [
        "medical-doctor", "hospital-building", "healthy-food", "yoga-meditation",
        "stethoscope-heart", "medicine-pills", "elderly-care", "mental-health",
        "fitness-exercise", "sleep-health", "nutrition-veggies", "vaccine-injection",
        "heart-beat", "brain-health", "dental-care", "eye-vision",
        "physical-therapy", "pregnancy-care", "baby-health", "herbal-tea",
    ],
    "sanat": [
        "art-gallery", "paintbrush-art", "theater-stage", "music-concert",
        "sculpture-art", "dance-performance", "museum-interior", "classical-music",
        "street-art-graffiti", "photography-camera", "cinema-movie", "opera-house",
        "book-library", "piano-music", "ballet-dance", "modern-art",
        "ceramic-pottery", "film-director", "jazz-music", "fashion-design",
    ],
    "magazin": [
        "red-carpet", "celebrity-event", "fashion-show", "luxury-life",
        "hollywood-sign", "movie-premiere", "pop-star-concert", "magazine-cover",
        "fashion-model", "award-ceremony", "celebrity-wedding", "party-night",
        "luxury-car", "diamond-jewelry", "designer-dress", "penthouse-view",
        "social-media-star", "tv-studio", "reality-show", "youtube-creator",
    ],
}

# Picsum fallback temalari
PICSUM_THEMES = {
    "gundem": [10, 50, 100, 150, 200, 250, 300, 350, 400, 450],
    "ekonomi": [20, 60, 110, 160, 210, 260, 310, 360, 410, 460],
    "teknoloji": [30, 70, 120, 170, 220, 270, 320, 370, 420, 470],
    "spor": [40, 80, 130, 180, 230, 280, 330, 380, 430, 480],
    "dunya": [15, 55, 105, 155, 205, 255, 305, 355, 405, 455],
    "bilim": [25, 65, 115, 165, 215, 265, 315, 365, 415, 465],
    "saglik": [35, 75, 125, 175, 225, 275, 325, 375, 425, 475],
    "sanat": [45, 85, 135, 185, 235, 285, 335, 385, 435, 485],
    "magazin": [5, 95, 145, 195, 245, 295, 345, 395, 445, 495],
}

# Unsplash source ile gercek gorseller
def get_image_url(category, index):
    themes = CATEGORY_IMAGES.get(category, CATEGORY_IMAGES["gundem"])
    seed = themes[index % len(themes)]
    return f"https://picsum.photos/seed/{seed}/800/450"

def get_thumbnail_url(category, index):
    themes = CATEGORY_IMAGES.get(category, CATEGORY_IMAGES["gundem"])
    seed = themes[index % len(themes)]
    return f"https://picsum.photos/seed/{seed}/400/225"

def enhance_all():
    conn = get_db()
    rows = conn.execute("SELECT id, category, title FROM news ORDER BY id").fetchall()
    updated = 0
    for i, row in enumerate(rows):
        news_id = row["id"]
        cat = row["category"] or "gundem"
        new_image = get_image_url(cat, i)
        gallery = json.dumps([
            {"url": get_image_url(cat, i), "caption": ""},
            {"url": get_image_url(cat, i + 100), "caption": ""},
            {"url": get_image_url(cat, i + 200), "caption": ""},
        ], ensure_ascii=False)
        conn.execute("UPDATE news SET image=?, gallery=? WHERE id=?", (new_image, gallery, news_id))
        updated += 1
    conn.commit()
    conn.close()
    print(f"{updated} habere yeni gorseller eklendi!")

    # Ayrica kategorilere gore count goster
    conn = get_db()
    print("\nKategori dagilimi:")
    for row in conn.execute("SELECT category, COUNT(*) as cnt FROM news GROUP BY category ORDER BY cnt DESC").fetchall():
        print(f"  {row['category']}: {row['cnt']} haber")
    conn.close()

if __name__ == "__main__":
    enhance_all()
