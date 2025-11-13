import json
import pathlib
from collections import OrderedDict


INPUT_PATH = pathlib.Path('images/Korea/korea_processed.json')
OUTPUT_PATH = pathlib.Path('images/Korea/korea_processed.js')


def main():
    data = json.loads(INPUT_PATH.read_text(encoding='utf-8'))
    lines = ['window.koreaUnder160CarsData = [']
    total = len(data)
    for index, item in enumerate(data):
        ordered = OrderedDict()
        for key in ['name', 'brand', 'model', 'image', 'priceFrom', 'priceLabel', 'link', 'specs', 'description']:
            if key in item:
                ordered[key] = item[key]
        json_block = json.dumps(ordered, ensure_ascii=False, indent=4)
        indented = '    ' + json_block.replace('\n', '\n    ')
        if index < total - 1:
            indented += ','
        lines.append(indented)
    lines.append('];')
    OUTPUT_PATH.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()

