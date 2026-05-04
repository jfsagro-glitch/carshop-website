#!/usr/bin/env python3
"""
Generate 494 realistic European cars for cars_europe_new.json.
Matches structure expected by europe-orders.html:
  external_id, source, brand, model, year, first_registration (MM/YYYY),
  price (EUR), currency, mileage, fuel_type, transmission, engine,
  power_hp, power_kw, color, drive, country, images (URL array), url, region
All cars: May 2021 – May 2023, power <= 160 hp.
"""
import json, hashlib, random
from collections import Counter

def _wiki_thumb(filename: str, width: int = 400) -> str:
    name = filename.replace(" ", "_")
    h = hashlib.md5(name.encode()).hexdigest()
    return (
        f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[0]}{h[1]}/"
        f"{name}/{width}px-{name}"
    )

BRANDS = {
    "Volkswagen": {
        "Golf":    {"engine": "1.5", "hp": 130, "kw": 96,  "fuel": "Бензин",
                    "photo": _wiki_thumb("2020_Volkswagen_Golf_VIII.jpg")},
        "Tiguan":  {"engine": "1.4", "hp": 150, "kw": 110, "fuel": "Бензин",
                    "photo": _wiki_thumb("VW_Tiguan_II_facelift_2020.jpg")},
        "Polo":    {"engine": "1.0", "hp": 95,  "kw": 70,  "fuel": "Бензин",
                    "photo": _wiki_thumb("Volkswagen_Polo_VI_facelift_2021.jpg")},
    },
    "Toyota": {
        "Corolla": {"engine": "1.8", "hp": 122, "kw": 90,  "fuel": "Гибрид",
                    "photo": _wiki_thumb("2019_Toyota_Corolla_sedan.jpg")},
        "Yaris":   {"engine": "1.5", "hp": 116, "kw": 85,  "fuel": "Гибрид",
                    "photo": _wiki_thumb("2020_Toyota_Yaris_XP210.jpg")},
        "C-HR":    {"engine": "1.8", "hp": 122, "kw": 90,  "fuel": "Гибрид",
                    "photo": _wiki_thumb("2022_Toyota_C-HR.jpg")},
        "RAV4":    {"engine": "2.0", "hp": 149, "kw": 110, "fuel": "Гибрид",
                    "photo": _wiki_thumb("2022_Toyota_RAV4.jpg")},
    },
    "Skoda": {
        "Octavia":  {"engine": "1.5", "hp": 150, "kw": 110, "fuel": "Бензин",
                     "photo": _wiki_thumb("Skoda_Octavia_IV_facelift.jpg")},
        "Karoq":    {"engine": "1.5", "hp": 150, "kw": 110, "fuel": "Бензин",
                     "photo": _wiki_thumb("2021_Skoda_Karoq_facelift.jpg")},
        "Fabia":    {"engine": "1.0", "hp": 95,  "kw": 70,  "fuel": "Бензин",
                     "photo": _wiki_thumb("2021_Skoda_Fabia_IV.jpg")},
    },
    "Renault": {
        "Clio":    {"engine": "1.0", "hp": 90,  "kw": 66,  "fuel": "Бензин",
                    "photo": _wiki_thumb("2019_Renault_Clio_V.jpg")},
        "Captur":  {"engine": "1.0", "hp": 90,  "kw": 66,  "fuel": "Бензин",
                    "photo": _wiki_thumb("2020_Renault_Captur.jpg")},
        "Arkana":  {"engine": "1.3", "hp": 140, "kw": 103, "fuel": "Бензин",
                    "photo": _wiki_thumb("2021_Renault_Arkana.jpg")},
    },
    "Hyundai": {
        "i30":     {"engine": "1.5", "hp": 110, "kw": 81,  "fuel": "Бензин",
                    "photo": _wiki_thumb("2020_Hyundai_i30_facelift.jpg")},
        "Tucson":  {"engine": "1.6", "hp": 150, "kw": 110, "fuel": "Гибрид",
                    "photo": _wiki_thumb("2022_Hyundai_Tucson_NX4.jpg")},
        "Kona":    {"engine": "1.0", "hp": 120, "kw": 88,  "fuel": "Бензин",
                    "photo": _wiki_thumb("2021_Hyundai_Kona_Europe.jpg")},
    },
    "Kia": {
        "Ceed":    {"engine": "1.5", "hp": 160, "kw": 118, "fuel": "Бензин",
                    "photo": _wiki_thumb("2021_Kia_Ceed_facelift.jpg")},
        "Sportage":{"engine": "1.6", "hp": 150, "kw": 110, "fuel": "Гибрид",
                    "photo": _wiki_thumb("2022_Kia_Sportage_NQ5.jpg")},
        "Stonic":  {"engine": "1.0", "hp": 120, "kw": 88,  "fuel": "Бензин",
                    "photo": _wiki_thumb("2021_Kia_Stonic_facelift.jpg")},
    },
    "Ford": {
        "Focus":   {"engine": "1.5", "hp": 150, "kw": 110, "fuel": "Бензин",
                    "photo": _wiki_thumb("2022_Ford_Focus_facelift.jpg")},
        "Puma":    {"engine": "1.0", "hp": 125, "kw": 92,  "fuel": "Гибрид",
                    "photo": _wiki_thumb("2020_Ford_Puma_ST-Line.jpg")},
        "Kuga":    {"engine": "1.5", "hp": 150, "kw": 110, "fuel": "Бензин",
                    "photo": _wiki_thumb("2020_Ford_Kuga.jpg")},
    },
    "Opel": {
        "Astra":    {"engine": "1.2", "hp": 130, "kw": 96,  "fuel": "Бензин",
                     "photo": _wiki_thumb("2022_Opel_Astra_L.jpg")},
        "Corsa":    {"engine": "1.2", "hp": 100, "kw": 74,  "fuel": "Бензин",
                     "photo": _wiki_thumb("2020_Opel_Corsa_F.jpg")},
        "Crossland":{"engine": "1.2", "hp": 110, "kw": 81,  "fuel": "Бензин",
                     "photo": _wiki_thumb("2021_Opel_Crossland_facelift.jpg")},
    },
    "Peugeot": {
        "308":     {"engine": "1.2", "hp": 130, "kw": 96,  "fuel": "Бензин",
                    "photo": _wiki_thumb("2022_Peugeot_308_II.jpg")},
        "2008":    {"engine": "1.2", "hp": 130, "kw": 96,  "fuel": "Бензин",
                    "photo": _wiki_thumb("2021_Peugeot_2008.jpg")},
        "208":     {"engine": "1.2", "hp": 100, "kw": 74,  "fuel": "Бензин",
                    "photo": _wiki_thumb("2021_Peugeot_208.jpg")},
    },
    "Seat": {
        "Leon":    {"engine": "1.5", "hp": 150, "kw": 110, "fuel": "Бензин",
                    "photo": _wiki_thumb("2020_SEAT_Leon_IV.jpg")},
        "Ateca":   {"engine": "1.5", "hp": 150, "kw": 110, "fuel": "Бензин",
                    "photo": _wiki_thumb("2021_SEAT_Ateca_facelift.jpg")},
    },
    "Nissan": {
        "Qashqai": {"engine": "1.3", "hp": 140, "kw": 103, "fuel": "Гибрид",
                    "photo": _wiki_thumb("2022_Nissan_Qashqai_J12.jpg")},
        "Juke":    {"engine": "1.0", "hp": 114, "kw": 84,  "fuel": "Бензин",
                    "photo": _wiki_thumb("2020_Nissan_Juke.jpg")},
    },
    "Mazda": {
        "3":       {"engine": "2.0", "hp": 122, "kw": 90,  "fuel": "Бензин",
                    "photo": _wiki_thumb("2019_Mazda3_sedan_sedan.jpg")},
        "CX-5":    {"engine": "2.0", "hp": 165, "kw": 121, "fuel": "Бензин",
                    "photo": _wiki_thumb("2022_Mazda_CX-5.jpg")},
    },
    "Honda": {
        "Civic":   {"engine": "1.5", "hp": 182, "kw": 134, "fuel": "Бензин",
                    "photo": _wiki_thumb("2022_Honda_Civic_XI.jpg")},
        "HR-V":    {"engine": "1.5", "hp": 131, "kw": 96,  "fuel": "Гибрид",
                    "photo": _wiki_thumb("2022_Honda_HR-V_III.jpg")},
    },
    "BMW": {
        "116i":    {"engine": "1.5", "hp": 109, "kw": 80,  "fuel": "Бензин",
                    "photo": _wiki_thumb("BMW_1_Series_F40.jpg")},
        "320d":    {"engine": "2.0", "hp": 150, "kw": 110, "fuel": "Дизель",
                    "photo": _wiki_thumb("2022_BMW_320d_G20.jpg")},
    },
    "Audi": {
        "A3":      {"engine": "1.5", "hp": 150, "kw": 110, "fuel": "Бензин",
                    "photo": _wiki_thumb("2021_Audi_A3_Sedan_40_TFSI.jpg")},
        "Q3":      {"engine": "1.5", "hp": 150, "kw": 110, "fuel": "Бензин",
                    "photo": _wiki_thumb("2022_Audi_Q3_35_TFSI.jpg")},
    },
    "Mercedes-Benz": {
        "A 180":   {"engine": "1.3", "hp": 136, "kw": 100, "fuel": "Бензин",
                    "photo": _wiki_thumb("Mercedes-Benz_A-Class_W177.jpg")},
        "GLA 200": {"engine": "1.3", "hp": 163, "kw": 120, "fuel": "Бензин",
                    "photo": _wiki_thumb("2021_Mercedes-Benz_GLA_200.jpg")},
    },
}

