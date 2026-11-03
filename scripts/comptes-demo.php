<?php
// Comptes fictifs publics pour les essais locaux du groupe, sans remise à zéro métier.
declare(strict_types=1);
if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
require_once __DIR__.'/../src/bootstrap.php';
$config=require __DIR__.'/../config/local.php';
if(!preg_match('/(?:^|;)host=(127\.0\.0\.1|localhost)(?:;|$)/',preg_replace('/^mysql:/','',$config['dsn'])))throw new RuntimeException('Base locale requise.');
$db=new Database($config);$name=(string)$db->scalar('SELECT DATABASE()');
if(!preg_match('/^bd70_(demo|test)[a-z0-9_]*$/',$name))throw new RuntimeException('Base pédagogique bd70_demo* ou bd70_test* requise.');
$carriers=$db->all('SELECT id,code,name FROM carrier ORDER BY id LIMIT 2');
if(count($carriers)<2)throw new RuntimeException('Importer ou générer le jeu fictif avant de préparer les comptes : deux sociétés sont nécessaires.');
$definitions=[
 ['admin','Administration du groupe','admin',1,null],
 ['admin2','Administration secondaire','admin',1,null],
 ['manager','Responsable du groupe','manager',1,null],
 ['pilotage','Responsable secondaire','manager',1,null],
 ['gate','Accueil du groupe','gate',1,null],
 ['gate2','Accueil secondaire','gate',1,null],
 ['warehouse','Préparateur principal','warehouse',1,null],
 ['warehouse2','Préparateur secondaire','warehouse',1,null],
 ['warehouse3','Préparateur supplémentaire','warehouse',1,null],
 ['carrier1','Transporteur société 1','carrier',1,$carriers[0]['id']],
 ['carrier2','Transporteur société 2','carrier',1,$carriers[1]['id']],
 ['pending','Inscription en attente','pending',0,null],
 ['inactive','Compte magasinier désactivé','warehouse',0,null],
];
$reset=in_array('--reinitialiser',$_SERVER['argv']??[],true);$password='Entrepot2026!';$messages=[];
$db->pdo->beginTransaction();
try{
 $lock=$db->run('CALL lock_site()');$lock->closeCursor();
 $admin=$db->scalar("SELECT id FROM user_account WHERE email='admin@bd70.test'");$db->run('SET @actor_id=?',[$admin?:null]);
 foreach($definitions as [$local,$label,$role,$active,$carrier]){
  $email=$local.'@bd70.test';$old=$db->run('SELECT * FROM user_account WHERE email=? FOR UPDATE',[$email])->fetch();
  if(!$old){
   $id=$db->insert('user_account',['email'=>$email,'name'=>$label,'password_hash'=>password_hash($password,PASSWORD_DEFAULT),'role'=>$role,'active'=>$active,'carrier_id'=>$carrier]);
   if($local==='admin')$db->run('SET @actor_id=?',[$id]);$state='créé';
  }else{
   $matches=$old['role']===$role&&(int)$old['active']===$active&&$old['carrier_id']==$carrier&&password_verify($password,$old['password_hash']);
   if(!$matches&&$reset){$db->run('UPDATE user_account SET role=?,active=?,carrier_id=?,password_hash=? WHERE id=?',[$role,$active,$carrier,password_hash($password,PASSWORD_DEFAULT),$old['id']]);$state='rétabli (identifiant conservé)';}
   elseif(!$matches)$state='conservé ; configuration différente (voir --reinitialiser)';
   else $state='déjà conforme';
  }
  $messages[]=$email.' : '.$state;
 }
 $db->pdo->commit();
}catch(Throwable $e){if($db->pdo->inTransaction())$db->pdo->rollBack();throw $e;}
echo 'Comptes pédagogiques dans '.$name."\n".implode("\n",$messages)."\n";
echo 'carrier1 : '.$carriers[0]['code'].' / '.$carriers[0]['name']."\n";
echo 'carrier2 : '.$carriers[1]['code'].' / '.$carriers[1]['name']."\nVoir COMPTES-TEST.md et COMMENT-TESTER.md.\n";
