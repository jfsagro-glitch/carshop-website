#!/usr/bin/env python3
"""
Supplement cars_georgia_stock.json with synthetic Georgian cars
to reach 480 total. Preserves existing real cars.
"""
import json
import random

BRANDS_MODELS = {
    "Toyota": {
        "Camry":   {"engine": "2.5", "hp": 150, "kw": 110, "fuel": "Бензин", "trans_w": [70, 30]},
        "RAV4":    {"engine": "2.0", "hp": 150, "kw": 110, "fuel": "Бензин", "trans_w": [80, 20]},
        "Corolla": {"engine": "1.8", "hp": 122, "kw": 90,  "fuel": "Гибрид", "trans_w": [90, 10]},
        "C-HR":    {"engine": "1.8", "hp": 122, "kw": 90,  "fuel": "Гибрид", "trans_w": [90, 10]},
        "Yaris":   {"engine": "1.5", "hp": 116, "kw": 85,  "fuel": "Гибрид", "trans_w": [90, 10]},
    },
    "Hyundai": {
        "Tucson":  {"engine": "2.0", "hp": 150, "kw": 110, "fuel": "Бензин", "trans_w": [70, 30]},
        "Santa Fe":{"engine": "2.0", "hp": 150, "kw": 110, "fuel": "Дизель", "trans_w": [60, 40]},
        "Creta":   {"engine": "1.6", "hp": 123, "kw": 90,  "fuel": "Бензин", "trans_w": [70, 30]},
        "i30":     {"engine": "1.5", "hp": 110, "kw": 81,  "fuel": "Бензин", "trans_w": [60, 40]},
    },
    "Kia": {
        "Sportage":{"engine": "2.0", "hp": 150, "kw": 110, "fuel": "Бензин", "trans_w": [70, 30]},
        "Seltos":  {"engine": "1.6", "hp": 123, "kw": 90,  "fuel": "Бензин", "trans_w": [70, 30]},
        "Ceed":    {"engine": "1.5", "hp": 160, "kw": 118, "fuel": "Бензин", "trans_w": [60, 40]},
        "Sorento": {"engine": "2.0", "hp": 149, "kw": 110, "fuel": "Дизель", "trans_w": [50, 50]},
    },
    "Volkswagen": {
        "Tiguan":  {"engine": "1.4", "hp": 150, "kw": 110, "fuel": "Бензин", "trans_w": [80, 20]},
        "Golf":    {"engine": "1.5", "hp": 130, "kw": 96,  "fuel": "Бензин", "trans_w": [70, 30]},
        "Polo":    {"engine": "1.0", "hp": 95,  "kw": 70,  "fuel": "Бензин", "trans_w": [60, 40]},
    },
    "BMW": {
        "118i":    {"engine": "1.5", "hp": 140, "kw": 103, "fuel": "Бензин", "trans_w": [80, 20]},
        "316d":    {"engine": "2.0", "hp": 122, "kw": 90,  "fuel": "Дизель", "trans_w": [70, 30]},
    },
    "Mercedes-Benz": {
        "A 200":   {"engine": "1.3", "hp": 163, "kw": 120, "fuel": "Бензин", "trans_w": [85, 15]},
        "GLA 200": {"engine": "1.3", "hp": 163, "kw": 120, "fuel": "Бензин", "trans_w": [85, 15]},
        "C 200":   {"engine": "1.5", "hp": 150, "kw": 110, "fuel": "Бензин", "trans_w": [85, 15]},
    },
    "Subaru": {
        "Outback":  {"engine": "2.5", "hp": 175, "kw": 129, "fuel": "Бензин", "trans_w": [85, 15]},
        "Forester": {"engine": "2.0", "hp": 150, "kw": 110, "fuel": "Бензин", "trans_w": [85, 15]},
    },
    "Lexus": {
        "NX 300h": {"engine": "2.5", "hp": 150, "kw": 110, "fuel": "Гибрид", "trans_w": [90, 10]},
        "UX 250h": {"engine": "2.0", "hp": 135, "kw": 99,  "fuel": "Гибрид", "trans_w": [90, 10]},
    },
    "Nissan": {
        "Qashqai": {"engine": "1.3", "hp": 140, "kw": 103, "fuel": "Бензин", "trans_w": [70, 30]},
        "Juke":    {"engine": "1.0", "hp": 114, "kw": 84,  "fuel": "Бензин", "trans_w": [65, 35]},
        "X-Trail": {"engine": "1.3", "hp": 160, "kw": 118, "fuel": "Бензин", "trans_w": [70, 30]},
    },
    "Mazda": {
        "CX-5":    {"engine": "2.0", "hp": 150, "kw": 110, "fuel": "Бензин", "trans_w": [75, 25]},
        "3":       {"engine": "2.0", "hp": 150, "kw": 110, "fuel": "Бензин", "trans_w": [65, 35]},
    },
    "Honda": {
        "CR-V":    {"engine": "1.5", "hp": 150, "kw": 110, "fuel": "Бензин", "trans_w": [75, 25]},
        "HR-V":    {"engine": "1.5", "hp": 131, "kw": 96,  "fuel": "Гибрид", "trans_w": [80, 20]},
    },
    "Mitsubishi": {
        "Outlander":    {"engine": "2.0", "hp": 146, "kw": 107, "fuel": "Бензин", "trans_w": [70, 30]},
        "Eclipse Cross":{"engine": "1.5", "hp": 150, "kw": 110, "fuel": "Бензин", "trans_w": [75, 25]},
    },
    "Ford": {
        "Focus":   {"engine": "1.5", "hp": 150, "kw": 110, "fuel": "Бензин", "trans_w": [65, 35]},
        "Kuga":    {"engine": "1.5", "hp": 150, "kw": 110, "fuel": "Бензин", "trans_w": [70, 30]},
    },
    "Renault": {
        "Duster":  {"engine": "1.3", "hp": 130, "kw": 96,  "fuel": "Бензин", "trans_w": [60, 40]},
        "Arkana":  {"engine": "1.3", "hp": 150, "kw": 110, "fuel": "Бензин", "trans_w": [80, 20]},
    },
}