# Keep only models with hp <= 160
MODELS_160 = {
    brand: {m: s for m, s in models.items() if s["hp"] <= 160}
    for brand, models in BRANDS.items()
}

COUNTRIES = {
    "Volkswagen": "Германия", "Skoda": "Германия", "BMW": "Германия",
    "Audi": "Германия", "Mercedes-Benz": "Германия", "Opel": "Германия",
    "Ford": "Германия", "Toyota": "Нидерланды", "Renault": "Франция",
    "Peugeot": "Франция", "Seat": "Испания", "Kia": "Чехия",
    "Hyundai": "Чехия", "Nissan": "Великобритания", "Mazda": "Германия",
    "Honda": "Германия",
}

PRICE_BASE = {
    "Volkswagen": 14000, "Toyota": 15000, "Skoda": 13000, "Renault": 11000,
    "Hyundai": 13000, "Kia": 13500, "Ford": 13000, "Opel": 12000,
    "Peugeot": 12000, "Seat": 13000, "Nissan": 13000, "Mazda": 14000,
    "Honda": 14000, "BMW": 19000, "Audi": 19000, "Mercedes-Benz": 20000,
}

COLORS = ["Белый", "Чёрный", "Серебристый", "Серый", "Синий",
          "Красный", "Зелёный", "Тёмно-синий", "Бежевый", "Коричневый"]
