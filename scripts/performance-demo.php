<?php
// Mesure en lecture seule des requêtes principales sur le jeu de démonstration riche.
// BD70_DATABASE=bd70_test_xxx (copie chargée par import-demo.php) php scripts/performance-demo.php
// BD70_PERF_OUT=chemin.json : fichier de sortie (défaut docs/preuves/performances-demo.json).
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';
$name=getenv('BD70_DATABASE')?:'';
if(!preg_match('/^bd70_(demo|test)[a-z0-9_]*$/',$name))die("Base de démonstration ou de test requise.\n");
$db=new Database();
// EXPLAIN sur des vues exige le droit SHOW VIEW : plan lu avec le compte d'installation, mesures avec le compte applicatif.
$planDb=new Database(['dsn'=>'mysql:host=127.0.0.1;port='.(getenv('BD70_PORT')?:3307).';dbname='.$name.';charset=utf8mb4','user'=>getenv('BD70_ADMIN_USER')?:'root','password'=>getenv('BD70_ADMIN_PASSWORD')?:'','timezone'=>'Europe/Paris']);
$lot=(int)$db->scalar("SELECT i.lot_id FROM pick p JOIN receipt_item i ON i.id=p.receipt_item_id GROUP BY i.lot_id ORDER BY COUNT(*) DESC LIMIT 1");
$article=(int)$db->scalar('SELECT article_id FROM v_stock GROUP BY article_id ORDER BY COUNT(*) DESC LIMIT 1');
$owner=(int)$db->scalar('SELECT owner_id FROM article WHERE id=?',[$article]);
$zone=(int)$db->scalar('SELECT zone_id FROM v_stock WHERE article_id=? LIMIT 1',[$article]);
$queries=[
 'disponibilite_quai'=>["SELECT reference FROM appointment WHERE dock_id=? AND status='active' AND starts_at<? AND ends_at>?",[1,'2026-10-22 10:00:00','2026-10-22 09:00:00']],
 'recherche_passages'=>["SELECT reference,carrier_name,status,arrived_at FROM v_visit WHERE arrived_at>=? AND arrived_at<? AND carrier_id=? AND status=? ORDER BY arrived_at DESC LIMIT 20",['2026-09-01','2026-10-01',1,'departed']],
 'recherche_stock'=>["SELECT sku,lot_code,location_code,qty,available_qty FROM v_stock WHERE article_id=? AND owner_id=? AND zone_id=? ORDER BY lot_code,location_code LIMIT 20",[$article,$owner,$zone]],
 'emplacements'=>["SELECT l.code,u.used_kg,u.used_pallets FROM v_location l JOIN v_location_usage u ON u.id=l.id JOIN article a ON a.id=? WHERE l.storage=a.storage AND l.width_m>=a.width_m AND l.height_m>=a.height_m AND l.depth_m>=a.depth_m AND u.used_kg+?*a.unit_kg<=l.max_kg AND u.used_m3+?*a.width_m*a.height_m*a.depth_m<=l.capacity_m3 AND u.used_pallets+?/a.units_per_pallet<=l.max_pallets",[$article,5,5,5]],
 'historique_lot'=>['SELECT m.operation_ref,m.created_at,m.delta,l.code FROM v_stock_movement m JOIN receipt_item i ON i.id=m.receipt_item_id JOIN location l ON l.id=m.location_id WHERE i.lot_id=? ORDER BY m.created_at,m.id LIMIT 20',[$lot]],
 'selection_fefo'=>['SELECT receipt_item_id,location_id,available_qty,expires_on FROM v_stock WHERE article_id=? AND available_qty>0 AND blocked=0 AND (expires_on IS NULL OR expires_on>=?) ORDER BY expires_on IS NULL,expires_on,received_at,receipt_item_id,location_id LIMIT 20',[$article,'2026-10-22']],
 'statistiques_transporteur'=>['SELECT carrier_name,COUNT(*) passages,AVG(wait_minutes),AVG(immobilized_minutes) FROM v_visit WHERE arrived_at>=? AND arrived_at<? GROUP BY carrier_id,carrier_name',['2026-08-01','2026-10-29']],
 'transporteurs_lents'=>['SELECT carrier_name,COUNT(*) passages,AVG(wait_minutes) attente FROM v_visit WHERE arrived_at>=? AND arrived_at<? AND wait_minutes IS NOT NULL GROUP BY carrier_id,carrier_name HAVING AVG(wait_minutes)>? ORDER BY attente DESC',['2026-08-01','2026-10-29',8]],
 'historique_rendez_vous'=>["SELECT reference,origine,starts_at FROM v_appointment_all WHERE dock_id=? AND starts_at>=? AND starts_at<? ORDER BY starts_at LIMIT 20",[1,'2026-08-01','2026-10-29']],
 'remplissage_zone'=>['SELECT l.zone_name,SUM(u.used_kg),SUM(l.max_kg),SUM(u.used_pallets),SUM(l.max_pallets) FROM v_location l JOIN v_location_usage u ON u.id=l.id GROUP BY l.zone_id,l.zone_name',[]],
];
$result=['date'=>date(DATE_ATOM),'database'=>$name,'engine'=>$db->scalar('SELECT VERSION()'),'php'=>PHP_VERSION,'volumes'=>[],'queries'=>[]];
foreach(['truck_visit','visit_event','appointment','stock_movement','pick','receipt_item','lot','article','location'] as $t)$result['volumes'][$t]=(int)$db->scalar('SELECT COUNT(*) FROM `'.$t.'`');
foreach($queries as $key=>[$sql,$params]){
 $db->all($sql,$params);$raw=[];
 for($i=0;$i<10;$i++){$start=hrtime(true);$rows=$db->all($sql,$params);$raw[]=(hrtime(true)-$start)/1e6;}
 $sorted=$raw;sort($sorted);
 $result['queries'][$key]=['sql'=>$sql,'params'=>$params,'raw_ms'=>$raw,'median_ms'=>($sorted[4]+$sorted[5])/2,'min_ms'=>$sorted[0],'max_ms'=>$sorted[9],'rows'=>count($rows),'explain'=>$planDb->all('EXPLAIN '.$sql,$params)];
 echo $key.' médiane '.round($result['queries'][$key]['median_ms'],3)." ms\n";
}
file_put_contents(getenv('BD70_PERF_OUT')?:__DIR__.'/../docs/preuves/performances-demo.json',json_encode($result,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
