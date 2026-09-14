// Optional maintainer QA: npm install --no-save playwright; npx playwright install chromium
// Run against a served _book: node scripts/browser_qa.cjs http://127.0.0.1:8765
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const report = JSON.parse(fs.readFileSync(path.join(root, 'qa-output/render-check.json'), 'utf8'));
const base = process.argv[2] || 'http://127.0.0.1:8765';
let browser;
(async () => {
  browser = await chromium.launch({headless: true, ...(process.env.QA_BROWSER_CHANNEL ? {channel: process.env.QA_BROWSER_CHANNEL} : {})});
  const page = await browser.newPage();
  const errors = [];
  const results = [];
  page.on('pageerror', error => errors.push({url: page.url(), error: error.message}));
  for (const section of report.sections) {
    const url = `${base}/${section.source.replace(/\.qmd$/, '.html')}`;
    await page.setViewportSize({width: 1440, height: 1000});
    await page.goto(url, {waitUntil: 'networkidle'});
    if (section.math) {
      await page.waitForFunction(() => window.MathJax?.startup?.promise, null, {timeout: 20000});
      await page.evaluate(() => window.MathJax.startup.promise);
    }
    // Check collapsed math after an actual click, then inspect every opened proof.
    const proof = page.locator('main .callout-header[data-bs-toggle="collapse"]').first();
    if (await proof.count()) {
      await proof.click();
      const target = await proof.getAttribute('data-bs-target');
      if (target) await page.locator(target).waitFor({state:'visible'});
    }
    await page.evaluate(() => {
      document.querySelectorAll('main .callout-collapse').forEach(el => el.classList.add('show'));
      document.querySelectorAll('main .callout-header[data-bs-toggle="collapse"]').forEach(el => el.setAttribute('aria-expanded', 'true'));
    });
    for (const width of [1440, 390, 320]) {
      await page.setViewportSize({width, height: 1000});
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      const state = await page.evaluate(() => ({
        mathErrors: [...document.querySelectorAll('mjx-merror, [data-mjx-error]')].map(el => el.textContent),
        renderedMath: document.querySelectorAll('mjx-container[jax="CHTML"]').length,
        pageOverflow: document.documentElement.scrollWidth > innerWidth + 2,
        overflowElements: [...document.querySelectorAll('main *')].filter(el => {
          const box = el.getBoundingClientRect();
          return box.width > 0 && box.right > innerWidth + 2 && !el.closest('mjx-container, .table-scroll, pre');
        }).slice(0, 6).map(el => ({tag:el.tagName, class:el.className, text:el.textContent.slice(0,80)})),
        tables: document.querySelectorAll('main table').length,
        wrappedTables: document.querySelectorAll('main .table-scroll table').length,
      }));
      if (state.mathErrors.length || state.pageOverflow || state.tables !== state.wrappedTables || (section.math && state.renderedMath < section.math)) errors.push({source: section.source, width, ...state});
      results.push({source: section.source, width, ...state});
    }
    console.log(`Checked ${section.source}`);
  }
  await page.setViewportSize({width:1440,height:1000});
  await page.goto(base, {waitUntil:'networkidle'});
  await page.locator('#quarto-search input').fill('Slutsky');
  await page.locator('#quarto-search-results a').first().waitFor();
  const searchLinks = await page.locator('#quarto-search-results a').evaluateAll(elements => elements.map(el => el.href));
  if (!searchLinks.some(link => link.includes('05-demand-properties'))) errors.push({error:'Slutsky search did not find the demand Section'});
  for (const width of [390, 320]) {
    await page.setViewportSize({width,height:844});
    await page.goto(base, {waitUntil:'networkidle'});
    await page.locator('button[aria-label="사이드바 전환"]').click();
    await page.locator('#quarto-sidebar.show').waitFor();
    await page.waitForFunction(() => !document.querySelector('#quarto-sidebar').classList.contains('collapsing'));
    const menuFits = await page.locator('#quarto-sidebar').evaluate(el => el.getBoundingClientRect().right <= innerWidth);
    if (!menuFits) errors.push({width,error:'Mobile menu exceeds viewport'});
    await page.locator('a.sidebar-item-toggle[data-bs-target="#quarto-sidebar-section-2"]').click();
    await page.locator('#quarto-sidebar-section-2.show').waitFor();
    await page.screenshot({path:path.join(root, `qa-output/menu-${width}.png`)});
    await page.locator('#quarto-sidebar-section-2 a[href$="04-indirect-utility-expenditure.html"]').click();
    await page.waitForURL('**/04-indirect-utility-expenditure.html');
  }
  console.log('Search and mobile Section navigation passed.');
  for (const [name, source, width] of [
    ['home-desktop', 'index.html', 1440],
    ['consumer-desktop', 'microeconomics/ch01-consumer/04-indirect-utility-expenditure.html', 1440],
    ['consumer-mobile', 'microeconomics/ch01-consumer/04-indirect-utility-expenditure.html', 390],
  ]) {
    await page.setViewportSize({width,height:1000});
    await page.goto(`${base}/${source}`, {waitUntil:'networkidle'});
    await page.evaluate(async () => { if (window.MathJax?.startup?.promise) await window.MathJax.startup.promise; });
    await page.screenshot({path:path.join(root, `qa-output/${name}.png`)});
  }
  fs.writeFileSync(path.join(root, 'qa-output/browser-check.json'), JSON.stringify({errors, results}, null, 2));
  await browser.close();
  console.log(`Browser checks: ${results.length}; errors: ${errors.length}`);
  process.exitCode = errors.length ? 1 : 0;
})().catch(async error => {console.error(error); if (browser) await browser.close(); process.exitCode=1;});
