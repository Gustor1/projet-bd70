<?php
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';
if (!preg_match('/^bd70_test_/',getenv('BD70_DATABASE')?:'')) throw new RuntimeException('Base de test requise.');
$db=new Database();
$reports=new Reports($db);
function check(bool $ok,string $label): void { if (!$ok) throw new RuntimeException($label); echo "OK $label\n"; }
foreach ([['2026-01-01','2027-01-01',true],['2026-01-01','2027-01-02',false],['2026-03-29','2026-03-29',true],['2026-10-25','2026-10-24',false]] as [$from,$to,$accepted]) {
    try { $reports->period(compact('from','to')); $actual=true; } catch (DomainException) { $actual=false; }
    check($actual===$accepted,"Période $from / $to");
}
$db->pdo->beginTransaction();
try {
    foreach (['2026-03-29','2026-10-25','2026-10-20'] as $day) {
        $dock=(int)$db->scalar('SELECT MIN(id) FROM dock');
        $db->insert('dock_downtime',['dock_id'=>$dock,'starts_at'=>$day.' 14:00:00','ends_at'=>$day.' 16:00:00','reason'=>'Régression heure civile']);
        $visit=$db->insert('truck_visit',['reference'=>'DST-'.$day,'driver_id'=>1,'vehicle_id'=>1,'dock_id'=>$dock,'operation'=>'reception','status'=>'finished']);
        foreach (['working'=>'00:00:00','finished'=>'12:00:00'] as $state=>$hour) $db->insert('visit_event',['visit_id'=>$visit,'state'=>$state,'happened_at'=>$day.' '.$hour,'actor_id'=>1]);
        $r=$reports->dashboard(['from'=>$day,'to'=>$day]);
        $expected=(int)$db->scalar('SELECT COUNT(*) FROM dock')*86400-7200;
        check($r['occupied']===43200.0&&$r['down']===7200.0&&$r['capacity']==$expected,"Durées civiles et taux ".($r['occupied']/$r['capacity'])." le $day");
    }
} finally { $db->pdo->rollBack(); }

