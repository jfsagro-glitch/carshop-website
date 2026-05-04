#!/usr/bin/env python3
"""
Generate 456 realistic Korean cars for cars_korea_stock.json.
Matches structure used by korea-orders.html:
  external_id, source, brand, model, year, productionDate (MM.YYYY),
  price (USD), mileage, fuel_type, transmission, engine,
  power_hp, power_kw, color, drive, images (URL array), url, region
All cars: 2021-2023, power <= 160 hp / <= 116 kW.
"""
import json, hashlib, random, itertools

# Wikimedia thumbnail URL builder
def _wiki_thumb(filename: str, width: int = 400) -> str:
    name = filename.replace(" ", "_")
    h = hashlib.md5(name.encode()).hexdigest()
    return (
        f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[0]}{h[1]}/"
        f"{name}/{width}px-{name}"
    )

BRANDS = {
    "Hyundai": {
        "Sonata":    {"engine": "2.0", "hp": 150, "kw": 110, "fuel": "Бензин",
                      "photo": _wiki_thumb("Hyundai_Sonata_DN8.jpg")},
        "Tucson":    {"engine": "2.0", "hp": 150, "kw": 110, "fuel": "Бензин",
                      "photo": _wiki_thumb("2022_Hyundai_Tucson_NX4.jpg")},
        "Elantra":   {"engine": "1.6", "hp": 123, "kw": 90,  "fuel": "Бензин",
                      "photo": _wiki_thumb("2021_Hyundai_Elantra_CN7.jpg")},
        "i30":       {"engine": "1.5", "hp": 110, "kw": 81,  "fuel": "Бензин",
                      "photo": _wiki_thumb("Hyundai_i30_PD_facelift.jpg")},
        "Kona":      {"engine": "1.6", "hp": 141, "kw": 104, "fuel": "Бензин",
                      "photo": _wiki_thumb("2021_Hyundai_Kona.jpg")},
        "IONIQ":     {"engine": "1.6", "hp": 141, "kw": 104, "fuel": "Гибрид",
                      "photo": _wiki_thumb("2021_Hyundai_Ioniq_hybrid.jpg")},
    },
    "Kia": {
        "Cerato":    {"engine": "2.0", "hp": 150, "kw": 110, "fuel": "Бензин",
                      "photo": _wiki_thumb("2021_Kia_Cerato_facelift.jpg")},
        "Sportage":  {"engine": "2.0", "hp": 150, "kw": 110, "fuel": "Бензин",
                      "photo": _wiki_thumb("2022_Kia_Sportage_NQ5.jpg")},
        "Seltos":    {"engine": "1.6", "hp": 123, "kw": 90,  "fuel": "Бензин",
                      "photo": _wiki_thumb("2021_Kia_Seltos.jpg")},
        "Ceed":      {"engine": "1.5", "hp": 160, "kw": 118, "fuel": "Бензин",
                      "photo": _wiki_thumb("2021_Kia_Ceed_facelift.jpg")},
        "Niro":      {"engine": "1.6", "hp": 139, "kw": 102, "fuel": "Гибрид",
                      "photo": _wiki_thumb("2021_Kia_Niro_HEV.jpg")},
        "Soul":      {"engine": "2.0", "hp": 149, "kw": 110, "fuel": "Бензин",
                      "photo": _wiki_thumb("2021_Kia_Soul_facelift.jpg")},
    },
    "Ssangyong": {
        "Tivoli":    {"engine": "1.5", "hp": 128, "kw": 94,  "fuel": "Бензин",
                      "photo": _wiki_thumb("2021_SsangYong_Tivoli.jpg")},
        "Korando":   {"engine": "1.5", "hp": 163, "kw": 120, "fuel": "Бензин",
                      "photo": _wiki_thumb("2022_SsangYong_Korando.jpg")},
        "Rexton":    {"engine": "2.2", "hp": 181, "kw": 133, "fuel": "Дизель",
                      "photo": _wiki_thumb("2021_SsangYong_Rexton.jpg")},
    },
    "Renault Samsung": {
        "SM6":       {"engine": "1.6", "hp": 150, "kw": 110, "fuel": "Бензин",
                      "photo": _wiki_thumb("Renault_Samsung_SM6.jpg")},
        "QM6":       {"engine": "2.0", "hp": 143, "kw": 105, "fuel": "Бензин",
                      "photo": _wiki_thumb("Renault_Samsung_QM6_facelift.jpg")},
        "XM3":       {"engine": "1.3", "hp": 140, "kw": 103, "fuel": "Бензин",
                      "photo": _wiki_thumb("Renault_Samsung_XM3.jpg")},
    },
    "Chevrolet": {
        "Malibu":    {"engine": "2.0", "hp": 252, "kw": 185, "fuel": "Бензин",
                      "photo": _wiki_thumb("2021_Chevrolet_Malibu.jpg")},
        "Trailblazer":{"engine": "1.35", "hp": 156, "kw": 115, "fuel": "Бензин",
                       "photo": _wiki_thumb("2021_Chevrolet_Trailblazer.jpg")},
        "Trax":      {"engine": "1.4", "hp": 140, "kw": 103, "fuel": "Бензин",
                      "photo": _wiki_thumb("2021_Chevrolet_Trax.jpg")},
    },
    "Genesis": {
        "G70":       {"engine": "2.0", "hp": 252, "kw": 185, "fuel": "Бензин",
                      "photo": _wiki_thumb("2021_Genesis_G70.jpg")},
        "GV70":      {"engine": "2.0", "hp": 300, "kw": 221, "fuel": "Бензин",
                      "photo": _wiki_thumb("2022_Genesis_GV70.jpg")},
        "GV80":      {"engine": "2.0", "hp": 304, "kw": 224, "fuel": "Бензин",
                      "photo": _wiki_thumb("2021_Genesis_GV80.jpg")},
    },
}

