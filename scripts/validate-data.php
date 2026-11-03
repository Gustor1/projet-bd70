<?php
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';$db=new Database();$checks=[];$details=[];
$queries=[
 'stock_non_negatif'=>'SELECT COUNT(*) FROM v_balance WHERE qty<0',
 'reservations_couvertes'=>'SELECT COUNT(*) FROM v_stock WHERE reserved_qty>qty',
 'capacites_stock'=>'SELECT COUNT(*) FROM v_location l JOIN v_location_usage u ON u.id=l.id WHERE u.used_kg>l.max_kg+0.00001 OR u.used_m3>l.capacity_m3+0.00001 OR u.used_pallets>l.max_pallets+0.00001',
 'zones_compatibles'=>'SELECT COUNT(*) FROM v_stock_movement m JOIN receipt_item i ON i.id=m.receipt_item_id JOIN lot t ON t.id=i.lot_id JOIN article a ON a.id=t.article_id JOIN v_location l ON l.id=m.location_id WHERE a.storage<>l.storage',
 'transferts_conservatifs'=>"SELECT COUNT(*) FROM (SELECT operation_ref FROM v_stock_movement WHERE kind='transfer' GROUP BY operation_ref HAVING SUM(delta)<>0) t",
 'entrees_exactes'=>"SELECT COUNT(*) FROM receipt_item i JOIN receipt_line l ON l.id=i.line_id JOIN receipt r ON r.id=l.receipt_id LEFT JOIN (SELECT receipt_item_id,SUM(delta) qty FROM v_stock_movement WHERE kind='entry' GROUP BY receipt_item_id) m ON m.receipt_item_id=i.id WHERE r.status='validated' AND i.accepted_qty<>COALESCE(m.qty,0)",
 'colis_expedies_complets'=>"SELECT COUNT(*) FROM pick p LEFT JOIN (SELECT pick_id,SUM(qty) qty FROM package_pick GROUP BY pick_id) pp ON pp.pick_id=p.id WHERE p.status='shipped' AND p.qty<>COALESCE(pp.qty,0)",
 'colis_pas_de_surallocation'=>'SELECT COUNT(*) FROM pick p JOIN (SELECT pick_id,SUM(qty) qty FROM package_pick GROUP BY pick_id) pp ON pp.pick_id=p.id WHERE pp.qty>p.qty',
 'colis_meme_commande'=>'SELECT COUNT(*) FROM package_pick pp JOIN package c ON c.id=pp.package_id JOIN pick p ON p.id=pp.pick_id JOIN order_line l ON l.id=p.order_line_id WHERE c.order_id<>l.order_id',
 'sorties_exactes'=>"SELECT COUNT(*) FROM pick p LEFT JOIN v_stock_movement m ON m.pick_id=p.id WHERE p.status='shipped' AND (m.id IS NULL OR m.delta<>-p.qty OR m.receipt_item_id<>p.receipt_item_id OR m.location_id<>p.location_id)",
 'quantites_commandes_expediees'=>"SELECT COUNT(*) FROM order_line l JOIN customer_order o ON o.id=l.order_id LEFT JOIN (SELECT order_line_id,SUM(qty) qty FROM pick WHERE status='shipped' GROUP BY order_line_id) p ON p.order_line_id=l.id WHERE o.status='shipped' AND l.qty<>COALESCE(p.qty,0)",
 'aucun_lot_perime_a_expedition'=>"SELECT COUNT(*) FROM pick p JOIN order_line ol ON ol.id=p.order_line_id JOIN shipment s ON s.order_id=ol.order_id JOIN receipt_item i ON i.id=p.receipt_item_id JOIN lot l ON l.id=i.lot_id WHERE p.status='shipped' AND l.expires_on<DATE(s.shipped_at)",
 'chronologie_camions'=>'SELECT COUNT(*) FROM v_visit WHERE working_at<arrived_at OR finished_at<working_at OR departed_at<finished_at',
 'occupation_quai_sans_chevauchement'=>"SELECT COUNT(*) FROM v_visit a JOIN v_visit b ON a.dock_id=b.dock_id AND a.id<b.id AND a.working_at<COALESCE(b.finished_at,NOW()) AND b.working_at<COALESCE(a.finished_at,NOW())",
 'rendez_vous_sans_chevauchement'=>"SELECT COUNT(*) FROM appointment a JOIN appointment b ON a.id<b.id AND a.status='active' AND b.status='active' AND a.starts_at<b.ends_at AND b.starts_at<a.ends_at AND (a.dock_id=b.dock_id OR a.driver_id=b.driver_id OR a.vehicle_id=b.vehicle_id OR a.trailer_id=b.trailer_id)",
 'reserve_rattachement_unique'=>'SELECT COUNT(*) FROM receipt_reserve WHERE (receipt_id IS NULL)=(line_id IS NULL)',
 'proprietaire_commande'=>'SELECT COUNT(*) FROM order_line l JOIN customer_order o ON o.id=l.order_id JOIN article a ON a.id=l.article_id WHERE o.owner_id<>a.owner_id',
 'article_lot_reception'=>'SELECT COUNT(*) FROM receipt_item i JOIN receipt_line l ON l.id=i.line_id JOIN notice_line n ON n.id=l.notice_line_id JOIN lot t ON t.id=i.lot_id WHERE n.article_id<>t.article_id',
 'stock_bloque_perime_indisponible'=>'SELECT COUNT(*) FROM v_stock WHERE (blocked=1 OR expires_on<CURRENT_DATE()) AND available_qty<>0',
 'operations_chargement_coherentes'=>"SELECT COUNT(*) FROM shipment s JOIN v_visit v ON v.id=s.visit_id WHERE v.operation<>'expedition' OR s.shipped_at<v.working_at OR (v.finished_at IS NOT NULL AND s.shipped_at>v.finished_at)",
 'aucun_secret_audit'=>"SELECT COUNT(*) FROM audit_log WHERE details LIKE '%password_hash%'",
];
foreach($queries as $key=>$sql){$count=(int)$db->scalar($sql);$checks[$key]=$count===0;$details[$key]=$count;echo ($count?'ECHEC ':'OK ').$key.' : '.$count."\n";}
// Toutes les contraintes FK réellement définies, pas uniquement quelques exemples.
foreach($db->all('SELECT TABLE_NAME,COLUMN_NAME,REFERENCED_TABLE_NAME,REFERENCED_COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA=DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL') as $f){$sql='SELECT COUNT(*) FROM `'.$f['TABLE_NAME'].'` c LEFT JOIN `'.$f['REFERENCED_TABLE_NAME'].'` p ON p.`'.$f['REFERENCED_COLUMN_NAME'].'`=c.`'.$f['COLUMN_NAME'].'` WHERE c.`'.$f['COLUMN_NAME'].'` IS NOT NULL AND p.`'.$f['REFERENCED_COLUMN_NAME'].'` IS NULL';$checks['fk_'.$f['TABLE_NAME'].'_'.$f['COLUMN_NAME']]=(int)$db->scalar($sql)===0;}
$result=['database'=>$db->scalar('SELECT DATABASE()'),'date'=>Clock::now(),'timezone'=>'Europe/Paris','checks'=>$checks,'anomalies'=>$details];file_put_contents(__DIR__.'/../livrables/preuves/integrite-donnees.json',json_encode($result,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));echo count($checks).' contrôles, '.count(array_filter($checks,fn($v)=>!$v))." échecs\n";exit(in_array(false,$checks,true)?1:0);