PERIODS = [(y, m) for y in range(2021, 2024) for m in range(1, 13)
           if not (y == 2021 and m < 5) and not (y == 2023 and m > 5)]

def gen_price(brand, hp, year, mileage):
    base = PRICE_BASE.get(brand, 13000) + (hp - 90) * 50 + (year - 2021) * 600
    p = round(base * (1 - mileage / 500000), -2)
    return max(int(p), 8000)

def generate(target=494, seed=29):
    random.seed(seed)
    models_list = [(b, m, s) for b, ms in MODELS_160.items() for m, s in ms.items()]
    cars = []
    for i in range(target):
        brand, model, specs = models_list[i % len(models_list)]
        year, month = random.choice(PERIODS)
        mileage = random.randint(4000, 90000)
        if year == 2023: mileage = random.randint(3000, 30000)
        trans = random.choices(["Автомат", "Механика"], weights=[70, 30])[0]
        color = random.choice(COLORS)
        drive = random.choices(["FWD", "AWD"], weights=[75, 25])[0]
        price = gen_price(brand, specs["hp"], year, mileage)
        eid = f"as24-{10001 + i}"
        cars.append({
            "external_id": eid,
            "source": "autoscout24",
            "brand": brand,
            "model": model,
            "year": year,
            "first_registration": f"{month:02d}/{year}",
            "price": price,
            "currency": "EUR",
            "mileage": mileage,
            "fuel_type": specs["fuel"],
            "transmission": trans,
            "engine": specs["engine"],
            "power_hp": specs["hp"],
            "power_kw": specs["kw"],
            "color": color,
            "drive": drive,
            "country": COUNTRIES.get(brand, "Германия"),
            "images": [specs["photo"]],
            "url": f"https://www.autoscout24.de/angebote/{eid}",
            "region": "europe",
        })
    return cars

if __name__ == "__main__":
    cars = generate()
    with open("cars_europe_new.json", "w", encoding="utf-8") as f:
        json.dump(cars, f, ensure_ascii=False, indent=2)
    print(f"Generated {len(cars)} Europe cars -> cars_europe_new.json")
    from collections import Counter
    print("Brands:", dict(Counter(c["brand"] for c in cars).most_common(8)))
    print("Years:", dict(Counter(c["year"] for c in cars)))
