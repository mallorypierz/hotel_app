// Controlled discovery responses + a REAL backend using a temporary database.
// Set LOCAL_TEST_BACKEND to an isolated instance; never point it at the user's DB.
const { chromium } = require(process.env.PLAYWRIGHT_RUNTIME || '/Applications/ChatGPT.app/Contents/Resources/cua_node/lib/node_modules/playwright');
const assert = require('node:assert/strict');
const backend = process.env.LOCAL_TEST_BACKEND;
if (!backend) throw new Error('LOCAL_TEST_BACKEND must name an isolated temporary-database server');
(async () => {
 const browser = await chromium.launch({headless:true, channel:'chrome'});
 try {
 const page = await browser.newPage({viewport:{width:1280,height:1000}});
 await page.request.delete(backend+'/api/local-hotels?hotel_id=browser-test-A');
 await page.request.delete(backend+'/api/local-hotels?hotel_id=browser-test-B');
 const errors=[]; page.on('pageerror',e=>errors.push(e.message));
 let calls=0, failRead=false, failSave=false, failRemove=false, delaySave=false;
 const center={postcode:'02108',country_code:'us',locality:'Boston',latitude:42.36,longitude:-71.06};
 const hotels=[{place_id:'browser-test-A',name:'Controlled hotel A',address:null,latitude:42.361,longitude:-71.061},
 {place_id:'browser-test-B',name:null,address:null,latitude:42.38,longitude:-71.08}];
 await page.route('**/api/local-hotels**',async route=>{
  const method=route.request().method();
  if ((method==='GET'&&failRead)||(method==='POST'&&failSave)||(method==='DELETE'&&failRemove)) {
   return route.fulfill({status:503,json:{detail:'Controlled failure'}});
  }
  if(method==='POST'&&delaySave) await new Promise(r=>setTimeout(r,500));
  const url=new URL(route.request().url());
  const response=await route.fetch({url:backend+url.pathname+url.search});
  await route.fulfill({response});
 });
 await page.route('**/api/discovery/hotels?**',route=>{
  calls++; const postcode=new URL(route.request().url()).searchParams.get('postcode');
  return route.fulfill({json:{center:{...center,postcode},hotels,count:2,radius_meters:5000,
   provider:'geoapify',limit:20,limit_reached:false,omitted_count:0,duplicates_removed:0}});
 });
 await page.route('https://tile.openstreetmap.org/**',route=>route.fulfill({contentType:'image/png',body:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=','base64')}));
 async function search(zip='02108') {
  await page.getByLabel('U.S. ZIP code',{exact:true}).fill(zip);
  await page.getByRole('button',{name:'Search hotels',exact:true}).click();
 }
 await page.goto('http://localhost:5173/');
 failRead=true; await search();
 await page.getByText('Saved hotels could not be checked.',{exact:false}).waitFor();
 assert.equal(calls,0);
 failRead=false; await search();
 await page.getByRole('heading',{name:'API results',exact:true}).waitFor();
 assert.equal(calls,1);
 const first=page.locator('.hotel-list > ol > li').first();
 assert.equal(await page.getByRole('button',{name:'Remove from Local',exact:true}).count(),0);
 failSave=true; await first.getByRole('button',{name:'Add to Local',exact:true}).click();
 await page.getByText('Save could not be confirmed.',{exact:false}).waitFor();
 assert(await first.getByRole('button',{name:'Add to Local',exact:true}).isEnabled());
 failSave=false; delaySave=true;
 await first.getByRole('button',{name:'Add to Local',exact:true}).click();
 assert(await first.getByRole('button',{name:'Saving…',exact:true}).isDisabled());
 await first.getByRole('button',{name:'Remove from Local',exact:true}).waitFor();
 assert(await first.getByRole('button',{name:'Saved locally',exact:true}).isDisabled());
 await first.getByRole('button',{name:/1. Controlled hotel A/}).click();
 assert.equal(await page.locator('.hotel-marker').first().getAttribute('aria-pressed'),'true');
 await page.locator('.hotel-marker').nth(1).press('Enter');
 assert.equal(await page.locator('.hotel-list').getByRole('button',{name:/2. Name not provided/}).getAttribute('aria-pressed'),'true');
 await page.reload(); await search();
 await page.getByRole('heading',{name:'Saved locally',exact:true}).waitFor();
 assert.equal(calls,1); assert.equal(await page.locator('.hotel-marker').count(),1);
 assert.match(await first.innerText(),/Simulated classroom data/);
 for(let d=10;d<=14;d++) assert.match(await first.innerText(),new RegExp(`2026-10-${d} · \\$100.00/night · 20 rooms`));
 assert.match(await page.locator('.discovery-summary').innerText(),/not a complete list/);
 // A different ZIP returns the API hotel but gets saved status by provider ID.
 await search('02109'); await page.getByRole('heading',{name:'API results',exact:true}).waitFor();
 assert.equal(calls,2); assert(await first.getByRole('button',{name:'Saved locally',exact:true}).isDisabled());
 await search(); await page.getByRole('heading',{name:'Saved locally',exact:true}).waitFor();
 failRemove=true; await first.getByRole('button',{name:'Remove from Local',exact:true}).click();
 await page.getByText('Removal could not be confirmed.',{exact:false}).waitFor();
 assert.equal(await page.locator('.hotel-marker').count(),1);
 assert(await first.getByRole('button',{name:'Saved locally',exact:true}).isDisabled());
 failRemove=false; await first.getByRole('button',{name:'Remove from Local',exact:true}).click();
 await page.getByText('No saved hotels remain for this ZIP.',{exact:false}).waitFor();
 assert.equal(await page.locator('.hotel-marker').count(),0); assert.equal(calls,2);
 await page.reload(); await search();
 await page.getByRole('heading',{name:'API results',exact:true}).waitFor();
 assert.equal(calls,3); assert(await first.getByRole('button',{name:'Add to Local',exact:true}).isEnabled());
 await page.setViewportSize({width:390,height:844});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.getByRole('searchbox').fill('Boston'); await page.getByRole('button',{name:'Search',exact:true}).click();
 await page.getByRole('heading',{name:'4 places to consider'}).waitFor();
 await page.getByRole('searchbox').fill('Aspen'); await page.getByRole('button',{name:'Search',exact:true}).click();
 await page.getByRole('heading',{name:'No stays matched'}).waitFor();
 assert.deepEqual(errors,[]);
 console.log('PASS: local-first, read failure blocks API, save pending/failure/success, exact saved status across ZIPs, refresh persistence, 5 demo nights, map/list selection, removal failure/success, empty-local fallback, mobile, Boston/Aspen; no page errors.');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
