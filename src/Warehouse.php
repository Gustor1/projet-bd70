<?php
declare(strict_types=1);

/** Règles métier : toutes les écritures critiques passent par une transaction sérialisée. */
final class Warehouse
{
    public function __construct(public Database $db,public int $actor,private ?string $clock=null) {}
    public function now(): string { return $this->clock??date('Y-m-d H:i:s'); }
    public static function date(string $s): string
    {
        $d=DateTimeImmutable::createFromFormat('!Y-m-d',$s);
        if(!$d||$d->format('Y-m-d')!==$s)throw new DomainException('Date invalide.');return $s;
    }
    public static function datetime(string $s): string
    {
        $s=str_replace('T',' ',$s);if(strlen($s)===16)$s.=':00';
        $d=DateTimeImmutable::createFromFormat('!Y-m-d H:i:s',$s);
        if(!$d||$d->format('Y-m-d H:i:s')!==$s)throw new DomainException('Date ou heure invalide.');
        $day=$d->setTime(0,0);$tz=new DateTimeZone(date_default_timezone_get());
        if(count($tz->getTransitions($day->getTimestamp(),$day->modify('+1 day')->getTimestamp())?:[])>1)throw new DomainException('Jour de changement d’heure : choisissez un autre créneau pour cette démonstration.');
        return $s;
    }
    public static function positive(mixed $value): int
    {
        if(!is_scalar($value)||!preg_match('/^[1-9]\d*$/',(string)$value)||(float)$value>2147483647)throw new DomainException('Quantité entière strictement positive requise.');return (int)$value;
    }
    private function ref(string $prefix): string { return $prefix.'-'.strtoupper(bin2hex(random_bytes(6))); }
    public function compatible(int $dock,int $driver,int $vehicle,?int $trailer,string $operation,string $date): void
    {
        $d=$this->db->one('SELECT * FROM dock WHERE id=?',[$dock]);
        if($d['type']!=='mixte'&&$d['type']!==$operation)throw new DomainException('Ce quai ne permet pas cette opération.');
        $v=$this->db->one('SELECT * FROM vehicle WHERE id=?',[$vehicle]);$p=$this->db->one('SELECT * FROM driver WHERE id=?',[$driver]);
        if($v['carrier_id']!==$p['carrier_id']||$v['type']==='remorque')throw new DomainException('Chauffeur et véhicule moteur doivent appartenir au même transporteur.');
        if(!$this->db->scalar('SELECT COUNT(*) FROM dock_vehicle_type WHERE dock_id=? AND vehicle_type=?',[$dock,$v['type']]))throw new DomainException('Type de véhicule incompatible avec le quai.');
        if(($v['type']==='tracteur')!==($trailer!==null))throw new DomainException('Un tracteur nécessite une remorque ; les autres véhicules ne prennent pas de remorque.');
        if($trailer){$t=$this->db->one('SELECT * FROM vehicle WHERE id=?',[$trailer]);if($t['type']!=='remorque'||$t['carrier_id']!==$v['carrier_id'])throw new DomainException('Remorque incompatible avec le transporteur.');}
        $missing=$this->db->scalar('SELECT COUNT(*) FROM vehicle_equipment ve WHERE ve.vehicle_id IN (?,?) AND NOT EXISTS (SELECT 1 FROM dock_equipment de WHERE de.dock_id=? AND de.equipment_id=ve.equipment_id)',[$vehicle,$trailer??$vehicle,$dock]);
        if($missing)throw new DomainException('Équipements du quai insuffisants pour ce véhicule.');
    }
    public function saveAppointmentInside(?int $id,array $d): int
    {
        $start=self::datetime($d['starts_at']);$end=self::datetime($d['ends_at']);
        if($end<=$start)throw new DomainException('La fin doit suivre le début.');
        if($id){$old=$this->db->one('SELECT * FROM appointment WHERE id=?',[$id]);if($old['status']!=='active'||$this->db->scalar('SELECT COUNT(*) FROM truck_visit WHERE appointment_id=?',[$id]))throw new DomainException('Rendez-vous annulé ou déjà utilisé : modification interdite.');}
        $this->compatible((int)$d['dock_id'],(int)$d['driver_id'],(int)$d['vehicle_id'],$d['trailer_id']?(int)$d['trailer_id']:null,$d['operation'],$start);
        if($this->db->scalar("SELECT COUNT(*) FROM appointment WHERE dock_id=? AND status='active' AND starts_at<? AND ends_at>? AND id<>?",[$d['dock_id'],$end,$start,$id??0]))throw new DomainException('Ce créneau chevauche un rendez-vous actif.');
        if($this->db->scalar('SELECT COUNT(*) FROM dock_downtime WHERE dock_id=? AND starts_at<? AND ends_at>?',[$d['dock_id'],$end,$start]))throw new DomainException('Quai hors service pendant le créneau.');
        if($id){$this->db->run('UPDATE appointment SET reference=?,dock_id=?,driver_id=?,vehicle_id=?,trailer_id=?,operation=?,starts_at=?,ends_at=? WHERE id=?',[$d['reference'],$d['dock_id'],$d['driver_id'],$d['vehicle_id'],$d['trailer_id'],$d['operation'],$start,$end,$id]);return $id;}
        $d['starts_at']=$start;$d['ends_at']=$end;return $this->db->insert('appointment',$d);
    }
    public function appointment(array $d,?int $id=null): int { return $this->db->transaction($this->actor,fn()=>$this->saveAppointmentInside($id,$d)); }
    public function cancelAppointment(int $id): void
    {
        $this->db->transaction($this->actor,function()use($id){
            $a=$this->db->one('SELECT * FROM appointment WHERE id=?',[$id]);
            if($a['status']!=='active'||$this->db->scalar('SELECT COUNT(*) FROM truck_visit WHERE appointment_id=?',[$id]))throw new DomainException('Annulation impossible : rendez-vous déjà utilisé ou annulé.');
            $this->db->run("UPDATE appointment SET status='cancelled' WHERE id=?",[$id]);
        });
    }
    public function checkDowntime(?int $id,array $d): void
    {
        $start=self::datetime($d['starts_at']);$end=self::datetime($d['ends_at']);if($end<=$start)throw new DomainException('Période invalide.');
        if($this->db->scalar("SELECT COUNT(*) FROM appointment WHERE dock_id=? AND status='active' AND starts_at<? AND ends_at>?",[$d['dock_id'],$end,$start])||$this->db->scalar("SELECT COUNT(*) FROM truck_visit WHERE dock_id=? AND status IN ('called','working')",[$d['dock_id']]))throw new DomainException('Déplacez les réservations et libérez le quai avant son indisponibilité.');
        if($this->db->scalar('SELECT COUNT(*) FROM dock_downtime WHERE dock_id=? AND starts_at<? AND ends_at>? AND id<>?',[$d['dock_id'],$end,$start,$id??0]))throw new DomainException('Indisponibilité déjà enregistrée sur cette période.');
    }
    public function arrive(array $d): int
    {
        return $this->db->transaction($this->actor,function()use($d){
            $a=!empty($d['appointment_id'])?$this->db->one('SELECT * FROM appointment WHERE id=?',[$d['appointment_id']]):null;
            if($a){if($a['status']!=='active')throw new DomainException('Rendez-vous annulé.');foreach(['driver_id','vehicle_id','trailer_id','operation'] as $k)$d[$k]=$a[$k];}
            self::positive($d['vehicle_id']??0);self::positive($d['driver_id']??0);
            if(!in_array($d['operation']??'',['reception','expedition'],true))throw new DomainException('Choisissez une opération.');
            $v=$this->db->one('SELECT * FROM vehicle WHERE id=?',[$d['vehicle_id']]);$driver=$this->db->one('SELECT * FROM driver WHERE id=?',[$d['driver_id']]);
            $trailer=!empty($d['trailer_id'])?(int)$d['trailer_id']:null;
            if($v['type']==='remorque'||$v['carrier_id']!==$driver['carrier_id']||(($v['type']==='tracteur')!==($trailer!==null)))throw new DomainException('Ensemble véhicule/chauffeur/remorque incohérent.');
            if($trailer){$t=$this->db->one('SELECT * FROM vehicle WHERE id=?',[$trailer]);if($t['type']!=='remorque'||$t['carrier_id']!==$v['carrier_id'])throw new DomainException('Remorque incompatible.');}
            if($this->db->scalar("SELECT COUNT(*) FROM truck_visit WHERE status NOT IN ('departed','rejected') AND (vehicle_id=? OR driver_id=? OR (trailer_id IS NOT NULL AND trailer_id=?))",[$v['id'],$driver['id'],$trailer??0]))throw new DomainException('Véhicule, chauffeur ou remorque déjà sur le site.');
            $id=$this->db->insert('truck_visit',['reference'=>($d['reference']??'')?:$this->ref('PASS'),'appointment_id'=>$a['id']??null,'driver_id'=>$d['driver_id'],'vehicle_id'=>$d['vehicle_id'],'trailer_id'=>$trailer,'operation'=>$d['operation'],'status'=>'arrived']);
            $this->db->insert('visit_event',['visit_id'=>$id,'state'=>'arrived','happened_at'=>$this->now(),'actor_id'=>$this->actor]);return $id;
        });
    }
    public function transition(int $id,string $next,?int $dock=null,string $note=''): void
    {
        $this->db->transaction($this->actor,function()use($id,$next,$dock,$note){
            $v=$this->db->one('SELECT * FROM truck_visit WHERE id=?',[$id]);
            $map=['arrived'=>['checked','rejected'],'checked'=>['parking','called'],'parking'=>['called'],'called'=>['working'],'working'=>['finished'],'finished'=>['departed']];
            if(!in_array($next,$map[$v['status']]??[],true))throw new DomainException('Transition non autorisée depuis cet état.');
            if($this->now()<$this->db->scalar('SELECT MAX(happened_at) FROM visit_event WHERE visit_id=?',[$id]))throw new DomainException('Horodatage antérieur à la dernière étape.');
            if(in_array($next,['checked','rejected'],true)&&trim($note)==='')throw new DomainException('Renseignez le résultat du contrôle documentaire.');
            if(in_array($next,['called','working'],true)){
                $dock=$next==='called'?$dock:(int)$v['dock_id'];if(!$dock)throw new DomainException('Choisissez un quai.');
                $this->compatible($dock,(int)$v['driver_id'],(int)$v['vehicle_id'],$v['trailer_id']?(int)$v['trailer_id']:null,$v['operation'],$this->now());
                if($this->db->scalar("SELECT COUNT(*) FROM truck_visit WHERE dock_id=? AND status IN ('called','working') AND id<>?",[$dock,$id]))throw new DomainException('Quai déjà occupé.');
                if($this->db->scalar('SELECT COUNT(*) FROM dock_downtime WHERE dock_id=? AND starts_at<=? AND ends_at>?',[$dock,$this->now(),$this->now()]))throw new DomainException('Quai hors service.');
                if($this->db->scalar("SELECT COUNT(*) FROM appointment WHERE dock_id=? AND status='active' AND starts_at<=? AND ends_at>? AND id<>?",[$dock,$this->now(),$this->now(),$v['appointment_id']??0]))throw new DomainException('Quai réservé pour un autre camion à cette heure.');
            }
            if($next==='finished'&&$this->db->scalar("SELECT COUNT(*) FROM receipt WHERE visit_id=? AND status='draft'",[$id]))throw new DomainException('Validez ou supprimez les réceptions brouillon avant de terminer.');
            $this->db->run('UPDATE truck_visit SET status=?,dock_id=?,document_note=? WHERE id=?',[$next,$dock??$v['dock_id'],$note?:$v['document_note'],$id]);
            $this->db->insert('visit_event',['visit_id'=>$id,'state'=>$next,'happened_at'=>$this->now(),'actor_id'=>$this->actor]);
        });
    }
    public function capacity(int $location,array $article,int $qty): void
    {
        $l=$this->db->one('SELECT l.*,u.used_kg,u.used_m3,u.used_pallets FROM v_location l JOIN v_location_usage u ON u.id=l.id WHERE l.id=?',[$location]);
        if($l['storage']!==$article['storage'] || $article['width_m']>$l['width_m'] || $article['depth_m']>$l['depth_m'] || $article['height_m']>$l['height_m'])throw new DomainException('Dimensions ou conditions de stockage incompatibles.');
        $vol=$article['width_m']*$article['depth_m']*$article['height_m'];
        if($l['used_kg']+$qty*$article['unit_kg']>$l['max_kg']+0.000001 || $l['used_m3']+$qty*$vol>$l['capacity_m3']+0.000001 || $l['used_pallets']+$qty/$article['units_per_pallet']>$l['max_pallets']+0.000001)throw new DomainException('Capacité restante insuffisante (kg, volume ou palettes).');
    }
    public function suggestions(int $articleId,int $qty): array
    {
        $a=$this->db->one('SELECT * FROM article WHERE id=?',[$articleId]);$out=[];
        foreach($this->db->all('SELECT id,code FROM location ORDER BY code') as $l){try{$this->capacity((int)$l['id'],$a,$qty);$out[]=$l;}catch(DomainException){}}
        return $out;
    }
    private function goodsVehicle(array $visit,array $article): void
    {
        if($article['storage']==='froid'){
            foreach([['dock_equipment','dock_id',$visit['dock_id']],['vehicle_equipment','vehicle_id',$visit['trailer_id']?:$visit['vehicle_id']]] as [$table,$key,$id])if(!$this->db->scalar("SELECT COUNT(*) FROM $table x JOIN equipment e ON e.id=x.equipment_id WHERE x.$key=? AND e.code='FROID'",[$id]))throw new DomainException('Article froid : quai et véhicule frigorifiques requis.');
        }
        if($article['storage']==='dangereux'&&!$this->db->scalar("SELECT COUNT(*) FROM driver_qualification x JOIN qualification q ON q.id=x.qualification_id WHERE x.driver_id=? AND q.code='ADR' AND x.expires_on>=?",[$visit['driver_id'],substr($this->now(),0,10)]))throw new DomainException('Habilitation ADR valide requise pour les produits dangereux.');
    }
    public function validateReceipt(int $id): void
    {
        $this->db->transaction($this->actor,function()use($id){
            $r=$this->db->one('SELECT * FROM receipt WHERE id=?',[$id]);if($r['status']!=='draft')throw new DomainException('Cette réception a déjà été validée.');
            $visit=$this->db->one('SELECT * FROM truck_visit WHERE id=?',[$r['visit_id']]);if($visit['status']!=='working'||$visit['operation']!=='reception')throw new DomainException('Le camion doit être en déchargement sur un quai.');
            $lines=$this->db->all('SELECT rl.*,n.article_id,n.notice_id,n.expected_qty notice_qty FROM receipt_line rl JOIN notice_line n ON n.id=rl.notice_line_id WHERE rl.receipt_id=?',[$id]);
            if(!$lines)throw new DomainException('Ajoutez au moins une ligne de réception.');
            $kg=0;$pallets=0;
            foreach($lines as $line){
                if($line['notice_id']!=$r['notice_id'])throw new DomainException('Ligne d’un autre avis.');
                $allocated=(int)$this->db->scalar("SELECT COALESCE(SUM(l.expected_qty),0) FROM receipt_line l JOIN receipt c ON c.id=l.receipt_id WHERE c.status='validated' AND l.notice_line_id=?",[$line['notice_line_id']]);
                if($allocated+$line['expected_qty']>$line['notice_qty'])throw new DomainException('Quantité attendue déjà réceptionnée dans une livraison précédente.');
                $article=$this->db->one('SELECT * FROM article WHERE id=?',[$line['article_id']]);$this->goodsVehicle($visit,$article);
                foreach($this->db->all('SELECT i.*,t.article_id FROM receipt_item i JOIN lot t ON t.id=i.lot_id WHERE i.line_id=? ORDER BY i.id',[$line['id']]) as $i){
                    if($i['article_id']!=$line['article_id'])throw new DomainException('Lot d’un autre article.');
                    $kg+=($i['accepted_qty']+$i['damaged_qty'])*$article['unit_kg'];$pallets+=($i['accepted_qty']+$i['damaged_qty'])/$article['units_per_pallet'];
                    if($i['accepted_qty']>0){$this->capacity((int)$i['location_id'],$article,(int)$i['accepted_qty']);$this->movement('REC-'.$id,(int)$i['id'],(int)$i['location_id'],(int)$i['accepted_qty'],'entry','Réception validée');}
                }
            }
            $this->truckCapacity($visit,$kg,$pallets,false);
            $this->db->run("UPDATE receipt SET status='validated',validated_at=? WHERE id=?",[$this->now(),$id]);
        });
    }
    private function movement(string $ref,int $item,int $location,int $delta,string $kind,string $reason,?int $pick=null): void
    {
        $this->db->insert('stock_movement',['operation_ref'=>$ref,'receipt_item_id'=>$item,'location_id'=>$location,'delta'=>$delta,'kind'=>$kind,'reason'=>$reason,'pick_id'=>$pick,'actor_id'=>$this->actor,'created_at'=>$this->now()]);
    }
    private function free(int $item,int $location): int
    {
        return (int)$this->db->scalar('SELECT COALESCE((SELECT SUM(delta) FROM stock_movement WHERE receipt_item_id=? AND location_id=?),0)-COALESCE((SELECT SUM(qty) FROM pick WHERE receipt_item_id=? AND location_id=? AND status IN (\'planned\',\'confirmed\')),0)',[$item,$location,$item,$location]);
    }
    public function transfer(int $item,int $source,int $dest,int $qty,string $reason): void
    {
        self::positive($qty);if($source===$dest||trim($reason)==='')throw new DomainException('Choisissez une autre destination et un motif.');
        $this->db->transaction($this->actor,function()use($item,$source,$dest,$qty,$reason){
            if($this->free($item,$source)<$qty)throw new DomainException('Stock libre insuffisant ou réservé.');
            $a=$this->db->one('SELECT a.* FROM article a JOIN lot l ON l.article_id=a.id JOIN receipt_item i ON i.lot_id=l.id WHERE i.id=?',[$item]);
            $this->capacity($dest,$a,$qty);$ref=$this->ref('TRF');$this->movement($ref,$item,$source,-$qty,'transfer',$reason);$this->movement($ref,$item,$dest,$qty,'transfer',$reason);
        });
    }
    public function adjust(int $item,int $location,int $delta,string $reason): void
    {
        if($delta===0||trim($reason)==='')throw new DomainException('Variation non nulle et motif requis.');
        $this->db->transaction($this->actor,function()use($item,$location,$delta,$reason){
            $i=$this->db->one("SELECT i.* FROM receipt_item i JOIN receipt_line l ON l.id=i.line_id JOIN receipt r ON r.id=l.receipt_id WHERE i.id=? AND r.status='validated'",[$item]);
            if($delta<0&&$this->free($item,$location)<-$delta)throw new DomainException('Ajustement refusé : stock libre insuffisant.');
            if($delta>0){$a=$this->db->one('SELECT a.* FROM article a JOIN lot l ON l.article_id=a.id WHERE l.id=?',[$i['lot_id']]);$this->capacity($location,$a,$delta);}
            $this->movement($this->ref('INV'),$item,$location,$delta,'adjustment',$reason);
        });
    }
    public function prepare(int $id,int $preparer): void
    {
        $this->db->transaction($this->actor,function()use($id,$preparer){
            $o=$this->db->one('SELECT * FROM customer_order WHERE id=?',[$id]);if($o['status']!=='draft')throw new DomainException('Commande déjà lancée ou annulée.');
            $p=$this->db->one('SELECT * FROM user_account WHERE id=?',[$preparer]);if(!$p['active']||!in_array($p['role'],['warehouse','manager','admin'],true))throw new DomainException('Choisissez un préparateur actif.');
            $lines=$this->db->all('SELECT * FROM order_line WHERE order_id=? ORDER BY id',[$id]);if(!$lines)throw new DomainException('Ajoutez des lignes à la commande.');
            foreach($lines as $line){
                if($o['owner_id']!=$this->db->scalar('SELECT owner_id FROM article WHERE id=?',[$line['article_id']]))throw new DomainException('Article d’un autre propriétaire.');
                $need=(int)$line['qty'];
                $stock=$this->db->all('SELECT * FROM v_stock WHERE article_id=? AND available_qty>0 AND blocked=0 AND (expires_on IS NULL OR expires_on>=?) ORDER BY expires_on IS NULL,expires_on,received_at,receipt_item_id,location_id',[$line['article_id'],substr($this->now(),0,10)]);
                foreach($stock as $s){$take=min($need,(int)$s['available_qty']);$this->db->insert('pick',['order_line_id'=>$line['id'],'receipt_item_id'=>$s['receipt_item_id'],'location_id'=>$s['location_id'],'qty'=>$take]);$need-=$take;if(!$need)break;}
                if($need>0)throw new DomainException('Stock FEFO disponible insuffisant : aucune ligne réservée.');
            }
            $this->db->run("UPDATE customer_order SET status='picking',preparer_id=?,picking_at=? WHERE id=?",[$preparer,$this->now(),$id]);
        });
    }
    public function confirmPick(int $id,int $userId,string $role): void
    {
        $this->db->transaction($this->actor,function()use($id,$userId,$role){
            $o=$this->db->one('SELECT * FROM customer_order WHERE id=?',[$id]);
            if($o['status']!=='picking'||($role==='warehouse'&&$o['preparer_id']!=$userId))throw new DomainException('Préparation non affectée à cet utilisateur ou déjà confirmée.');
            if($this->db->scalar("SELECT COUNT(*) FROM pick p JOIN order_line ol ON ol.id=p.order_line_id JOIN receipt_item i ON i.id=p.receipt_item_id JOIN lot l ON l.id=i.lot_id WHERE ol.order_id=? AND p.status='planned' AND (l.blocked=1 OR l.expires_on<?)",[$id,substr($this->now(),0,10)]))throw new DomainException('Un lot réservé est bloqué ou périmé : annulez la préparation.');
            $this->db->run("UPDATE pick p JOIN order_line l ON l.id=p.order_line_id SET p.status='confirmed',p.confirmed_at=? WHERE l.order_id=? AND p.status='planned'",[$this->now(),$id]);
            $this->db->run("UPDATE customer_order SET status='ready',ready_at=? WHERE id=?",[$this->now(),$id]);
        });
    }
    public function cancelOrder(int $id): void
    {
        $this->db->transaction($this->actor,function()use($id){
            $o=$this->db->one('SELECT * FROM customer_order WHERE id=?',[$id]);if(in_array($o['status'],['shipped','cancelled'],true))throw new DomainException('Commande expédiée ou déjà annulée.');
            $this->db->run("UPDATE pick p JOIN order_line l ON l.id=p.order_line_id SET p.status='cancelled' WHERE l.order_id=?",[$id]);
            $this->db->run("UPDATE customer_order SET status='cancelled' WHERE id=?",[$id]);
        });
    }
    private function truckCapacity(array $visit,float $kg,float $pallets,bool $out): void
    {
        if($out){$previous=$this->db->one('SELECT COALESCE(SUM(p.qty*a.unit_kg),0) kg,COALESCE(SUM(p.qty/a.units_per_pallet),0) palettes FROM shipment s JOIN order_line ol ON ol.order_id=s.order_id JOIN pick p ON p.order_line_id=ol.id JOIN article a ON a.id=ol.article_id WHERE s.visit_id=?',[$visit['id']]);$kg+=(float)$previous['kg'];$pallets+=(float)$previous['palettes'];}
        else {$previous=$this->db->one("SELECT COALESCE(SUM((i.accepted_qty+i.damaged_qty)*a.unit_kg),0) kg,COALESCE(SUM((i.accepted_qty+i.damaged_qty)/a.units_per_pallet),0) palettes FROM receipt r JOIN receipt_line rl ON rl.receipt_id=r.id JOIN receipt_item i ON i.line_id=rl.id JOIN lot l ON l.id=i.lot_id JOIN article a ON a.id=l.article_id WHERE r.visit_id=? AND r.status='validated'",[$visit['id']]);$kg+=(float)$previous['kg'];$pallets+=(float)$previous['palettes'];}
        $v=$this->db->one('SELECT * FROM vehicle WHERE id=?',[$visit['trailer_id']?:$visit['vehicle_id']]);if($kg>$v['max_kg']+0.000001||$pallets>$v['max_pallets']+0.000001)throw new DomainException('Capacité de chargement du véhicule dépassée.');
    }
    public function ship(int $order,int $visit): void
    {
        $this->db->transaction($this->actor,function()use($order,$visit){
            $o=$this->db->one('SELECT * FROM customer_order WHERE id=?',[$order]);if($o['status']!=='ready')throw new DomainException('Commande non prête ou déjà expédiée.');
            $v=$this->db->one('SELECT * FROM truck_visit WHERE id=?',[$visit]);if($v['status']!=='working'||$v['operation']!=='expedition')throw new DomainException('Camion sortant non disponible au chargement.');
            $picks=$this->db->all('SELECT p.*,a.unit_kg,a.units_per_pallet,a.storage,a.id article_id,l.blocked,l.expires_on FROM pick p JOIN order_line ol ON ol.id=p.order_line_id JOIN article a ON a.id=ol.article_id JOIN receipt_item i ON i.id=p.receipt_item_id JOIN lot l ON l.id=i.lot_id WHERE ol.order_id=? AND p.status=\'confirmed\' ORDER BY p.id',[$order]);
            if(!$picks)throw new DomainException('Aucun prélèvement confirmé.');$kg=0;$pallets=0;
            foreach($picks as $p){
                if($p['blocked']||($p['expires_on']&&$p['expires_on']<substr($this->now(),0,10)))throw new DomainException('Lot bloqué ou périmé.');
                if(!$this->db->scalar('SELECT COUNT(*) FROM package_pick pp JOIN package c ON c.id=pp.package_id WHERE pp.pick_id=? AND c.order_id=?',[$p['id'],$order]))throw new DomainException('Affectez chaque prélèvement à un colis ou une palette.');
                $this->goodsVehicle($v,$p);$kg+=$p['qty']*$p['unit_kg'];$pallets+=$p['qty']/$p['units_per_pallet'];
                if((int)$this->db->scalar('SELECT COALESCE(SUM(delta),0) FROM stock_movement WHERE receipt_item_id=? AND location_id=?',[$p['receipt_item_id'],$p['location_id']])<$p['qty'])throw new DomainException('Stock physique insuffisant.');
            }
            $this->truckCapacity($v,$kg,$pallets,true);$ref=$this->ref('EXP');
            $this->db->insert('shipment',['order_id'=>$order,'visit_id'=>$visit,'reference'=>$ref,'shipped_at'=>$this->now(),'actor_id'=>$this->actor]);
            foreach($picks as $p){$this->movement($ref,(int)$p['receipt_item_id'],(int)$p['location_id'],-(int)$p['qty'],'shipment','Chargement confirmé',(int)$p['id']);$this->db->run("UPDATE pick SET status='shipped' WHERE id=?",[$p['id']]);}
            $this->db->run("UPDATE customer_order SET status='shipped' WHERE id=?",[$order]);
        });
    }
}
