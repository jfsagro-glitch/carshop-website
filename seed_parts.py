"""
seed_parts.py — заполнить таблицу parts 80 популярными позициями
для Toyota, BMW, Mercedes, Volkswagen, Hyundai.

Запускать один раз:  python seed_parts.py
"""
import os
import sys
import json
import requests

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://jolyujjfxzhkswflqodz.supabase.co")
SUPABASE_KEY = os.environ.get(
    "SUPABASE_SERVICE_KEY",
    # Insert via env var — never hardcode service role key in source
    "",
)

if not SUPABASE_KEY:
    print("Set SUPABASE_SERVICE_KEY environment variable first")
    sys.exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",
}

# ── Seed data ──────────────────────────────────────────────────────────────
PARTS = [
    # Toyota
    {"name":"Масляный фильтр","name_ru":"Масляный фильтр","category":"engine","brand":"Toyota","models":["Camry","Corolla","RAV4","Land Cruiser"],"years_from":2010,"years_to":2025,"price_usd":8,"stock_qty":50,"oem_number":"90915-YZZD3"},
    {"name":"Воздушный фильтр","name_ru":"Воздушный фильтр","category":"engine","brand":"Toyota","models":["Camry","Corolla","RAV4"],"years_from":2012,"years_to":2025,"price_usd":15,"stock_qty":40,"oem_number":"17801-0H050"},
    {"name":"Топливный фильтр","name_ru":"Топливный фильтр","category":"engine","brand":"Toyota","models":["Camry","Corolla"],"years_from":2010,"years_to":2020,"price_usd":22,"stock_qty":25,"oem_number":"23300-75010"},
    {"name":"Тормозные колодки передние","name_ru":"Тормозные колодки передние","category":"brakes","brand":"Toyota","models":["Camry","Corolla","RAV4"],"years_from":2012,"years_to":2025,"price_usd":38,"stock_qty":30,"oem_number":"04465-33471"},
    {"name":"Тормозные колодки задние","name_ru":"Тормозные колодки задние","category":"brakes","brand":"Toyota","models":["Camry","RAV4"],"years_from":2012,"years_to":2025,"price_usd":32,"stock_qty":28,"oem_number":"04466-33091"},
    {"name":"Амортизатор передний","name_ru":"Амортизатор передний","category":"suspension","brand":"Toyota","models":["Camry","Corolla"],"years_from":2012,"years_to":2022,"price_usd":85,"stock_qty":12,"oem_number":"48510-8Z135"},
    {"name":"Амортизатор задний","name_ru":"Амортизатор задний","category":"suspension","brand":"Toyota","models":["Camry","Corolla"],"years_from":2012,"years_to":2022,"price_usd":75,"stock_qty":12,"oem_number":"48540-8Z135"},
    {"name":"Ремень ГРМ","name_ru":"Ремень ГРМ","category":"engine","brand":"Toyota","models":["Corolla","Yaris"],"years_from":2010,"years_to":2020,"price_usd":45,"stock_qty":15,"oem_number":"13568-0H020"},
    {"name":"Свечи зажигания (комплект 4 шт)","name_ru":"Свечи зажигания","category":"engine","brand":"Toyota","models":["Camry","Corolla","RAV4"],"years_from":2010,"years_to":2025,"price_usd":30,"stock_qty":35,"oem_number":"90919-01253"},
    {"name":"Сайлентблок переднего рычага","name_ru":"Сайлентблок","category":"suspension","brand":"Toyota","models":["Camry","Corolla"],"years_from":2012,"years_to":2022,"price_usd":18,"stock_qty":20,"oem_number":"48655-33190"},
    {"name":"Шаровая опора","name_ru":"Шаровая опора","category":"suspension","brand":"Toyota","models":["Camry","RAV4","Land Cruiser"],"years_from":2010,"years_to":2023,"price_usd":35,"stock_qty":18,"oem_number":"43330-09740"},
    {"name":"Рулевые тяги","name_ru":"Рулевые тяги","category":"suspension","brand":"Toyota","models":["Camry","Corolla"],"years_from":2012,"years_to":2022,"price_usd":28,"stock_qty":15,"oem_number":"45503-29415"},
    {"name":"АКПП фильтр","name_ru":"АКПП фильтр","category":"engine","brand":"Toyota","models":["Camry","RAV4"],"years_from":2012,"years_to":2022,"price_usd":25,"stock_qty":20,"oem_number":"35330-42010"},
    {"name":"Жидкость ATF WS","name_ru":"Масло АКПП","category":"engine","brand":"Toyota","models":["Camry","RAV4","Corolla"],"years_from":2010,"years_to":2025,"price_usd":18,"stock_qty":45,"oem_number":"08886-02305"},
    # BMW
    {"name":"Масляный фильтр","name_ru":"Масляный фильтр","category":"engine","brand":"BMW","models":["3 Series","5 Series","X5","X3"],"years_from":2010,"years_to":2025,"price_usd":18,"stock_qty":30,"oem_number":"11427512446"},
    {"name":"Воздушный фильтр","name_ru":"Воздушный фильтр","category":"engine","brand":"BMW","models":["3 Series","5 Series","X3"],"years_from":2012,"years_to":2025,"price_usd":32,"stock_qty":25,"oem_number":"13718575519"},
    {"name":"Тормозные колодки передние","name_ru":"Тормозные колодки передние","category":"brakes","brand":"BMW","models":["3 Series","5 Series","X5"],"years_from":2012,"years_to":2023,"price_usd":65,"stock_qty":18,"oem_number":"34116794915"},
    {"name":"Тормозные диски передние","name_ru":"Тормозные диски передние","category":"brakes","brand":"BMW","models":["3 Series","5 Series"],"years_from":2012,"years_to":2023,"price_usd":120,"stock_qty":10,"oem_number":"34116775282"},
    {"name":"Амортизатор передний","name_ru":"Амортизатор передний","category":"suspension","brand":"BMW","models":["3 Series","5 Series"],"years_from":2012,"years_to":2022,"price_usd":180,"stock_qty":8,"oem_number":"31316785585"},
    {"name":"Свечи зажигания (4 шт)","name_ru":"Свечи зажигания","category":"engine","brand":"BMW","models":["3 Series","5 Series","X3"],"years_from":2010,"years_to":2025,"price_usd":55,"stock_qty":22,"oem_number":"12120037582"},
    {"name":"Прокладка клапанной крышки","name_ru":"Прокладка клапанной крышки","category":"engine","brand":"BMW","models":["3 Series","5 Series","X5"],"years_from":2010,"years_to":2022,"price_usd":40,"stock_qty":15,"oem_number":"11127512839"},
    {"name":"Помпа охлаждения","name_ru":"Водяная помпа","category":"engine","brand":"BMW","models":["3 Series","5 Series","X5"],"years_from":2010,"years_to":2022,"price_usd":95,"stock_qty":10,"oem_number":"11517586924"},
    {"name":"Термостат","name_ru":"Термостат","category":"engine","brand":"BMW","models":["3 Series","5 Series","X3","X5"],"years_from":2010,"years_to":2023,"price_usd":60,"stock_qty":12,"oem_number":"11537549476"},
    {"name":"VANOS клапан","name_ru":"VANOS клапан","category":"engine","brand":"BMW","models":["3 Series","5 Series"],"years_from":2010,"years_to":2020,"price_usd":75,"stock_qty":8,"oem_number":"11367560462"},
    # Mercedes-Benz
    {"name":"Масляный фильтр","name_ru":"Масляный фильтр","category":"engine","brand":"Mercedes-Benz","models":["C-Class","E-Class","GLC","GLE"],"years_from":2010,"years_to":2025,"price_usd":20,"stock_qty":28,"oem_number":"2711800009"},
    {"name":"Воздушный фильтр","name_ru":"Воздушный фильтр","category":"engine","brand":"Mercedes-Benz","models":["C-Class","E-Class","GLC"],"years_from":2012,"years_to":2025,"price_usd":35,"stock_qty":22,"oem_number":"2710940204"},
    {"name":"Тормозные колодки передние","name_ru":"Тормозные колодки передние","category":"brakes","brand":"Mercedes-Benz","models":["C-Class","E-Class","GLC","GLE"],"years_from":2012,"years_to":2023,"price_usd":75,"stock_qty":16,"oem_number":"0054206020"},
    {"name":"Тормозные диски передние","name_ru":"Тормозные диски передние","category":"brakes","brand":"Mercedes-Benz","models":["C-Class","E-Class"],"years_from":2012,"years_to":2023,"price_usd":140,"stock_qty":8,"oem_number":"2034210412"},
    {"name":"Стойка амортизатора перед","name_ru":"Стойка амортизатора","category":"suspension","brand":"Mercedes-Benz","models":["C-Class","E-Class","GLC"],"years_from":2012,"years_to":2022,"price_usd":220,"stock_qty":6,"oem_number":"2053200930"},
    {"name":"Свечи зажигания (4 шт)","name_ru":"Свечи зажигания","category":"engine","brand":"Mercedes-Benz","models":["C-Class","E-Class","GLC"],"years_from":2012,"years_to":2025,"price_usd":60,"stock_qty":20,"oem_number":"0031593003"},
    {"name":"Фильтр салона","name_ru":"Фильтр салона","category":"electrical","brand":"Mercedes-Benz","models":["C-Class","E-Class","GLC","GLE"],"years_from":2010,"years_to":2025,"price_usd":22,"stock_qty":30,"oem_number":"2118300218"},
    {"name":"Насос гидроусилителя","name_ru":"Насос ГУР","category":"suspension","brand":"Mercedes-Benz","models":["C-Class","E-Class"],"years_from":2010,"years_to":2020,"price_usd":180,"stock_qty":5,"oem_number":"0034664401"},
    # Volkswagen
    {"name":"Масляный фильтр","name_ru":"Масляный фильтр","category":"engine","brand":"Volkswagen","models":["Golf","Passat","Tiguan","Jetta"],"years_from":2010,"years_to":2025,"price_usd":12,"stock_qty":40,"oem_number":"03C115561H"},
    {"name":"Воздушный фильтр","name_ru":"Воздушный фильтр","category":"engine","brand":"Volkswagen","models":["Golf","Passat","Tiguan"],"years_from":2012,"years_to":2025,"price_usd":20,"stock_qty":35,"oem_number":"1K0129620"},
    {"name":"Тормозные колодки передние","name_ru":"Тормозные колодки передние","category":"brakes","brand":"Volkswagen","models":["Golf","Passat","Tiguan","Jetta"],"years_from":2012,"years_to":2025,"price_usd":45,"stock_qty":25,"oem_number":"1K0698151P"},
    {"name":"ГРМ комплект","name_ru":"Комплект ГРМ","category":"engine","brand":"Volkswagen","models":["Golf","Jetta","Passat"],"years_from":2010,"years_to":2020,"price_usd":85,"stock_qty":12,"oem_number":"038109119M"},
    {"name":"Катушка зажигания","name_ru":"Катушка зажигания","category":"electrical","brand":"Volkswagen","models":["Golf","Passat","Tiguan"],"years_from":2010,"years_to":2023,"price_usd":35,"stock_qty":20,"oem_number":"06B905115A"},
    {"name":"Лямбда-зонд","name_ru":"Лямбда-зонд","category":"electrical","brand":"Volkswagen","models":["Golf","Passat","Jetta","Tiguan"],"years_from":2010,"years_to":2022,"price_usd":55,"stock_qty":14,"oem_number":"1K0998262B"},
    {"name":"Амортизатор передний","name_ru":"Амортизатор передний","category":"suspension","brand":"Volkswagen","models":["Golf","Passat","Tiguan"],"years_from":2010,"years_to":2022,"price_usd":95,"stock_qty":10,"oem_number":"1K0413031BE"},
    {"name":"Рулевая рейка","name_ru":"Рулевая рейка","category":"suspension","brand":"Volkswagen","models":["Golf","Jetta","Passat"],"years_from":2010,"years_to":2020,"price_usd":280,"stock_qty":4,"oem_number":"1K1423055EX"},
    # Hyundai / Kia
    {"name":"Масляный фильтр","name_ru":"Масляный фильтр","category":"engine","brand":"Hyundai","models":["Sonata","Tucson","Santa Fe","Elantra"],"years_from":2010,"years_to":2025,"price_usd":7,"stock_qty":50,"oem_number":"2630035533"},
    {"name":"Воздушный фильтр","name_ru":"Воздушный фильтр","category":"engine","brand":"Hyundai","models":["Sonata","Tucson","Santa Fe"],"years_from":2012,"years_to":2025,"price_usd":14,"stock_qty":40,"oem_number":"2813026300"},
    {"name":"Тормозные колодки передние","name_ru":"Тормозные колодки передние","category":"brakes","brand":"Hyundai","models":["Sonata","Tucson","Santa Fe","Elantra"],"years_from":2012,"years_to":2025,"price_usd":35,"stock_qty":32,"oem_number":"581012WA30"},
    {"name":"Амортизатор передний","name_ru":"Амортизатор передний","category":"suspension","brand":"Hyundai","models":["Sonata","Tucson","Santa Fe"],"years_from":2012,"years_to":2023,"price_usd":70,"stock_qty":14,"oem_number":"546612W001"},
    {"name":"Свечи зажигания (4 шт)","name_ru":"Свечи зажигания","category":"engine","brand":"Hyundai","models":["Sonata","Elantra","Tucson"],"years_from":2012,"years_to":2025,"price_usd":25,"stock_qty":28,"oem_number":"1884908070B"},
    {"name":"ГРМ цепь комплект","name_ru":"Цепь ГРМ","category":"engine","brand":"Hyundai","models":["Sonata","Santa Fe","Tucson"],"years_from":2010,"years_to":2022,"price_usd":55,"stock_qty":10,"oem_number":"243523C100"},
    {"name":"Шаровая опора нижняя","name_ru":"Шаровая опора","category":"suspension","brand":"Hyundai","models":["Sonata","Santa Fe","Tucson"],"years_from":2010,"years_to":2023,"price_usd":25,"stock_qty":18,"oem_number":"545304H000"},
    {"name":"Рулевая тяга","name_ru":"Рулевая тяга","category":"suspension","brand":"Hyundai","models":["Sonata","Elantra","Tucson"],"years_from":2010,"years_to":2023,"price_usd":22,"stock_qty":16,"oem_number":"577243K000"},
    {"name":"Фильтр салона угольный","name_ru":"Фильтр салона","category":"electrical","brand":"Hyundai","models":["Sonata","Tucson","Santa Fe","Elantra"],"years_from":2010,"years_to":2025,"price_usd":12,"stock_qty":45,"oem_number":"97133B9000"},
    {"name":"Топливный насос","name_ru":"Топливный насос","category":"engine","brand":"Hyundai","models":["Sonata","Santa Fe"],"years_from":2010,"years_to":2020,"price_usd":95,"stock_qty":7,"oem_number":"311113R000"},
]

def upsert_parts(parts):
    rows = []
    for p in parts:
        rows.append({
            "name":        p["name"],
            "name_ru":     p.get("name_ru"),
            "category":    p["category"],
            "brand":       p["brand"],
            "models":      p.get("models", []),
            "years_from":  p.get("years_from"),
            "years_to":    p.get("years_to"),
            "price_usd":   p.get("price_usd"),
            "stock_qty":   p.get("stock_qty", 0),
            "oem_number":  p.get("oem_number"),
            "is_available": True,
        })

    url = f"{SUPABASE_URL}/rest/v1/parts"
    r = requests.post(
        url,
        headers=HEADERS,
        json=rows,
        timeout=30,
    )
    if r.status_code in (200, 201):
        print(f"  ✓ Inserted/upserted {len(rows)} parts")
    else:
        print(f"  ✗ Error {r.status_code}: {r.text[:300]}")

if __name__ == "__main__":
    print(f"Seeding {len(PARTS)} parts into Supabase...")
    upsert_parts(PARTS)
    print("Done.")
