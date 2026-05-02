import json
from pathlib import Path


BRANDS = {
    "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Land Cruiser Prado", "Prius", "Yaris", "Hilux"],
    "Volkswagen": ["Jetta", "Passat", "Tiguan", "Golf", "Polo", "Touareg", "Arteon", "T-Roc"],
    "BMW": ["3 Series", "5 Series", "X1", "X3", "X5", "7 Series"],
    "Mercedes-Benz": ["A-Class", "B-Class", "C-Class", "E-Class", "GLA", "GLC", "GLE"],
    "Audi": ["A3", "A4", "A6", "Q3", "Q5", "Q7"],
    "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Kona", "Palisade"],
    "Kia": ["Rio", "Cerato", "K5", "Sportage", "Sorento", "Seltos", "Carnival"],
    "Nissan": ["Sentra", "Altima", "Rogue", "X-Trail", "Qashqai", "Juke", "Pathfinder"],
    "Honda": ["Civic", "Accord", "CR-V", "HR-V", "Fit", "Pilot"],
    "Ford": ["Focus", "Fusion", "Escape", "Explorer", "F-150", "EcoSport"],
    "Chevrolet": ["Cruze", "Malibu", "Equinox", "Trax", "Trailblazer", "Tahoe"],
    "Mazda": ["Mazda 3", "Mazda 6", "CX-3", "CX-5", "CX-30", "CX-9"],
    "Lexus": ["ES", "IS", "NX", "RX", "GX", "LX", "UX"],
    "Subaru": ["Impreza", "Legacy", "Forester", "Outback", "XV", "Crosstrek"],
    "Mitsubishi": ["Lancer", "Outlander", "ASX", "Eclipse Cross", "Pajero", "Mirage"],
    "Peugeot": ["2008", "3008", "5008", "308", "408", "508"],
    "Renault": ["Logan", "Sandero", "Duster", "Kaptur", "Koleos", "Megane"],
    "Opel": ["Astra", "Corsa", "Mokka", "Insignia", "Grandland", "Crossland"],
    "Skoda": ["Octavia", "Superb", "Kodiaq", "Karoq", "Rapid", "Fabia"],
    "Volvo": ["XC40", "XC60", "XC90", "S60", "S90", "V60"],
}


PARTS = [
    ("ТО", "Масляный фильтр", "OF", "Фильтры", 1),
    ("ТО", "Воздушный фильтр", "AF", "Фильтры", 1),
    ("ТО", "Салонный фильтр", "CF", "Фильтры", 1),
    ("ТО", "Топливный фильтр", "FF", "Фильтры", 1),
    ("Двигатель", "Свеча зажигания", "SP", "Зажигание", 4),
    ("Двигатель", "Катушка зажигания", "IC", "Зажигание", 1),
    ("Двигатель", "Ремень/цепь ГРМ комплект", "TK", "ГРМ", 1),
    ("Двигатель", "Водяной насос", "WP", "Охлаждение", 1),
    ("Тормоза", "Колодки тормозные передние", "BPF", "Тормозная система", 1),
    ("Тормоза", "Колодки тормозные задние", "BPR", "Тормозная система", 1),
    ("Тормоза", "Диск тормозной передний", "BDF", "Тормозная система", 2),
    ("Тормоза", "Диск тормозной задний", "BDR", "Тормозная система", 2),
    ("Тормоза", "Датчик ABS", "ABS", "Тормозная система", 1),
    ("Подвеска", "Амортизатор передний левый", "SFL", "Передняя подвеска", 1),
    ("Подвеска", "Амортизатор передний правый", "SFR", "Передняя подвеска", 1),
    ("Подвеска", "Амортизатор задний", "SR", "Задняя подвеска", 2),
    ("Подвеска", "Рычаг передний левый", "CFL", "Передняя подвеска", 1),
    ("Подвеска", "Рычаг передний правый", "CFR", "Передняя подвеска", 1),
    ("Подвеска", "Стойка стабилизатора", "SL", "Стабилизатор", 2),
    ("Рулевое", "Рулевой наконечник левый", "TEL", "Рулевое управление", 1),
    ("Рулевое", "Рулевой наконечник правый", "TER", "Рулевое управление", 1),
    ("Трансмиссия", "ШРУС наружный", "CVJ", "Привод", 1),
    ("Трансмиссия", "Пыльник ШРУС", "CVB", "Привод", 1),
    ("Электрика", "Аккумулятор", "BAT", "Питание", 1),
    ("Электрика", "Стартер", "STA", "Пуск", 1),
    ("Электрика", "Генератор", "ALT", "Зарядка", 1),
    ("Кузов/свет", "Фара передняя левая", "HLL", "Оптика", 1),
    ("Кузов/свет", "Фара передняя правая", "HLR", "Оптика", 1),
    ("Кузов/свет", "Фонарь задний левый", "TLL", "Оптика", 1),
    ("Кузов/свет", "Фонарь задний правый", "TLR", "Оптика", 1),
    ("Кузов/свет", "Зеркало левое", "ML", "Кузов", 1),
    ("Кузов/свет", "Зеркало правое", "MR", "Кузов", 1),
]


BRAND_PREFIX = {
    "Toyota": "TY", "Volkswagen": "VW", "BMW": "BM", "Mercedes-Benz": "MB", "Audi": "AU",
    "Hyundai": "HY", "Kia": "KI", "Nissan": "NI", "Honda": "HO", "Ford": "FO",
    "Chevrolet": "CH", "Mazda": "MA", "Lexus": "LX", "Subaru": "SU", "Mitsubishi": "MI",
    "Peugeot": "PE", "Renault": "RE", "Opel": "OP", "Skoda": "SK", "Volvo": "VO",
}


def slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-").replace("--", "-")


def build_number(brand: str, model: str, code: str, idx: int) -> str:
    prefix = BRAND_PREFIX.get(brand, brand[:2].upper())
    model_code = "".join(ch for ch in model.upper() if ch.isalnum())[:4].ljust(4, "X")
    return f"{prefix}-{model_code}-{code}-{idx:03d}"


def main() -> None:
    brands = []
    for brand, models in BRANDS.items():
        brand_entry = {"name": brand, "slug": slug(brand), "models": []}
        for model in models:
            parts = []
            for idx, (category, name, code, group, qty) in enumerate(PARTS, start=1):
                oe = build_number(brand, model, code, idx)
                parts.append({
                    "category": category,
                    "group": group,
                    "name": name,
                    "number": oe,
                    "analog_numbers": [f"{oe}-A", f"{oe}-B"],
                    "quantity": qty,
                    "note": "Применимость и точный OEM подтверждаем по VIN перед заказом."
                })
            brand_entry["models"].append({
                "name": model,
                "slug": slug(model),
                "years": list(range(2026, 2009, -1)),
                "parts": parts,
            })
        brands.append(brand_entry)

    data = {
        "source_note": "Локальная витрина подбора EXPO MIR. Номера являются каталожными позициями для заявки; финальный OEM/аналог подтверждается по VIN.",
        "last_updated": "2026-05-02",
        "brands": brands,
    }
    out = Path("data")
    out.mkdir(exist_ok=True)
    (out / "parts_catalog.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
