const {chromium}=require('/Applications/ChatGPT.app/Contents/Resources/cua_node/lib/node_modules/playwright');
const assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const report={started:new Date().toISOString(),created:[],console:[],failedRequests:[],apiErrors:[],pageErrors:[]};
 const save=()=>fs.writeFileSync('docs/browser-checks/smoke-bookings-results.json',JSON.stringify(report,null,2)+'\n');
 try{
  const page=await browser.newPage({viewport:{width:1280,height:1000}});page.setDefaultTimeout(10000);
  page.on('console',m=>{if(['warning','error'].includes(m.type())){let u;try{u=new URL(m.location().url)}catch{}report.console.push({type:m.type(),message:m.text().replace(/https?:\/\/\S+/g,'[URL omitted]').slice(0,300),sourceHost:u?.host,sourcePath:u?.pathname});}});
  page.on('requestfailed',r=>{const u=new URL(r.url());report.failedRequests.push({host:u.host,path:u.pathname,failure:r.failure()?.errorText});});
  page.on('pageerror',e=>report.pageErrors.push(e.message));
  page.on('response',r=>{const u=new URL(r.url());if(u.pathname.startsWith('/api/')&&r.status()>=400)report.apiErrors.push({path:u.pathname,status:r.status()});});
  await page.goto('http://127.0.0.1:5173/');await page.waitForTimeout(1500);
  report.travelerAccessibility=await page.locator('#bookings select').ariaSnapshot();
  await page.getByRole('combobox',{name:/Demo traveler/}).selectOption('U006');await page.waitForFunction(()=>document.querySelector('#bookings').getAttribute('aria-busy')==='false');
  await page.locator('#search input').fill('Trail');await page.locator('#search button').click();await page.getByRole('button',{name:'Select stay',exact:true}).click();await page.getByRole('heading',{name:'Review your stay'}).waitFor();assert.match(await page.locator('#bookings form').innerText(),/Valley Trail Inn/);
  let waiting=page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname==='/api/bookings');await page.getByRole('button',{name:'Confirm simulated booking'}).click();let response=await waiting;assert.equal(response.status(),201);const a=(await response.json()).booking_id;report.created.push(a);save();
  let card=page.locator('#bookings article').filter({hasText:a});await card.waitFor();assert.match(await card.innerText(),/confirmed/);assert.match(await page.locator('#bookings .notice').innerText(),/simulated reservation/);await page.locator('#bookings').screenshot({path:'docs/smoke-booking-created.png'});
  await card.getByRole('button',{name:'Cancel booking',exact:true}).click();await page.getByRole('heading',{name:'Cancel this booking?'}).waitFor();await page.getByRole('button',{name:'Confirm cancellation'}).click();await page.waitForFunction(id=>[...document.querySelectorAll('#bookings article')].find(el=>el.innerText.includes(id))?.innerText.includes('cancelled'),a);
  await page.getByRole('button',{name:'Select stay',exact:true}).click();waiting=page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname==='/api/bookings');await page.getByRole('button',{name:'Confirm simulated booking'}).click();response=await waiting;assert.equal(response.status(),201);const b=(await response.json()).booking_id;report.created.push(b);save();assert.notEqual(a,b);
  card=page.locator('#bookings article').filter({hasText:b});await card.waitFor();await card.getByRole('button',{name:'Delete test booking'}).click();await page.getByRole('heading',{name:'Delete this test booking?'}).waitFor();await page.getByRole('button',{name:'Keep booking'}).click();assert(await card.isVisible());await card.getByRole('button',{name:'Delete test booking'}).click();waiting=page.waitForResponse(r=>r.request().method()==='DELETE'&&r.url().endsWith(b));await page.getByRole('button',{name:'Confirm deletion'}).click();assert.equal((await waiting).status(),204);await card.waitFor({state:'detached'});
  await page.reload();card=page.locator('#bookings article').filter({hasText:a});await card.waitFor();assert.match(await card.innerText(),/cancelled/);assert.equal(await page.locator('#bookings article').filter({hasText:b}).count(),0);assert.equal(await page.getByRole('combobox',{name:/Demo traveler/}).inputValue(),'U006');await page.locator('#bookings').screenshot({path:'docs/smoke-booking-refreshed.png'});
  report.status='PASS';report.retainedForRestart=a;report.deleted=b;
 }catch(e){report.status='FAIL';report.error=e.message.replace(/https?:\/\/\S+/g,'[URL omitted]').slice(0,500);}
 finally{report.finished=new Date().toISOString();save();console.log(JSON.stringify(report,null,2));await browser.close();}
})();
