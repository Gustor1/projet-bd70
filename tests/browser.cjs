// Navigateur réel local, données de démonstration ; cookies et sessions jamais exportés.
const path = require('path');
const fs = require('fs');
const {chromium}=require(process.env.BD70_PLAYWRIGHT || 'C:/Users/eliot/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const origin=process.env.BD70_URL||'http://127.0.0.1:8070';
const results=[];
function check(ok,name){results.push({name,ok});console.log(`${ok?'OK':'ECHEC'} ${name}`);}
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(origin);await page.screenshot({path:'livrables/preuves/connexion.png',fullPage:true});
 await page.getByLabel('Email',{exact:true}).first().fill('admin@bd70.test');await page.getByLabel('Mot de passe',{exact:true}).fill('Entrepot2026!');await page.getByRole('button',{name:'Se connecter',exact:true}).click();await page.waitForURL(origin+'/');
 check(await page.getByRole('heading',{name:'Vue d’ensemble'}).isVisible(),'Connexion admin et tableau de bord');
 await page.screenshot({path:'livrables/preuves/tableau-de-bord.png',fullPage:true});
 const routes=[['planning','Quais & rendez-vous'],['visits','Passages camions'],['receipts','Réceptions'],['stock','Stocks & rangement'],['orders','Préparation & expédition'],['trace','Traçabilité des lots'],['reports','Indicateurs & états']];
 for(const [route,title] of routes){const response=await page.goto(`${origin}/?page=${route}`);check(response.status()===200&&await page.getByRole('heading',{name:title,exact:true}).isVisible()&&await page.locator('[role=alert]').count()===0,`Écran ${route}`);await page.screenshot({path:`livrables/preuves/${route}.png`,fullPage:true});}
 await page.goto(`${origin}/?page=trace&lot_id=1`);check(await page.getByText('DEMO-001',{exact:true}).count()>=2,'Traçabilité lot multi-commandes jusqu’au camion');
 for(const table of ['user_account','carrier','carrier_contact','carrier_contract','qualification','driver','driver_qualification','equipment','vehicle','vehicle_equipment','dock','dock_equipment','dock_vehicle_type','dock_downtime','appointment','truck_visit','visit_event','owner','supplier','article','zone','aisle','rack','rack_level','location','lot','supplier_notice','notice_line','receipt','receipt_line','receipt_item','customer_order','order_line','pick','package','package_pick','shipment','stock_movement','audit_log']){
  const response=await page.goto(`${origin}/?page=catalog&t=${table}&new=1`);check(response.status()===200&&await page.locator('[role=alert]').count()===0,`Formulaire/liste ${table}`);
 }
 // CRUD complet dans l'interface avec caractères susceptibles de casser HTML/SQL.
 await page.goto(`${origin}/?page=catalog&t=carrier&new=1`);
 const f=page.locator('form').filter({has:page.locator('input[name="action"][value="save"]')});
 for(const [key,val] of Object.entries({code:'WEB-CRUD',name:`O'Neil <script>alert(1)</script>`,address:'Adresse fictive',phone:'000',email:'web-crud@bd70.test'}))await f.locator(`[name="${key}"]`).fill(val);
 await f.getByRole('button',{name:'Enregistrer',exact:true}).click();check(await page.getByRole('status').isVisible(),'Création formulaire avec apostrophe et HTML échappé');
 await page.locator('form.filters input[name="q"]').fill('WEB-CRUD');await page.getByRole('button',{name:'Afficher',exact:true}).click();
 check(await page.locator('tbody tr').count()===1&&await page.locator('tbody script').count()===0,'Filtre et absence d’exécution HTML');
 await page.getByRole('link',{name:'Modifier',exact:true}).click();await page.locator('details form input[name="name"]').fill('Fiche modifiée par navigateur');await page.getByRole('button',{name:'Enregistrer',exact:true}).click();
 await page.locator('form.filters input[name="q"]').fill('WEB-CRUD');await page.getByRole('button',{name:'Afficher',exact:true}).click();check(await page.getByText('Fiche modifiée par navigateur',{exact:true}).isVisible(),'Modification formulaire');
 page.once('dialog',d=>d.accept());await page.getByRole('button',{name:'Supprimer',exact:true}).click();check(await page.getByRole('status').isVisible(),'Suppression formulaire');
 // CSRF et accès directs, y compris export sans droits.
 let resp=await page.request.post(origin+'/',{form:{action:'adjust',receipt_item_id:'1',location_id:'1',delta:'-1',reason:'Sans CSRF'}});check(resp.status()===403,'HTTP écriture sans CSRF rejetée');
 resp=await page.request.get(`${origin}/?page=export&kind=stock&article_id=1&zone_id=1&q=LOT-A`);const csv=await resp.text();check(resp.status()===200&&csv.includes('LOT-A')&&!csv.includes('LOT-B;'),'CSV respecte les filtres combinés');fs.writeFileSync('livrables/preuves/stock-filtre.csv',csv);
 for(const kind of ['pick','delivery','waybill']){await page.goto(`${origin}/?page=document&id=1&kind=${kind}`);check(await page.locator('[role=alert]').count()===0,`Document ${kind}`);await page.emulateMedia({media:'print'});await page.pdf({path:`livrables/preuves/document-${kind}.pdf`,landscape:true,format:'A4',printBackground:true});await page.emulateMedia({media:'screen'});}
 await page.goto(`${origin}/?page=reports&from=2026-10-22&to=2026-10-22`);await page.emulateMedia({media:'print'});await page.pdf({path:'livrables/preuves/etat-indicateurs.pdf',format:'A4',landscape:true,printBackground:true});await page.emulateMedia({media:'screen'});
 await page.setViewportSize({width:390,height:844});for(const route of ['home','planning','stock','reports']){await page.goto(`${origin}/?page=${route}`);check(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),`Largeur mobile ${route}`);await page.screenshot({path:`livrables/preuves/mobile-${route}.png`,fullPage:true});}
 for(const role of ['manager','gate','warehouse']){
  const ctx=await browser.newContext();const p=await ctx.newPage();await p.goto(origin);await p.getByLabel('Email',{exact:true}).first().fill(`${role}@bd70.test`);await p.getByLabel('Mot de passe',{exact:true}).fill('Entrepot2026!');await p.getByRole('button',{name:'Se connecter',exact:true}).click();await p.waitForURL(origin+'/');
  check((await p.request.get(`${origin}/?page=catalog&t=user_account`)).status()===403,`HTTP ${role} interdit comptes par URL`);
  const csrf=await p.locator('input[name="csrf"]').first().inputValue();const response=await p.request.post(origin+'/',{form:{csrf,action:'save',table:'user_account',name:'Élévation',email:'attack@bd70.test',role:'admin',active:'1',password:'Interdit2026!'}});check(response.status()===403,`HTTP ${role} interdit écriture comptes`);
  if(role!=='manager')check((await p.request.get(`${origin}/?page=export&kind=stock`)).status()===403,`HTTP ${role} export protégé`);
  await ctx.close();
 }
 const ctx=await browser.newContext();const p=await ctx.newPage();await p.goto(origin);await p.getByText('Créer un compte',{exact:true}).click();const rf=p.locator('form').filter({has:p.locator('input[value="register"]')});await rf.getByLabel('Nom complet').fill('Compte navigateur');await rf.getByLabel('Email',{exact:true}).fill(`browser-${Date.now()}@bd70.test`);await rf.getByLabel('Mot de passe (10 à 72 caractères)').fill('Inscription2026!');await rf.getByRole('button',{name:'Demander un accès'}).click();check((await p.getByRole('status').textContent()).includes('attente'),'Inscription depuis formulaire en attente');await ctx.close();
 const http={};for(const route of ['planning','stock','reports']){await page.request.get(`${origin}/?page=${route}`);const raw=[];for(let i=0;i<10;i++){const t=performance.now();const response=await page.request.get(`${origin}/?page=${route}`);await response.body();raw.push(performance.now()-t);}const sorted=[...raw].sort((a,b)=>a-b);http[route]={raw_ms:raw,median_ms:(sorted[4]+sorted[5])/2,min_ms:sorted[0],max_ms:sorted[9],dataset:'démonstration, compte admin',includes:'HTTP local, rendu PHP et transfert de la réponse ; sans téléchargement des ressources'};}fs.writeFileSync('livrables/preuves/http.json',JSON.stringify(http,null,2));
 check(errors.length===0,'Aucune erreur JavaScript');await browser.close();
 const report={date:new Date().toISOString(),passed:results.filter(x=>x.ok).length,failed:results.filter(x=>!x.ok).length,results,errors};fs.writeFileSync('livrables/preuves/navigateur.json',JSON.stringify(report,null,2));console.log(`${report.passed} réussis, ${report.failed} échecs`);process.exitCode=report.failed?1:0;
})().catch(e=>{console.error(e);process.exit(1)});
