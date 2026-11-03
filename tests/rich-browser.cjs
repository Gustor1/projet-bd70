// Lecture uniquement : base riche finale, aucune mutation métier.
const fs=require('fs');
const {chromium}=require(process.env.BD70_PLAYWRIGHT||'C:/Users/eliot/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const origin=process.env.BD70_URL||'http://127.0.0.1:8070';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});const results=[];const errors=[];
 try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});page.on('pageerror',e=>errors.push(e.message));
 await page.goto(origin);await page.getByLabel('Email',{exact:true}).first().fill('admin@bd70.test');await page.getByLabel('Mot de passe',{exact:true}).fill('Entrepot2026!');await page.getByRole('button',{name:'Se connecter',exact:true}).click();await page.waitForURL(origin+'/');
 const routes={home:'',planning:'page=planning&day=2026-10-28',reports:'page=reports&from=2026-09-29&to=2026-10-28',notices:'page=notices',receipts:'page=receipts&from=2026-07-30&to=2026-10-28',receipt:'page=receipt_detail&id=901',orders:'page=orders',order:'page=order_detail&id=902',stock:'page=stock',trace:'page=trace&lot_id=1',search:'page=trace&ref_search=LOT',pagination:'page=receipts&draft_p=2'};
 for(const [key,query] of Object.entries(routes)){
  const start=performance.now();const r=await page.goto(origin+'/?'+query);const ok=r.status()===200&&await page.getByRole('alert').count()===0;
  results.push({name:key,ok,status:r.status(),load_ms:Math.round(performance.now()-start)});if(!ok)throw new Error(key+' : '+await page.getByRole('alert').allTextContents());
  if(['reports','notices','stock','order','trace'].includes(key))await page.screenshot({path:`livrables/preuves/riche-${key}.png`,fullPage:true});
 }
 await page.setViewportSize({width:390,height:844});
 for(const [key,query] of Object.entries(routes).filter(([key])=>['receipt','order','notices'].includes(key))){await page.goto(origin+'/?'+query);const ok=await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1);results.push({name:'mobile '+key,ok});}
 results.push({name:'aucune erreur JavaScript',ok:errors.length===0});
 const report={date:new Date().toISOString(),database:'bd70_demo_rich_final',read_only:true,passed:results.filter(x=>x.ok).length,failed:results.filter(x=>!x.ok).length,results,errors};fs.writeFileSync('livrables/preuves/navigateur-riche.json',JSON.stringify(report,null,2));if(report.failed)throw new Error('Contrôle riche échoué');console.log(`${report.passed} contrôles sur la démonstration riche réussis.`);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
