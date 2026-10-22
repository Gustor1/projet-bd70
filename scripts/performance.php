<?php
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';
require_once __DIR__.'/seed.php';
$name=getenv('BD70_DATABASE')?:'bd70_perf';if(!preg_match('/^bd70_perf[a-z0-9_]*$/',$name))die("Base de performance distincte requise.\n");putenv('BD70_DATABASE='.$name);
$db=new Database();
if(!$db->scalar('SELECT COUNT(*) FROM user_account'))seed($db);
$size=max(100,min(50000,(int)($argv[1]??10000)));$receipts=max(100,(int)($size/5));
if(!$db->scalar("SELECT COUNT(*) FROM truck_visit WHERE reference LIKE 'PERF-%'")){
 $db->transaction(1,function()use($db,$size,$receipts){
  $db->run('UPDATE location SET max_kg=?,max_pallets=? WHERE id IN (1,2)',[max(30000,$receipts*4),max(100,$receipts/20+20)]);
  $base=new DateTimeImmutable('2025-01-01 00:00:00');$in=[];
  for($i=0;$i<$size;$i++){
   $date=$base->modify('+'.$i.' hours');$dock=$i%3+1;$driver=$i%2+1;$vehicle=$i%2+1;$operation=$dock===3?'expedition':'reception';
   $a=$db->insert('appointment',['reference'=>'PERF-RDV-'.$i,'dock_id'=>$dock,'driver_id'=>$driver,'vehicle_id'=>$vehicle,'operation'=>$operation,'starts_at'=>$date->format('Y-m-d H:i:s'),'ends_at'=>$date->modify('+50 minutes')->format('Y-m-d H:i:s')]);
   $v=$db->insert('truck_visit',['reference'=>'PERF-PASS-'.$i,'appointment_id'=>$a,'driver_id'=>$driver,'vehicle_id'=>$vehicle,'operation'=>$operation,'dock_id'=>$dock,'status'=>'departed','document_note'=>'Simulation volumétrique, documents conformes']);
   foreach(['arrived'=>0,'checked'=>5,'called'=>10,'working'=>15,'finished'=>35,'departed'=>45] as $state=>$minute)$db->insert('visit_event',['visit_id'=>$v,'state'=>$state,'happened_at'=>$date->modify('+'.$minute.' minutes')->format('Y-m-d H:i:s'),'actor_id'=>1]);
   if($operation==='reception'&&count($in)<$receipts)$in[]=[$v,$date];
  }
  $lot=$db->insert('lot',['article_id'=>1,'code'=>'LOT-PERFORMANCE','expires_on'=>'2028-12-31']);$items=[];
  foreach($in as $i=>[$visit,$date]){
   $n=$db->insert('supplier_notice',['reference'=>'PERF-AVIS-'.$i,'supplier_id'=>1,'expected_on'=>$date->format('Y-m-d')]);
   $nl=$db->insert('notice_line',['notice_id'=>$n,'article_id'=>1,'expected_qty'=>1]);
   $r=$db->insert('receipt',['reference'=>'PERF-REC-'.$i,'notice_id'=>$n,'visit_id'=>$visit,'status'=>'validated','validated_at'=>$date->modify('+30 minutes')->format('Y-m-d H:i:s')]);
   $rl=$db->insert('receipt_line',['receipt_id'=>$r,'notice_line_id'=>$nl,'expected_qty'=>1]);$location=$i%2+1;
   $it=$db->insert('receipt_item',['line_id'=>$rl,'lot_id'=>$lot,'pallet_code'=>'PERF-PAL-'.$i,'accepted_qty'=>1,'location_id'=>$location]);$items[]=[$it,$location];
   $db->insert('stock_movement',['operation_ref'=>'PERF-ENTRY-'.$i,'receipt_item_id'=>$it,'location_id'=>$location,'delta'=>1,'kind'=>'entry','reason'=>'Jeu volumétrique fictif','actor_id'=>1,'created_at'=>$date->modify('+30 minutes')->format('Y-m-d H:i:s')]);
  }
  $time=$base->modify('+'.$size.' hours')->modify('+1 day');
  for($i=0;$i<$size;$i++){
   [$item,$original]=$items[$i%count($items)];$source=(intdiv($i,count($items))%2)===0?$original:3-$original;$destination=3-$source;
   foreach([[$source,-1],[$destination,1]] as [$location,$delta])$db->insert('stock_movement',['operation_ref'=>'PERF-TRF-'.$i,'receipt_item_id'=>$item,'location_id'=>$location,'delta'=>$delta,'kind'=>'transfer','reason'=>'Transfert simulé conservatif','actor_id'=>1,'created_at'=>$time->modify('+'.$i.' seconds')->format('Y-m-d H:i:s')]);
  }
 });echo "Volume créé : $size passages, $receipts réceptions et ".($receipts+2*$size)." mouvements supplémentaires.\n";
}
$queries=[
 'disponibilite_quai'=>["SELECT reference FROM appointment WHERE dock_id=? AND status='active' AND starts_at<? AND ends_at>?",[1,'2025-05-02 09:00:00','2025-05-02 08:00:00']],
 'recherche_passages'=>["SELECT reference,carrier_name,status,arrived_at FROM v_visit WHERE arrived_at>=? AND arrived_at<? AND carrier_id=? AND status=? ORDER BY arrived_at DESC LIMIT 20",['2025-05-01','2025-06-01',1,'departed']],
 'recherche_stock'=>["SELECT sku,lot_code,location_code,qty,available_qty FROM v_stock WHERE article_id=? AND owner_id=? AND zone_id=? ORDER BY lot_code,location_code LIMIT 20",[1,1,1]],
 'emplacements'=>["SELECT l.code,u.used_kg,u.used_pallets FROM v_location l JOIN v_location_usage u ON u.id=l.id JOIN article a ON a.id=? WHERE l.storage=a.storage AND l.width_m>=a.width_m AND l.height_m>=a.height_m AND l.depth_m>=a.depth_m AND u.used_kg+?*a.unit_kg<=l.max_kg AND u.used_m3+?*a.width_m*a.height_m*a.depth_m<=l.capacity_m3 AND u.used_pallets+?/a.units_per_pallet<=l.max_pallets",[1,5,5,5]],
 'historique_lot'=>['SELECT m.operation_ref,m.created_at,m.delta,l.code FROM stock_movement m JOIN receipt_item i ON i.id=m.receipt_item_id JOIN location l ON l.id=m.location_id WHERE i.lot_id=? ORDER BY m.created_at,m.id LIMIT 20',[7]],
 'selection_fefo'=>['SELECT receipt_item_id,location_id,available_qty,expires_on FROM v_stock WHERE article_id=? AND available_qty>0 AND blocked=0 AND (expires_on IS NULL OR expires_on>=?) ORDER BY expires_on IS NULL,expires_on,received_at,receipt_item_id,location_id LIMIT 20',[1,'2026-10-22']],
 'statistiques_transporteur'=>['SELECT carrier_name,COUNT(*) passages,AVG(wait_minutes),AVG(immobilized_minutes) FROM v_visit WHERE arrived_at>=? AND arrived_at<? GROUP BY carrier_id,carrier_name',['2025-05-01','2025-06-01']],
 'remplissage_zone'=>['SELECT l.zone_name,SUM(u.used_kg),SUM(l.max_kg),SUM(u.used_pallets),SUM(l.max_pallets) FROM v_location l JOIN v_location_usage u ON u.id=l.id GROUP BY l.zone_id,l.zone_name',[]],
];
$planDb=new Database(['dsn'=>'mysql:host=127.0.0.1;port=3307;dbname='.$name.';charset=utf8mb4','user'=>getenv('BD70_ADMIN_USER')?:'root','password'=>getenv('BD70_ADMIN_PASSWORD')?:'','timezone'=>'Europe/Paris']);
function measure(Database $db,string $sql,array $params): array {
 global $planDb;
 $db->all($sql,$params);$raw=[];for($i=0;$i<10;$i++){$start=hrtime(true);$rows=$db->all($sql,$params);$raw[]=(hrtime(true)-$start)/1e6;}
 $sorted=$raw;sort($sorted);return ['sql'=>$sql,'params'=>$params,'raw_ms'=>$raw,'median_ms'=>($sorted[4]+$sorted[5])/2,'min_ms'=>$sorted[0],'max_ms'=>$sorted[9],'rows'=>count($rows),'explain'=>$planDb->all('EXPLAIN '.$sql,$params)];
}
function measureWrite(Database $db): array {
 $raw=[];
 for($i=-1;$i<10;$i++){
  $db->pdo->beginTransaction();$db->run('SET @actor_id=1');$start=hrtime(true);
  try{$db->insert('appointment',['reference'=>'PERF-WRITE-ROLLBACK','dock_id'=>1,'driver_id'=>1,'vehicle_id'=>1,'operation'=>'reception','starts_at'=>'2060-01-01 08:00:00','ends_at'=>'2060-01-01 09:00:00']);}finally{$db->pdo->rollBack();}
  if($i>=0)$raw[]=(hrtime(true)-$start)/1e6;
 }
 $sorted=$raw;sort($sorted);return ['operation'=>'INSERT rendez-vous et son trigger, suivi de ROLLBACK ; mêmes valeurs, aucune ligne conservée','raw_ms'=>$raw,'median_ms'=>($sorted[4]+$sorted[5])/2,'min_ms'=>$sorted[0],'max_ms'=>$sorted[9]];
}
$measurements=[];foreach($queries as $key=>[$sql,$p]){$measurements[$key]=measure($db,$sql,$p);echo $key.' médiane '.round($measurements[$key]['median_ms'],3)." ms\n";}
$volumes=[];$indexes=[];foreach($db->all('SHOW FULL TABLES WHERE Table_type="BASE TABLE"') as $row){$table=array_values($row)[0];$volumes[$table]=(int)$db->scalar('SELECT COUNT(*) FROM `'.$table.'`');$indexes[$table]=$db->all('SHOW INDEX FROM `'.$table.'`');}
$checks=['stock_non_negatif'=>(int)$db->scalar('SELECT COUNT(*) FROM v_balance WHERE qty<0')===0,'capacites'=>(int)$db->scalar('SELECT COUNT(*) FROM v_location l JOIN v_location_usage u ON u.id=l.id WHERE u.used_kg>l.max_kg OR u.used_pallets>l.max_pallets OR u.used_m3>l.capacity_m3')===0,'transferts_conserves'=>(int)$db->scalar("SELECT COUNT(*) FROM (SELECT operation_ref FROM stock_movement WHERE kind='transfer' GROUP BY operation_ref HAVING SUM(delta)<>0) x")===0];
$cfg=$db->one('SELECT @@innodb_buffer_pool_size buffer_pool_bytes,@@max_connections max_connections,@@tx_isolation isolation_level');
// Comparaison contrôlée sur la seule base volumétrique, avec le compte d'installation.
$admin=new PDO('mysql:host=127.0.0.1;port=3307;dbname='.$name.';charset=utf8mb4',getenv('BD70_ADMIN_USER')?:'root',getenv('BD70_ADMIN_PASSWORD')?:'',[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
// Un index FK de remplacement maintient les contraintes pendant le retrait du composé.
$admin->exec('CREATE INDEX IF NOT EXISTS idx_appt_dock_baseline ON appointment(dock_id)');
$admin->exec('ALTER TABLE appointment DROP INDEX idx_appointment_slot');
try{$before=measure($db,...$queries['disponibilite_quai']);$writeBefore=measureWrite($db);}finally{$admin->exec('CREATE INDEX idx_appointment_slot ON appointment(dock_id,status,starts_at,ends_at)');}
$after=measure($db,...$queries['disponibilite_quai']);
$writeAfter=measureWrite($db);
$result=['date'=>date(DATE_ATOM),'database'=>$name,'engine'=>$db->scalar('SELECT VERSION()'),'php'=>PHP_VERSION,'os'=>php_uname(),'config'=>$cfg,'seed'=>70,'reference_date'=>'2026-10-22','volumes'=>$volumes,'indexes'=>$indexes,'checks'=>$checks,'queries'=>$measurements,'comparison'=>['changed'=>'idx_appointment_slot uniquement ; index FK simple maintenu','before'=>$before,'after'=>$after,'write_before'=>$writeBefore,'write_after'=>$writeAfter]];
file_put_contents(__DIR__.'/../livrables/preuves/performances.json',json_encode($result,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
$text="-- Requêtes réellement mesurées, paramètres dans performances.json.\n";foreach($queries as $key=>[$sql,$p])$text.="\n-- $key\n$sql;\n";file_put_contents(__DIR__.'/../sql/requetes_metier.sql',$text);
if(in_array(false,$checks,true))throw new RuntimeException('Jeu volumétrique incohérent.');
