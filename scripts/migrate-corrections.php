<?php
/** Copy to a fresh schema; source is read in a consistent transaction and never altered. */
declare(strict_types=1);
$source=$argv[1]??'';$target=$argv[2]??'';
foreach([$source,$target] as $n)if(!preg_match('/^bd70_(demo|test|restore)[a-z0-9_]+$/',$n))throw new RuntimeException('Noms de bases pédagogiques requis.');
if($source===$target)throw new RuntimeException('Cible distincte requise.');
$dsn='mysql:host=127.0.0.1;port='.(getenv('BD70_PORT')?:3307).';charset=utf8mb4';
$opts=[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC];
$from=new PDO($dsn.';dbname='.$source,getenv('BD70_ADMIN_USER')?:'root',getenv('BD70_ADMIN_PASSWORD')?:'',$opts);
$admin=new PDO($dsn,getenv('BD70_ADMIN_USER')?:'root',getenv('BD70_ADMIN_PASSWORD')?:'',$opts);
if($admin->query("SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name=".$admin->quote($target))->fetchColumn())throw new RuntimeException('Cible existante refusée.');
// Installation uses a separate process and refuses non-empty targets.
$proc=proc_open([PHP_BINARY,__DIR__.'/install.php',$target],[0=>STDIN,1=>STDOUT,2=>STDERR],$pipes);if(proc_close($proc)!==0)throw new RuntimeException('Installation échouée.');
$to=new PDO($dsn.';dbname='.$target,getenv('BD70_ADMIN_USER')?:'root',getenv('BD70_ADMIN_PASSWORD')?:'',$opts);
$triggers=$to->query('SHOW TRIGGERS')->fetchAll();foreach($triggers as $t)$to->exec('DROP TRIGGER `'.$t['Trigger'].'`');
$to->exec('DELETE FROM site_lock');
$before=$from->query("CHECKSUM TABLE ".implode(',',array_map(fn($r)=>'`'.array_values($r)[0].'`',$from->query('SHOW FULL TABLES WHERE Table_type="BASE TABLE"')->fetchAll())))->fetchAll();
$from->exec('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ');$from->exec('START TRANSACTION WITH CONSISTENT SNAPSHOT');$to->beginTransaction();
preg_match_all('/CREATE TABLE (\w+)/',file_get_contents(__DIR__.'/../sql/01_schema.sql'),$m);$counts=[];
try{
 foreach($m[1] as $table){
  $rows=$from->query('SELECT * FROM `'.$table.'`')->fetchAll();$count=0;
  foreach($rows as $row){
   if($table==='stock_movement'&&$row['kind']==='shipment'){
    $pick=$from->query('SELECT * FROM pick WHERE id='.(int)$row['pick_id'])->fetch();
    if(!$pick||($row['delta']!==null&&((int)$row['delta']!==-(int)$pick['qty']||$row['receipt_item_id']!=$pick['receipt_item_id']||$row['location_id']!=$pick['location_id'])))throw new RuntimeException('Sortie incohérente : copie arrêtée.');
    $row['delta']=$row['receipt_item_id']=$row['location_id']=null;
   }
   $cols=array_keys($row);$q=$to->prepare('INSERT INTO `'.$table.'` (`'.implode('`,`',$cols).'`) VALUES ('.implode(',',array_fill(0,count($cols),'?')).')');$q->execute(array_values($row));$count++;
  }
  $counts[$table]=$count;
 }
 $to->commit();$from->commit();
}catch(Throwable $e){if($to->inTransaction())$to->rollBack();if($from->inTransaction())$from->rollBack();throw $e;}
// Restore the exact current trigger definitions.
$delimiter=';';$buf='';foreach(file(__DIR__.'/../sql/04_triggers.sql') as $line){if(preg_match('/^DELIMITER\s+(\S+)/',trim($line),$x)){$delimiter=$x[1];continue;}$buf.=$line."\n";if(str_ends_with(trim($buf),$delimiter)){$sql=substr(trim($buf),0,-strlen($delimiter));if(trim($sql)!=='')$to->exec($sql);$buf='';}}
$after=$from->query("CHECKSUM TABLE ".implode(',',array_map(fn($t)=>'`'.$t.'`',array_keys($counts))))->fetchAll();
$beforeMap=array_column($before,'Checksum','Table');$afterMap=array_column($after,'Checksum','Table');$preserved=$beforeMap==$afterMap;
if(!$preserved)throw new RuntimeException('Source modifiée pendant la copie ; vérifier avant bascule.');
$verified=true;foreach($counts as $table=>$count){$sourceRead=$table==='stock_movement'&&(int)$from->query("SELECT COUNT(*) FROM stock_movement WHERE kind='shipment' AND delta IS NULL")->fetchColumn()>0?'v_stock_movement':$table;$rows=$from->query('SELECT * FROM `'.$sourceRead.'` ORDER BY id')->fetchAll();$copied=$to->query('SELECT * FROM `'.($table==='stock_movement'?'v_stock_movement':$table).'` ORDER BY id')->fetchAll();if(count($copied)!==$count)$verified=false;foreach($rows as $i=>$row)foreach($row as $k=>$v)if((string)$copied[$i][$k]!== (string)$v)$verified=false;}
// For an already normalized source, compare its projection instead.
if(!$verified){$rawNull=(int)$from->query("SELECT COUNT(*) FROM stock_movement WHERE kind='shipment' AND delta IS NULL")->fetchColumn();if(!$rawNull)throw new RuntimeException('Comparaison des valeurs source/cible échouée.');}
file_put_contents(__DIR__.'/../livrables/preuves/migration-corrections.json',json_encode(['source'=>$source,'target'=>$target,'source_unchanged'=>$preserved,'original_values_and_projected_movements_equal'=>$verified,'counts'=>$counts,'triggers_restored'=>count($to->query('SHOW TRIGGERS')->fetchAll())],JSON_PRETTY_PRINT));
if(!$verified)throw new RuntimeException('Copie normalisée : comparaison exhaustive non validée.');
echo "Copie migrée, source préservée et valeurs métier comparées.\n";
