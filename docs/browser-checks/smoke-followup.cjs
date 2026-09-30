const {chromium}=require('/Applications/ChatGPT.app/Contents/Resources/cua_node/lib/node_modules/playwright');
const fs=require('node:fs'),assert=require('node:assert/strict');
const prior=JSON.parse(fs.readFileSync('docs/browser-checks/smoke-bookings-results.json'));
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const report={started:new Date().toISOString(),checks:[],console:[],pageErrors:[]};
 try{
 const context=await browser.newContext({viewport:{width:1280,height:1000}});const page=await context.newPage();page.setDefaultTimeout(10000);
 page.on('pageerror',e=>report.pageErrors.push(e.message));
 page.on('console',m=>{if(['error','warning'].includes(m.type())){let u;try{u=new URL(m.location().url)}catch{}report.console.push({type:m.type(),sourceHost:u?.host,sourcePath:u?.pathname,message:m.text().replace(/https?:\/\/\S+/g,'[URL omitted]').slice(0,160)});}});
 await page.goto('http://127.0.0.1:5173/');await page.getByRole('combobox',{name:/Demo traveler/}).selectOption('U006');
 await page.waitForFunction(()=>document.querySelector('#bookings').getAttribute('aria-busy')==='false');
 for(const id of prior.created){assert.equal(await page.locator('#bookings article').filter({hasText:id}).count(),0);}
 report.checks.push({name:'Temporary smoke booking IDs absent; existing traveler bookings preserved',status:'PASS',observed:`${await page.locator('#bookings article').count()} existing U006 records remain; full database baseline checked separately.`});
 await page.locator('#bookings').screenshot({path:'docs/smoke-booking-cleanup.png'});
 const invalid=await context.request.get('http://127.0.0.1:8010/api/discovery/hotels?postcode=2108');assert.equal(invalid.status(),422);report.checks.push({name:'Actual FastAPI invalid input',status:'PASS',observed:'HTTP 422 for 2108'});
 const favicon=await context.request.get('http://127.0.0.1:5173/favicon.ico');report.checks.push({name:'Frontend favicon',status:favicon.status()===200?'PASS':'FAIL',observed:`HTTP ${favicon.status()} for /favicon.ico`});
 // Controlled tile failure, no external hotel or tile calls.
 await page.route('https://tile.openstreetmap.org/**',route=>route.abort());
 await page.route('**/api/discovery/hotels?**',route=>route.fulfill({json:{provider:'geoapify',center:{postcode:'02108',country_code:'us',locality:'Controlled locality',latitude:42.36,longitude:-71.06},radius_meters:5000,hotels:[{place_id:'controlled-tile-case',name:null,address:null,latitude:42.36,longitude:-71.06}],count:1,limit:20,limit_reached:false,omitted_count:0,duplicates_removed:0}}));
 await page.getByLabel('U.S. ZIP code',{exact:true}).fill('02108');await page.getByRole('button',{name:'Search hotels',exact:true}).click();await page.getByText('Map imagery could not fully load.',{exact:false}).waitFor();assert.equal(await page.locator('.hotel-list li').count(),1);assert.equal(await page.locator('.hotel-marker').count(),1);assert.match(await page.locator('.hotel-list').innerText(),/Name not provided/);assert.match(await page.locator('.hotel-list').innerText(),/Address not provided/);
 await page.locator('#discovery').screenshot({path:'docs/smoke-simulated-tile-failure.png'});report.checks.push({name:'Simulated tile failure retains list/marker and honest missing-field labels',status:'PASS'});
 }catch(e){report.fatal=e.message.replace(/https?:\/\/\S+/g,'[URL omitted]').slice(0,500);}
 finally{report.finished=new Date().toISOString();fs.writeFileSync('docs/browser-checks/smoke-followup-results.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));await browser.close();}
})();
