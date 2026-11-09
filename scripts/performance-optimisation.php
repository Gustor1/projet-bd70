<?php
// Mesure avant/après de l'optimisation du stock (sql/09_optimisation.sql), démarche du TD « Optimisation » :
// mesurer, optimiser, mesurer à nouveau, calculer le gain absolu et relatif.
//   BD70_DATABASE=bd70_test_xxx php scripts/performance-optimisation.php
// Base de test chargée par import-demo.php (mêmes données pour les deux mesures). Le script remet temporairement
// les anciennes définitions des vues v_balance/v_reserved (recalcul par GROUP BY sur tout l'historique) et retire
// le trigger de solde pour mesurer « avant », puis rétablit l'état optimisé, même en cas d'erreur.
// Sortie : docs/preuves/performances-optimisation.json
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';
$name=getenv('BD70_DATABASE')?:'';
if(!preg_match('/^bd70_test[a-z0-9_]*$/',$name))die("Base de test requise (bd70_test...).\n");
$db=new Database();
$admin=new Database(['dsn'=>'mysql:host=127.0.0.1;port='.(getenv('BD70_PORT')?:3307).';dbname='.$name.';charset=utf8mb4','user'=>getenv('BD70_ADMIN_USER')?:'root','password'=>getenv('BD70_ADMIN_PASSWORD')?:'','timezone'=>'Europe/Paris']);
if(!(int)$admin->scalar("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND table_name='stock_balance'"))die("Optimisation absente : lancer scripts/migrate-optimisation.php.\n");
$article=(int)$db->scalar('SELECT article_id FROM v_stock GROUP BY article_id ORDER BY COUNT(*) DESC LIMIT 1');
$owner=(int)$db->scalar('SELECT owner_id FROM article WHERE id=?',[$article]);
$zone=(int)$db->scalar('SELECT zone_id FROM v_stock WHERE article_id=? LIMIT 1',[$article]);
$cell=$db->one('SELECT receipt_item_id,location_id FROM stock_balance WHERE qty>0 ORDER BY receipt_item_id DESC LIMIT 1');
$actor=(int)$db->scalar("SELECT id FROM user_account WHERE role='warehouse' LIMIT 1");

// Requêtes de l'application touchées par l'optimisation (mêmes textes que sql/requetes_metier.sql et src/).
$reads=[
 'recherche_stock'=>['Stocks : filtres article, propriétaire, zone',"SELECT sku,lot_code,location_code,qty,available_qty FROM v_stock WHERE article_id=? AND owner_id=? AND zone_id=? ORDER BY lot_code,location_code LIMIT 20",[$article,$owner,$zone]],
 'selection_fefo'=>['Préparation : réservation FEFO','SELECT receipt_item_id,location_id,available_qty,expires_on FROM v_stock WHERE article_id=? AND available_qty>0 AND blocked=0 AND (expires_on IS NULL OR expires_on>=?) ORDER BY expires_on IS NULL,expires_on,received_at,receipt_item_id,location_id LIMIT 20',[$article,'2026-10-22']],
 'emplacements'=>['Réception : emplacements compatibles',"SELECT l.code,u.used_kg,u.used_pallets FROM v_location l JOIN v_location_usage u ON u.id=l.id JOIN article a ON a.id=? WHERE l.storage=a.storage AND l.width_m>=a.width_m AND l.height_m>=a.height_m AND l.depth_m>=a.depth_m AND u.used_kg+?*a.unit_kg<=l.max_kg AND u.used_m3+?*a.width_m*a.height_m*a.depth_m<=l.capacity_m3 AND u.used_pallets+?/a.units_per_pallet<=l.max_pallets",[$article,5,5,5]],
 'remplissage_zone'=>['Indicateurs : remplissage par zone','SELECT l.zone_name,SUM(u.used_kg),SUM(l.max_kg),SUM(u.used_pallets),SUM(l.max_pallets) FROM v_location l JOIN v_location_usage u ON u.id=l.id GROUP BY l.zone_id,l.zone_name',[]],
];
// Contrôle du stock libre avant transfert/ajustement : l'ancien texte agrège, le nouveau lit une ligne.
$free=['avant'=>"SELECT COALESCE((SELECT SUM(delta) FROM v_stock_movement WHERE receipt_item_id=? AND location_id=?),0)-COALESCE((SELECT SUM(qty) FROM pick WHERE receipt_item_id=? AND location_id=? AND status IN ('planned','confirmed')),0)",
       'apres'=>'SELECT COALESCE((SELECT qty-reserved_qty FROM stock_balance WHERE receipt_item_id=? AND location_id=?),0)'];
$freeParams=['avant'=>[$cell['receipt_item_id'],$cell['location_id'],$cell['receipt_item_id'],$cell['location_id']],'apres'=>[$cell['receipt_item_id'],$cell['location_id']]];

