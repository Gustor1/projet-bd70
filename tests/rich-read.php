<?php
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';
$db=new Database();$cat=new Catalog($db);$checks=[];
$checks['jeu_superieur_2000_fractions']=(int)$db->scalar('SELECT COUNT(*) FROM receipt_item')>2000;
$_GET=[];$initial=$cat->options('receipt_item');$row=$db->one('SELECT id,pallet_code FROM receipt_item ORDER BY pallet_code DESC LIMIT 1');
$checks['cible_hors_premiere_liste']=!in_array((int)$row['id'],array_map('intval',array_column($initial,'id')),true);
$_GET['ref_search']=$row['pallet_code'];$found=$cat->options('receipt_item');
$checks['recherche_retrouve_cible']=count($found)===1&&(int)$found[0]['id']===(int)$row['id'];
$_GET['ref_search']='AUCUNE-REFERENCE-EXISTANTE';$selected=$cat->options('receipt_item',$row['id']);
$checks['selection_conservee_apres_filtre']=count($selected)===1&&(int)$selected[0]['id']===(int)$row['id'];
$checks['remplissage_equivalent_au_stock']=(int)$db->scalar('SELECT COUNT(*) FROM v_location_usage u LEFT JOIN (SELECT location_id,SUM(qty*unit_kg) kg,SUM(qty*unit_m3) m3,SUM(qty/units_per_pallet) palettes FROM v_stock GROUP BY location_id) s ON s.location_id=u.id WHERE ABS(u.used_kg-COALESCE(s.kg,0))>0.0001 OR ABS(u.used_m3-COALESCE(s.m3,0))>0.0001 OR ABS(u.used_pallets-COALESCE(s.palettes,0))>0.0001')===0;
$result=['database'=>$db->scalar('SELECT DATABASE()'),'read_only'=>true,'checks'=>$checks,'passed'=>!in_array(false,$checks,true)];
file_put_contents(__DIR__.'/../docs/preuves/lecture-riche.json',json_encode($result,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
echo json_encode($checks,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE)."\n";exit($result['passed']?0:1);
