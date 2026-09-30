// One live ZIP search, with normal browser tile loading and caching.
const { chromium } = require(process.env.PLAYWRIGHT_RUNTIME || '/Applications/ChatGPT.app/Contents/Resources/cua_node/lib/node_modules/playwright');
const fs = require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try {
  const page=await browser.newPage({viewport:{width:1280,height:1000}});
  const errors=[], requests=[], tiles=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('request',r=>{const u=new URL(r.url());requests.push({host:u.host,path:u.pathname,hasCredentialParameter:/apikey|api_key/i.test(u.search)});});
  page.on('response',async r=>{if(new URL(r.url()).host==='tile.openstreetmap.org') tiles.push({status:r.status(),referer:(await r.request().allHeaders()).referer});});
  await page.goto('http://127.0.0.1:5173/');
  await page.getByLabel('U.S. ZIP code',{exact:true}).fill('02108');
  const responsePromise=page.waitForResponse(r=>r.url().includes('/api/discovery/hotels?'),{timeout:30000});
  await page.getByRole('button',{name:'Search hotels',exact:true}).click();
  const response=await responsePromise;
  const body=await response.json();
  await page.waitForTimeout(2500);
  if(response.ok() && body.hotels.length) {
   await page.locator('.hotel-list button').first().click();
   await page.locator('#discovery').screenshot({path:'docs/live-hotel-ui-live-02108.png'});
  }
  const output={date:new Date().toISOString(),postcode:'02108',status:response.status(),feedback:await page.locator('#discovery-feedback').innerText(),count:body.count??null,limitReached:body.limit_reached??null,omitted:body.omitted_count??null,duplicates:body.duplicates_removed??null,markers:await page.locator('.hotel-marker').count(),tileResponses:tiles.length,tileStatuses:[...new Set(tiles.map(t=>t.status))],tileRefererValid:tiles.length>0&&tiles.every(t=>t.referer?.startsWith('http://127.0.0.1:5173/')),browserGeoapifyApiRequests:requests.filter(r=>r.host==='api.geoapify.com').length,credentialParameters:requests.filter(r=>r.hasCredentialParameter).length,uncaughtErrors:errors};
  fs.writeFileSync('docs/browser-checks/discovery-live-results.json',JSON.stringify(output,null,2)+'\n');
  console.log(JSON.stringify(output,null,2));
 } finally {await browser.close();}
})().catch(e=>{console.error(e.message);process.exitCode=1});
