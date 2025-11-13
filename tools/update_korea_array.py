import pathlib


SCRIPT_PATH = pathlib.Path('script.js')
MARKER = 'const koreaUnder160Cars = ['
REPLACEMENT = "const koreaUnder160Cars = Array.isArray(window.koreaUnder160CarsData) ? window.koreaUnder160CarsData : [];\n"


def main():
    content = SCRIPT_PATH.read_text(encoding='utf-8')
    start = content.find(MARKER)
    if start == -1:
        raise SystemExit('Marker not found')

    bracket_start = content.find('[', start)
    if bracket_start == -1:
        raise SystemExit('Opening bracket not found')

    depth = 0
    end = None
    for index in range(bracket_start, len(content)):
        char = content[index]
        if char == '[':
            depth += 1
        elif char == ']':
            depth -= 1
            if depth == 0:
                end = index + 1
                break
    if end is None:
        raise SystemExit('Closing bracket not found')

    # include trailing semicolon and newline if present
    if end < len(content) and content[end] == ';':
        end += 1
    if end < len(content) and content[end] == '\n':
        end += 1

    updated = content[:start] + REPLACEMENT + content[end:]
    SCRIPT_PATH.write_text(updated, encoding='utf-8')


if __name__ == '__main__':
    main()

