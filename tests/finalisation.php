<?php
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';
if(!preg_match('/^bd70_test_/',getenv('BD70_DATABASE')?:''))die("Base de test dédiée requise.\n");
putenv('BD70_NOW=2026-10-22 12:00:00');
$db=new Database();$cat=new Catalog($db);$checks=[];
function check(bool $ok,string $name):void{global $checks;$checks[$name]=$ok;echo ($ok?'OK ':'ECHEC ').$name."\n";}
function rejects(callable $fn,string $name):void{try{$fn();check(false,$name);}catch(DomainException|PDOException){check(true,$name);}}
$r=$db->one("SELECT * FROM receipt WHERE status='validated' LIMIT 1");
$before=$db->one('SELECT COUNT(*) n,SUM(delta) qty FROM v_stock_movement');
check($cat->restrictions('receipt',$r)['edit']!==null,'Réception validée sans action Modifier');
rejects(fn()=>$cat->save('receipt',(int)$r['id'],[...$r,'reference'=>'INTERDIT'],1),'POST direct refuse édition réception validée');
rejects(fn()=>$cat->delete('receipt',(int)$r['id'],1),'POST direct refuse suppression réception validée');
$a=$db->one('SELECT * FROM article WHERE id=1');
check(in_array('unit_kg',$cat->protectedFields('article',$a),true)&&!in_array('name',$cat->protectedFields('article',$a),true),'Champs structurels protégés et désignation disponible');
check($cat->restrictions('vehicle',$db->one('SELECT * FROM vehicle WHERE id=1'))['edit']!==null,'Véhicule utilisé sans action Modifier inutile');
$cat->save('article',1,[...$a,'name'=>'Désignation corrigée'],1);
check($db->scalar('SELECT name FROM article WHERE id=1')==='Désignation corrigée','Article utilisé : libellé modifiable');
rejects(fn()=>$cat->save('article',1,[...$a,'unit_kg'=>999],1),'Article utilisé : poids protégé');
$used=$db->one('SELECT a.* FROM appointment a JOIN truck_visit v ON v.appointment_id=a.id LIMIT 1');
check($cat->restrictions('appointment',$used)['edit']!==null,'Rendez-vous utilisé sans modification ni annulation');
$notice=$cat->save('supplier_notice',null,['reference'=>'CLOSED-EMPTY','supplier_id'=>1,'expected_on'=>'2026-10-22'],1);
$line=$cat->save('notice_line',null,['notice_id'=>$notice,'article_id'=>1,'expected_qty'=>1],1);
(new Warehouse($db,1))->closeNotice($notice,'Avis créé par erreur, annulé avant réception');
$n=$db->one('SELECT * FROM supplier_notice WHERE id=?',[$notice]);
check($cat->restrictions('supplier_notice',$n)['edit']!==null,'Avis clôturé sans réception protégé dans interface');
rejects(fn()=>$cat->save('supplier_notice',$notice,[...$n,'reference'=>'REWRITE'],1),'Avis clôturé : édition directe refusée');
rejects(fn()=>$cat->delete('notice_line',$line,1),'Avis clôturé : suppression de ligne refusée');
$draft=$cat->save('supplier_notice',null,['reference'=>'DRAFT-CORRECTION','supplier_id'=>1,'expected_on'=>'2026-10-22'],1);
$dl=$cat->save('notice_line',null,['notice_id'=>$draft,'article_id'=>1,'expected_qty'=>1],1);
$old=$db->one('SELECT * FROM notice_line WHERE id=?',[$dl]);
$cat->save('notice_line',$dl,[...$old,'expected_qty'=>2],1);$cat->delete('notice_line',$dl,1);$cat->delete('supplier_notice',$draft,1);
check(!$db->scalar('SELECT COUNT(*) FROM supplier_notice WHERE id=?',[$draft]),'Brouillon : correction puis suppression sans SQL utilisateur');
check($cat->restrictions('carrier',$db->one('SELECT * FROM carrier WHERE id=1'))['delete']!==null,'Fiche référencée sans suppression proposée');
check($before===$db->one('SELECT COUNT(*) n,SUM(delta) qty FROM v_stock_movement'),'Corrections sans altération des mouvements historiques');
$result=['executed_at'=>gmdate(DATE_ATOM),'database'=>getenv('BD70_DATABASE'),'fixed_clock'=>Clock::now(),'passed'=>count(array_filter($checks)),'failed'=>count(array_filter($checks,fn($v)=>!$v)),'checks'=>$checks];
file_put_contents(__DIR__.'/../livrables/preuves/finalisation.json',json_encode($result,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
exit($result['failed']?1:0);
