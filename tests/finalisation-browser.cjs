const fs=require('fs');
const {chromium}=require(process.env.BD70_PLAYWRIGHT);
const origin=process.env.BD70_URL;
if(!origin||!/^http:\/\/127\.0\.0\.1:8071$/.test(origin))throw Error('Serveur de recette dédié requis');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage();const checks=[];const timings={};
 function check(ok,name){checks.push({name,ok});if(!ok)throw Error(name);}
 try{
  await page.goto(origin);await page.getByLabel('Email',{exact:true}).first().fill('admin@bd70.test');await page.getByLabel('Mot de passe',{exact:true}).fill('Entrepot2026!');await page.getByRole('button',{name:'Se connecter',exact:true}).click();await page.waitForURL(origin+'/');
  await page.goto(origin+'/?page=catalog&t=receipt&edit=1');
  check(await page.getByText('Réception validée : corriger par un mouvement motivé.',{exact:true}).count()>0,'Accès direct au formulaire validé expliqué');
  check(await page.locator('details.editor').count()===0,'Formulaire impossible masqué');
  await page.goto(origin+'/?page=catalog&t=carrier');
  const row=page.locator('tbody tr').filter({hasText:'Nord Transit'});
  check(await row.getByRole('link',{name:'Modifier',exact:true}).count()===1,'Fiche utilisée reste modifiable');
  check(await row.getByRole('button',{name:'Supprimer',exact:true}).count()===0,'Suppression référencée masquée');
  await page.goto(origin+'/?page=catalog&t=article&edit=1');
  check(await page.locator('fieldset[disabled] input[name=unit_kg]').count()===1,'Poids historique désactivé dans formulaire');
  check(await page.locator('details.editor input[name=name]').isEnabled(),'Désignation descriptive disponible');
  const csrf=await page.locator('input[name=csrf]').first().inputValue();
  const response=await page.request.post(origin,{form:{csrf,action:'delete',table:'receipt',id:'1'}});
  check(response.status()===422,'POST direct de suppression validée refusé');
  for(const route of ['catalog&t=receipt','catalog&t=carrier','stock','reports']){
   timings[route]=[];
   for(let i=0;i<3;i++){const start=performance.now();await page.goto(origin+'/?page='+route,{waitUntil:'load'});timings[route].push(performance.now()-start);}
  }
  await page.goto(origin+'/?page=reports&from=2099-01-01&to=2099-01-02');
  check(await page.locator('[role=alert]').count()===0,'Rapport sur période vide sans erreur');
  await page.setViewportSize({width:390,height:844});await page.goto(origin+'/?page=catalog&t=receipt');
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Catalogue mobile simulé sans débordement global');
  await page.screenshot({path:'livrables/preuves/finalisation-catalogue-mobile.png',fullPage:true});
 }finally{
  fs.writeFileSync('livrables/preuves/finalisation-navigateur.json',JSON.stringify({executed_at:new Date().toISOString(),checks,timings_ms:timings,measurement:'Navigation Chromium jusqu’à load, ressources incluses ; trois observations ; jeu réduit',passed:checks.filter(x=>x.ok).length,failed:checks.filter(x=>!x.ok).length},null,2));await browser.close();
 }
})().catch(e=>{console.error(e);process.exit(1)});
