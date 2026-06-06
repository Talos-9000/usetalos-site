const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const baseURL = process.env.QA_BASE_URL || 'http://127.0.0.1:4173';
const phase = process.env.QA_PHASE || 'visual-quality';
const artifactDir = path.join(process.cwd(), 'qa-artifacts', phase);
fs.mkdirSync(artifactDir, { recursive: true });

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
  '/consulting/',
  '/consultation/',
  '/contact/',
];

const viewports = [
  { name: 'mobile-390', width: 390, height: 844, isMobile: true },
];

for (const viewport of viewports) {
  test.describe(`${viewport.name} visual quality`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height }, isMobile: viewport.isMobile });

    for (const route of routes) {
      test(`${route} looks non-broken`, async ({ page }) => {
        const url = new URL(route, baseURL).toString() + `?visual=${Date.now()}`;
        const response = await page.goto(url, { waitUntil: 'networkidle' });
        expect(response && response.status(), `${route} HTTP status`).toBeLessThan(400);

        await expect(page.locator('body')).toBeVisible();
        await expect(page.locator('header.site-header, header').first(), `${route} header visible`).toBeVisible();
        const contentRoot = page.locator('main, body').first();
        await expect(contentRoot, `${route} content visible`).toBeVisible();

        const metrics = await page.evaluate(() => {
          const text = document.body.innerText.replace(/\s+/g, ' ').trim();
          const root = document.querySelector('main') || document.body;
          const mainText = (root.innerText || root.textContent || '').replace(/\s+/g, ' ').trim();
          const viewportW = window.innerWidth;
          const viewportH = window.innerHeight;
          const doc = document.documentElement;
          const badVisibleTextBlocks = [...document.querySelectorAll('main p, main li, main h1, main h2, main h3, main a.btn, main button')]
            .filter((el) => {
              const r = el.getBoundingClientRect();
              const style = window.getComputedStyle(el);
              const visible = r.width > 1 && r.height > 1 && style.visibility !== 'hidden' && style.display !== 'none';
              return visible && (el.textContent || '').trim().length === 0;
            })
            .slice(0, 12)
            .map((el) => ({ tag: el.tagName, className: el.className, html: el.outerHTML.slice(0, 160) }));

          const brokenImages = [...document.images]
            .filter((img) => !img.complete || img.naturalWidth < 1 || img.naturalHeight < 1)
            .map((img) => ({ src: img.currentSrc || img.src, alt: img.alt }));

          const overflowElements = [...document.querySelectorAll('*')]
            .filter((el) => {
              const style = window.getComputedStyle(el);
              if (style.position === 'fixed' || style.position === 'absolute') return false;
              return el.scrollWidth > doc.clientWidth + 1;
            })
            .slice(0, 12)
            .map((el) => ({ tag: el.tagName, className: String(el.className), scrollWidth: el.scrollWidth, clientWidth: el.clientWidth }));

          const giantBlankBlocks = [...root.querySelectorAll('section, .card, .container, article')]
            .filter((el) => {
              const r = el.getBoundingClientRect();
              const txt = (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim();
              return r.height > viewportH * 0.95 && txt.length < 80;
            })
            .slice(0, 8)
            .map((el) => ({ tag: el.tagName, className: String(el.className), height: Math.round(el.getBoundingClientRect().height), text: (el.innerText || el.textContent || '').trim().slice(0, 120) }));

          const logo = document.querySelector('.site-logo img, .site-header img, header img');
          const logoRect = logo ? logo.getBoundingClientRect() : null;

          return {
            title: document.title,
            bodyTextLength: text.length,
            mainTextLength: mainText.length,
            scrollWidth: doc.scrollWidth,
            viewportW,
            overflow: doc.scrollWidth - viewportW,
            badVisibleTextBlocks,
            brokenImages,
            overflowElements,
            giantBlankBlocks,
            logoRect: logoRect ? { width: Math.round(logoRect.width), height: Math.round(logoRect.height) } : null,
          };
        });

        console.log(JSON.stringify({ route, viewport: viewport.name, ...metrics }));

        expect(metrics.mainTextLength, `${route} should not look empty`).toBeGreaterThan(250);
        expect(metrics.overflow, `${route} horizontal overflow`).toBeLessThanOrEqual(1);
        expect(metrics.overflowElements, `${route} overflowing elements`).toEqual([]);
        expect(metrics.brokenImages, `${route} broken images`).toEqual([]);
        expect(metrics.badVisibleTextBlocks, `${route} visible empty text blocks`).toEqual([]);
        expect(metrics.giantBlankBlocks, `${route} giant blank blocks`).toEqual([]);

        if (metrics.logoRect) {
          expect(metrics.logoRect.width, `${route} logo too wide`).toBeLessThanOrEqual(viewport.isMobile ? 180 : 260);
          expect(metrics.logoRect.height, `${route} logo too tall`).toBeLessThanOrEqual(viewport.isMobile ? 52 : 72);
        }

        const name = `${viewport.name}-${route === '/' ? 'home' : route.replace(/^\//, '').replace(/\/$/, '').replace(/\//g, '-')}.png`;
        await page.screenshot({ path: path.join(artifactDir, name), fullPage: false });
      });
    }
  });
}
