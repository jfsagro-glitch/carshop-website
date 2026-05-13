import json
import hashlib
import random
from generate_parts_catalog import (
    make_oem, get_merged_oem_lookup, 
    price_for, compatible_cars_str, generate_records
)
from pathlib import Path

# Load catalog
catalog_path = Path("data/parts_catalog.json")
catalog = json.load(open(catalog_path, encoding="utf-8"))

# Generate first 100 records manually with debug
records = []
oem_lookup = get_merged_oem_lookup()
count = 0
skipped = 0

for brand_data in catalog["brands"][:1]:  # Only first brand
    bname = brand_data["name"]
    prefix = brand_data.get("prefix", bname[:2].upper())
    
    print(f"Brand: {bname}, Prefix: {prefix}")
    
    for model in brand_data.get("models", [])[:1]:  # Only first model
        mname = model["name"]
        mslug = model["slug"]
        years = sorted(model.get("years", []))
        
        print(f"  Model: {mname} ({mslug}), Years: {years}")
        
        for part in catalog["parts_template"][:5]:  # Only first 5 parts
            code = part["code"]
            name = part["name"]
            
            # Check for OEM
            key = (prefix, code)
            has_oem_key = key in oem_lookup
            
            oem = make_oem(prefix, f"{mslug}", code, max(years) if years else 2020, oem_lookup)
            
            print(f"    Part {code:3} ({name:20}): OEM key {key} in lookup: {has_oem_key}, Result: {oem}")
            
            if oem:
                count += 1
            else:
                skipped += 1

print(f"\nTotal generated: {count}, Skipped (no OEM): {skipped}")
