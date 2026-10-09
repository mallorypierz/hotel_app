// Controlled UI verification. Successful chat responses are labeled mocks, not OpenAI evidence.
// Run against Vite + an isolated backend; existing external Playwright/Chrome, no app dependency.
const { chromium } = require(process.env.PLAYWRIGHT_RUNTIME || '/Applications/ChatGPT.app/Contents/Resources/cua_node/lib/node_modules/playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const fixture = JSON.parse(fs.readFileSync('docs/chatbot-backend-mock-trace.json'));
(async () => {
 const browser = await chromium.launch({ headless: true, channel: 'chrome' });
 const passed = [], errors = [], providerRequests = [];
 try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
  page.setDefaultTimeout(6000);
  page.on('pageerror', e => errors.push(e.message));
  page.on('request', r => { if (/openai|openrouter|generativelanguage/.test(r.url())) providerRequests.push(r.url()); });
  await page.route('https://fonts.googleapis.com/**', r => r.fulfill({ body: '' }));
  await page.route('https://images.unsplash.com/**', r => r.fulfill({ body: '' }));
  let mode = 'answer', calls = 0, release;
  await page.route('**/api/chat', async route => {
   calls++;
   const question = route.request().postDataJSON().question;
   if (mode === 'delay') await new Promise(resolve => { release = resolve; });
   if (mode === 'malformed') return route.fulfill({ body: '{bad' });
   if (mode === 'failure') return route.fulfill({ status: 503, headers: { 'Retry-After': '2' }, json: { detail: { message: 'Controlled provider rate limit.' } } });
   const data = structuredClone(fixture.response);
   data.evidence.question = question;
   if (['clarification', 'no_matches', 'insufficient_data'].includes(mode)) {
    data.status = mode; data.hotels = []; data.answer = `Controlled ${mode} response.`;
   }
   if (mode === 'xss') {
    data.answer = '<img src=x onerror="window.injected=true">';
    data.hotels[0].name = data.answer; data.evidence.proposal.sql = data.answer;
   }
   await route.fulfill({ json: data }).catch(() => {});
  });
  await page.goto('http://127.0.0.1:5173/');
  const panel = page.locator('#chatbot'), field = page.getByLabel('Your question', { exact: true });
  const send = panel.getByRole('button', { name: 'Send', exact: true });
  assert(await send.isDisabled());
  await field.fill(fixture.question); await field.press('Enter'); assert.equal(calls, 0);
  await field.press('Tab'); assert(await send.evaluate(el => el === document.activeElement));
  await send.press('Enter'); await panel.getByText('Your saved-hotel answer', { exact: true }).waitFor();
  assert.match(await panel.innerText(), /\$260\.00/); assert.match(await panel.innerText(), /2026-10-12/);
  assert(await send.evaluate(el => el === document.activeElement));
  const summary = panel.locator('summary'); await summary.focus(); await summary.press('Enter');
  assert(await panel.locator('details').evaluate(el => el.open));
  assert.match(await panel.locator('details').innerText(), /gpt-4.1-mini-2025-04-14/);
  assert.match(await panel.locator('details').innerText(), /nightly_rate_cents/);
  passed.push('Keyboard newline/Tab/Enter, focus retained, grounded cards, expandable SQL/records/model');
  await panel.getByRole('button', { name: 'Edit question or dates' }).click();
  assert(await field.evaluate(el => el === document.activeElement));
  mode = 'delay'; await field.fill('Delayed question'); await send.click();
  await panel.getByText('Checking saved hotels…', { exact: true }).waitFor();
  assert(await panel.getByRole('button', { name: 'Sending…' }).isDisabled());
  const count = calls; await panel.locator('form').evaluate(el => el.requestSubmit()); assert.equal(calls, count);
  await field.fill('New question'); release();
  await panel.getByText('Ready for your question', { exact: true }).waitFor();
  assert.equal(await panel.locator('.answer').count(), 0);
  mode = 'answer'; await send.click(); await panel.locator('.answer').waitFor();
  passed.push('Loading, duplicate guard, edit cancellation, stale response ignored, next request succeeds');
  for (const state of ['clarification','no_matches','insufficient_data']) {
   mode = state; await field.fill(state); await send.click();
   await panel.getByText(`Controlled ${state} response.`, { exact: true }).waitFor();
   assert.equal(await panel.locator('.hotel-fact').count(), 0);
   assert(await panel.locator('.simulation-label').isVisible());
  }
  passed.push('Clarification, no matches, insufficient data, persistent simulated label');
  mode = 'failure'; await field.fill('limited'); await send.click();
  await panel.getByText('Controlled provider rate limit.', { exact: true }).waitFor();
  await field.fill('edited while limited'); assert(await send.isDisabled());
  await page.waitForTimeout(2100); assert(await send.isEnabled());
  mode = 'malformed'; await send.click(); await panel.getByText('The server returned an unreadable response. Please try again.', { exact: true }).waitFor();
  passed.push('Failure, cooldown retained across edits, malformed response');
  mode = 'delay'; await field.fill('Timeout check');
  await page.clock.install(); await send.click();
  await panel.getByText('Checking saved hotels…', { exact: true }).waitFor();
  await page.clock.runFor(50001);
  await panel.getByText('The request timed out. Please try again.', { exact: true }).waitFor();
  release(); await page.clock.resume();
  passed.push('50-second browser deadline with controlled clock');
  mode = 'xss'; await field.fill('Literal text test'); await send.click(); await panel.locator('.answer').waitFor();
  assert.equal(await panel.locator('img').count(), 0); assert.equal(await page.evaluate(() => window.injected), undefined);
  passed.push('Model, hotel name and SQL HTML payloads rendered as text');
  mode = 'answer'; await field.fill(fixture.question); await send.click(); await panel.locator('.answer').waitFor();
  await page.evaluate(() => { const label = document.createElement('p'); label.textContent = 'CONTROLLED VERIFICATION — mocked chatbot response, not a live OpenAI call'; document.querySelector('#chatbot').prepend(label); });
  await panel.screenshot({ path: 'docs/chatbot-ui-desktop-v2.png' });
  await page.setViewportSize({ width: 390, height: 844 });
  await summary.click();
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await panel.screenshot({ path: 'docs/chatbot-ui-mobile-v2.png' });
  await page.setViewportSize({ width: 320, height: 844 });
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  passed.push('390px and 320px layouts including expanded evidence have no page overflow');
  await page.unroute('**/api/chat');
  await field.fill('Test missing backend configuration'); await send.click();
  await panel.getByText('Request failed', { exact: true }).waitFor();
  assert.match(await panel.innerText(), /configured|configuration|API key/i);
  passed.push('Actual FastAPI missing-configuration failure (test server key deliberately empty)');
  await page.locator('#search input').fill('Boston'); await page.locator('#search button').click();
  await page.getByRole('heading', { name: '4 places to consider' }).waitFor();
  assert.equal(await page.locator('.results tbody tr').count(), 4);
  await page.locator('#search input').fill('Aspen'); await page.locator('#search button').click();
  await page.getByRole('heading', { name: 'No stays matched' }).waitFor();
  passed.push('Actual sample Boston four rows and Aspen no-results');
  assert.deepEqual(providerRequests, []); assert.deepEqual(errors, []);
  passed.push('No browser provider requests or JavaScript errors');
  fs.writeFileSync('docs/browser-checks/chatbot-results.json', JSON.stringify({ label: 'Controlled mocked frontend checks; isolated real backend for sample search and configuration failure', passed, errors, providerRequests }, null, 2) + '\n');
  console.log(JSON.stringify({ passed }, null, 2));
 } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