function serie(callable $f): array {$f();$raw=[];for($i=0;$i<15;$i++){$t=hrtime(true);$f();$raw[]=(hrtime(true)-$t)/1e6;}sort($raw);return ['median_ms'=>$raw[7],'min_ms'=>$raw[0],'max_ms'=>$raw[14],'raw_ms'=>$raw];}
function mesurer(string $etat): array {
 global $db,$admin,$reads,$free,$freeParams,$cell,$actor;$out=[];
 foreach($reads as $k=>[$label,$sql,$p]){$rows=0;$out[$k]=serie(function()use($db,$sql,$p,&$rows){$rows=count($db->all($sql,$p));})+['ecran'=>$label,'sql'=>$sql,'rows'=>$rows,'explain'=>$admin->all('EXPLAIN '.$sql,$p)];}
 $v=0;$out['stock_libre']=serie(function()use($db,$free,$freeParams,$etat,&$v){$v=(int)$db->scalar($free[$etat],$freeParams[$etat]);})+['ecran'=>'Transfert et ajustement : contrôle du stock libre','sql'=>$free[$etat],'valeur'=>$v,'explain'=>$admin->all('EXPLAIN '.$free[$etat],$freeParams[$etat])];
 // Coût d'écriture : un mouvement (triggers d'audit, et de solde « après »), annulé par ROLLBACK.
 $out['ecriture_mouvement']=serie(function()use($db,$cell,$actor){$db->pdo->beginTransaction();$db->run('SET @actor_id=?',[$actor]);try{$db->insert('stock_movement',['operation_ref'=>'PERF-OPTI-ROLLBACK','receipt_item_id'=>$cell['receipt_item_id'],'location_id'=>$cell['location_id'],'delta'=>1,'kind'=>'adjustment','reason'=>'Mesure annulée','actor_id'=>$actor]);}finally{$db->pdo->rollBack();}})+['ecran'=>'Écriture d\'un mouvement (puis ROLLBACK)'];
 return $out;
}
$apres=mesurer('apres');
$trigger=$admin->one("SELECT ACTION_STATEMENT FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=DATABASE() AND TRIGGER_NAME='balance_movement_insert'")['ACTION_STATEMENT'];
$admin->run('CREATE OR REPLACE VIEW v_balance AS SELECT receipt_item_id,location_id,SUM(delta) qty FROM v_stock_movement GROUP BY receipt_item_id,location_id');
$admin->run("CREATE OR REPLACE VIEW v_reserved AS SELECT receipt_item_id,location_id,SUM(qty) qty FROM pick WHERE status IN ('planned','confirmed') GROUP BY receipt_item_id,location_id");
$admin->run('DROP TRIGGER balance_movement_insert');
try{$avant=mesurer('avant');}
finally{
 $admin->run('CREATE TRIGGER balance_movement_insert AFTER INSERT ON stock_movement FOR EACH ROW '.$trigger);
 $admin->run('CREATE OR REPLACE VIEW v_balance AS SELECT receipt_item_id,location_id,qty FROM stock_balance');
 $admin->run('CREATE OR REPLACE VIEW v_reserved AS SELECT receipt_item_id,location_id,reserved_qty qty FROM stock_balance WHERE reserved_qty<>0');
}
$res=['date'=>date(DATE_ATOM),'database'=>$name,'engine'=>$db->scalar('SELECT VERSION()'),'php'=>PHP_VERSION,
 'volumes'=>['stock_movement'=>(int)$db->scalar('SELECT COUNT(*) FROM stock_movement'),'pick'=>(int)$db->scalar('SELECT COUNT(*) FROM pick'),'stock_balance'=>(int)$db->scalar('SELECT COUNT(*) FROM stock_balance')],
 'methode'=>'Même base et mêmes données ; 1 exécution de chauffe puis 15 mesures, médiane retenue. « Avant » : anciennes vues GROUP BY et pas de trigger de solde.','mesures'=>[]];
foreach($apres as $k=>$a){$b=$avant[$k];$res['mesures'][$k]=['ecran'=>$a['ecran'],'avant_ms'=>$b['median_ms'],'apres_ms'=>$a['median_ms'],'gain_absolu_ms'=>$b['median_ms']-$a['median_ms'],'gain_relatif_pct'=>100*($b['median_ms']-$a['median_ms'])/$b['median_ms'],'detail_avant'=>$b,'detail_apres'=>$a];
 printf("%-20s avant %8.3f ms  après %8.3f ms  gain %8.3f ms (%5.1f %%)\n",$k,$b['median_ms'],$a['median_ms'],$b['median_ms']-$a['median_ms'],$res['mesures'][$k]['gain_relatif_pct']);}
$check=(int)$admin->scalar('SELECT COUNT(*) FROM (SELECT receipt_item_id,location_id FROM v_balance_controle UNION SELECT receipt_item_id,location_id FROM stock_balance) k LEFT JOIN v_balance_controle c USING(receipt_item_id,location_id) LEFT JOIN stock_balance b USING(receipt_item_id,location_id) WHERE COALESCE(c.qty,0)<>COALESCE(b.qty,0)');
$res['ecarts_apres_mesure']=$check;echo "Écarts soldes/historique après mesure : $check\n";
file_put_contents(__DIR__.'/../docs/preuves/performances-optimisation.json',json_encode($res,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
