<div class="page-heading"><div><p class="context">Approvisionnement</p><h1>Avis fournisseurs & restes à livrer</h1><p>Préparez les lignes attendues, réceptionnez les livraisons partielles puis clôturez l’avis.</p></div><a class="button" href="/?page=catalog&t=supplier_notice&new=1">Nouvel avis</a></div>
<form method="get" class="filters"><input type="hidden" name="page" value="notices"><?php inputField('q','Référence',$_GET['q']??'','search',false);selectField('supplier_id','Fournisseur',$catalog->options('supplier'),$_GET['supplier_id']??'',true);selectField('closed','État',[['id'=>'open','label'=>'Ouvert'],['id'=>'closed','label'=>'Clôturé']],$_GET['closed']??'',true);filterEnd('notices'); ?>
<?php
$where=['1=1'];$params=[];
if(!empty($_GET['q'])){$where[]='n.reference LIKE ?';$params[]='%'.$_GET['q'].'%';}
if(!empty($_GET['supplier_id'])){$where[]='n.supplier_id=?';$params[]=(int)$_GET['supplier_id'];}
if(($_GET['closed']??'')==='open')$where[]='n.closed_at IS NULL';
if(($_GET['closed']??'')==='closed')$where[]='n.closed_at IS NOT NULL';
$pageNumber=max(1,(int)($_GET['p']??1));$condition=implode(' AND ',$where);$total=(int)$db->scalar('SELECT COUNT(*) FROM supplier_notice n WHERE '.$condition,$params);
$notices=$db->all('SELECT n.*,s.name supplier_name FROM supplier_notice n JOIN supplier s ON s.id=n.supplier_id WHERE '.$condition.' ORDER BY n.id DESC LIMIT 20 OFFSET '.(($pageNumber-1)*20),$params);
foreach($notices as $n):
 $lines=$db->all('SELECT p.*,a.sku,a.name FROM v_notice_line_progress p JOIN article a ON a.id=p.article_id WHERE p.notice_id=?',[$n['id']]);
?>
<article class="panel"><div class="section-heading"><div><h2><?= h($n['reference']) ?></h2><p><?= h($n['supplier_name']) ?> · Attendu le <?= h($n['expected_on']) ?></p></div><?= badge($n['closed_at']?'Clôturé':(array_sum(array_column($lines,'allocated_qty'))?'Livraisons en cours':'Ouvert')) ?></div>
<?php dataTable(array_map(fn($l)=>['Article'=>$l['sku'].' / '.$l['name'],'Attendu'=>$l['expected_qty'],'Attendu traité'=>$l['allocated_qty'],'Reçu'=>$l['received_qty'],'Avarié'=>$l['damaged_qty'],'Reste à traiter'=>$l['remaining_qty']],$lines)); ?>
<p class="hint">Le reste correspond à l’attendu non encore traité. Un manquant constaté sur une réception est un écart distinct ; clôturer signifie qu’aucune autre livraison n’est attendue.</p>
<?php if(!$n['closed_at']): ?>
<details><summary>Ajouter un article attendu</summary><?php startForm('save',['table'=>'notice_line','notice_id'=>$n['id']]);selectField('article_id','Article',$catalog->options('article'));inputField('expected_qty','Quantité attendue',1,'number'); ?><button>Ajouter la ligne</button></form></details>
<?php startForm('open_receipt',['notice_id'=>$n['id']],'inline-form');inputField('reference','Référence de réception (automatique si vide)','','text',false);selectField('visit_id','Camion entrant en déchargement',$db->all("SELECT id,reference label FROM truck_visit WHERE status='working' AND operation='reception' ORDER BY id DESC")); ?><button>Ouvrir une réception guidée</button></form>
<details><summary>Clôturer cet avis</summary><?php startForm('close_notice',['notice_id'=>$n['id']]);inputField('reason','Bilan et motif, y compris les restes non livrés'); ?><button class="secondary" data-confirm="Clôturer l’avis et empêcher toute nouvelle réception ?">Clôturer l’avis</button></form></details>
<?php else: ?><p>Clôturé le <?= h($n['closed_at']) ?> : <?= h($n['closure_note']) ?></p><?php endif; ?>
<?php foreach($db->all('SELECT id,reference,status FROM receipt WHERE notice_id=? ORDER BY id',[$n['id']]) as $r): ?><a class="button secondary" href="<?= h(url(['page'=>'receipt_detail','id'=>$r['id']])) ?>"><?= h($r['reference']) ?> · <?= h(Catalog::VALUES[$r['status']]) ?></a> <?php endforeach; ?>
</article><?php endforeach;pagination($total,$pageNumber); ?>
