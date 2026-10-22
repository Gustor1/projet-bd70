<?php
declare(strict_types=1);
require_once __DIR__.'/../src/Database.php';
require_once __DIR__.'/../src/Warehouse.php';

function seed(Database $db): array
{
    if($db->scalar('SELECT COUNT(*) FROM user_account'))throw new RuntimeException('Jeu refusé : base déjà alimentée.');
    mt_srand(70);$ids=[];
    foreach(['admin'=>'Alice Martin','manager'=>'Samir Petit','gate'=>'Léa Dubois','warehouse'=>'Noah Bernard'] as $role=>$name)$ids[$role]=$db->insert('user_account',['email'=>$role.'@bd70.test','name'=>$name,'password_hash'=>password_hash('Entrepot2026!',PASSWORD_DEFAULT),'role'=>$role,'active'=>1]);
    $db->run('SET @actor_id=?',[$ids['admin']]);
    foreach(['Nord Transit','Froid Express','Route Est'] as $i=>$name){
        $c=$db->insert('carrier',['code'=>'TR-'.($i+1),'name'=>$name,'address'=>($i+1).' rue des Entrepôts, Belfort (fictif)','phone'=>'+33 30000000'.($i+1),'email'=>'contact'.($i+1).'@bd70.test']);$ids['carriers'][]=$c;
        $db->insert('carrier_contact',['carrier_id'=>$c,'name'=>'Contact démo '.($i+1),'phone'=>'+33 300000001','email'=>'contact'.($i+1).'@bd70.test']);
        $db->insert('carrier_contract',['carrier_id'=>$c,'reference'=>'CTR-'.($i+1),'starts_on'=>'2026-01-01','ends_on'=>'2027-12-31','terms'=>'Contrat fictif de démonstration']);
        $ids['drivers'][]=$db->insert('driver',['carrier_id'=>$c,'name'=>['Marc Démo','Julie Exemple','Paul Test'][$i],'phone'=>'+33 300000010','license_number'=>'PERMIS-DEMO-'.($i+1)]);
    }
    $adr=$db->insert('qualification',['code'=>'ADR','name'=>'Transport de matières dangereuses']);
    foreach($ids['drivers'] as $d)$db->insert('driver_qualification',['driver_id'=>$d,'qualification_id'=>$adr,'expires_on'=>'2028-12-31']);
    foreach(['FROID'=>'Frigorifique','HAYON'=>'Hayon','NIVELEUR'=>'Niveleur'] as $code=>$label)$ids['eq'][$code]=$db->insert('equipment',['code'=>$code,'name'=>$label]);
    foreach(['porteur','fourgon','tracteur','remorque'] as $i=>$type)$ids['vehicles'][]=$db->insert('vehicle',['carrier_id'=>$ids['carriers'][$i===1?1:0],'plate'=>'DEMO-00'.($i+1),'type'=>$type,'max_kg'=>20000,'max_pallets'=>40]);
    $db->insert('vehicle_equipment',['vehicle_id'=>$ids['vehicles'][1],'equipment_id'=>$ids['eq']['FROID']]);
    foreach(['Q-Ambiant','Q-Froid','Q-Sortie'] as $i=>$name){
        $dock=$db->insert('dock',['code'=>'Q-'.($i+1),'name'=>$name,'type'=>$i===2?'expedition':'mixte']);$ids['docks'][]=$dock;
        foreach(['porteur','fourgon','tracteur','remorque'] as $t)$db->insert('dock_vehicle_type',['dock_id'=>$dock,'vehicle_type'=>$t]);
        foreach($ids['eq'] as $e)$db->insert('dock_equipment',['dock_id'=>$dock,'equipment_id'=>$e]);
    }
    foreach(['Atlas Distribution','Marché des Alpes'] as $i=>$name)$ids['owners'][]=$db->insert('owner',['code'=>'CLI-'.($i+1),'name'=>$name,'address'=>'10 avenue du Commerce, Belfort (fictif)','email'=>'client'.($i+1).'@bd70.test']);
    $supplier=$db->insert('supplier',['code'=>'FOU-01','name'=>'Manufacture Démo','address'=>'Rue des Ateliers, Belfort (fictif)','phone'=>'+33 300000021']);$ids['supplier']=$supplier;
    foreach(['ambiant','froid','dangereux'] as $i=>$storage){
        $z=$db->insert('zone',['code'=>'Z-'.($i+1),'name'=>['Halle ambiante','Chambre froide','Zone sécurisée'][$i],'storage'=>$storage]);
        $a=$db->insert('aisle',['zone_id'=>$z,'code'=>'A-'.($i+1)]);$r=$db->insert('rack',['aisle_id'=>$a,'code'=>'R-'.($i+1)]);$l=$db->insert('rack_level',['rack_id'=>$r,'code'=>'N-'.($i+1)]);
        foreach([1,2] as $k)$ids['locations'][]=$db->insert('location',['level_id'=>$l,'code'=>'EMP-'.($i+1).'-'.$k,'width_m'=>5,'depth_m'=>5,'height_m'=>4,'max_kg'=>30000,'max_pallets'=>100]);
        $ids['articles'][]=$db->insert('article',['owner_id'=>$ids['owners'][0],'sku'=>['ART-CAFE','ART-FRAIS','ART-ADR'][$i],'name'=>['Café en cartons','Produits frais','Produit réglementé démo'][$i],'storage'=>$storage,'packaging'=>'Carton indivisible','width_m'=>0.2,'depth_m'=>0.2,'height_m'=>0.2,'unit_kg'=>2,'units_per_pallet'=>20]);
    }
    foreach([['LOT-A','2026-11-10',0],['LOT-B','2026-12-10',0],['LOT-PERIME','2026-10-01',0],['LOT-BLOQUE','2027-01-01',1]] as [$code,$date,$blocked])$ids['lots'][]=$db->insert('lot',['article_id'=>$ids['articles'][0],'code'=>$code,'expires_on'=>$date,'blocked'=>$blocked,'block_reason'=>$blocked?'Contrôle qualité démo':'']);
    $ids['lots'][]=$db->insert('lot',['article_id'=>$ids['articles'][1],'code'=>'LOT-FRAIS','expires_on'=>'2026-10-29']);
    $ids['lots'][]=$db->insert('lot',['article_id'=>$ids['articles'][2],'code'=>'LOT-ADR']);
    // Planning et passage entrant, réalisés avec le même service que l'application.
    $w=new Warehouse($db,$ids['admin'],'2026-10-22 08:00:00');
    $appt=$w->appointment(['reference'=>'RDV-DEMO-01','dock_id'=>$ids['docks'][0],'driver_id'=>$ids['drivers'][0],'vehicle_id'=>$ids['vehicles'][0],'trailer_id'=>null,'operation'=>'reception','starts_at'=>'2026-10-22 08:00:00','ends_at'=>'2026-10-22 09:00:00']);
    $visit=$w->arrive(['reference'=>'PASS-ENTREE-01','appointment_id'=>$appt]);$ids['inbound']=$visit;
    foreach([['08:05','checked','Documents conformes'],['08:10','parking',''],['08:15','called',''],['08:20','working','']] as [$time,$state,$note])(new Warehouse($db,$ids['gate'],'2026-10-22 '.$time.':00'))->transition($visit,$state,$ids['docks'][0],$note);
    $notice=$db->insert('supplier_notice',['reference'=>'AVIS-DEMO-01','supplier_id'=>$supplier,'expected_on'=>'2026-10-22']);$ids['notice']=$notice;
    $nl=$db->insert('notice_line',['notice_id'=>$notice,'article_id'=>$ids['articles'][0],'expected_qty'=>200]);$ids['notice_line']=$nl;
    $receipt=$db->insert('receipt',['reference'=>'REC-DEMO-01','notice_id'=>$notice,'visit_id'=>$visit]);$ids['receipt']=$receipt;
    $rl=$db->insert('receipt_line',['receipt_id'=>$receipt,'notice_line_id'=>$nl,'expected_qty'=>180]);
    foreach([[0,100,5,0],[1,60,0,0],[2,10,0,0],[3,10,0,0]] as $k=>[$lot,$qty,$damaged,$loc])$ids['items'][]=$db->insert('receipt_item',['line_id'=>$rl,'lot_id'=>$ids['lots'][$lot],'pallet_code'=>'PAL-DEMO-'.($k+1),'accepted_qty'=>$qty,'damaged_qty'=>$damaged,'pallet_state'=>$damaged?'abime':'bon','reservation'=>$damaged?'5 cartons détériorés':'','location_id'=>$ids['locations'][$loc]]);
    (new Warehouse($db,$ids['warehouse'],'2026-10-22 08:35:00'))->validateReceipt($receipt);
    $receipt2=$db->insert('receipt',['reference'=>'REC-DEMO-02','notice_id'=>$notice,'visit_id'=>$visit]);
    $rl2=$db->insert('receipt_line',['receipt_id'=>$receipt2,'notice_line_id'=>$nl,'expected_qty'=>20]);
    $ids['items'][]=$db->insert('receipt_item',['line_id'=>$rl2,'lot_id'=>$ids['lots'][0],'pallet_code'=>'PAL-DEMO-5','accepted_qty'=>20,'location_id'=>$ids['locations'][0]]);
    (new Warehouse($db,$ids['warehouse'],'2026-10-22 08:40:00'))->validateReceipt($receipt2);
    (new Warehouse($db,$ids['warehouse'],'2026-10-22 08:45:00'))->transfer($ids['items'][0],$ids['locations'][0],$ids['locations'][1],20,'Répartition sur deux emplacements');
    foreach([['08:50','finished'],['09:00','departed']] as [$time,$state])(new Warehouse($db,$ids['gate'],'2026-10-22 '.$time.':00'))->transition($visit,$state);
    // Arrivée sortante sans rendez-vous.
    $out=(new Warehouse($db,$ids['gate'],'2026-10-22 09:10:00'))->arrive(['reference'=>'PASS-SORTIE-01','driver_id'=>$ids['drivers'][0],'vehicle_id'=>$ids['vehicles'][0],'trailer_id'=>null,'operation'=>'expedition']);$ids['outbound']=$out;
    foreach([['09:15','checked','Documents conformes'],['09:20','called',''],['09:25','working','']] as [$time,$state,$note])(new Warehouse($db,$ids['gate'],'2026-10-22 '.$time.':00'))->transition($out,$state,$ids['docks'][2],$note);
    foreach([30,20] as $k=>$qty){
        $order=$db->insert('customer_order',['reference'=>'CMD-DEMO-'.($k+1),'owner_id'=>$ids['owners'][0],'destination'=>'Entrepôt client, Belfort (fictif)','desired_on'=>'2026-10-22']);$ids['orders'][]=$order;
        $db->insert('order_line',['order_id'=>$order,'article_id'=>$ids['articles'][0],'qty'=>$qty]);
        (new Warehouse($db,$ids['manager'],'2026-10-22 09:30:00'))->prepare($order,$ids['warehouse']);
        (new Warehouse($db,$ids['warehouse'],'2026-10-22 09:40:00'))->confirmPick($order,$ids['warehouse'],'warehouse');
        $pkg=$db->insert('package',['order_id'=>$order,'code'=>'COL-DEMO-'.($k+1),'type'=>'colis']);
        foreach($db->all('SELECT p.id FROM pick p JOIN order_line l ON l.id=p.order_line_id WHERE l.order_id=?',[$order]) as $p)$db->insert('package_pick',['package_id'=>$pkg,'pick_id'=>$p['id']]);
        (new Warehouse($db,$ids['warehouse'],'2026-10-22 09:45:00'))->ship($order,$out);
    }
    foreach([['09:50','finished'],['10:00','departed']] as [$time,$state])(new Warehouse($db,$ids['gate'],'2026-10-22 '.$time.':00'))->transition($out,$state);
    // Une livraison frigorifique avec deux lignes : froid et produit ADR, avec manquant.
    $cold=(new Warehouse($db,$ids['gate'],'2026-10-22 10:10:00'))->arrive(['reference'=>'PASS-FROID-01','driver_id'=>$ids['drivers'][1],'vehicle_id'=>$ids['vehicles'][1],'operation'=>'reception']);
    foreach([['10:15','checked','Documents conformes et ADR vérifiée'],['10:20','called',''],['10:25','working','']] as [$time,$state,$note])(new Warehouse($db,$ids['gate'],'2026-10-22 '.$time.':00'))->transition($cold,$state,$ids['docks'][1],$note);
    $nc=$db->insert('supplier_notice',['reference'=>'AVIS-FROID-ADR','supplier_id'=>$supplier,'expected_on'=>'2026-10-22']);
    $rc=$db->insert('receipt',['reference'=>'REC-FROID-ADR','notice_id'=>$nc,'visit_id'=>$cold]);
    foreach([[1,4,40,40,2],[2,5,20,15,4]] as [$article,$lot,$expected,$accepted,$loc]){
        $nline=$db->insert('notice_line',['notice_id'=>$nc,'article_id'=>$ids['articles'][$article],'expected_qty'=>$expected]);$rline=$db->insert('receipt_line',['receipt_id'=>$rc,'notice_line_id'=>$nline,'expected_qty'=>$expected]);
        $db->insert('receipt_item',['line_id'=>$rline,'lot_id'=>$ids['lots'][$lot],'pallet_code'=>'PAL-ZONE-'.$article,'accepted_qty'=>$accepted,'location_id'=>$ids['locations'][$loc]]);
    }
    (new Warehouse($db,$ids['warehouse'],'2026-10-22 10:35:00'))->validateReceipt($rc);
    foreach([['10:50','finished'],['11:00','departed']] as [$time,$state])(new Warehouse($db,$ids['gate'],'2026-10-22 '.$time.':00'))->transition($cold,$state);
    // Brouillons utilisables dans la démonstration, sans simulation de validation.
    $ids['draft_order']=$db->insert('customer_order',['reference'=>'CMD-A-PREPARER','owner_id'=>$ids['owners'][0],'destination'=>'Client démo, Lyon','desired_on'=>'2026-10-23']);
    $db->insert('order_line',['order_id'=>$ids['draft_order'],'article_id'=>$ids['articles'][0],'qty'=>15]);
    $db->insert('dock_downtime',['dock_id'=>$ids['docks'][1],'starts_at'=>'2026-10-23 13:00:00','ends_at'=>'2026-10-23 14:00:00','reason'=>'Maintenance planifiée de démonstration']);
    return $ids;
}
if(realpath($_SERVER['SCRIPT_FILENAME'])===__FILE__){$db=new Database();$ids=seed($db);file_put_contents(__DIR__.'/../.local/seed-'.($db->scalar('SELECT DATABASE()')).'.json',json_encode($ids,JSON_PRETTY_PRINT));echo "Jeu BD70, graine 70, référence 2026-10-22 chargé.\n";}
