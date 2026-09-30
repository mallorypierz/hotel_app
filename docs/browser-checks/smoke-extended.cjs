// Verification only. Two live searches, then intercepted controlled API responses.
const {chromium}=require(process.env.PLAYWRIGHT_RUNTIME || '/Applications/ChatGPT.app/Contents/Resources/cua_node/lib/node_modules/playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const cases=JSON.parse(fs.readFileSync('docs/browser-checks/smoke-provider-results.json'));
const report={started:new Date().toISOString(),checks:[],live:[],createdBookingIds:[],console:[],pageErrors:[],httpErrors:[],credentialFlags:0,directGeoapifyRequests:0};
const save=()=>fs.writeFileSync('docs/browser-checks/smoke-extended-results.json',JSON.stringify(report,null,2)+'\n');
const check=async(name,mode,fn)=>{try{const observed=await fn();report.checks.push({name,mode,status:'PASS',observed:observed||'As expected'});}catch(e){report.checks.push({name,mode,status:'FAIL',observed:e.message.replace(/https?:\/\/\S+/g,'[URL omitted]').slice(0,450)});}save();};
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try{
 const context=await browser.newContext({viewport:{width:1280,height:1000}});
 const page=await context.newPage(); page.setDefaultTimeout(10000);
 let phase='live',apiRequests=0;
 const tiles=[];
 page.on('console',m=>{if(['error','warning'].includes(m.type()))report.console.push({phase,type:m.type(),resourceError:/Failed to load resource|net::ERR_/.test(m.text()),credentialFlag:/apiKey[=:]|GEOAPIFY_API_KEY/.test(m.text())});});
 page.on('pageerror',e=>report.pageErrors.push({phase,message:e.message.replace(/https?:\/\/\S+/g,'[URL omitted]').slice(0,200)}));
 page.on('request',r=>{const u=new URL(r.url());if(u.host==='api.geoapify.com')report.directGeoapifyRequests++;if(/api[_-]?key|access_token/i.test(u.search))report.credentialFlags++;if(u.pathname==='/api/discovery/hotels')apiRequests++;});
 page.on('response',async r=>{const u=new URL(r.url());if(r.status()>=400)report.httpErrors.push({phase,host:u.host,path:u.pathname,status:r.status()});if(u.host==='tile.openstreetmap.org')tiles.push({phase,status:r.status(),referer:(await r.request().allHeaders()).referer});});
 await page.goto('http://127.0.0.1:5173/');
 await check('Healthy services and initial discovery','live',async()=>{assert.equal((await context.request.get('http://127.0.0.1:8010/api/health')).status(),200);assert.equal(apiRequests,0);assert.match(await page.locator('#discovery-feedback').innerText(),/Enter a ZIP/);});
 const input=page.getByLabel('U.S. ZIP code',{exact:true});
 const search=page.getByRole('button',{name:'Search hotels',exact:true});
 let lastBody;
 for(const zip of ['16802','02108']){
  await check(`Live ZIP ${zip}: center, API/list/marker correspondence, selection`,'live',async()=>{
   await input.fill(zip);const waiting=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/discovery/hotels',{timeout:30000});
   await input.press('Enter');const response=await waiting;const body=await response.json();
   report.live.push({zip,observed:new Date().toISOString(),status:response.status(),center:body.center,count:body.count,limitReached:body.limit_reached,omitted:body.omitted_count,duplicates:body.duplicates_removed}); save();
   assert.equal(response.status(),200); assert.equal(body.center.postcode,zip);assert.equal(body.center.country_code,'us');assert.equal(await input.inputValue(),zip);
   assert.equal(body.radius_meters,5000);assert.equal(new Set(body.hotels.map(h=>h.place_id)).size,body.count);
   await page.locator('.hotel-map').waitFor();
   assert.equal(await page.locator('.hotel-list li').count(),body.count);assert.equal(await page.locator('.hotel-marker').count(),body.count);
   for(let i=0;i<body.count;i++){const h=body.hotels[i],row=page.locator('.hotel-list button').nth(i);assert((await row.innerText()).includes(h.name||'Name not provided'));assert((await row.innerText()).includes(h.address||'Address not provided'));assert.equal(await page.locator('.hotel-marker').nth(i).getAttribute('aria-label'),`${i+1}. ${h.name||'Name not provided'} — select hotel`);}
   assert.match(await page.locator('.discovery-summary').innerText(),/not a complete hotel inventory/);
   const callsBefore=apiRequests;
   if(body.count){await page.locator('.hotel-list button').first().click();await page.waitForFunction(()=>document.querySelector('.hotel-marker').getAttribute('aria-pressed')==='true');
    const index=body.count-1;const marker=page.locator('.hotel-marker').nth(index);await marker.focus();await marker.press('Enter');
    await page.waitForFunction(i=>document.querySelectorAll('.hotel-list button')[i].getAttribute('aria-pressed')==='true',index);
    assert(await marker.evaluate(el=>el===document.activeElement));
   }
   assert.equal(apiRequests,callsBefore);
   assert(await page.getByRole('link',{name:'OpenStreetMap contributors'}).isVisible());assert(await page.getByRole('link',{name:'Powered by Geoapify'}).isVisible());
   await page.locator('.hotel-map').scrollIntoViewIfNeeded();await page.screenshot({path:`docs/smoke-live-${zip}.png`});
   lastBody=body;
   return `HTTP 200; exact US ZIP; ${body.count} API records/list rows/markers; selection matched.`;
  });
 }
 await check('Live narrow layout and attribution at 390 / 320 CSS pixels','live',async()=>{
  for(const width of [390,320]){await page.setViewportSize({width,height:844});await page.locator('.hotel-map').scrollIntoViewIfNeeded();assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert(await page.getByRole('link',{name:'OpenStreetMap contributors'}).isVisible());}
  await page.screenshot({path:'docs/smoke-live-320.png'});return 'No document overflow; attribution visible at both widths.';
 });
 await check('Live console, HTTP, tiles and credential checks','live',async()=>{
  assert.equal(report.pageErrors.length,0);assert.equal(report.credentialFlags,0);assert.equal(report.directGeoapifyRequests,0);
  assert.equal(report.httpErrors.filter(e=>e.phase==='live'&&e.path.startsWith('/api/')).length,0);
  assert(tiles.some(t=>t.phase==='live'&&t.status===200));assert(tiles.filter(t=>t.phase==='live').every(t=>t.referer?.startsWith('http://127.0.0.1:5173/')));
  assert.equal(report.console.filter(c=>c.phase==='live').length,0);
  return `${tiles.length} successful/observed tile responses; normal localhost Referer; no direct provider API or credential parameters.`;
 });
 // Simulated checks use actual offline-controller responses for error mapping.
 phase='simulated';await page.setViewportSize({width:1280,height:1000});
 let scenario='empty';let discoveryCalls=0;
 const fixture={...(lastBody||{}),provider:'geoapify',center:{postcode:'02108',country_code:'us',locality:'Controlled locality',latitude:42.36,longitude:-71.06},radius_meters:5000,hotels:[{place_id:'test-a',name:'Controlled hotel',address:'Controlled address A',latitude:42.36,longitude:-71.06},{place_id:'test-b',name:'Controlled hotel',address:null,latitude:42.385,longitude:-71.08}],count:2,limit:20,limit_reached:false,omitted_count:0,duplicates_removed:0};
 await page.route('https://tile.openstreetmap.org/**',route=>route.fulfill({contentType:'image/png',body:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=','base64')}));
 await page.route('**/api/discovery/hotels?**',async route=>{discoveryCalls++;if(scenario==='slow'){await new Promise(r=>setTimeout(r,1200));return route.fulfill({json:fixture}).catch(()=>{});}if(scenario==='results')return route.fulfill({json:fixture});const c=cases[scenario];await route.fulfill({status:c.status,headers:c.headers,json:c.body});});
 await check('Invalid input blocks provider requests','simulated',async()=>{const before=discoveryCalls;await input.fill('2108');await search.click();assert.match(await page.locator('#discovery-feedback').innerText(),/five-digit/);assert.equal(await input.getAttribute('aria-invalid'),'true');assert.equal(discoveryCalls,before);await page.locator('#discovery').screenshot({path:'docs/smoke-simulated-invalid.png'});});
 for(const name of Object.keys(cases)){
  await check(`Controlled ${name}`,'simulated',async()=>{
   scenario=name;await input.fill('02108');await search.click();
   if(cases[name].status===404){await page.getByText('could not be located',{exact:false}).waitFor();assert.equal(await page.locator('.hotel-map').count(),0);assert.equal(cases[name].calls.places,0);}
   else if(name==='empty'){await page.getByText('No nearby hotels were returned',{exact:false}).waitFor();assert.equal(await page.locator('.hotel-marker').count(),0);assert.equal(await page.locator('.zip-center').count(),1);}
   else {await page.getByRole('button',{name:'Retry search'}).waitFor();assert.equal(await page.locator('.hotel-map').count(),0);assert(!/No nearby hotels/.test(await page.locator('#discovery-feedback').innerText()));if(cases[name].status===503){assert(await search.isDisabled());assert(await page.getByRole('button',{name:'Retry search'}).isDisabled());await page.waitForTimeout(2200);assert(await search.isEnabled());}}
   await page.locator('#discovery').screenshot({path:`docs/smoke-simulated-${name}.png`});return `Controller returned ${cases[name].status}; Vue displayed matching state; no live provider call.`;
  });
 }
 await check('Loading, repeated submit guard, old marker clearing and stale response','simulated',async()=>{
  scenario='results';await input.fill('02108');await search.click();await page.locator('.hotel-list li').first().waitFor();
  scenario='slow';await search.click();await page.getByRole('button',{name:'Searching…'}).waitFor();assert(await page.getByRole('button',{name:'Searching…'}).isDisabled());assert.equal(await page.locator('.hotel-marker').count(),0);
  await page.locator('#discovery').screenshot({path:'docs/smoke-simulated-loading.png'});await input.fill('16802');await page.waitForTimeout(1400);assert.equal(await page.locator('.hotel-marker').count(),0);assert.match(await page.locator('#discovery-feedback').innerText(),/Enter a ZIP/);
 });
 await check('Shared ID selection with same-name hotels; Tab, Space, Enter and pointer','simulated',async()=>{
  scenario='results';await input.fill('02108');await input.press('Tab');assert(await search.evaluate(el=>el===document.activeElement));await search.press('Enter');await page.locator('.hotel-marker').nth(1).waitFor();
  const row=page.locator('.hotel-list button').first();await row.focus();await row.press('Space');await page.waitForFunction(()=>document.querySelector('.hotel-marker').getAttribute('aria-pressed')==='true');
  const other=page.locator('.hotel-marker').nth(1);await other.click();await page.waitForFunction(()=>document.querySelectorAll('.hotel-list button')[1].getAttribute('aria-pressed')==='true');
  assert.equal(await row.getAttribute('aria-pressed'),'false');await page.setViewportSize({width:390,height:844});await other.focus();await other.press('Space');await page.waitForFunction(()=>{let r=document.querySelectorAll('.hotel-list button')[1].getBoundingClientRect();return r.top>=-1&&r.bottom<=innerHeight+1});assert(await other.evaluate(el=>el===document.activeElement));
  await page.locator('#discovery').screenshot({path:'docs/smoke-simulated-selection-mobile.png'});await page.setViewportSize({width:1280,height:1000});
 });
 phase='sample';
 await check('Boston sample joined rows and labels','real local sample API',async()=>{await page.locator('#search input').fill('Boston');await page.locator('#search button').click();await page.locator('.table-wrap tbody tr').first().waitFor();assert.equal(await page.locator('.table-wrap tbody tr').count(),4);assert.deepEqual(await page.locator('.table-wrap thead th').allTextContents(),[' Hotel ',' City ',' State ',' Nightly rate ',' Trip ',' Check in ',' Check out ',' Book a stay ']);await page.locator('.table-wrap').screenshot({path:'docs/smoke-sample-boston.png'});});
 await check('Aspen no-results feedback','real local sample API',async()=>{await page.locator('#search input').fill('Aspen');await page.locator('#search button').click();await page.getByRole('heading',{name:'No stays matched'}).waitFor();await page.locator('.results').screenshot({path:'docs/smoke-sample-aspen.png'});});
 await check('Sample booking review, creation, history, cancellation, delete confirmation and refresh','real local sample API',async()=>{
  await page.getByLabel('Demo traveler',{exact:true}).selectOption('U006');await page.waitForFunction(()=>document.querySelector('#bookings').getAttribute('aria-busy')==='false');
  await page.locator('#search input').fill('Trail');await page.locator('#search button').click();await page.getByRole('button',{name:'Select stay',exact:true}).click();await page.getByRole('heading',{name:'Review your stay'}).waitFor();
  assert.match(await page.locator('#bookings form').innerText(),/Valley Trail Inn/);
  let respPromise=page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname==='/api/bookings');
  await page.getByRole('button',{name:'Confirm simulated booking'}).click();let resp=await respPromise;assert.equal(resp.status(),201);const a=(await resp.json()).booking_id;report.createdBookingIds.push(a);save();
  let card=page.locator('#bookings article').filter({hasText:a});await card.waitFor();assert.match(await card.innerText(),/confirmed/);assert.match(await page.locator('#bookings .notice').innerText(),/simulated reservation/);
  await page.locator('#bookings').screenshot({path:'docs/smoke-booking-created.png'});
  await card.getByRole('button',{name:'Cancel booking',exact:true}).click();await page.getByRole('heading',{name:'Cancel this booking?'}).waitFor();await page.getByRole('button',{name:'Confirm cancellation'}).click();await page.waitForFunction(id=>[...document.querySelectorAll('#bookings article')].find(el=>el.innerText.includes(id))?.innerText.includes('cancelled'),a);
  await page.getByRole('button',{name:'Select stay',exact:true}).click();respPromise=page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname==='/api/bookings');await page.getByRole('button',{name:'Confirm simulated booking'}).click();resp=await respPromise;assert.equal(resp.status(),201);const b=(await resp.json()).booking_id;report.createdBookingIds.push(b);save();assert.notEqual(a,b);
  card=page.locator('#bookings article').filter({hasText:b});await card.waitFor();await card.getByRole('button',{name:'Delete test booking'}).click();await page.getByRole('heading',{name:'Delete this test booking?'}).waitFor();await page.getByRole('button',{name:'Keep booking'}).click();assert(await card.isVisible());await card.getByRole('button',{name:'Delete test booking'}).click();respPromise=page.waitForResponse(r=>r.request().method()==='DELETE'&&r.url().endsWith(b));await page.getByRole('button',{name:'Confirm deletion'}).click();assert.equal((await respPromise).status(),204);await card.waitFor({state:'detached'});
  await page.reload();card=page.locator('#bookings article').filter({hasText:a});await card.waitFor();assert.match(await card.innerText(),/cancelled/);assert.equal(await page.locator('#bookings article').filter({hasText:b}).count(),0);assert.equal(await page.getByLabel('Demo traveler',{exact:true}).inputValue(),'U006');await page.locator('#bookings').screenshot({path:'docs/smoke-booking-refreshed.png'});
  return `Unique IDs ${a}, ${b}; cancelled first retained after refresh; second deleted after confirmation. First retained temporarily for restart check.`;
 });
 report.tiles={observed:tiles.length,statuses:[...new Set(tiles.map(t=>t.status))],liveRefererValid:tiles.filter(t=>t.phase==='live').every(t=>t.referer?.startsWith('http://127.0.0.1:5173/'))};
 report.finished=new Date().toISOString();save();
 console.log(JSON.stringify({checks:report.checks,live:report.live,pageErrors:report.pageErrors,consoleCount:report.console.length,httpErrors:report.httpErrors,credentialFlags:report.credentialFlags,directGeoapifyRequests:report.directGeoapifyRequests,createdBookingIds:report.createdBookingIds},null,2));
 }finally{await browser.close();}
})().catch(e=>{report.fatal=e.message.replace(/https?:\/\/\S+/g,'[URL omitted]');save();console.error(report.fatal);process.exitCode=1});
