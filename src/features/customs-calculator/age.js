export function resolveManufactureDate(input) {
  if (input.manufactureDate) {
    return input.manufactureDate;
  }

  if (input.manufactureMonth && input.manufactureYear) {
    const month = String(input.manufactureMonth).slice(5, 7) || String(input.manufactureMonth).padStart(2, '0');
    return `${input.manufactureYear}-${month}-01`;
  }

  if (input.manufactureYear) {
    return `${input.manufactureYear}-07-01`;
  }

  return '';
}

export function getAgeBand(manufactureDate, calculationDate) {
  const made = parseDate(manufactureDate);
  const calc = parseDate(calculationDate);
  if (!made || !calc) return '';

  if (calc <= addYears(made, 3)) return 'under_3';
  if (calc <= addYears(made, 5)) return 'from_3_to_5';
  if (calc <= addYears(made, 7)) return 'from_5_to_7';
  return 'over_7';
}

export function resolveAgeBand(input) {
  if (input.ageBand) return input.ageBand;
  const date = resolveManufactureDate(input);
  return date ? getAgeBand(date, input.calculationDate) : '';
}

function parseDate(value) {
  if (!value) return null;
  const date = new Date(`${value}T00:00:00`);
  return Number.isNaN(date.getTime()) ? null : date;
}

function addYears(date, years) {
  const out = new Date(date.getTime());
  out.setFullYear(out.getFullYear() + years);
  return out;
}