# Keep only models with power <= 160 hp
MODELS_160 = {
    brand: {m: s for m, s in models.items() if s["hp"] <= 160}
    for brand, models in BRANDS.items()
}

COLORS = ["Белый", "Чёрный", "Серебристый", "Серый", "Синий",
          "Красный", "Бежевый", "Тёмно-синий", "Зелёный", "Коричневый"]
PERIODS = [(y, m) for y in range(2021, 2024) for m in range(1, 13)
           if not (y == 2021 and m < 5) and not (y == 2023 and m > 5)]

def gen_price(brand, hp, year, mileage):
    base = {"Hyundai": 12000, "Kia": 11000, "Ssangyong": 10000,
            "Renault Samsung": 11000, "Chevrolet": 12000, "Genesis": 25000}
    p = base.get(brand, 12000) + (hp - 100) * 60 + (year - 2021) * 800
    p = round(p * (1 - mileage / 400000), -2)
    return max(p, 7000)

def generate(target=456, seed=37):
    random.seed(seed)
    models_list = [(b, m, s) for b, ms in MODELS_160.items() for m, s in ms.items()]
    cars = []
    for i in range(target):
        brand, model, specs = models_list[i % len(models_list)]
        year, month = random.choice(PERIODS)
        mileage = random.randint(3000, 88000)
        if year == 2023: mileage = random.randint(2000, 28000)
        trans = random.choices(["Автомат", "Механика"], weights=[80, 20])[0]
        color = random.choice(COLORS)
        drive = random.choices(["FWD", "AWD", "4WD"], weights=[65, 25, 10])[0]
        price = gen_price(brand, specs["hp"], year, mileage)
        cid = 11000 + i
        cars.append({
            "external_id": f"encar-{cid}",
            "source": "encar",
            "brand": brand,
            "model": model,
            "year": year,
            "productionDate": f"{month:02d}.{year}",
            "price": price,
            "currency": "USD",
            "mileage": mileage,
            "fuel_type": specs["fuel"],
            "transmission": trans,
            "engine": specs["engine"],
            "power_hp": specs["hp"],
            "power_kw": specs["kw"],
            "color": color,
            "drive": drive,
            "images": [specs["photo"]],
            "url": f"https://www.encar.com/dc/dc_cardetailview.do?carid={cid}",
            "region": "korea",
        })
    return cars

if __name__ == "__main__":
    cars = generate()
    with open("cars_korea_stock.json", "w", encoding="utf-8") as f:
        json.dump(cars, f, ensure_ascii=False, indent=2)
    print(f"Generated {len(cars)} Korea cars -> cars_korea_stock.json")
    from collections import Counter
    brands = Counter(c["brand"] for c in cars)
    years = Counter(c["year"] for c in cars)
    print("Brands:", dict(brands.most_common()))
    print("Years:", dict(years))
