const { chromium } = require('/Applications/ChatGPT.app/Contents/Resources/cua_node/lib/node_modules/playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
(async () => {
 const browser = await chromium.launch({headless:true,channel:'chrome'});
 const result = {date:new Date().toISOString(),consoleErrors:[],pageErrors:[],faviconRequests:[],faviconResponses:[],directGeoapifyRequests:0};
 try {
  const context = await browser.newContext();
  const page = await context.newPage();
  page.on('console',m=>{if(['error','warning'].includes(m.type()))result.consoleErrors.push({type:m.type(),message:m.text().replace(/https?:\/\/\S+/g,'[URL omitted]')});});
  page.on('pageerror',e=>result.pageErrors.push(e.message));
  page.on('request',r=>{const u=new URL(r.url());if(u.pathname.includes('favicon'))result.faviconRequests.push(u.pathname);if(u.host==='api.geoapify.com')result.directGeoapifyRequests++;});
  page.on('response',r=>{const u=new URL(r.url());if(u.pathname.includes('favicon'))result.faviconResponses.push({path:u.pathname,status:r.status(),contentType:r.headers()['content-type']});});
  await page.goto('http://127.0.0.1:5173/');
  await page.waitForTimeout(1500);
  assert.equal(await page.locator('link[rel="icon"]').getAttribute('href'),'/favicon.svg');
  const icon = await context.request.get('http://127.0.0.1:5173/favicon.svg');
  result.asset={status:icon.status(),contentType:icon.headers()['content-type']};
  assert.equal(icon.status(),200);assert.match(icon.headers()['content-type'],/image\/svg\+xml/);
  assert((await icon.text()).includes('<svg'));
  assert(result.faviconRequests.includes('/favicon.svg'));
  assert(!result.faviconRequests.includes('/favicon.ico'));
  assert.deepEqual(result.consoleErrors,[]);assert.deepEqual(result.pageErrors,[]);
  assert.equal(result.directGeoapifyRequests,0);
  assert(fs.readFileSync('frontend/dist/index.html','utf8').includes('href="/favicon.svg"'));
  assert(fs.readFileSync('frontend/dist/favicon.svg').equals(fs.readFileSync('frontend/public/favicon.svg')));
  result.buildAssetCopied=true;
  await page.screenshot({path:'docs/d1-fresh-load.png'});
  result.status='PASS';
 } catch(e) {result.status='FAIL';result.error=e.message;process.exitCode=1;}
 finally {fs.writeFileSync('docs/browser-checks/d1-favicon-results.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));await browser.close();}
})();
