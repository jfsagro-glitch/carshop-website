import csv

with open('generated_parts_catalog.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    
    with_oem = 0
    without_oem = 0
    
    for row in rows:
        oem = row.get('oem_number', row.get('\ufeffoem_number', '')).strip()
        if oem and oem not in ('None', 'null', ''):
            with_oem += 1
        else:
            without_oem += 1
    
    print(f'Total rows: {len(rows):,}')
    print(f'With OEM: {with_oem:,} ({100*with_oem/len(rows):.1f}%)')
    print(f'Without OEM: {without_oem:,} ({100*without_oem/len(rows):.1f}%)')
    
    print('\nSample with OEM:')
    for i, row in enumerate(rows[:3]):
        oem = row.get('oem_number', row.get('\ufeffoem_number', ''))
        print(f'  {oem}')

