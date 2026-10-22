<?php
declare(strict_types=1);

final class Reports
{
    public function __construct(public Database $db) {}
    public function period(array $input): array
    {
        $from=Warehouse::date((string)($input['from']??date('Y-m-d')));$to=Warehouse::date((string)($input['to']??$from));
        if($to<$from||strtotime($to)-strtotime($from)>366*86400)throw new DomainException('Choisissez une période de 366 jours au maximum.');
        return [$from.' 00:00:00',(new DateTimeImmutable($to))->modify('+1 day')->format('Y-m-d').' 00:00:00'];
    }
    public function stock(array $f,bool $export=false): array
    {
        $where=['s.qty<>0'];$p=[];
        foreach(['article_id','owner_id','zone_id','lot_id'] as $key)if(!empty($f[$key])){$where[]='s.'.$key.'=?';$p[]=(int)$f[$key];}
        if(!empty($f['q'])){$where[]='(s.sku LIKE ? OR s.article_name LIKE ? OR s.lot_code LIKE ? OR s.pallet_code LIKE ?)';for($i=0;$i<4;$i++)$p[]='%'.$f['q'].'%';}
        $sort=match($f['sort']??'article'){'lot'=>'s.lot_code,s.location_code','quantity'=>'s.qty DESC,s.sku',default=>'s.sku,s.lot_code,s.location_code'};
        $sql=' FROM v_stock s WHERE '.implode(' AND ',$where);$total=(int)$this->db->scalar('SELECT COUNT(*)'.$sql,$p);
        $page=max(1,(int)($f['p']??1));$limit=$export?'':' LIMIT 20 OFFSET '.(($page-1)*20);
        return ['rows'=>$this->db->all('SELECT s.*'.$sql.' ORDER BY '.$sort.$limit,$p),'total'=>$total,'page'=>$page];
    }
    public function visits(array $f,bool $export=false): array
    {
        [$from,$to]=$this->period($f);$where=['arrived_at>=?','arrived_at<?'];$p=[$from,$to];
        if(!empty($f['carrier_id'])){$where[]='carrier_id=?';$p[]=(int)$f['carrier_id'];}
        if(!empty($f['status'])){$where[]='status=?';$p[]=$f['status'];}
        if(!empty($f['q'])){$where[]='(reference LIKE ? OR plate LIKE ? OR driver_name LIKE ?)';for($i=0;$i<3;$i++)$p[]='%'.$f['q'].'%';}
        $sql=' FROM v_visit WHERE '.implode(' AND ',$where);$total=(int)$this->db->scalar('SELECT COUNT(*)'.$sql,$p);$page=max(1,(int)($f['p']??1));
        $sort=($f['sort']??'recent')==='wait'?'wait_minutes DESC,id DESC':'arrived_at DESC,id DESC';
        return ['rows'=>$this->db->all('SELECT *'.$sql.' ORDER BY '.$sort.($export?'':' LIMIT 20 OFFSET '.(($page-1)*20)),$p),'total'=>$total,'page'=>$page];
    }
    public function receipts(array $f,bool $export=false): array
    {
        [$from,$to]=$this->period($f);$where=['r.validated_at>=?','r.validated_at<?'];$p=[$from,$to];
        if(!empty($f['supplier_id'])){$where[]='n.supplier_id=?';$p[]=(int)$f['supplier_id'];}
        if(!empty($f['q'])){$where[]='r.reference LIKE ?';$p[]='%'.$f['q'].'%';}
        if(($f['gap']??'')==='1')$where[]='(d.missing_qty>0 OR d.excess_qty>0 OR d.damaged_qty>0)';
        $sql=' FROM v_receipt_discrepancy d JOIN receipt r ON r.id=d.receipt_id JOIN supplier_notice n ON n.id=r.notice_id JOIN supplier s ON s.id=n.supplier_id WHERE '.implode(' AND ',$where);
        $page=max(1,(int)($f['p']??1));return ['rows'=>$this->db->all('SELECT r.reference,s.name fournisseur,d.expected_qty attendu,d.received_qty recu,d.missing_qty manquant,d.excess_qty excedent,d.damaged_qty endommage'.$sql.' ORDER BY r.reference'.($export?'':' LIMIT 20 OFFSET '.(($page-1)*20)),$p),'total'=>(int)$this->db->scalar('SELECT COUNT(*)'.$sql,$p),'page'=>$page];
    }
    public function dashboard(array $f): array
    {
        [$from,$to]=$this->period($f);$period=(new DateTimeImmutable($to))->getTimestamp()-(new DateTimeImmutable($from))->getTimestamp();
        $occupied=(float)$this->db->scalar("SELECT COALESCE(SUM(GREATEST(0,TIMESTAMPDIFF(SECOND,GREATEST(working_at,?),LEAST(COALESCE(finished_at,NOW()),?)))),0) FROM v_visit WHERE working_at<? AND COALESCE(finished_at,NOW())>?",[$from,$to,$to,$from]);
        $down=(float)$this->db->scalar('SELECT COALESCE(SUM(TIMESTAMPDIFF(SECOND,GREATEST(starts_at,?),LEAST(ends_at,?))),0) FROM dock_downtime WHERE starts_at<? AND ends_at>?',[$from,$to,$to,$from]);
        $capacity=(int)$this->db->scalar('SELECT COUNT(*) FROM dock')*$period-$down;
        $carriers=$this->db->all("SELECT carrier_name transporteur,COUNT(*) passages,SUM(departed_at IS NULL) ouverts,AVG(wait_minutes) attente_min,AVG(immobilized_minutes) immobilisation_min,COUNT(wait_minutes) attentes_mesurees,COUNT(immobilized_minutes) departs_mesures FROM v_visit WHERE arrived_at>=? AND arrived_at<? GROUP BY carrier_id,carrier_name ORDER BY carrier_name",[$from,$to]);
        $zones=$this->db->all('SELECT z.name zone,COALESCE(SUM(u.used_kg),0) kg,COALESCE(SUM(l.max_kg),0) capacite_kg,COALESCE(SUM(u.used_m3),0) m3,COALESCE(SUM(l.capacity_m3),0) capacite_m3,COALESCE(SUM(u.used_pallets),0) palettes,COALESCE(SUM(l.max_pallets),0) capacite_palettes FROM zone z LEFT JOIN v_location l ON l.zone_id=z.id LEFT JOIN v_location_usage u ON u.id=l.id GROUP BY z.id,z.name ORDER BY z.id');
        $gaps=$this->db->one('SELECT COUNT(*) lignes,COALESCE(SUM(d.missing_qty>0 OR d.excess_qty>0 OR d.damaged_qty>0),0) lignes_ecart,COALESCE(SUM(d.missing_qty),0) manquant,COALESCE(SUM(d.excess_qty),0) excedent,COALESCE(SUM(d.damaged_qty),0) endommage FROM v_receipt_discrepancy d JOIN receipt r ON r.id=d.receipt_id WHERE r.validated_at>=? AND r.validated_at<?',[$from,$to]);
        // Agrégation préalable par commande : aucune multiplication de la durée par le nombre de picks.
        $productivity=$this->db->all("SELECT u.name preparateur,SUM(p.qty) quantite,SUM(p.line_count) lignes,SUM(TIMESTAMPDIFF(SECOND,o.picking_at,o.ready_at))/60 minutes_observees,SUM(p.qty)*3600/NULLIF(SUM(TIMESTAMPDIFF(SECOND,o.picking_at,o.ready_at)),0) unites_heure FROM customer_order o JOIN user_account u ON u.id=o.preparer_id JOIN (SELECT ol.order_id,SUM(p.qty) qty,COUNT(DISTINCT ol.id) line_count FROM order_line ol JOIN pick p ON p.order_line_id=ol.id WHERE p.status IN ('confirmed','shipped') GROUP BY ol.order_id) p ON p.order_id=o.id WHERE o.status IN ('ready','shipped') AND o.ready_at>=? AND o.ready_at<? GROUP BY u.id,u.name",[$from,$to]);
        $reference=substr($from,0,10);$horizon=max(0,min(365,(int)($f['horizon']??14)));$until=(new DateTimeImmutable($reference))->modify('+'.$horizon.' days')->format('Y-m-d');
        $dlc=$this->db->all('SELECT sku,lot_code,expires_on,SUM(available_qty) disponible FROM v_stock WHERE blocked=0 AND available_qty>0 AND expires_on>=? AND expires_on<=? GROUP BY article_id,lot_id,sku,lot_code,expires_on ORDER BY expires_on',[$reference,$until]);
        $expiry=$this->db->one('SELECT COALESCE(SUM(CASE WHEN expires_on<? THEN qty-reserved_qty ELSE 0 END),0) perime,COALESCE(SUM(CASE WHEN expires_on IS NULL THEN qty-reserved_qty ELSE 0 END),0) sans_dlc FROM v_stock WHERE blocked=0',[$reference]);
        return compact('from','to','occupied','capacity','down','carriers','zones','gaps','productivity','dlc','expiry','horizon');
    }
    public function docks(string $day): array
    {
        Warehouse::date($day);return $this->db->all("SELECT d.*,
        CASE WHEN EXISTS(SELECT 1 FROM dock_downtime x WHERE x.dock_id=d.id AND x.starts_at<=NOW() AND x.ends_at>NOW()) THEN 'Hors service'
        WHEN EXISTS(SELECT 1 FROM truck_visit v WHERE v.dock_id=d.id AND v.status IN ('called','working')) THEN 'Occupé'
        WHEN EXISTS(SELECT 1 FROM appointment a WHERE a.dock_id=d.id AND a.status='active' AND a.starts_at<=NOW() AND a.ends_at>NOW()) THEN 'Réservé' ELSE 'Libre' END live_state,
        (SELECT COUNT(*) FROM appointment a WHERE a.dock_id=d.id AND a.status='active' AND a.starts_at<? AND a.ends_at>?) appointments
        FROM dock d ORDER BY d.code",[(new DateTimeImmutable($day))->modify('+1 day')->format('Y-m-d'),$day]);
    }
}
