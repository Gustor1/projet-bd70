<?php
// Recette de sql/09_optimisation.sql : soldes tenus par triggers, fonction stock_disponible, prélèvement expédié figé.
// Base neuve chargée par scripts/seed.php (voir COMMENT-TESTER.md), comme les autres suites.
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';
putenv('BD70_NOW=2026-10-22 12:00:00');
$testName=getenv('BD70_TEST_DATABASE')?:'';if(!preg_match('/^bd70_test[a-z0-9_]+$/',$testName))die('Base de test requise.');putenv('BD70_DATABASE='.$testName);
$db=new Database();$ids=json_decode(file_get_contents(__DIR__.'/../.local/seed-'.$testName.'.json'),true);
$w=new Warehouse($db,$ids['admin'],'2026-10-22 12:00:00');$passed=[];$failures=[];
function check(bool $ok,string $name): void {global $passed,$failures;if($ok){$passed[]=$name;echo "OK $name\n";}else{$failures[]=$name;echo "ECHEC $name\n";}}
function ecarts(Database $db): int {
 return (int)$db->scalar('SELECT COUNT(*) FROM (SELECT receipt_item_id,location_id FROM v_balance_controle UNION SELECT receipt_item_id,location_id FROM stock_balance) k LEFT JOIN v_balance_controle c USING(receipt_item_id,location_id) LEFT JOIN stock_balance b USING(receipt_item_id,location_id) WHERE COALESCE(c.qty,0)<>COALESCE(b.qty,0)')
  +(int)$db->scalar("SELECT COUNT(*) FROM stock_balance b LEFT JOIN (SELECT receipt_item_id,location_id,SUM(qty) qty FROM pick WHERE status IN ('planned','confirmed') GROUP BY receipt_item_id,location_id) p USING(receipt_item_id,location_id) WHERE b.reserved_qty<>COALESCE(p.qty,0)");
}
$article=$ids['articles'][0];$day='2026-10-22';
$dispo=fn()=>(int)$db->scalar('SELECT stock_disponible(?,?)',[$article,$day]);
$vue=fn()=>(int)$db->scalar('SELECT COALESCE(SUM(available_qty),0) FROM v_stock WHERE article_id=? AND blocked=0 AND (expires_on IS NULL OR expires_on>=?) AND available_qty>0',[$article,$day]);

check(ecarts($db)===0,'Soldes et réservations égaux au recalcul depuis l\'historique après le jeu de test');
check($dispo()===$vue()&&$dispo()>0,'Fonction stock_disponible égale à la somme disponible de v_stock');

$o=$db->insert('customer_order',['reference'=>'OPTI-TROP','owner_id'=>$ids['owners'][0],'destination'=>'Adresse fictive','desired_on'=>$day]);
$db->insert('order_line',['order_id'=>$o,'article_id'=>$article,'qty'=>$dispo()+1]);$picks=(int)$db->scalar('SELECT COUNT(*) FROM pick');
try{$w->prepare($o,$ids['warehouse']);check(false,'Préparation au-delà du disponible refusée par la fonction');}
catch(DomainException $e){check(str_contains($e->getMessage(),'disponible(s) pour')&&(int)$db->scalar('SELECT COUNT(*) FROM pick')===$picks,'Préparation au-delà du disponible refusée par la fonction');}

$avant=$dispo();
$o=$db->insert('customer_order',['reference'=>'OPTI-OK','owner_id'=>$ids['owners'][0],'destination'=>'Adresse fictive','desired_on'=>$day]);
$db->insert('order_line',['order_id'=>$o,'article_id'=>$article,'qty'=>3]);$w->prepare($o,$ids['warehouse']);
check($dispo()===$avant-3&&ecarts($db)===0,'Réservation : trigger sur pick, disponible diminué de 3, aucun écart');
$w->cancelOrder($o);check($dispo()===$avant&&ecarts($db)===0,'Annulation : réservations libérées par trigger');

$item=$ids['items'][0];[$src,$dest]=[$ids['locations'][0],$ids['locations'][1]];
$solde=fn($l)=>(int)$db->scalar('SELECT COALESCE((SELECT qty FROM stock_balance WHERE receipt_item_id=? AND location_id=?),0)',[$item,$l]);
[$s0,$d0]=[$solde($src),$solde($dest)];$w->transfer($item,$src,$dest,2,'Test soldes');
check($solde($src)===$s0-2&&$solde($dest)===$d0+2&&ecarts($db)===0,'Transfert : deux soldes mis à jour dans la même transaction');

$shipped=$db->one("SELECT id,qty FROM pick WHERE status='shipped' LIMIT 1");
try{$db->run('UPDATE pick SET qty=qty+1 WHERE id=?',[$shipped['id']]);check(false,'Prélèvement expédié figé');}
catch(PDOException $e){check((int)$db->scalar('SELECT qty FROM pick WHERE id=?',[$shipped['id']])===(int)$shipped['qty'],'Prélèvement expédié figé');}
try{$db->run('UPDATE stock_balance SET qty=qty+100 WHERE receipt_item_id=?',[$item]);check(false,'Soldes non modifiables par le compte applicatif');}
catch(PDOException $e){check(ecarts($db)===0,'Soldes non modifiables par le compte applicatif');}

// EXPLAIN sur une vue exige SHOW VIEW : plan lu avec le compte d'installation.
$planDb=new Database(['dsn'=>'mysql:host=127.0.0.1;port='.(getenv('BD70_PORT')?:3307).';dbname='.$testName.';charset=utf8mb4','user'=>getenv('BD70_ADMIN_USER')?:'root','password'=>getenv('BD70_ADMIN_PASSWORD')?:'','timezone'=>'Europe/Paris']);
$plan=$planDb->all('EXPLAIN SELECT sku,qty FROM v_stock WHERE article_id=?',[$article]);
check(!array_filter($plan,fn($r)=>str_starts_with((string)$r['table'],'<derived')),'Plan de v_stock sans table dérivée (vues fusionnées)');

$result=['date'=>date(DATE_ATOM),'engine'=>$db->scalar('SELECT VERSION()'),'passed'=>count($passed),'failed'=>count($failures),'successes'=>$passed,'failures'=>$failures];
file_put_contents(__DIR__.'/../docs/preuves/optimisation.json',json_encode($result,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
echo count($passed).' réussis, '.count($failures)." échecs\n";exit($failures?1:0);
