import fs from 'node:fs/promises';

const host = 'cmsauto.store';
const key = '0f83c120d4a94e40b7e83759043b3651';
const keyLocation = `https://${host}/${key}.txt`;
const sitemap = await fs.readFile(new URL('../sitemap.xml', import.meta.url), 'utf8');
const urlList = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((match) => match[1]);

if (!urlList.length) {
  throw new Error('No URLs found in sitemap.xml');
}

const response = await fetch('https://api.indexnow.org/indexnow', {
  method: 'POST',
  headers: { 'content-type': 'application/json; charset=utf-8' },
  body: JSON.stringify({ host, key, keyLocation, urlList }),
});

if (!response.ok && response.status !== 202) {
  throw new Error(`IndexNow returned ${response.status}: ${await response.text()}`);
}

console.log(`IndexNow accepted ${urlList.length} URLs (${response.status}).`);
