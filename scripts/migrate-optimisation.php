<?php
// Ajoute à une base BD70 existante les objets de sql/09_optimisation.sql : table stock_balance tenue à jour par
// triggers, vues v_balance/v_reserved réécrites, vue de contrôle, fonction stock_disponible, puis initialise les
// soldes depuis l'historique dans une transaction. Idempotent : ne fait rien si stock_balance existe déjà.
// Les mouvements et réservations existants ne sont pas modifiés ; le script vérifie ensuite que chaque solde
// est égal au recalcul complet depuis l'historique.
//   php scripts/migrate-optimisation.php            (base désignée par config/local.php)
//   php scripts/migrate-optimisation.php bd70_xxx   (base explicite)
declare(strict_types=1);
$name=$argv[1]??'';
if($name===''){
 $cfgFile=__DIR__.'/../config/local.php';
 if(!file_exists($cfgFile)){fwrite(STDERR,"config/local.php absent : préciser la base.\n");exit(1);}
 $cfg=require $cfgFile;preg_match('/dbname=([^;]+)/',$cfg['dsn'],$m);$name=$m[1]??'';
}
if(!preg_match('/^bd70_(demo|test|perf|restore)[a-z0-9_]*$/',$name)){fwrite(STDERR,"Nom limité aux bases BD70.\n");exit(1);}
$admin=new PDO('mysql:host=127.0.0.1;port='.(getenv('BD70_PORT')?:3307).';dbname='.$name.';charset=utf8mb4',getenv('BD70_ADMIN_USER')?:'root',getenv('BD70_ADMIN_PASSWORD')?:'',[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
$exists=fn(string $t)=>(int)$admin->query("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND table_name='$t'")->fetchColumn();
if($exists('stock_balance')){echo "Optimisation du stock déjà installée dans $name.\n";exit(0);}
if(!$exists('stock_movement')){fwrite(STDERR,"Base $name non installée.\n");exit(1);}
$text=file_get_contents(__DIR__.'/../sql/09_optimisation.sql');$delimiter=';';$buf='';
foreach(explode("\n",$text) as $line){
 if(preg_match('/^DELIMITER\s+(\S+)/',trim($line),$m)){$delimiter=$m[1];continue;}
 $buf.=$line."\n";
 if(str_ends_with(trim($buf),$delimiter)){$sql=substr(trim($buf),0,-strlen($delimiter));if(trim($sql)!=='')$admin->exec($sql);$buf='';}
}
$rows=(int)$admin->query('SELECT COUNT(*) FROM stock_balance')->fetchColumn();
$diff=(int)$admin->query("SELECT COUNT(*) FROM (SELECT receipt_item_id,location_id FROM v_balance_controle UNION SELECT receipt_item_id,location_id FROM stock_balance) k
 LEFT JOIN v_balance_controle c USING(receipt_item_id,location_id) LEFT JOIN stock_balance b USING(receipt_item_id,location_id)
 WHERE COALESCE(c.qty,0)<>COALESCE(b.qty,0)")->fetchColumn();
echo "Optimisation ajoutée à $name : $rows soldes initialisés, $diff écart avec le recalcul depuis l'historique.\n";
if($diff){fwrite(STDERR,"Soldes incohérents : vérifier la base.\n");exit(1);}
