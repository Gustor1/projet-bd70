<?php
// Installation non destructive : refuse une base non vide.
declare(strict_types=1);
require __DIR__.'/../src/Database.php';
$name=$argv[1]??'bd70_demo';
if (!preg_match('/^bd70_(demo|test|perf|restore)[a-z0-9_]*$/',$name)) die("Nom limité aux bases BD70 de démonstration/test.\n");
$admin=new PDO('mysql:host=127.0.0.1;port='.(getenv('BD70_PORT')?:3307).';charset=utf8mb4',getenv('BD70_ADMIN_USER')?:'root',getenv('BD70_ADMIN_PASSWORD')?:'',[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
$admin->exec("CREATE DATABASE IF NOT EXISTS `$name` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
$admin->exec("USE `$name`");
if ((int)$admin->query('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE()')->fetchColumn()) die("Installation refusée : base non vide.\n");
foreach (['01_schema','02_vues','03_procedures','04_triggers','05_index'] as $file) {
 $text=file_get_contents(__DIR__.'/../sql/'.$file.'.sql'); $delimiter=';';$buf='';
 foreach (explode("\n",$text) as $line) {
  if (preg_match('/^DELIMITER\s+(\S+)/',trim($line),$m)) { $delimiter=$m[1]; continue; }
  $buf.=$line."\n";
  if (str_ends_with(trim($buf),$delimiter)) { $sql=substr(trim($buf),0,-strlen($delimiter)); if(trim($sql)!=='')$admin->exec($sql);$buf=''; }
 }
 echo "$file installé\n";
}
// Même compte applicatif local pour les bases de test désignées, secret généré hors dépôt.
$configFile=__DIR__.'/../config/local.php';
if(file_exists($configFile)) $cfg=require $configFile;
else $cfg=['dsn'=>'mysql:host=127.0.0.1;port='.(getenv('BD70_PORT')?:3307).';dbname='.$name.';charset=utf8mb4','user'=>'bd70_app_'.bin2hex(random_bytes(4)),'password'=>bin2hex(random_bytes(24)),'timezone'=>'Europe/Paris'];
$pw=$admin->quote($cfg['password']);
$appUser=$admin->quote($cfg['user']);
$admin->exec("CREATE USER IF NOT EXISTS $appUser@'127.0.0.1' IDENTIFIED BY $pw");
$admin->exec("GRANT SELECT, EXECUTE ON `$name`.* TO $appUser@'127.0.0.1'");
$tables=$admin->query('SHOW FULL TABLES WHERE Table_type="BASE TABLE"')->fetchAll(PDO::FETCH_COLUMN);
foreach($tables as $table) {
 if(in_array($table,['audit_log','site_lock'],true))continue;
 $rights=in_array($table,['stock_movement','visit_event','shipment'],true)?'INSERT':'INSERT, UPDATE, DELETE';
 $admin->exec("GRANT $rights ON `$name`.`$table` TO $appUser@'127.0.0.1'");
}
if(!file_exists($configFile))file_put_contents($configFile,"<?php\nreturn ".var_export($cfg,true).";\n");
echo "Base $name prête ; configuration locale exclue de Git.\n";
