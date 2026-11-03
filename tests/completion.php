<?php
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';
if(!preg_match('/^bd70_test_/',getenv('BD70_DATABASE')?:''))die("Base de test dédiée requise.\n");
putenv('BD70_NOW=2026-10-22 12:00:00');$db=new Database();$cat=new Catalog($db);$w=new Warehouse($db,1);$checks=[];
function check(bool $ok,string $name):void{global $checks;$checks[$name]=$ok;echo ($ok?'OK ':'ECHEC ').$name."\n";}
function rejects(callable $fn,string $name):void{try{$fn();check(false,$name);}catch(DomainException|PDOException){check(true,$name);}}
function createOrder(string $ref,int $qty):int{global $db,$cat;$id=$cat->save('customer_order',null,['reference'=>$ref,'owner_id'=>1,'destination'=>'Client fictif','desired_on'=>'2026-10-22'],1);$cat->save('order_line',null,['order_id'=>$id,'article_id'=>1,'qty'=>$qty],1);return $id;}
$d=$db->one('SELECT * FROM driver WHERE id=1');$cat->save('driver',1,[...$d,'phone'=>'NOUVEAU-TEST'],1);check($db->scalar('SELECT phone FROM driver WHERE id=1')==='NOUVEAU-TEST','Téléphone chauffeur utilisé modifiable');
$q=$db->one('SELECT * FROM driver_qualification WHERE id=1');$cat->save('driver_qualification',1,[...$q,'expires_on'=>'2029-12-31'],1);check($db->scalar('SELECT expires_on FROM driver_qualification WHERE id=1')==='2029-12-31','Renouvellement ADR utilisé');
rejects(fn()=>$cat->save('driver_qualification',1,[...$q,'expires_on'=>'2020-01-01'],1),'Validité historique non raccourcie');
$details=$db->scalar("SELECT details FROM audit_log WHERE entity='driver' AND operation='UPDATE' ORDER BY id DESC LIMIT 1");$audit=json_decode($details,true);check($audit['avant']['phone']!==$audit['apres']['phone'],'Audit avant/après lisible');
check(!$db->scalar("SELECT COUNT(*) FROM audit_log WHERE details LIKE '%password_hash%'"),'Aucun hachage dans audit');
$appt=['reference'=>'NEW-APPT','dock_id'=>1,'driver_id'=>1,'vehicle_id'=>1,'trailer_id'=>null,'operation'=>'reception','starts_at'=>'2026-10-24 08:00:00','ends_at'=>'2026-10-24 09:00:00'];$w->appointment($appt);
rejects(fn()=>$w->appointment([...$appt,'reference'=>'NEW-CONFLICT','dock_id'=>2]),'Conflit même ressource sur deux quais');
$dock=$db->insert('dock',['code'=>'ONLY-TRACTOR','name'=>'Tracteur seulement','type'=>'mixte']);$db->insert('dock_vehicle_type',['dock_id'=>$dock,'vehicle_type'=>'tracteur']);
rejects(fn()=>$w->appointment([...$appt,'reference'=>'NO-TRAILER','dock_id'=>$dock,'vehicle_id'=>3,'trailer_id'=>4]),'Type de remorque contrôlé');
$visit=$w->arrive(['reference'=>'NEW-IN','driver_id'=>1,'vehicle_id'=>1,'operation'=>'reception']);$w->transition($visit,'checked',null,'Conforme');$w->transition($visit,'called',1);$w->transition($visit,'working');
$notice=$cat->save('supplier_notice',null,['reference'=>'MISSING-NOTICE','supplier_id'=>1,'expected_on'=>'2026-10-22'],1);$cat->save('notice_line',null,['notice_id'=>$notice,'article_id'=>1,'expected_qty'=>10],1);
$receipt=$w->openReceipt($notice,$visit,'MISSING-RECEIPT');$line=$db->one('SELECT * FROM receipt_line WHERE receipt_id=?',[$receipt]);$w->reserveReceipt($receipt,(int)$line['id'],'manquant','Dix unités non livrées');$w->validateReceipt($receipt);
check((int)$db->scalar('SELECT missing_qty FROM v_receipt_discrepancy WHERE receipt_id=?',[$receipt])===10,'Manquant total avec réserve sans fausse palette');
check((int)$db->scalar('SELECT COUNT(*) FROM receipt_reserve x LEFT JOIN receipt_line l ON l.id=x.line_id WHERE COALESCE(x.receipt_id,l.receipt_id)=?',[$receipt])===1,'Réserve liée et horodatée');
$w->closeNotice($notice,'Livraison terminée, dix unités manquantes signalées');rejects(fn()=>$w->openReceipt($notice,$visit,'AFTER-CLOSE'),'Avis clôturé interdit nouvelle réception');
$notice2=$cat->save('supplier_notice',null,['reference'=>'PARTIAL-NOTICE','supplier_id'=>1,'expected_on'=>'2026-10-22'],1);$cat->save('notice_line',null,['notice_id'=>$notice2,'article_id'=>1,'expected_qty'=>20],1);
$receipt2=$w->openReceipt($notice2,$visit,'PARTIAL-1');$line2=$db->one('SELECT * FROM receipt_line WHERE receipt_id=?',[$receipt2]);$cat->save('receipt_line',(int)$line2['id'],[...$line2,'expected_qty'=>10],1);
$w->receiveItem($receipt2,['line_id'=>$line2['id'],'lot_id'=>1,'pallet_code'=>'PARTIAL-PAL-1','accepted_qty'=>10,'damaged_qty'=>0,'pallet_state'=>'bon','reservation'=>'','location_id'=>2]);$w->validateReceipt($receipt2);
check((int)$db->scalar('SELECT remaining_qty FROM v_notice_line_progress WHERE notice_id=?',[$notice2])===10,'Reste à livrer après réception partielle');
$receipt3=$w->openReceipt($notice2,$visit,'PARTIAL-2');$line3=$db->one('SELECT * FROM receipt_line WHERE receipt_id=?',[$receipt3]);check($line3['expected_qty']===10,'Réception suivante reprend seulement le reste');
rejects(fn()=>$w->closeNotice($notice2,'Clôture prématurée'),'Clôture refuse un brouillon');
$w->receiveItem($receipt3,['line_id'=>$line3['id'],'new_lot'=>'NEW-GUIDED-LOT','expires_on'=>'2027-01-01','pallet_code'=>'PARTIAL-PAL-2','accepted_qty'=>11,'damaged_qty'=>0,'pallet_state'=>'bon','reservation'=>'Une unité supplémentaire','location_id'=>2]);$w->reserveReceipt($receipt3,(int)$line3['id'],'excedent','Une unité en excédent');$w->validateReceipt($receipt3);$w->closeNotice($notice2,'Soldé avec un excédent accepté');
check((int)$db->scalar('SELECT remaining_qty FROM v_notice_line_progress WHERE notice_id=?',[$notice2])===0,'Avis soldé après réception du reste');
$w->transition($visit,'finished');$w->transition($visit,'departed');
$order=createOrder('SPLIT-ORDER',20);$w->prepare($order,4);$pick=$db->one('SELECT p.* FROM pick p JOIN order_line l ON l.id=p.order_line_id WHERE l.order_id=?',[$order]);$w->confirmPickLine((int)$pick['id'],4,'warehouse');
check($db->scalar('SELECT status FROM customer_order WHERE id=?',[$order])==='ready','Confirmation ligne termine préparation');
$a=$cat->save('package',null,['order_id'=>$order,'code'=>'SPLIT-A','type'=>'colis'],1);$b=$cat->save('package',null,['order_id'=>$order,'code'=>'SPLIT-B','type'=>'colis'],1);
$cat->save('package_pick',null,['package_id'=>$a,'pick_id'=>$pick['id'],'qty'=>10],1);
rejects(fn()=>$cat->save('package_pick',null,['package_id'=>$b,'pick_id'=>$pick['id'],'qty'=>11],1),'Surallocation de colis refusée');
$cat->save('package_pick',null,['package_id'=>$b,'pick_id'=>$pick['id'],'qty'=>10],1);
check((int)$db->scalar('SELECT COUNT(*) FROM package_pick WHERE pick_id=?',[$pick['id']])===2,'Un prélèvement réparti dans deux colis');
$out=$w->arrive(['reference'=>'NEW-OUT','driver_id'=>1,'vehicle_id'=>1,'operation'=>'expedition']);$w->transition($out,'checked',null,'Conforme');$w->transition($out,'called',3);$w->transition($out,'working');
$before=(int)$db->scalar('SELECT SUM(delta) FROM v_stock_movement');$w->ship($order,$out);check((int)$db->scalar('SELECT SUM(delta) FROM v_stock_movement')===$before-20,'Expédition multicolis débite exactement 20');
rejects(fn()=>$w->ship($order,$out),'Double expédition refusée');rejects(fn()=>$w->resetPreparation($order,'Trop tard'),'Reprise après expédition interdite');
$redo=createOrder('REWORK',2);$w->prepare($redo,4);$w->confirmPick($redo,4,'warehouse');$p=$db->one('SELECT p.* FROM pick p JOIN order_line l ON l.id=p.order_line_id WHERE l.order_id=?',[$redo]);$pkg=$cat->save('package',null,['order_id'=>$redo,'code'=>'REDO-COL','type'=>'colis'],1);$cat->save('package_pick',null,['package_id'=>$pkg,'pick_id'=>$p['id'],'qty'=>2],1);$w->resetPreparation($redo,'Correction de destination');
check($db->scalar('SELECT status FROM customer_order WHERE id=?',[$redo])==='draft'&&!$db->scalar('SELECT COUNT(*) FROM package WHERE order_id=?',[$redo]),'Reprise libère colis et remet en brouillon');
$o=$db->one('SELECT * FROM customer_order WHERE id=?',[$redo]);$cat->save('customer_order',$redo,[...$o,'destination'=>'Destination corrigée'],1);$w->prepare($redo,4);check((int)$db->scalar('SELECT SUM(reserved_qty) FROM v_stock')===2,'Reprise puis nouvelle réservation sans double compte');$w->cancelOrder($redo);check((int)$db->scalar('SELECT SUM(reserved_qty) FROM v_stock')===0,'Annulation libère le stock');
$result=['date'=>Clock::now(),'timezone'=>'Europe/Paris','passed'=>count(array_filter($checks)),'failed'=>count(array_filter($checks,fn($v)=>!$v)),'checks'=>$checks];file_put_contents(__DIR__.'/../livrables/preuves/completion.json',json_encode($result,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));echo $result['passed'].' réussis, '.$result['failed']." échecs\n";exit($result['failed']?1:0);
