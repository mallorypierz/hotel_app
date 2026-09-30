// Controlled browser checks. Uses an existing external Playwright runtime;
// no npm installation and no fixture records enter application source.
const { chromium } = require(process.env.PLAYWRIGHT_RUNTIME || '/Applications/ChatGPT.app/Contents/Resources/cua_node/lib/node_modules/playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
(async () => {
 const browser = await chromium.launch({ headless: true, channel: 'chrome' });
 try {
 const page = await browser.newPage({viewport:{width:1280,height:1000}});
 page.setDefaultTimeout(10000);
 const errors=[], calls=[], tileHeaders=[];
 page.on('pageerror',e=>errors.push(e.message));
 let scenario='results', tileFailure=false;
 const fixture={provider:'geoapify',center:{postcode:'02108',country_code:'us',locality:'Boston',latitude:42.36,longitude:-71.06},radius_meters:5000,hotels:[{place_id:'fixture-a',name:'Controlled hotel A',address:'Controlled address A',latitude:42.361,longitude:-71.061},{place_id:'fixture-b',name:null,address:null,latitude:42.38,longitude:-71.08}],count:2,limit:20,limit_reached:false,omitted_count:1,duplicates_removed:1};
 await page.route('**/api/discovery/hotels?**',async route=>{
  calls.push(route.request().url());
  if(scenario==='results') await route.fulfill({json:fixture});
  else if(scenario==='empty') await route.fulfill({json:{...fixture,hotels:[],count:0,omitted_count:0,duplicates_removed:0}});
  else if(scenario==='unresolved') await route.fulfill({status:404,json:{detail:{code:'zip_unresolved'}}});
  else if(scenario==='limited') await route.fulfill({status:503,headers:{'Retry-After':'2'},json:{detail:{code:'provider_limited'}}});
  else if(scenario==='failure') await route.abort();
  else if(scenario==='slow'){await new Promise(r=>setTimeout(r,1000));await route.fulfill({json:fixture}).catch(()=>{});}
 });
 await page.route('https://tile.openstreetmap.org/**',async route=>{
  tileHeaders.push(await route.request().allHeaders());
  if(tileFailure) return route.abort();
  await route.fulfill({contentType:'image/png',body:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=','base64')});
 });
 await page.goto('http://127.0.0.1:5173/');
 const zip=page.getByLabel('U.S. ZIP code',{exact:true});
 const search=page.getByRole('button',{name:'Search hotels',exact:true});
 const feedback=page.locator('#discovery-feedback');
 const rowA=page.locator('.hotel-list').getByRole('button',{name:/1. Controlled hotel A/});
 const markerB=page.locator('.hotel-marker').nth(1);
 assert.equal(calls.length,0);
 await zip.fill('2108'); await search.click();
 assert.match(await feedback.innerText(),/five-digit/); assert.equal(calls.length,0);
 await zip.fill('02108'); await zip.press('Enter');
 await rowA.waitFor();
 assert.match(calls[0],/postcode=02108$/);
 await rowA.focus(); await rowA.press('Space');
 await page.waitForFunction(()=>document.querySelector('.hotel-list button')?.getAttribute('aria-pressed')==='true');
 assert.equal(await rowA.getAttribute('aria-pressed'),'true');
 assert.equal(await page.locator('.hotel-marker').first().getAttribute('aria-pressed'),'true');
 await markerB.focus(); await markerB.press('Enter');
 await page.waitForFunction(()=>document.querySelectorAll('.hotel-list button')[1]?.getAttribute('aria-pressed')==='true');
 assert.equal(await page.locator('.hotel-list').getByRole('button',{name:/2. Name not provided/}).getAttribute('aria-pressed'),'true');
 assert.equal(await markerB.getAttribute('aria-pressed'),'true');
 assert(await markerB.evaluate(el=>el===document.activeElement));
 assert.match(await page.locator('.hotel-list').innerText(),/Address not provided/);
 assert(await page.getByRole('link',{name:'OpenStreetMap contributors'}).isVisible());
 assert(await page.getByRole('link',{name:'Powered by Geoapify'}).isVisible());
 await page.locator('#discovery').screenshot({path:'docs/live-hotel-ui-controlled-desktop.png'});
 const callsBeforeSelection=calls.length;
 await page.getByRole('button',{name:'Show search area'}).click();
 await rowA.click(); assert.equal(calls.length,callsBeforeSelection);
 for (const width of [390,320]) {
  await page.setViewportSize({width,height:844});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert(await page.getByRole('link',{name:'OpenStreetMap contributors'}).isVisible());
  await markerB.focus(); await markerB.press('Space');
  await page.waitForFunction(()=>{const r=document.querySelectorAll('.hotel-list button')[1].getBoundingClientRect();return r.top>=-1 && r.bottom<=innerHeight+1});
  const rect=await page.locator('.hotel-list').getByRole('button',{name:/2. Name not provided/}).boundingBox();
  assert(rect.y>=-1 && rect.y+rect.height<=845);
  assert(await markerB.evaluate(el=>el===document.activeElement));
  if(width===390) await page.locator('#discovery').screenshot({path:'docs/live-hotel-ui-controlled-mobile.png'});
 }
 await page.setViewportSize({width:1280,height:1000});
 scenario='slow'; await zip.fill('02108'); await search.click();
 await page.getByRole('button',{name:'Searching…'}).waitFor();
 assert.equal(await page.locator('.hotel-marker').count(),0);
 await zip.fill('10001');
 await page.waitForTimeout(1200);
 assert.equal(await page.locator('.hotel-marker').count(),0);
 assert.match(await feedback.innerText(),/Enter a ZIP/);
 scenario='empty'; await zip.fill('02108'); await search.click();
 await page.getByText('No nearby hotels were returned', {exact:false}).waitFor();
 assert.equal(await page.locator('.hotel-marker').count(),0);
 assert.equal(await page.locator('.zip-center').count(),1);
 scenario='unresolved'; await search.click(); await page.getByText('could not be located',{exact:false}).waitFor();
 assert.equal(await page.locator('.hotel-map').count(),0);
 scenario='failure'; await search.click(); await page.getByRole('button',{name:'Retry search'}).waitFor();
 assert.match(await feedback.innerText(),/could not be completed/);
 scenario='limited'; await page.getByRole('button',{name:'Retry search'}).click();
 await page.getByText('temporarily limited',{exact:false}).waitFor();
 assert(await page.getByRole('button',{name:'Retry search'}).isDisabled());
 assert(await search.isDisabled());
 await page.waitForTimeout(2200); assert(await search.isEnabled());
 scenario='results'; tileFailure=true;
 await page.reload(); await zip.fill('02108'); await search.click();
 await page.getByText('Map imagery could not fully load.',{exact:false}).waitFor();
 assert(await rowA.isVisible()); assert.equal(await page.locator('.hotel-marker').count(),2);
 await page.locator('#discovery').screenshot({path:'docs/live-hotel-ui-tile-failure.png'});
 // Existing sample routes use the real local backend; no booking mutations.
 await page.locator('#search input').fill('Boston'); await page.locator('#search button').click();
 await page.locator('.table-wrap tbody tr').first().waitFor();
 assert.equal(await page.locator('.table-wrap tbody tr').count(),4);
 await page.locator('#search input').fill('Aspen'); await page.locator('#search button').click();
 await page.getByRole('heading',{name:'No stays matched'}).waitFor();
 assert.deepEqual(errors,[]);
 assert(tileHeaders.length>0 && tileHeaders.every(h=>h.referer?.startsWith('http://127.0.0.1:5173/')));
 assert(calls.every(url=>!url.includes('apiKey') && url.startsWith('http://127.0.0.1:5173/api/')));
 const output={status:'passed', scenarios:['initial','invalid','leading zero','list Space selects marker','marker Enter/Space selects and reveals list without moving focus','selection makes no API call','390px and 320px no overflow','loading clears markers','edited ZIP rejects stale response','empty retains center','unresolved removes map','network failure','rate limit honors Retry-After','tile failure retains results','Boston four rows','Aspen no results'],uncaughtErrors:errors,discoveryRequests:calls.length,tileReferer:'http://127.0.0.1:5173/ (verified on controlled tile requests)',providerCalls:'controlled, no live Geoapify calls'};
 fs.writeFileSync('docs/browser-checks/discovery-results.json',JSON.stringify(output,null,2)+'\n');
 console.log(JSON.stringify(output,null,2));
 } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1});
