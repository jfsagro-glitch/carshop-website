import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const outputPath = path.join(rootDir, 'data', 'stock_counts.json');

const SOURCES = {
  georgia: 'cars_georgia_stock.json',
  europe: 'cars_europe_new.json',
  korea: 'cars_korea_stock.json',
};

async function countJsonArray(fileName) {
  try {
    const payload = JSON.parse(await fs.readFile(path.join(rootDir, fileName), 'utf8'));
    return Array.isArray(payload) ? payload.length : 0;
  } catch (error) {
    if (error?.code === 'ENOENT') return 0;
    throw error;
  }
}

const counts = {};
for (const [key, fileName] of Object.entries(SOURCES)) {
  counts[key] = await countJsonArray(fileName);
}

await fs.writeFile(
  outputPath,
  `${JSON.stringify({ generated_at: new Date().toISOString(), counts }, null, 2)}\n`,
  'utf8',
);

console.log(`Saved stock counts: ${JSON.stringify(counts)}`);