PRICE_MAP = {
    "Toyota/Camry":    (18000, 28000),
    "Toyota/RAV4":     (22000, 32000),
    "Toyota/Corolla":  (14000, 20000),
    "Toyota/C-HR":     (15000, 22000),
    "Toyota/Yaris":    (11000, 17000),
    "Hyundai/Tucson":  (17000, 25000),
    "Hyundai/Santa Fe":(20000, 30000),
    "Hyundai/Creta":   (13000, 19000),
    "Hyundai/i30":     (12000, 18000),
    "Kia/Sportage":    (17000, 25000),
    "Kia/Seltos":      (14000, 20000),
    "Kia/Ceed":        (13000, 19000),
    "Kia/Sorento":     (22000, 32000),
    "Volkswagen/Tiguan":(18000, 27000),
    "Volkswagen/Golf": (12000, 18000),
    "Volkswagen/Polo": (9000,  14000),
    "BMW/118i":        (18000, 26000),
    "BMW/316d":        (17000, 25000),
    "Mercedes-Benz/A 200":  (20000, 28000),
    "Mercedes-Benz/GLA 200":(22000, 30000),
    "Mercedes-Benz/C 200":  (25000, 35000),
    "Subaru/Outback":  (20000, 28000),
    "Subaru/Forester": (18000, 26000),
    "Lexus/NX 300h":   (28000, 38000),
    "Lexus/UX 250h":   (24000, 32000),
    "Nissan/Qashqai":  (15000, 22000),
    "Nissan/Juke":     (12000, 18000),
    "Nissan/X-Trail":  (18000, 26000),
    "Mazda/CX-5":      (17000, 25000),
    "Mazda/3":         (13000, 19000),
    "Honda/CR-V":      (18000, 26000),
    "Honda/HR-V":      (15000, 22000),
    "Mitsubishi/Outlander":    (16000, 24000),
    "Mitsubishi/Eclipse Cross":(17000, 25000),
    "Ford/Focus":      (12000, 18000),
    "Ford/Kuga":       (16000, 23000),
    "Renault/Duster":  (11000, 17000),
    "Renault/Arkana":  (14000, 20000),
}

COLORS = [
    "Белый", "Чёрный", "Серебристый", "Серый", "Синий",
    "Красный", "Зелёный", "Бежевый", "Коричневый",
    "Синий металлик", "Графитовый", "Перламутровый белый",
]
YEARS = [2021, 2021, 2022, 2022, 2022, 2023, 2023]

MYAUTO_PHOTO_BASE = "https://static.my.ge/myauto/photos"


def fake_photo(car_id: int) -> str:
    d1 = (car_id // 100000) % 10
    d2 = (car_id // 10000) % 10
    d3 = (car_id // 1000) % 10
    d4 = (car_id // 100) % 10
    d5 = (car_id // 10) % 10
    return f"{MYAUTO_PHOTO_BASE}/{d1}/{d2}/{d3}/{d4}/{d5}/large/{car_id}_1.jpg"


def generate(existing_count: int, target: int = 480, seed: int = 42) -> list:
    random.seed(seed)
    cars = []
    needed = max(0, target - existing_count)
    car_id = 150000000 + existing_count

    model_list = [(brand, model, specs)
                  for brand, models in BRANDS_MODELS.items()
                  for model, specs in models.items()]

    for i in range(needed):
        brand, model, specs = model_list[i % len(model_list)]
        year = random.choice(YEARS)
        mileage = random.randint(4000, 85000)
        if year == 2023:
            mileage = random.randint(3000, 30000)
        lo, hi = PRICE_MAP.get(f"{brand}/{model}", (12000, 22000))
        price = random.randint(lo, hi)
        if mileage > 70000:
            price = round(price * 0.88)
        elif mileage < 20000:
            price = round(price * 1.06)
        trans_w = specs["trans_w"]
        transmission = random.choices(["Автомат", "Механика"], weights=trans_w, k=1)[0]
        drive = random.choices(["FWD", "AWD"], weights=[65, 35], k=1)[0]
        color = random.choice(COLORS)
        cars.append({
            "id": existing_count + i + 1,
            "brand": brand,
            "model": model,
            "year": year,
            "engine": specs["engine"],
            "vin": "",
            "price": price,
            "mileage": mileage,
            "fuel_type": specs["fuel"],
            "transmission": transmission,
            "color": color,
            "drive": drive,
            "power": f"{specs['hp']} л.с. / {specs['kw']} кВт",
            "date": "",
            "description": f"myauto.ge/ru/pr/{car_id + i}",
            "photos": fake_photo(car_id + i),
            "folder_id": "",
            "sold": False,
        })
    return cars


if __name__ == "__main__":
    stock_file = "cars_georgia_stock.json"
    with open(stock_file, "r", encoding="utf-8") as f:
        existing = json.load(f)

    print(f"Existing: {len(existing)} cars")
    synthetic = generate(len(existing), target=480)
    print(f"Adding {len(synthetic)} synthetic cars")

    combined = existing + synthetic
    for i, car in enumerate(combined, 1):
        car["id"] = i

    with open(stock_file, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"Total: {len(combined)} -> {stock_file}")
    brands = {}
    for c in combined:
        brands[c["brand"]] = brands.get(c["brand"], 0) + 1
    print("Brand distribution:", dict(sorted(brands.items(), key=lambda x: -x[1])[:10]))
