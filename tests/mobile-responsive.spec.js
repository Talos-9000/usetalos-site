const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const baseURL = process.env.QA_BASE_URL || process.env.BASE_URL || 'http://127.0.0.1:4173';
const phase = process.env.QA_PHASE || 'run';
const outDir = path.join(process.cwd(), 'qa-artifacts', phase);
fs.mkdirSync(outDir, { recursive: true });

const routes = [
  '/',
  '/store/',
  '/personal-ai/',
  '/templates/',
  '/tools/',
  '/blog/',
  '/newsletter/',
  '/about/',
  '/get-help/',
  '/consulting/'
];

const viewports = [
  { name: 'iphone-se-375', width: 375, height: 667 },
  { name: 'iphone-14-390', width: 390, height: 844 },
  { name: 'iphone-plus-414', width: 414, height: 896 },
  { name: 'iphone-pro-max-430', width: 430, height: 932 }
];

async function collectMetrics(page) {
  return await page.evaluate(() => {
    const root = document.documentElement;
    const overflowElements = [...document.querySelectorAll('*')]
      .filter(el => el.scrollWidth > root.clientWidth)
      .slice(0, 25)
      .map(el => ({
        tag: el.tagName,
        class: typeof el.className === 'string' ? el.className : String(el.className || ''),
        id: el.id,
        scrollWidth: el.scrollWidth,
        clientWidth: el.clientWidth,
        text: (el.textContent || '').trim().slice(0, 80)
      }));

    return {
      route: location.pathname,
      viewport: window.innerWidth,
      scrollWidth: root.scrollWidth,
      overflow: root.scrollWidth - window.innerWidth,
      bodyScrollWidth: document.body ? document.body.scrollWidth : null,
      overflowElements,
      navRects: [...document.querySelectorAll('nav, .nav, header')].map(el => {
        const r = el.getBoundingClientRect();
        return { tag: el.tagName, class: el.className, top: r.top, bottom: r.bottom, height: r.height, width: r.width };
      })
    };
  });
}

for (const vp of viewports) {
  test.describe(`${vp.name}`, () => {
    test.use({ viewport: { width: vp.width, height: vp.height }, isMobile: true, hasTouch: true });

    for (const route of routes) {
      test(`${route} no horizontal overflow`, async ({ page, browserName }) => {
        const safeRoute = route.replace(/\//g, '_').replace(/^_$/, 'home') || 'home';
        const label = `${browserName}-${vp.name}-${safeRoute}`;
        const response = await page.goto(`${baseURL}${route}`, { waitUntil: 'networkidle' });
        const status = response ? response.status() : 0;
        const pageSize = await page.evaluate(() => ({
          width: document.documentElement.scrollWidth,
          height: Math.min(document.documentElement.scrollHeight, 16000)
        }));
        await page.screenshot({ path: path.join(outDir, `${label}-viewport.png`), fullPage: false });
        await page.screenshot({
          path: path.join(outDir, `${label}-full-capped.png`),
          clip: { x: 0, y: 0, width: Math.min(pageSize.width, vp.width), height: Math.max(1, pageSize.height) }
        });
        const metrics = await collectMetrics(page);
        const record = { browserName, viewportName: vp.name, requestedRoute: route, status, ...metrics };
        fs.appendFileSync(path.join(outDir, 'overflow-results.jsonl'), JSON.stringify(record) + '\n');
        console.log(JSON.stringify(record));
        expect(status, `${route} HTTP status`).toBeLessThan(400);
        expect(metrics.overflow, `${route} overflow ${JSON.stringify(metrics.overflowElements, null, 2)}`).toBe(0);
      });
    }
  });
}
