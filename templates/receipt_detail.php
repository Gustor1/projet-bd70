<?php
$r=$db->one('SELECT r.*,n.reference notice,s.name supplier_name,v.reference visit_reference FROM receipt r JOIN supplier_notice n ON n.id=r.notice_id JOIN supplier s ON s.id=n.supplier_id JOIN truck_visit v ON v.id=r.visit_id WHERE r.id=?',[(int)($_GET['id']??0)]);
$lines=$db->all('SELECT l.*,n.article_id,a.sku,a.name,d.received_qty,d.missing_qty,d.excess_qty,d.damaged_qty FROM receipt_line l JOIN notice_line n ON n.id=l.notice_line_id JOIN article a ON a.id=n.article_id JOIN v_receipt_discrepancy d ON d.id=l.id WHERE l.receipt_id=? ORDER BY l.id',[$r['id']]);
?>
<div class="page-heading"><div><p class="context">Réception guidée</p><h1><?= h($r['reference']) ?></h1><p><?= h($r['supplier_name'].' · '.$r['notice'].' · '.$r['visit_reference']) ?></p></div><?= badge($r['status']) ?></div>
<div class="actions"><a href="/?page=receipts">Toutes les réceptions</a><a href="/?page=notices">Avis et restes à livrer</a></div>
<?php foreach($lines as $line): ?>
<section class="panel"><h2><?= h($line['sku'].' / '.$line['name']) ?></h2>
<?php dataTable([['Attendu'=>$line['expected_qty'],'Reçu'=>$line['received_qty'],'Manquant'=>$line['missing_qty'],'Excédent'=>$line['excess_qty'],'Avarié'=>$line['damaged_qty']]]); ?>
<?php dataTable($db->all('SELECT i.pallet_code palette,l.code lot,l.expires_on dlc,i.accepted_qty accepte,i.damaged_qty avarie,i.pallet_state etat,i.reservation reserve,e.code emplacement FROM receipt_item i JOIN lot l ON l.id=i.lot_id JOIN location e ON e.id=i.location_id WHERE i.line_id=?',[$line['id']])); ?>
<?php if($r['status']==='draft'): ?>
<details><summary>Livraison partielle : ajuster l’attendu de cette livraison</summary><?php startForm('save',['table'=>'receipt_line','id'=>$line['id'],'receipt_id'=>$r['id'],'notice_line_id'=>$line['notice_line_id']]);inputField('expected_qty','Attendu pour cette livraison',$line['expected_qty'],'number'); ?><button>Actualiser l’attendu</button></form></details>
<details><summary>Ajouter une palette ou une fraction reçue</summary><?php startForm('receive_item',['receipt_id'=>$r['id'],'line_id'=>$line['id']]); ?><div class="form-grid"><?php
 selectField('lot_id','Lot existant',$db->all('SELECT id,CONCAT(code,COALESCE(CONCAT(" / ",expires_on),"")) label FROM lot WHERE article_id=? ORDER BY code',[$line['article_id']]),'',true);
 inputField('new_lot','Ou créer un nouveau lot','','text',false);inputField('expires_on','DLC du nouveau lot','','date',false);
 inputField('pallet_code','Code de palette / fraction');inputField('accepted_qty','Quantité acceptée',0,'number');inputField('damaged_qty','Quantité endommagée',0,'number');
 selectField('pallet_state','État',[['id'=>'bon','label'=>'Bon'],['id'=>'abime','label'=>'Abîmé']],'bon');inputField('reservation','Réserve sur la palette','','text',false);
 $suggestions=(new Warehouse($db,(int)$user['id']))->suggestions((int)$line['article_id'],1);selectField('location_id','Emplacement compatible (capacité revérifiée à la validation)',array_map(fn($l)=>['id'=>$l['id'],'label'=>$l['code']],$suggestions));
?></div><button>Ajouter la fraction</button></form></details>
<?php endif; ?>
<details><summary>Émettre une réserve pour cette ligne, même sans palette reçue</summary><?php startForm('reserve_receipt',['receipt_id'=>$r['id'],'line_id'=>$line['id']]);selectField('kind','Nature',[['id'=>'manquant','label'=>'Manquant'],['id'=>'excedent','label'=>'Excédent'],['id'=>'avarie','label'=>'Avarie'],['id'=>'autre','label'=>'Autre']]);inputField('reason','Réserve détaillée au transporteur'); ?><button>Enregistrer la réserve</button></form></details>
</section><?php endforeach; ?>
<section class="panel"><h2>Réserves émises</h2><?php dataTable($db->all('SELECT COALESCE(a.sku,"Réception entière") article,x.kind nature,x.reason reserve,u.name auteur,x.created_at date FROM receipt_reserve x JOIN user_account u ON u.id=x.actor_id LEFT JOIN receipt_line l ON l.id=x.line_id LEFT JOIN notice_line n ON n.id=l.notice_line_id LEFT JOIN article a ON a.id=n.article_id WHERE COALESCE(x.receipt_id,l.receipt_id)=? ORDER BY x.id',[$r['id']])); ?>
<?php startForm('reserve_receipt',['receipt_id'=>$r['id'],'kind'=>'autre']);inputField('reason','Observation complémentaire sur la réception'); ?><button class="secondary">Ajouter une réserve générale</button></form></section>
<?php if($r['status']==='draft'){startForm('receipt',['id'=>$r['id']]); ?><button data-confirm="Valider les quantités, écarts et emplacements ? Les faits validés seront conservés.">Valider cette réception</button></form><?php } ?>
