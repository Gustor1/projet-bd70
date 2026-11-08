<?php
// Ajoute à une base BD70 existante les objets de sql/08_historisation.sql (table d'historique, vue UNION ALL,
// triggers anti-chevauchement, procédure d'archivage, évènement). Idempotent : ne fait rien si déjà présent.
// Aucune donnée existante n'est modifiée ; l'évènement n'archive que les rendez-vous terminés depuis plus d'un an.
//   php scripts/migrate-historisation.php            (base désignée par config/local.php)
//   php scripts/migrate-historisation.php bd70_xxx   (base explicite)
declare(strict_types=1);
$name=$argv[1]??'';
if($name===''){
 $cfgFile=__DIR__.'/../config/local.php';
 if(!file_exists($cfgFile)){fwrite(STDERR,"config/local.php absent : préciser la base.\n");exit(1);}
 $cfg=require $cfgFile;preg_match('/dbname=([^;]+)/',$cfg['dsn'],$m);$name=$m[1]??'';
}
if(!preg_match('/^bd70_(demo|test|perf|restore)[a-z0-9_]*$/',$name)){fwrite(STDERR,"Nom limité aux bases BD70.\n");exit(1);}
$admin=new PDO('mysql:host=127.0.0.1;port='.(getenv('BD70_PORT')?:3307).';dbname='.$name.';charset=utf8mb4',getenv('BD70_ADMIN_USER')?:'root',getenv('BD70_ADMIN_PASSWORD')?:'',[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
if((int)$admin->query("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND table_name='appointment_archive'")->fetchColumn()){echo "Historisation déjà installée dans $name.\n";exit(0);}
if(!(int)$admin->query("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND table_name='appointment'")->fetchColumn()){fwrite(STDERR,"Base $name non installée.\n");exit(1);}
// Les triggers ne contrôlent que les écritures futures : d'éventuels chevauchements anciens sont seulement signalés.
$overlaps=(int)$admin->query("SELECT COUNT(*) FROM appointment a JOIN appointment b ON a.dock_id=b.dock_id AND a.id<b.id AND a.status='active' AND b.status='active' AND a.starts_at<b.ends_at AND b.starts_at<a.ends_at")->fetchColumn();
if($overlaps)echo "Attention : $overlaps couples de rendez-vous actifs se chevauchent déjà ; ils restent inchangés.\n";
$text=file_get_contents(__DIR__.'/../sql/08_historisation.sql');$delimiter=';';$buf='';
foreach(explode("\n",$text) as $line){
 if(preg_match('/^DELIMITER\s+(\S+)/',trim($line),$m)){$delimiter=$m[1];continue;}
 $buf.=$line."\n";
 if(str_ends_with(trim($buf),$delimiter)){$sql=substr(trim($buf),0,-strlen($delimiter));if(trim($sql)!=='')$admin->exec($sql);$buf='';}
}
echo "Historisation ajoutée à $name : appointment_archive, v_appointment_all, 2 triggers, archive_appointments, ev_archive_appointments.\n";
echo "Pour exécuter l'évènement automatiquement : SET GLOBAL event_scheduler=ON (compte administrateur).\n";
