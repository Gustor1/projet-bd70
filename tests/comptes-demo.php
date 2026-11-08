<?php
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';
$db=new Database();$name=(string)$db->scalar('SELECT DATABASE()');
if(!preg_match('/^bd70_test[a-z0-9_]*$/',$name))throw new RuntimeException('Base de test dédiée requise.');
$results=[];
function check(bool $ok,string $label):void{global $results;$results[]=['name'=>$label,'ok'=>$ok];}
function prepareAccounts(array $args=[]):void{
 $process=proc_open([PHP_BINARY,__DIR__.'/../scripts/comptes-demo.php',...$args],[0=>['pipe','r'],1=>['pipe','w'],2=>['pipe','w']],$pipes,dirname(__DIR__));fclose($pipes[0]);$output=stream_get_contents($pipes[1]);$error=stream_get_contents($pipes[2]);fclose($pipes[1]);fclose($pipes[2]);if(proc_close($process)!==0)throw new RuntimeException('Préparation des comptes échouée : '.$error);
}
function snapshot():array{global $db;$out=[];foreach($db->all('SHOW FULL TABLES WHERE Table_type="BASE TABLE"') as $r){$table=array_values($r)[0];$out[$table]=$db->all('CHECKSUM TABLE `'.$table.'`');}return $out;}
$expected=['admin'=>['admin',1],'admin2'=>['admin',1],'manager'=>['manager',1],'pilotage'=>['manager',1],'gate'=>['gate',1],'gate2'=>['gate',1],'warehouse'=>['warehouse',1],'warehouse2'=>['warehouse',1],'warehouse3'=>['warehouse',1],'carrier1'=>['carrier',1],'carrier2'=>['carrier',1],'pending'=>['pending',0],'inactive'=>['warehouse',0]];
$carriers=array_column($db->all('SELECT id FROM carrier ORDER BY id LIMIT 2'),'id');
foreach($expected as $local=>[$role,$active]){
 $u=$db->one('SELECT * FROM user_account WHERE email=?',[$local.'@bd70.test']);
 check($u['role']===$role&&(int)$u['active']===$active&&password_verify('Entrepot2026!',$u['password_hash']),'Compte '.$local.' conforme après import');
 $carrier=match($local){'carrier1'=>$carriers[0],'carrier2'=>$carriers[1],default=>null};check($u['carrier_id']==$carrier,'Rattachement '.$local);
}
$before=snapshot();prepareAccounts();check($before===snapshot(),'Deuxième passage sans écriture dans les 41 tables');
$admin=(int)$db->scalar("SELECT id FROM user_account WHERE email='admin@bd70.test'");$id=(int)$db->scalar("SELECT id FROM user_account WHERE email='warehouse2@bd70.test'");
$extra=$db->transaction($admin,fn()=>$db->insert('user_account',['email'=>'personnel-preserve@bd70.test','name'=>'Compte à préserver','role'=>'gate','active'=>1,'password_hash'=>password_hash('AutreMotDePasse2026!',PASSWORD_DEFAULT)]));
$other=$db->one('SELECT * FROM user_account WHERE id=?',[$extra]);
$db->transaction($admin,fn()=>$db->run('UPDATE user_account SET active=0 WHERE id=?',[$id]));
prepareAccounts();check(!(bool)$db->scalar('SELECT active FROM user_account WHERE id=?',[$id]),'Configuration modifiée conservée sans option');
prepareAccounts(['--reinitialiser']);$u=$db->one('SELECT * FROM user_account WHERE id=?',[$id]);check($u['active']&&password_verify('Entrepot2026!',$u['password_hash']),'Réinitialisation explicite conserve identifiant et rétablit accès');
check($other===$db->one('SELECT * FROM user_account WHERE id=?',[$extra]),'Compte hors liste préservé');
$businessBefore=$before;unset($businessBefore['user_account'],$businessBefore['audit_log']);$after=snapshot();unset($after['user_account'],$after['audit_log']);check($businessBefore===$after,'Données métier inchangées après création et rétablissement de comptes');
$failed=count(array_filter($results,fn($r)=>!$r['ok']));$out=['database'=>$name,'passed'=>count($results)-$failed,'failed'=>$failed,'results'=>$results];
$path=__DIR__.'/../docs/preuves/comptes-2026-11-04';if(!is_dir($path))mkdir($path,0777,true);file_put_contents($path.'/comptes.json',json_encode($out,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));echo $out['passed']." contrôles réussis, $failed échecs\n";exit($failed?1:0);
