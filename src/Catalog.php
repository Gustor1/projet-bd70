<?php
declare(strict_types=1);

final class Catalog
{
    public const TITLES = [
      'user_account'=>'Utilisateurs','carrier'=>'Transporteurs','carrier_contact'=>'Contacts transporteurs','carrier_contract'=>'Contrats',
      'qualification'=>'Habilitations','driver'=>'Chauffeurs','driver_qualification'=>'Habilitations des chauffeurs','equipment'=>'Équipements',
      'vehicle'=>'Véhicules','vehicle_equipment'=>'Équipements des véhicules','dock'=>'Quais','dock_equipment'=>'Équipements des quais','dock_vehicle_type'=>'Compatibilités des quais',
      'dock_downtime'=>'Indisponibilités','appointment'=>'Rendez-vous','truck_visit'=>'Passages camions','visit_event'=>'Chronologie des passages',
      'owner'=>'Clients propriétaires','supplier'=>'Fournisseurs','article'=>'Articles','zone'=>'Zones','aisle'=>'Allées','rack'=>'Racks','rack_level'=>'Niveaux','location'=>'Emplacements',
      'lot'=>'Lots','supplier_notice'=>'Avis fournisseurs','notice_line'=>'Lignes attendues','receipt'=>'Réceptions','receipt_line'=>'Lignes de réception','receipt_item'=>'Palettes reçues',
      'customer_order'=>'Commandes','order_line'=>'Lignes de commande','pick'=>'Prélèvements','package'=>'Colis et palettes de sortie','package_pick'=>'Contenu des colis',
      'shipment'=>'Expéditions','stock_movement'=>'Mouvements de stock','audit_log'=>'Journal automatique',
    ];
    public const LABELS = [
      'email'=>'Email','name'=>'Nom','password'=>'Mot de passe','role'=>'Profil','active'=>'Compte actif','created_at'=>'Créé le',
      'code'=>'Code','reference'=>'Référence','address'=>'Adresse','phone'=>'Téléphone','terms'=>'Conditions du contrat','starts_on'=>'Date de début','ends_on'=>'Date de fin',
      'carrier_id'=>'Transporteur','driver_id'=>'Chauffeur','license_number'=>'Numéro de permis','qualification_id'=>'Habilitation','expires_on'=>'Date limite / validité',
      'vehicle_id'=>'Véhicule','equipment_id'=>'Équipement','plate'=>'Immatriculation','type'=>'Type','max_kg'=>'Capacité (kg)','max_pallets'=>'Capacité (équiv. palettes)',
      'dock_id'=>'Quai','vehicle_type'=>'Type de véhicule','starts_at'=>'Début','ends_at'=>'Fin','reason'=>'Motif','trailer_id'=>'Remorque (facultative)','operation'=>'Opération','status'=>'État',
      'appointment_id'=>'Rendez-vous (facultatif)','document_note'=>'Contrôle documentaire / observations','visit_id'=>'Passage camion','state'=>'Étape','happened_at'=>'Horodatage','actor_id'=>'Auteur',
      'owner_id'=>'Propriétaire','sku'=>'Référence article','storage'=>'Condition de stockage','packaging'=>'Conditionnement','width_m'=>'Largeur (m)','depth_m'=>'Profondeur (m)','height_m'=>'Hauteur (m)',
      'unit_kg'=>'Poids unitaire (kg)','units_per_pallet'=>'Unités par palette','zone_id'=>'Zone','aisle_id'=>'Allée','rack_id'=>'Rack','level_id'=>'Niveau',
      'article_id'=>'Article','blocked'=>'Lot bloqué','block_reason'=>'Motif du blocage','supplier_id'=>'Fournisseur','expected_on'=>'Livraison prévue','notice_id'=>'Avis fournisseur','expected_qty'=>'Quantité attendue',
      'validated_at'=>'Validation','receipt_id'=>'Réception','notice_line_id'=>'Ligne attendue','line_id'=>'Ligne de réception','lot_id'=>'Lot','pallet_code'=>'Code palette / fraction',
      'accepted_qty'=>'Quantité acceptée','damaged_qty'=>'Quantité endommagée','pallet_state'=>'État de palette','reservation'=>'Réserve transporteur','location_id'=>'Emplacement',
      'destination'=>'Adresse de livraison','desired_on'=>'Expédition souhaitée','preparer_id'=>'Préparateur','picking_at'=>'Début de préparation','ready_at'=>'Fin de préparation',
      'order_id'=>'Commande','qty'=>'Quantité','order_line_id'=>'Ligne de commande','receipt_item_id'=>'Palette reçue / fraction','confirmed_at'=>'Confirmation','package_id'=>'Colis / palette','pick_id'=>'Prélèvement',
      'shipped_at'=>'Expédition','operation_ref'=>'Opération liée','delta'=>'Variation (unités)','kind'=>'Nature','entity'=>'Entité','entity_id'=>'Référence technique d’audit','details'=>'Description',
    ];
    public const VALUES=['admin'=>'Administrateur','manager'=>'Responsable','gate'=>'Accueil','warehouse'=>'Magasinier','pending'=>'En attente','draft'=>'Brouillon','validated'=>'Validée','active'=>'Actif','cancelled'=>'Annulé','arrived'=>'Arrivé','checked'=>'Documents contrôlés','parking'=>'En attente parking','called'=>'Appelé à quai','working'=>'En opération','finished'=>'Opération terminée','departed'=>'Parti','rejected'=>'Refusé','picking'=>'En préparation','ready'=>'Prête','shipped'=>'Expédié','planned'=>'À prélever','confirmed'=>'Prélevé','entry'=>'Entrée','transfer'=>'Transfert','shipment'=>'Sortie expédition','adjustment'=>'Ajustement'];
    public const READONLY=['truck_visit','visit_event','pick','shipment','stock_movement','audit_log'];
    private array $columns=[];
    private array $foreign=[];
    public function __construct(public Database $db) {}
    public function check(string $t): void { if(!isset(self::TITLES[$t]))throw new DomainException('Rubrique inconnue.'); }
    public function columns(string $t): array
    { $this->check($t);return $this->columns[$t]??=$this->db->all('SHOW COLUMNS FROM `'.$t.'`'); }
    public function foreign(string $t): array
    {
        $this->check($t);
        if(!isset($this->foreign[$t])) {
            $this->foreign[$t]=[];
            foreach($this->db->all('SELECT COLUMN_NAME,REFERENCED_TABLE_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=? AND REFERENCED_TABLE_NAME IS NOT NULL',[$t]) as $f) $this->foreign[$t][$f['COLUMN_NAME']]=$f['REFERENCED_TABLE_NAME'];
        }
        return $this->foreign[$t];
    }
    public function labelSQL(string $t): string
    {
        return match($t) {
          'user_account'=>"CONCAT(name,' (',email,')')",'driver'=>"CONCAT(name,' / ',license_number)",'vehicle'=>'plate',
          'article'=>"CONCAT(sku,' / ',name)",'lot'=>"CONCAT(code,' / ',(SELECT sku FROM article WHERE article.id=lot.article_id))",'location'=>'code',
          'notice_line'=>"CONCAT((SELECT reference FROM supplier_notice WHERE id=notice_id),' / ',(SELECT sku FROM article WHERE id=article_id))",
          'receipt_line'=>"CONCAT((SELECT reference FROM receipt WHERE id=receipt_id),' / ',(SELECT a.sku FROM notice_line n JOIN article a ON a.id=n.article_id WHERE n.id=notice_line_id))",
          'receipt_item'=>'pallet_code','order_line'=>"CONCAT((SELECT reference FROM customer_order WHERE id=order_id),' / ',(SELECT sku FROM article WHERE id=article_id))",
          'pick'=>"CONCAT((SELECT reference FROM customer_order WHERE id=(SELECT order_id FROM order_line WHERE id=order_line_id)),' / ',(SELECT pallet_code FROM receipt_item WHERE id=receipt_item_id),' × ',qty)",
          default=>in_array('reference',array_column($this->columns($t),'Field'),true)?'reference':(in_array('name',array_column($this->columns($t),'Field'),true)?'name':(in_array('code',array_column($this->columns($t),'Field'),true)?'code':"CONCAT('Association ',id)")),
        };
    }
    public function options(string $t,mixed $selected=null): array
    {
        $this->check($t);$label=$this->labelSQL($t);$search=trim((string)($_GET['ref_search']??''));$p=[];$where='';
        if($search!==''&&(int)$this->db->scalar('SELECT COUNT(*) FROM `'.$t.'`')>2000){$where=' WHERE '.$label.' LIKE ?';$p[]='%'.$search.'%';}
        $options=$this->db->all('SELECT id,'.$label.' label FROM `'.$t.'`'.$where.' ORDER BY label LIMIT 2000',$p);
        if($selected&&!in_array((string)$selected,array_map('strval',array_column($options,'id')),true)){
            $s=$this->db->run('SELECT id,'.$label.' label FROM `'.$t.'` WHERE id=?',[(int)$selected])->fetch();if($s)$options[]=$s;
        }
        return $options;
    }
    public function right(string $t): string
    {
        return match(true) {
            $t==='user_account'=>'accounts',
            in_array($t,['appointment','dock_downtime'],true)=>'planning',
            in_array($t,['receipt','receipt_line','receipt_item','supplier_notice','notice_line','lot'],true)=>'stock',
            in_array($t,['customer_order','order_line','package','package_pick'],true)=>'orders',
            default=>'catalog',
        };
    }
    public function editable(string $t): array
    {
        if(in_array($t,self::READONLY,true))return [];
        return array_values(array_filter($this->columns($t),fn($c)=>!in_array($c['Field'],['id','status','password_hash','created_at','validated_at','picking_at','ready_at','preparer_id'],true)));
    }
    public function save(string $t,?int $id,array $input,int $actor): int
    {
        $this->check($t);
        if(in_array($t,self::READONLY,true))throw new DomainException('Ce fait se crée uniquement par une action métier.');
        return $this->db->transaction($actor,function()use($t,$id,$input,$actor){
            $data=[];
            foreach($this->editable($t) as $col) {
                $k=$col['Field']; $v=$input[$k]??'';
                if(!is_scalar($v))throw new DomainException('Valeur incorrecte.');
                $v=trim((string)$v);
                if($v==='' && $col['Null']==='YES') $v=null;
                elseif($v==='' && $col['Default']!==null)$v=$col['Default'];
                elseif($v==='')throw new DomainException((self::LABELS[$k]??$k).' : valeur obligatoire.');
                if($v!==null) {
                    if(str_starts_with($col['Type'],'tinyint')&&!in_array($v,['0','1'],true))throw new DomainException('Choix oui/non requis.');
                    if(str_starts_with($col['Type'],'enum(')) { preg_match_all("/'([^']*)'/",$col['Type'],$m);if(!in_array($v,$m[1],true))throw new DomainException('Choix invalide.'); }
                    elseif(preg_match('/^(int|bigint|tinyint)/',$col['Type']) && !preg_match('/^-?\d+$/',$v))throw new DomainException('Nombre entier requis.');
                    elseif(str_starts_with($col['Type'],'decimal')&&(!is_numeric($v)||!is_finite((float)$v)))throw new DomainException('Nombre décimal requis.');
                    elseif($col['Type']==='date') Warehouse::date($v);
                    elseif($col['Type']==='datetime') $v=Warehouse::datetime($v);
                    if(preg_match('/varchar\((\d+)\)/',$col['Type'],$m)&&mb_strlen($v)>(int)$m[1])throw new DomainException('Texte trop long : '.(self::LABELS[$k]??$k));
                }
                $data[$k]=$v;
            }
            if(isset($data['email'])&&!filter_var($data['email'],FILTER_VALIDATE_EMAIL))throw new DomainException('Email invalide.');
            $old=$id?$this->db->one('SELECT * FROM `'.$t.'` WHERE id=?',[$id]):null;
            $this->guard($t,$id,$old,$data);
            $service=new Warehouse($this->db,$actor);
            if($t==='appointment')return $service->saveAppointmentInside($id,$data);
            if($t==='dock_downtime')$service->checkDowntime($id,$data);
            if($t==='user_account'){
                if($id===$actor && ($data['role']!=='admin'||!$data['active']))throw new DomainException('Conservez votre propre accès administrateur.');
                $pass=$input['password']??'';
                if(!$id || $pass!==''){
                    if(strlen($pass)<10||strlen($pass)>72)throw new DomainException('Mot de passe de 10 à 72 caractères requis.');
                    $data['password_hash']=password_hash($pass,PASSWORD_DEFAULT);
                }
            }
            if($id){$sets=implode(',',array_map(fn($k)=>'`'.$k.'`=?',array_keys($data)));$this->db->run('UPDATE `'.$t.'` SET '.$sets.' WHERE id=?',[...array_values($data),$id]);return $id;}
            return $this->db->insert($t,$data);
        });
    }
    public function guard(string $t,?int $id,?array $old,array $d): void
    {
        $db=$this->db;
        if($t==='lot' && $d['blocked'] && trim($d['block_reason'])==='')throw new DomainException('Précisez le motif du blocage.');
        $frozen=match($t) {
          'article'=>$id&&(bool)$db->scalar('SELECT COUNT(*) FROM lot WHERE article_id=?',[$id]),
          'vehicle'=>$id&&(bool)$db->scalar('SELECT (SELECT COUNT(*) FROM appointment WHERE vehicle_id=? OR trailer_id=?)+(SELECT COUNT(*) FROM truck_visit WHERE vehicle_id=? OR trailer_id=?)',[$id,$id,$id,$id]),
          'driver'=>$id&&(bool)$db->scalar('SELECT (SELECT COUNT(*) FROM appointment WHERE driver_id=?)+(SELECT COUNT(*) FROM truck_visit WHERE driver_id=?)',[$id,$id]),
          'dock'=>$id&&(bool)$db->scalar('SELECT (SELECT COUNT(*) FROM appointment WHERE dock_id=?)+(SELECT COUNT(*) FROM truck_visit WHERE dock_id=?)',[$id,$id]),
          'zone','aisle','rack','rack_level','location'=>$id&&(bool)$db->scalar('SELECT COUNT(*) FROM stock_movement m JOIN location l ON l.id=m.location_id JOIN rack_level n ON n.id=l.level_id JOIN rack r ON r.id=n.rack_id JOIN aisle a ON a.id=r.aisle_id JOIN zone z ON z.id=a.zone_id WHERE '.(['zone'=>'z','aisle'=>'a','rack'=>'r','rack_level'=>'n','location'=>'l'][$t]).'.id=?',[$id]),
          'dock_equipment','dock_vehicle_type'=>$id&&(bool)$db->scalar('SELECT (SELECT COUNT(*) FROM appointment WHERE dock_id=?)+(SELECT COUNT(*) FROM truck_visit WHERE dock_id=?)',[$old['dock_id'],$old['dock_id']]),
          'vehicle_equipment'=>$id&&(bool)$db->scalar('SELECT (SELECT COUNT(*) FROM appointment WHERE vehicle_id=? OR trailer_id=?)+(SELECT COUNT(*) FROM truck_visit WHERE vehicle_id=? OR trailer_id=?)',[$old['vehicle_id'],$old['vehicle_id'],$old['vehicle_id'],$old['vehicle_id']]),
          'driver_qualification'=>$id&&(bool)$db->scalar('SELECT (SELECT COUNT(*) FROM appointment WHERE driver_id=?)+(SELECT COUNT(*) FROM truck_visit WHERE driver_id=?)',[$old['driver_id'],$old['driver_id']]),
          default=>false,
        };
        if($frozen && $old && array_filter($d,fn($v,$k)=>(string)$v!==(string)$old[$k],ARRAY_FILTER_USE_BOTH))throw new DomainException('Fiche structurelle déjà utilisée : modification protégée pour conserver la cohérence.');
        if($t==='lot'&&$id&&$db->scalar('SELECT COUNT(*) FROM receipt_item WHERE lot_id=?',[$id]))foreach(['article_id','code','expires_on'] as $k)if((string)$d[$k] !== (string)$old[$k])throw new DomainException('Identité du lot déjà reçu protégée ; seul son blocage est modifiable.');
        if(in_array($t,['receipt','receipt_line','receipt_item'],true)) {
            $receiptId=match($t){'receipt'=>$id,'receipt_line'=>$d['receipt_id'],default=>$db->scalar('SELECT receipt_id FROM receipt_line WHERE id=?',[$d['line_id']])};
            if($receiptId && $db->scalar('SELECT status FROM receipt WHERE id=?',[$receiptId])!=='draft')throw new DomainException('Réception validée : corriger par un mouvement motivé.');
            if($id && $t!=='receipt') {
                $oldReceipt=$t==='receipt_line'?$old['receipt_id']:$db->scalar('SELECT receipt_id FROM receipt_line WHERE id=?',[$old['line_id']]);
                if($db->scalar('SELECT status FROM receipt WHERE id=?',[$oldReceipt])!=='draft')throw new DomainException('Impossible de déplacer une ligne validée.');
            }
            if($t==='receipt_line') {
                $n=$db->one('SELECT * FROM notice_line WHERE id=?',[$d['notice_line_id']]);$r=$db->one('SELECT * FROM receipt WHERE id=?',[$d['receipt_id']]);
                if($n['notice_id']!==$r['notice_id'])throw new DomainException('Cette ligne ne correspond pas à l’avis de la réception.');
            }
            if($t==='receipt_item'){
                $a=$db->scalar('SELECT n.article_id FROM receipt_line r JOIN notice_line n ON n.id=r.notice_line_id WHERE r.id=?',[$d['line_id']]);
                if($a!=$db->scalar('SELECT article_id FROM lot WHERE id=?',[$d['lot_id']]))throw new DomainException('Lot d’un autre article.');
            }
        }
        if(in_array($t,['notice_line','supplier_notice'],true)&&$id){
            $notice=$t==='supplier_notice'?$id:$old['notice_id'];
            if($db->scalar('SELECT COUNT(*) FROM receipt WHERE notice_id=?',[$notice]))throw new DomainException('Avis déjà lié à une réception : modification protégée.');
        }
        if(in_array($t,['customer_order','order_line','package','package_pick'],true)){
            $oid=match($t){'customer_order'=>$id,'package_pick'=>$db->scalar('SELECT order_id FROM package WHERE id=?',[$d['package_id']]),default=>$d['order_id']};
            if($oid){$o=$db->one('SELECT * FROM customer_order WHERE id=?',[$oid]);
              if(in_array($t,['customer_order','order_line'],true)&&$o['status']!=='draft')throw new DomainException('Commande déjà lancée : annulez la préparation avant modification.');
              if(in_array($t,['package','package_pick'],true)&&$o['status']!=='ready')throw new DomainException('Constituez les colis lorsque la préparation est confirmée.');
              if($t==='order_line'&&$d['article_id']&&$o['owner_id']!=$db->scalar('SELECT owner_id FROM article WHERE id=?',[$d['article_id']]))throw new DomainException('Article d’un autre propriétaire.');
              if($t==='package_pick'){
                $p=$db->one('SELECT p.*,ol.order_id FROM pick p JOIN order_line ol ON ol.id=p.order_line_id WHERE p.id=?',[$d['pick_id']]);
                if($p['order_id']!=$oid||$p['status']!=='confirmed')throw new DomainException('Prélèvement non confirmé ou d’une autre commande.');
              }
            }
            if($id&&$t!=='customer_order'){
                $oldOid=$t==='package_pick'?$db->scalar('SELECT order_id FROM package WHERE id=?',[$old['package_id']]):$old['order_id'];
                if($oldOid!=$oid)throw new DomainException('Le rattachement d’une ligne ne peut pas être déplacé.');
            }
        }
    }
    public function delete(string $t,int $id,int $actor): void
    {
        $this->check($t);
        if(in_array($t,self::READONLY,true)||in_array($t,['appointment','user_account'],true))throw new DomainException('Utilisez l’annulation ou la désactivation.');
        $this->db->transaction($actor,function()use($t,$id){
            $old=$this->db->one('SELECT * FROM `'.$t.'` WHERE id=?',[$id]);
            $this->guard($t,$id,$old,$old);
            if(in_array($t,['dock_equipment','dock_vehicle_type','vehicle_equipment','driver_qualification'],true)){
                $key=match($t){'vehicle_equipment'=>'vehicle_id','driver_qualification'=>'driver_id',default=>'dock_id'};
                if($this->db->scalar('SELECT COUNT(*) FROM appointment WHERE `'.$key.'`=?',[$old[$key]])||$this->db->scalar('SELECT COUNT(*) FROM truck_visit WHERE `'.$key.'`=?',[$old[$key]]))throw new DomainException('Association utilisée par le planning : suppression protégée.');
            }
            $this->db->run('DELETE FROM `'.$t.'` WHERE id=?',[$id]);
        });
    }
}
