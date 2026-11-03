<?php
declare(strict_types=1);
// Migration additive. Les DDL MariaDB valident implicitement : sauvegarde obligatoire.
$name=$argv[1]??'';$backup=$argv[2]??'';
if(!preg_match('/^bd70_(demo|test|restore)[a-z0-9_]*$/',$name)||!is_file($backup)||filesize($backup)<1000){fwrite(STDERR,"Usage : php scripts/migrate.php bd70_restore_copie chemin/backup.sql\nTester d’abord sur une restauration distincte.\n");exit(1);}
$admin=new PDO('mysql:host=127.0.0.1;port='.(getenv('BD70_PORT')?:3307).';dbname='.$name.';charset=utf8mb4',getenv('BD70_ADMIN_USER')?:'root',getenv('BD70_ADMIN_PASSWORD')?:'',[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
if($admin->query("SHOW COLUMNS FROM supplier_notice LIKE 'closed_at'")->fetch()){echo "Schéma déjà actualisé ; aucune écriture effectuée.\n";exit;}
function executeFile(PDO $db,string $path,bool $replaceViews=false):void{
 $text=file_get_contents($path);if($replaceViews)$text=str_replace('CREATE VIEW','CREATE OR REPLACE VIEW',$text);$delimiter=';';$buffer='';
 foreach(explode("\n",$text) as $line){if(preg_match('/^DELIMITER\s+(\S+)/',trim($line),$m)){$delimiter=$m[1];continue;}$buffer.=$line."\n";if(str_ends_with(trim($buffer),$delimiter)){$db->exec(substr(trim($buffer),0,-strlen($delimiter)));$buffer='';}}
}
$root=dirname(__DIR__);
executeFile($admin,$root.'/sql/migrations/20261028_completion.sql');
executeFile($admin,$root.'/sql/02_vues.sql',true);
foreach($admin->query('SHOW TRIGGERS')->fetchAll(PDO::FETCH_ASSOC) as $trigger)$admin->exec('DROP TRIGGER `'.str_replace('`','``',$trigger['Trigger']).'`');
executeFile($admin,$root.'/sql/04_triggers.sql');
$cfg=require $root.'/config/local.php';$app=$admin->quote($cfg['user']);
$admin->exec("GRANT SELECT, EXECUTE ON `$name`.* TO $app@'127.0.0.1'");
foreach($admin->query('SHOW FULL TABLES WHERE Table_type="BASE TABLE"')->fetchAll(PDO::FETCH_COLUMN) as $table){
 if(in_array($table,['audit_log','site_lock'],true))continue;
 $rights=in_array($table,['stock_movement','visit_event','shipment','receipt_reserve'],true)?'INSERT':'INSERT, UPDATE, DELETE';
 $admin->exec("GRANT $rights ON `$name`.`$table` TO $app@'127.0.0.1'");
}
echo "Migration additive terminée sur $name ; allocations historiques conservées.\n";
