const fs=require('fs');const {chromium}=require(process.env.BD70_PLAYWRIGHT||'C:/Users/eliot/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const origin=process.env.BD70_URL||'http://127.0.0.1:8070';const results=[];
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});try{
 const page=await browser.newPage();
 for(const local of ['admin','admin2','manager','pilotage','gate','gate2','warehouse','warehouse2','warehouse3','carrier1','carrier2','pending','inactive']){
  await page.context().clearCookies();await page.goto(origin);await page.getByLabel('Email',{exact:true}).first().fill(local+'@bd70.test');await page.getByLabel('Mot de passe',{exact:true}).fill('Entrepot2026!');
  await page.getByRole('button',{name:'Se connecter',exact:true}).click();await page.waitForLoadState('networkidle');
  const refused=['pending','inactive'].includes(local);let ok;
  if(refused)ok=(await page.getByRole('alert').count())>0&&(await page.getByRole('button',{name:'Se connecter',exact:true}).count())===1&&(await page.getByRole('heading',{name:'Vue d’ensemble',exact:true}).count())===0;
  else ok=(await page.getByRole('button',{name:'Déconnexion',exact:true}).count())===1&&(await page.getByRole('alert').count())===0;
  if(ok&&local.startsWith('carrier'))ok=await page.getByRole('heading',{name:'Mes rendez-vous',exact:true}).isVisible();
  if(ok&&local.startsWith('admin'))ok=await page.getByRole('heading',{name:'Administration technique',exact:true}).isVisible();
  results.push({account:local+'@bd70.test',expected:refused?'refus':'connexion',ok});console.log((ok?'OK ':'ECHEC ')+local);
 }
 await page.context().clearCookies();await page.goto(origin+'/?page=reports');await page.getByLabel('Email',{exact:true}).first().fill('manager@bd70.test');await page.getByLabel('Mot de passe',{exact:true}).fill('MotDePasseIncorrect');await page.getByRole('button',{name:'Se connecter',exact:true}).click();await page.waitForLoadState('networkidle');
 const refusedWrong=(await page.getByRole('alert').count())>0&&(await page.getByRole('button',{name:'Se connecter',exact:true}).count())===1&&(await page.getByRole('heading',{name:'Indicateurs & états',exact:true}).count())===0;results.push({account:'manager@bd70.test',expected:'mauvais mot de passe : formulaire sans données métier',ok:refusedWrong});console.log((refusedWrong?'OK ':'ECHEC ')+'mauvais mot de passe');
 const response=await page.request.post(origin+'/?page=stock',{form:{action:'login',email:'manager@bd70.test',password:'Entrepot2026!',csrf:'invalide'}});const body=await response.text();const csrfOk=response.status()===403&&body.includes('Se connecter')&&!body.includes('<h1>Stocks &amp; rangement</h1>');results.push({expected:'CSRF anonyme refusé sans écran métier',ok:csrfOk});console.log((csrfOk?'OK ':'ECHEC ')+'CSRF');
}finally{await browser.close();const failed=results.filter(r=>!r.ok).length;fs.mkdirSync('livrables/preuves/comptes-2026-11-04',{recursive:true});fs.writeFileSync('livrables/preuves/comptes-2026-11-04/navigateur.json',JSON.stringify({origin,passed:results.length-failed,failed,results},null,2));if(failed)process.exitCode=1;}})().catch(e=>{console.error(e);process.exit(1)});
