"""Copie sans config/secrets/état local, installation neuve et smoke HTTP authentifié."""
from pathlib import Path
import shutil,subprocess,json,os,re,time,urllib.request,urllib.parse,http.cookiejar
project=Path.cwd();copy_name=os.environ.get('BD70_CLEAN_DIR','installation-propre')
if not re.fullmatch(r'[a-z0-9_-]+',copy_name):raise SystemExit('Nom de copie invalide.')
target=project/'.local'/copy_name
if target.exists():raise SystemExit('Copie de vérification existante : ne pas écraser, choisir un nouveau dossier.')
target.mkdir(parents=True)
for folder in ['src','templates','public','sql','scripts','tests'] :shutil.copytree(project/folder,target/folder)
(target/'config').mkdir();shutil.copy2('config/example.php',target/'config/example.php');(target/'.local').mkdir()
php=os.environ.get('BD70_PHP','C:/xampp2/php/php.exe');name=os.environ.get('BD70_CLEAN_DB','bd70_demo_installation_propre')
env=os.environ.copy();env.pop('BD70_DATABASE',None);env.pop('BD70_TEST_DATABASE',None)
subprocess.run([php,'scripts/install.php',name],cwd=target,env=env,check=True)
subprocess.run([php,'scripts/seed.php'],cwd=target,env=env,check=True)
validation='''<?php
require 'src/bootstrap.php';$db=new Database();$cat=new Catalog($db);$checks=[];
foreach(['UPDATE user_account SET active=2 WHERE id=1','UPDATE lot SET blocked=2 WHERE id=1'] as $sql){try{$db->run($sql);$checks[]=false;}catch(PDOException $e){$checks[]=true;}}
$lot=$db->one('SELECT * FROM lot WHERE id=1');$lot['blocked']='2';try{$cat->save('lot',1,$lot,1);$checks[]=false;}catch(DomainException $e){$checks[]=true;}
$driver=$cat->save('driver',null,['carrier_id'=>1,'name'=>'Test fiche inutilisée','phone'=>'000','license_number'=>'TEST-CRUD-LIBRE'],1);
$link=$cat->save('driver_qualification',null,['driver_id'=>$driver,'qualification_id'=>1,'expires_on'=>'2027-12-31'],1);
$cat->save('driver_qualification',$link,['driver_id'=>$driver,'qualification_id'=>1,'expires_on'=>'2028-12-31'],1);$cat->delete('driver_qualification',$link,1);$cat->delete('driver',$driver,1);$checks[]=true;
echo json_encode($checks);
'''
(target/'tests/verification-installation.php').write_text(validation,encoding='utf-8')
checks=json.loads(subprocess.check_output([php,'tests/verification-installation.php'],cwd=target,env=env))
assert all(checks),'Domaines booléens ou CRUD de référence inutilisée non valides'
log=(target/'.local/web.log').open('wb');creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
server=subprocess.Popen([php,'-S','127.0.0.1:8072','-t','public'],cwd=target,env=env,stdout=log,stderr=log,creationflags=creationflags)
try:
 opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
 origin='http://127.0.0.1:8072'
 for _ in range(30):
  try:content=opener.open(origin).read().decode('utf-8');break
  except OSError:time.sleep(.2)
 token=re.search(r'name="csrf" value="([a-f0-9]+)"',content).group(1)
 login=urllib.parse.urlencode({'csrf':token,'action':'login','email':'admin@bd70.test','password':'Entrepot2026!'}).encode()
 content=opener.open(origin+'/',login).read().decode('utf-8');assert 'Vue d’ensemble' in content
 results=[]
 for route in ['planning','visits','receipts','stock','orders','reports','trace&lot_id=1','catalog&t=carrier']:
  res=opener.open(origin+'/?page='+route);body=res.read().decode('utf-8');assert res.status==200 and 'role="alert"' not in body;results.append({'route':route,'ok':True})
 result={'date':time.strftime('%Y-%m-%dT%H:%M:%S'),'database':name,'new_config_generated':True,'isolated_sql_account_generated':True,'boolean_sql_and_server_rejections':checks[:3],'unused_driver_qualification_crud':checks[3],'authenticated_routes':results,'passed':True}
 (project/'livrables/preuves/installation-propre.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Installation propre : configuration neuve, connexion active et huit routes authentifiées réussies.')
finally:server.terminate();server.wait(timeout=10);log.close()
