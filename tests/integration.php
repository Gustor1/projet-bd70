<?php
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';
$testName=getenv('BD70_TEST_DATABASE')?:'bd70_test';if(!preg_match('/^bd70_test[a-z0-9_]*$/',$testName))die('Base de test requise.');putenv('BD70_DATABASE='.$testName);putenv('BD70_TEST_DATABASE='.$testName);
$db=new Database();$ids=json_decode(file_get_contents(__DIR__.'/../.local/seed-'.$testName.'.json'),true);
$w=new Warehouse($db,$ids['admin'],'2026-10-22 12:00:00');$cat=new Catalog($db);$passed=[];$failures=[];
function check(bool $ok,string $name): void {global $passed,$failures;if($ok){$passed[]=$name;echo "OK $name\n";}else{$failures[]=$name;echo "ECHEC $name\n";}}
function rejects(callable $f,string $name): void {try{$f();check(false,$name);}catch(DomainException|PDOException $e){check(true,$name);}}
function countMoves(): int {global $db;return (int)$db->scalar('SELECT COUNT(*) FROM stock_movement');}
function orderTest(string $ref,int $qty): int {global $db,$ids;$o=$db->insert('customer_order',['reference'=>$ref,'owner_id'=>$ids['owners'][0],'destination'=>'Adresse fictive','desired_on'=>'2026-10-22']);$db->insert('order_line',['order_id'=>$o,'article_id'=>$ids['articles'][0],'qty'=>$qty]);return $o;}
function race(string $action,array $payloads): array {
    $jobs=[];$at=microtime(true)+0.8;
    foreach($payloads as $payload){$cmd=[PHP_BINARY,__DIR__.'/race_worker.php',$action,base64_encode(json_encode($payload)),(string)$at];$proc=proc_open($cmd,[0=>['pipe','r'],1=>['pipe','w'],2=>['pipe','w']],$pipes,dirname(__DIR__));fclose($pipes[0]);$jobs[]=[$proc,$pipes];}
    $results=[];foreach($jobs as [$proc,$pipes]){$out=stream_get_contents($pipes[1]);$err=stream_get_contents($pipes[2]);fclose($pipes[1]);fclose($pipes[2]);$exit=proc_close($proc);$results[]=json_decode($out,true)??['ok'=>false,'error'=>$err,'exit'=>$exit];}return $results;
}
// Oracle calculable à la main avant modification de la base de test.
$r=(new Reports($db))->dashboard(['from'=>'2026-10-22','to'=>'2026-10-22']);
check(abs($r['occupied']/60-80)<0.001,'F08 occupation 80 minutes');
check(abs($r['capacity']/60-4320)<0.001,'F08 dénominateur trois quais 24h');
$carrierMetrics=array_column($r['carriers'],null,'transporteur');
check(abs((float)$carrierMetrics['Nord Transit']['attente_min']-17.5)<0.001&&abs((float)$carrierMetrics['Froid Express']['attente_min']-15)<0.001,'F08 attente par transporteur 17,5 et 15 min');
check(abs((float)$carrierMetrics['Nord Transit']['immobilisation_min']-55)<0.001&&abs((float)$carrierMetrics['Froid Express']['immobilisation_min']-50)<0.001,'F08 immobilisation par transporteur 55 et 50 min');
check($r['gaps']['lignes']==4&&$r['gaps']['lignes_ecart']==2&&$r['gaps']['excedent']==5&&$r['gaps']['manquant']==5&&$r['gaps']['endommage']==5,'F08 écarts 2/4 lignes, 5 manquant/excédent/avariées');
check(abs((float)$r['productivity'][0]['unites_heure']-150)<0.001,'F08 productivité 150 unités/h');
check((int)$db->scalar('SELECT SUM(qty) FROM v_stock')===205,'Conservation démo 255 entrées - 50 sorties = 205');
check(count($r['dlc'])===1&&$r['dlc'][0]['disponible']==40,'F08 horizon DLC : 40 unités froid');
check($r['expiry']['perime']==10&&$r['expiry']['sans_dlc']==15,'F08 périmés 10, sans DLC 15');
check((int)$db->scalar('SELECT SUM(available_qty) FROM v_stock WHERE blocked=1 OR expires_on<CURRENT_DATE()')===0,'R09 aucun disponible bloqué/périmé');
check((int)$db->scalar('SELECT COUNT(DISTINCT r.id) FROM receipt_item i JOIN receipt_line l ON l.id=i.line_id JOIN receipt r ON r.id=l.receipt_id WHERE i.lot_id=?',[$ids['lots'][0]])===2,'F05 même lot reçu dans deux réceptions');
check((int)$db->scalar('SELECT COUNT(DISTINCT ol.order_id) FROM pick p JOIN receipt_item i ON i.id=p.receipt_item_id JOIN order_line ol ON ol.id=p.order_line_id WHERE i.lot_id=?',[$ids['lots'][0]])===2,'F07 même lot pour deux commandes');
$trace=$db->run('CALL trace_lot(?,?)',[$ids['lots'][0],0]);$tr=$trace->fetchAll();$trace->closeCursor();check(count(array_filter($tr,fn($v)=>$v['camion']==='DEMO-001'))===2,'F08 provenance vers deux sorties et camion');
// Contraintes élémentaires et droits SQL.
rejects(fn()=>$db->insert('carrier',['code'=>'TR-1','name'=>'x','address'=>'x','phone'=>'x','email'=>'x@test.test']),'UNIQUE clé métier transporteur');
rejects(fn()=>$db->insert('driver',['carrier_id'=>999999,'name'=>'x','phone'=>'x','license_number'=>'BAD-FK']),'FK chauffeur transporteur');
rejects(fn()=>$db->insert('order_line',['order_id'=>$ids['draft_order'],'article_id'=>$ids['articles'][1],'qty'=>-1]),'CHECK quantité négative');
rejects(fn()=>$db->run('UPDATE stock_movement SET delta=999 WHERE id=1'),'R11 mouvement non éditable par compte applicatif');
rejects(fn()=>$db->run('DELETE FROM audit_log WHERE id=1'),'R11 journal non effaçable');
rejects(fn()=>$db->run('CREATE TABLE forbidden (id INT)'),'DCL compte applicatif sans DDL');
$before=countMoves();rejects(fn()=>$w->validateReceipt($ids['receipt']),'R05 réception validée une fois');check(countMoves()===$before,'R05 aucun double comptage');
rejects(fn()=>$w->ship($ids['orders'][0],$ids['outbound']),'R10 double expédition refusée');
// CRUD sans SQL manuel pour l'utilisateur final, apostrophes conservées.
$c=$cat->save('carrier',null,['code'=>'TEST-CRUD','name'=>"L’entrepôt d'Oscar <b>test</b>",'address'=>'Fictif','phone'=>'000','email'=>'crud@bd70.test'],$ids['admin']);
$cat->save('carrier',$c,['code'=>'TEST-CRUD','name'=>"L'entrepôt modifié",'address'=>'Fictif','phone'=>'000','email'=>'crud@bd70.test'],$ids['admin']);
check($db->scalar('SELECT name FROM carrier WHERE id=?',[$c])==="L'entrepôt modifié",'CRUD modification et apostrophe');$cat->delete('carrier',$c,$ids['admin']);check(!$db->scalar('SELECT COUNT(*) FROM carrier WHERE id=?',[$c]),'CRUD suppression inutilisée');
rejects(fn()=>$cat->delete('carrier',$ids['carriers'][0],$ids['admin']),'CRUD référentiel utilisé protégé');
check((int)$db->scalar("SELECT COUNT(*) FROM audit_log WHERE entity='carrier' AND actor_id=? AND operation='DELETE'",[$ids['admin']])>0,'R11 trigger auteur opération date');
check(!(bool)$db->scalar("SELECT COUNT(*) FROM audit_log WHERE details LIKE '%Entrepot2026%' OR details LIKE '%password_hash%'"),'R11 aucun mot de passe journalisé');
// R01/R02 : réservations et modification.
$ap=['reference'=>'TEST-RDV-1','dock_id'=>$ids['docks'][0],'driver_id'=>$ids['drivers'][0],'vehicle_id'=>$ids['vehicles'][0],'trailer_id'=>null,'operation'=>'reception','starts_at'=>'2026-10-24 08:00:00','ends_at'=>'2026-10-24 09:00:00'];
$a=$w->appointment($ap);rejects(fn()=>$w->appointment([...$ap,'reference'=>'TEST-RDV-CONFLIT']),'R01 chevauchement refusé');
$b=$w->appointment([...$ap,'reference'=>'TEST-RDV-ADJ','starts_at'=>'2026-10-24 09:00:00','ends_at'=>'2026-10-24 10:00:00']);check($b>0,'R01 créneaux adjacents autorisés');
rejects(fn()=>$w->appointment([...$ap,'reference'=>'TEST-RDV-ADJ'], $b),'R01 modification conflictuelle refusée');
check($db->scalar('SELECT starts_at FROM appointment WHERE id=?',[$b])==='2026-10-24 09:00:00','R12 modification rollback conserve ancien créneau');
rejects(fn()=>$w->appointment([...$ap,'reference'=>'TEST-RDV-TYPE','dock_id'=>$ids['docks'][2]]),'R02 type quai incompatible');
rejects(fn()=>$w->appointment([...$ap,'reference'=>'TEST-RDV-DATE','ends_at'=>$ap['starts_at']]),'R01 durée nulle refusée');
rejects(fn()=>$w->appointment([...$ap,'reference'=>'TEST-RDV-HS','dock_id'=>$ids['docks'][1],'starts_at'=>'2026-10-23 13:00:00','ends_at'=>'2026-10-23 13:30:00']),'R02 indisponibilité refusée');
rejects(fn()=>$cat->save('dock_downtime',null,['dock_id'=>$ids['docks'][0],'starts_at'=>$ap['starts_at'],'ends_at'=>$ap['ends_at'],'reason'=>'Test conflit'],$ids['admin']),'R02 indisponibilité sur réservation refusée');
$raceAp=[...$ap,'starts_at'=>'2026-10-24 11:00:00','ends_at'=>'2026-10-24 12:00:00'];
$rr=race('appointment',[[...$raceAp,'reference'=>'RACE-A'],[...$raceAp,'reference'=>'RACE-B']]);check(count(array_filter($rr,fn($x)=>$x['ok']))===1,'R01 deux connexions : une seule réservation');
file_put_contents(__DIR__.'/../livrables/preuves/concurrence.json',json_encode(['reservation'=>$rr],JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
// Flux et occupation sans rendez-vous.
$v1=$w->arrive(['reference'=>'TEST-V1','driver_id'=>$ids['drivers'][0],'vehicle_id'=>$ids['vehicles'][0],'trailer_id'=>null,'operation'=>'reception']);
$v2=$w->arrive(['reference'=>'TEST-V2','driver_id'=>$ids['drivers'][1],'vehicle_id'=>$ids['vehicles'][1],'trailer_id'=>null,'operation'=>'reception']);
rejects(fn()=>$w->transition($v1,'working',$ids['docks'][0]),'R04 début avant contrôle refusé');
foreach([$v1,$v2] as $v)$w->transition($v,'checked',null,'Documents de test vérifiés');
$rr=race('call',[['id'=>$v1,'dock'=>$ids['docks'][0]],['id'=>$v2,'dock'=>$ids['docks'][0]]]);check(count(array_filter($rr,fn($x)=>$x['ok']))===1,'R03 deux connexions : une seule occupation');
$winner=$db->scalar("SELECT id FROM truck_visit WHERE id IN (?,?) AND status='called'",[$v1,$v2]);$loser=$winner==$v1?$v2:$v1;
$w->transition((int)$winner,'working');$w->transition((int)$loser,'called',$ids['docks'][1]);$w->transition((int)$loser,'working');
rejects(fn()=>(new Warehouse($db,$ids['admin'],'2026-10-22 11:00:00'))->transition((int)$winner,'finished'),'R04 horodatage rétrograde refusé');
// R12 : deuxième fraction incompatible après insertion de la première : aucune entrée conservée.
$n=$db->insert('supplier_notice',['reference'=>'TEST-AVIS-ROLLBACK','supplier_id'=>$ids['supplier'],'expected_on'=>'2026-10-22']);$nl=$db->insert('notice_line',['notice_id'=>$n,'article_id'=>$ids['articles'][0],'expected_qty'=>20]);
$receipt=$db->insert('receipt',['reference'=>'TEST-REC-ROLLBACK','notice_id'=>$n,'visit_id'=>$winner]);$rl=$db->insert('receipt_line',['receipt_id'=>$receipt,'notice_line_id'=>$nl,'expected_qty'=>20]);
foreach([$ids['locations'][0],$ids['locations'][2]] as $k=>$loc)$db->insert('receipt_item',['line_id'=>$rl,'lot_id'=>$ids['lots'][0],'pallet_code'=>'TEST-PAL-ROLLBACK-'.$k,'accepted_qty'=>10,'location_id'=>$loc]);
$before=countMoves();rejects(fn()=>$w->validateReceipt($receipt),'R08/R12 réception multi-fractions rollback');check(countMoves()===$before&&$db->scalar('SELECT status FROM receipt WHERE id=?',[$receipt])==='draft','R12 aucune entrée partielle ni validation');
// R06/R07/R08 : transferts et réservations concurrentes.
$item=$ids['items'][0];$src=$ids['locations'][0];$dest=$ids['locations'][1];$sum=(int)$db->scalar('SELECT SUM(delta) FROM stock_movement WHERE receipt_item_id=?',[$item]);
$w->transfer($item,$src,$dest,5,'Test conservation');check((int)$db->scalar('SELECT SUM(delta) FROM stock_movement WHERE receipt_item_id=?',[$item])===$sum,'R07 transfert conserve quantité');
$before=countMoves();rejects(fn()=>$w->transfer($item,$src,$ids['locations'][2],1,'Incompatible'),'R08 zone incompatible');check(countMoves()===$before,'R12 transfert refusé sans débit');
rejects(fn()=>$w->adjust($item,$src,-99999,'Test négatif'),'R06 stock négatif refusé');
$tiny=$db->insert('location',['level_id'=>1,'code'=>'TEST-CAPACITE','width_m'=>1,'depth_m'=>1,'height_m'=>1,'max_kg'=>10,'max_pallets'=>2]);
$rr2=race('transfer',[['item'=>$item,'source'=>$src,'dest'=>$tiny,'qty'=>4],['item'=>$item,'source'=>$src,'dest'=>$tiny,'qty'=>4]]);check(count(array_filter($rr2,fn($x)=>$x['ok']))===1,'R08 capacité concurrente : une seule entrée de 4');
check((int)$db->scalar('SELECT SUM(delta) FROM stock_movement WHERE location_id=?',[$tiny])===4,'R08 capacité non dépassée');
$available=(int)$db->scalar('SELECT SUM(available_qty) FROM v_stock WHERE article_id=?',[$ids['articles'][0]]);
$o1=orderTest('RACE-STOCK-A',$available);$o2=orderTest('RACE-STOCK-B',$available);
$rr3=race('prepare',[['order'=>$o1,'preparer'=>$ids['warehouse']],['order'=>$o2,'preparer'=>$ids['warehouse']]]);check(count(array_filter($rr3,fn($x)=>$x['ok']))===1,'R06 deux préparations : aucune sur-réservation');
check((int)$db->scalar('SELECT COUNT(*) FROM v_stock WHERE reserved_qty>qty')===0,'R06 rapprochement réservé <= physique');
$winnerOrder=(int)$db->scalar("SELECT id FROM customer_order WHERE id IN (?,?) AND status='picking'",[$o1,$o2]);$w->cancelOrder($winnerOrder);
check((int)$db->scalar('SELECT SUM(reserved_qty) FROM v_stock')===0,'Annulation libère toutes les réservations');
$short=orderTest('TEST-STOCK-INSUFFISANT',9999);$before=(int)$db->scalar('SELECT COUNT(*) FROM pick');rejects(fn()=>$w->prepare($short,$ids['warehouse']),'R12 stock insuffisant refuse préparation');check((int)$db->scalar('SELECT COUNT(*) FROM pick')===$before,'R12 prélèvement sans état partiel');
// Le lot FEFO choisi doit être A ; ni périmé, ni bloqué, même s'ils sont physiquement présents.
$o=orderTest('TEST-FEFO',1);$w->prepare($o,$ids['warehouse']);
check($db->scalar('SELECT i.lot_id FROM pick p JOIN receipt_item i ON i.id=p.receipt_item_id JOIN order_line l ON l.id=p.order_line_id WHERE l.order_id=?',[$o])==$ids['lots'][0],'FEFO choisit LOT-A stable');
$w->cancelOrder($o);
// Authentification et formulaire : droits testés sans dépendre des menus.
foreach(['admin','manager','gate','warehouse'] as $role){$u=$db->one('SELECT * FROM user_account WHERE role=?',[$role]);check(Auth::can($u,'trace'),'F01 rôle '.$role.' accès traçabilité');check(Auth::can($u,'accounts')===($role==='admin'),'F01 rôle '.$role.' comptes protégés');}
Auth::register($db,['name'=>'Compte Test','email'=>'pending-test@bd70.test','password'=>'TestInscription2026!','role'=>'admin','active'=>1]);$u=$db->one('SELECT * FROM user_account WHERE email=?',['pending-test@bd70.test']);check($u['role']==='pending'&&!$u['active'],'F01 inscription sans élévation de privilèges');
check((new Reports($db))->stock(['article_id'=>$ids['articles'][0],'owner_id'=>$ids['owners'][0],'zone_id'=>1,'q'=>'LOT-A'])['total']>0,'F06 filtres stock combinés');
check((new Reports($db))->stock(['q'=>'INEXISTANT-TEST'])['total']===0,'F06 aucun résultat');
$e=json_decode(file_get_contents(__DIR__.'/../livrables/preuves/concurrence.json'),true);$e+=['occupation'=>$rr,'capacite'=>$rr2,'reservation_stock'=>$rr3];file_put_contents(__DIR__.'/../livrables/preuves/concurrence.json',json_encode($e,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
$result=['date'=>date(DATE_ATOM),'engine'=>$db->scalar('SELECT VERSION()'),'passed'=>count($passed),'failed'=>count($failures),'successes'=>$passed,'failures'=>$failures];file_put_contents(__DIR__.'/../livrables/preuves/integration.json',json_encode($result,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));echo count($passed).' réussis, '.count($failures)." échecs\n";exit($failures?1:0);
