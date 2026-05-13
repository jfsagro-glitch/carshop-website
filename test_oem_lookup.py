from generate_parts_catalog import make_oem, get_merged_oem_lookup

oem_lookup = get_merged_oem_lookup()

# Test with sample values
prefix = 'TY'  # Toyota
part_code = 'EN'  # Engine
model_slug = 'camry-2015-2025'
year = 2020

result = make_oem(prefix, model_slug, part_code, year, oem_lookup)
print('Test: make_oem(TY, camry-2015-2025, EN, 2020) =', result)

# Check if key exists
key = (prefix, part_code)
if key in oem_lookup:
    print(f'Key {key} found with {len(oem_lookup[key])} options')
    print(f'Options: {oem_lookup[key][:3]}...')
else:
    print(f'Key {key} NOT found in lookup')

# Show total lookup size
print(f'\nTotal OEM lookup entries: {len(oem_lookup)}')
ty_count = sum(1 for k in oem_lookup if k[0] == 'TY')
print(f'Keys with TY prefix: {ty_count}')

# Show first 10 TY keys
ty_keys = sorted([k for k in oem_lookup if k[0] == 'TY'])[:10]
print('\nFirst 10 TY keys:')
for k in ty_keys:
    print(f'  {k}')
