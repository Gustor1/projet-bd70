<?php
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';require __DIR__.'/../src/CarrierPortal.php';
$name=getenv('BD70_DATABASE');if(!preg_match('/^bd70_test[a-z0-9_]+$/',$name?:''))die('Base de test requise.');
$db=new Database();$results=[];
function check(bool $ok,string $name):void{global $results;$results[]=['name'=>$name,'ok'=>$ok];echo ($ok?'OK ':'ECHEC ').$name."\n";}
function denied(callable $f,string $name):void{try{$f();check(false,$name);}catch(RuntimeException $e){check($e->getCode()===403,$name);}}
$users=[];foreach(['admin','manager','gate','warehouse'] as $r)$users[$r]=$db->one('SELECT * FROM user_account WHERE role=? LIMIT 1',[$r]);
check(Auth::can($users['admin'],'accounts')&&!Auth::can($users['admin'],'orders')&&!Auth::can($users['admin'],'trace'),'Administrateur technique sans accès métier');
check(Auth::can($users['manager'],'manage_orders')&&!Auth::can($users['warehouse'],'manage_orders'),'Affectation réservée au responsable');
check(Auth::transitionAllowed($users['warehouse'],'working')&&!Auth::transitionAllowed($users['gate'],'working'),'Début opération réservé au magasinier');
check(Auth::transitionAllowed($users['gate'],'departed')&&!Auth::transitionAllowed($users['warehouse'],'departed'),'Départ réservé à accueil');
check(Auth::can($users['manager'],'planning')&&!Auth::can($users['gate'],'planning')&&!Auth::can($users['warehouse'],'planning'),'Planification des quais réservée au responsable (sujet et use case)');
$other=$db->insert('user_account',['email'=>'other@bd70.test','name'=>'Autre magasinier','role'=>'warehouse','active'=>1,'password_hash'=>password_hash('Entrepot2026!',PASSWORD_DEFAULT)]);
$order=$db->insert('customer_order',['reference'=>'CORR-AFFECTEE','owner_id'=>1,'destination'=>'Test','desired_on'=>'2026-10-22','preparer_id'=>$users['warehouse']['id']]);
(new Warehouse($db,(int)$users['manager']['id']))->assignPreparer($order,(int)$users['warehouse']['id']);check((int)$db->scalar('SELECT preparer_id FROM customer_order WHERE id=?',[$order])===(int)$users['warehouse']['id'],'Responsable affecte sans réserver le stock');
Auth::orderAccess($db,$users['warehouse'],$order);check(true,'Lecture de sa commande affectée');
denied(fn()=>Auth::orderAccess($db,[...$users['warehouse'],'id'=>$other],$order),'Autre préparateur refusé');
$pkg=$db->insert('package',['order_id'=>$order,'code'=>'CORR-PKG','type'=>'colis']);
denied(fn()=>Auth::catalogWrite($db,[...$users['warehouse'],'id'=>$other],'package',$pkg,['order_id'=>$order]),'Edition de colis autre préparateur refusée');
denied(fn()=>Auth::catalogWrite($db,$users['manager'],'package',$pkg,[]),'Conditionnement interdit au responsable');
foreach([1,2] as $carrier)$db->insert('user_account',['email'=>'carrier'.$carrier.'@bd70.test','name'=>'Transporteur '.$carrier,'role'=>'carrier','carrier_id'=>$carrier,'active'=>1,'password_hash'=>password_hash('Entrepot2026!',PASSWORD_DEFAULT)]);
$u=$db->one("SELECT * FROM user_account WHERE email='carrier1@bd70.test'");$portal=new CarrierPortal($db,$u);
$data=['reference'=>'CORR-PORTAL','dock_id'=>1,'driver_id'=>1,'vehicle_id'=>1,'trailer_id'=>'','operation'=>'reception','starts_at'=>'2026-11-15T14:00','ends_at'=>'2026-11-15T15:00'];
$portal->act('carrier_save',$data);$id=(int)$db->scalar("SELECT id FROM appointment WHERE reference='CORR-PORTAL'");check($id>0,'Transporteur crée un rendez-vous');
$portal->act('carrier_save',[...$data,'id'=>$id,'ends_at'=>'2026-11-15T15:30']);check($db->scalar('SELECT ends_at FROM appointment WHERE id=?',[$id])==='2026-11-15 15:30:00','Transporteur modifie son rendez-vous');
$otherPortal=new CarrierPortal($db,$db->one("SELECT * FROM user_account WHERE email='carrier2@bd70.test'"));
denied(fn()=>$otherPortal->act('carrier_cancel',['id'=>$id]),'Annulation entre sociétés refusée');
denied(fn()=>$otherPortal->act('carrier_save',[...$data,'id'=>$id]),'Edition entre sociétés refusée');
denied(fn()=>$portal->act('carrier_save',[...$data,'reference'=>'CORR-FORGE','driver_id'=>2,'vehicle_id'=>2]),'Ressources autre société refusées');
check(!in_array($id,array_column($otherPortal->appointments(),'id')),'Liste transporteur isolée');
$portal->act('carrier_cancel',['id'=>$id]);check($db->scalar('SELECT status FROM appointment WHERE id=?',[$id])==='cancelled','Transporteur annule son rendez-vous');
$raw=$db->one("SELECT * FROM stock_movement WHERE kind='shipment' LIMIT 1");$projection=$db->one('SELECT * FROM v_stock_movement WHERE id=?',[$raw['id']]);
check($raw['delta']===null&&$raw['location_id']===null&&$raw['receipt_item_id']===null,'Sortie sans duplication des faits du prélèvement');
check($projection['delta']<0&&$projection['location_id']>0&&$projection['receipt_item_id']>0,'Projection reconstitue le mouvement pour stock et trace');
$failed=count(array_filter($results,fn($r)=>!$r['ok']));file_put_contents(__DIR__.'/../docs/preuves/corrections.json',json_encode(['passed'=>count($results)-$failed,'failed'=>$failed,'results'=>$results],JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));exit($failed?1:0);
