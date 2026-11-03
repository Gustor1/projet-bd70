<?php
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';
if(!preg_match('/^bd70_test_/',getenv('BD70_DATABASE')?:''))die("Base de test requise.\n");
$results=[];
foreach(['2026-01-15 23:59:59','2026-07-15 00:00:00','2026-10-25 01:30:00','2026-10-25 03:30:00'] as $time){
    putenv('BD70_NOW='.$time);$db=new Database();
    $results[$time]=$db->scalar('SELECT NOW()')===$time&&$db->scalar('SELECT CURRENT_DATE()')===substr($time,0,10);
    if(Warehouse::datetime($time)!==$time)$results[$time]=false;
}
foreach(['2026-03-29 02:30:00','2026-10-25 02:30:00'] as $time){try{Warehouse::datetime($time);$results['refus '.$time]=false;}catch(DomainException){$results['refus '.$time]=true;}}
putenv('BD70_NOW=2026-10-22 12:00:00');$db=new Database();$report=(new Reports($db))->dashboard(['from'=>'2040-01-01','to'=>'2040-01-01']);
$results['DLC indépendantes de la période d’activité']=$report['reference']==='2026-10-22';
$results['période vide sans exception']=$report['carriers']===[];
echo json_encode($results,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE)."\n";
file_put_contents(__DIR__.'/../livrables/preuves/heure-paris.json',json_encode($results,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
exit(in_array(false,$results,true)?1:0);
