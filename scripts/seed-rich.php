<?php
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';

/** Historique fictif déterministe : chronologies, capacités et provenance conservées.
 * Les écritures historiques sont simulées ; les scénarios vivants finaux utilisent Warehouse.
 */
final class RichDataset
{
    public array $articles=[],$lots=[],$locations=[],$load=[],$stock=[],$carriers=[],$drivers=[],$vehicles=[],$owners=[],$suppliers=[],$preparers=[],$docks=[];
    private int $sequence=0;
    public function __construct(public Database $db,public DateTimeImmutable $reference){}
    public function ref(string $type):string{return $type.'-'.str_pad((string)++$this->sequence,7,'0',STR_PAD_LEFT);}
    public function insert(string $t,array $d):int{return $this->db->insert($t,$d);}
    public function setup():void
    {
        foreach(['admin'=>'Alice Martin','manager'=>'Samir Petit','gate'=>'Léa Dubois','warehouse'=>'Noah Bernard'] as $role=>$name){$id=$this->insert('user_account',['email'=>$role.'@bd70.test','name'=>$name,'password_hash'=>password_hash('Entrepot2026!',PASSWORD_DEFAULT),'role'=>$role,'active'=>1]);if($role==='warehouse')$this->preparers[]=$id;}
        foreach(['Camille Robert','Louise Moreau','Gabriel Simon','Emma Laurent','Adam Michel','Jade Garcia','Louis Roux','Lina Perrin','Arthur Faure','Chloé Blanc','Hugo Morel'] as $i=>$name)$this->preparers[]=$this->insert('user_account',['email'=>'preparateur'.($i+1).'@bd70.test','name'=>$name.' (fictif)','password_hash'=>password_hash('Entrepot2026!',PASSWORD_DEFAULT),'role'=>'warehouse','active'=>1]);
        for($i=1;$i<=5;$i++)$this->insert('user_account',['email'=>'demande'.$i.'@bd70.test','name'=>'Demande fictive '.$i,'password_hash'=>password_hash('Entrepot2026!',PASSWORD_DEFAULT),'role'=>'pending','active'=>0]);
        $equipment=[];foreach(['FROID'=>'Frigorifique','HAYON'=>'Hayon','NIVELEUR'=>'Niveleur'] as $c=>$n)$equipment[$c]=$this->insert('equipment',['code'=>$c,'name'=>$n]);
        $adr=$this->insert('qualification',['code'=>'ADR','name'=>'Transport de matières dangereuses']);$this->insert('qualification',['code'=>'FROID','name'=>'Chaîne du froid']);
        $names=['Nord Transit','Froid Express','Route Est','Alpes Cargo','Atlantique Transport','Rhône Logistique','Loire Distribution','Bourgogne Fret','Armor Livraison','Provence Routier','Alsace Colis','Picardie Express','Occitanie Cargo','Normandie Transport','Champagne Fret','Jura Distribution','Bretagne Routes','Centre Palettes','Aquitaine Logistique','Vosges Transport'];
        foreach($names as $i=>$name){
            $carrier=$this->insert('carrier',['code'=>sprintf('TR-%02d',$i+1),'name'=>$name.' Démo','address'=>($i+10).' avenue des Entrepôts, France (fictif)','phone'=>'03 00 '.sprintf('%02d 00 00',$i),'email'=>'transport'.$i.'@bd70.test']);$this->carriers[]=$carrier;
            foreach(['Exploitation','Facturation'] as $j=>$function)$this->insert('carrier_contact',['carrier_id'=>$carrier,'name'=>$function.' fictive','phone'=>'03 00 00 00 00','email'=>'contact'.$i.'-'.$j.'@bd70.test']);
            $this->insert('carrier_contract',['carrier_id'=>$carrier,'reference'=>sprintf('CONTRAT-%02d',$i+1),'starts_on'=>$this->reference->modify('-1 year')->format('Y-m-d'),'ends_on'=>$this->reference->modify('+1 year')->format('Y-m-d'),'terms'=>'Transport pédagogique : créneaux planifiés, réserves à réception, température contrôlée selon marchandise.']);
            for($j=0;$j<4;$j++){$driver=$this->insert('driver',['carrier_id'=>$carrier,'name'=>['Alex','Marie','Thomas','Sarah'][$j].' Conducteur '.($i+1).' (fictif)','phone'=>'06 00 '.sprintf('%02d %02d 00',$i,$j),'license_number'=>sprintf('PERMIS-DEMO-%02d-%d',$i,$j)]);if($j===0)$this->drivers[$carrier]=$driver;$this->insert('driver_qualification',['driver_id'=>$driver,'qualification_id'=>$adr,'expires_on'=>$this->reference->modify($j===3?'-5 days':'+2 years')->format('Y-m-d')]);}
            foreach(['porteur','fourgon','tracteur','remorque','porteur'] as $j=>$type){$vehicle=$this->insert('vehicle',['carrier_id'=>$carrier,'plate'=>sprintf('DEMO-%02d-%d',$i+1,$j+1),'type'=>$type,'max_kg'=>12000+2000*$j,'max_pallets'=>30+5*$j]);if($j===0)$this->vehicles[$carrier]=$vehicle;if($j!==1)$this->insert('vehicle_equipment',['vehicle_id'=>$vehicle,'equipment_id'=>$equipment['FROID']]);if($j===4)$this->insert('vehicle_equipment',['vehicle_id'=>$vehicle,'equipment_id'=>$equipment['HAYON']]);}
        }
        for($i=0;$i<9;$i++){$dock=$this->insert('dock',['code'=>sprintf('Q-%02d',$i+1),'name'=>($i<3?'Réception ':($i<6?'Expédition ':'Polyvalent ')).($i%3+1),'type'=>$i<3?'reception':($i<6?'expedition':'mixte')]);$this->docks[]=$dock;foreach(['porteur','fourgon','tracteur','remorque'] as $type)$this->insert('dock_vehicle_type',['dock_id'=>$dock,'vehicle_type'=>$type]);foreach($equipment as $e)$this->insert('dock_equipment',['dock_id'=>$dock,'equipment_id'=>$e]);}
        $clientNames=['Atlas Distribution','Marché des Alpes','Maison du Café','Comptoir Est','Cuisine & Co','Épicerie des Quais','Atelier Rhône','Nature Marché','Saveurs du Nord','Terroirs Distribution','Comptoir du Jura','Maison Océane','Panier Vert','Boutiques du Centre','Équipements Pro','Halles du Sud','Commerce Vosgien','Réseau Métropole'];
        foreach($clientNames as $i=>$n)$this->owners[]=$this->insert('owner',['code'=>sprintf('CLI-%02d',$i+1),'name'=>$n.' Démo','address'=>($i+1).' rue du Commerce, France (fictif)','email'=>'client'.$i.'@bd70.test']);
        for($i=0;$i<20;$i++)$this->suppliers[]=$this->insert('supplier',['code'=>sprintf('FOU-%02d',$i+1),'name'=>['Manufacture','Coopérative','Ateliers','Production'][$i%4].' Démo '.($i+1),'address'=>($i+1).' rue des Ateliers, France (fictif)','phone'=>'03 00 00 00 '.sprintf('%02d',$i)]);
        foreach(['ambiant','froid','dangereux'] as $storage)for($z=1;$z<=2;$z++){
            $zone=$this->insert('zone',['code'=>strtoupper(substr($storage,0,3)).'-'.$z,'name'=>ucfirst($storage).' secteur '.$z,'storage'=>$storage]);
            for($a=1;$a<=3;$a++){$aisle=$this->insert('aisle',['zone_id'=>$zone,'code'=>'Z'.$zone.'-A'.$a]);for($r=1;$r<=2;$r++){$rack=$this->insert('rack',['aisle_id'=>$aisle,'code'=>'Z'.$zone.'-A'.$a.'-R'.$r]);for($n=1;$n<=2;$n++){$level=$this->insert('rack_level',['rack_id'=>$rack,'code'=>'R'.$rack.'-N'.$n]);for($e=1;$e<=5;$e++){$loc=$this->insert('location',['level_id'=>$level,'code'=>sprintf('Z%02d-A%d-R%d-N%d-E%d',$zone,$a,$r,$n,$e),'width_m'=>2,'depth_m'=>2,'height_m'=>2,'max_kg'=>6000,'max_pallets'=>60]);$this->locations[$storage][]=$loc;$this->load[$loc]=['kg'=>0,'m3'=>0,'pallets'=>0];}}}}
        }
        $products=['Café','Biscuits','Conserves','Jus','Farine','Sauce','Lait','Fromage','Solvant','Peinture'];
        foreach($this->owners as $owner)for($j=0;$j<10;$j++){
            $storage=['ambiant','froid','dangereux'][$j%3];$article=['owner_id'=>$owner,'sku'=>sprintf('ART-%03d-%02d',$owner,$j+1),'name'=>$products[$j].' gamme '.$owner,'storage'=>$storage,'packaging'=>'Carton de vente indivisible','width_m'=>0.12,'depth_m'=>0.12,'height_m'=>0.15,'unit_kg'=>1+($j%4),'units_per_pallet'=>20];$id=$this->insert('article',$article);$article['id']=$id;$this->articles[$id]=$article;
            for($k=0;$k<4;$k++){$expiry=$k===0?null:$this->reference->modify([1=>'+7 days',2=>'+45 days',3=>'-10 days'][$k])->format('Y-m-d');$blocked=$k===2&&$id%7===0;$lot=$this->insert('lot',['article_id'=>$id,'code'=>sprintf('LOT-%03d-%d',$id,$k+1),'expires_on'=>$expiry,'blocked'=>(int)$blocked,'block_reason'=>$blocked?'Contrôle qualité pédagogique':'']);$this->lots[$id][$k]=['id'=>$lot,'expires_on'=>$expiry,'blocked'=>$blocked];}
        }
    }
    public function place(int $article,int $qty,?int $avoid=null):int
    {
        $a=$this->articles[$article];$places=$this->locations[$a['storage']];$offset=mt_rand(0,count($places)-1);
        for($i=0;$i<count($places);$i++){$loc=$places[($i+$offset)%count($places)];$used=$this->load[$loc];if($loc!==$avoid&&$used['kg']+$qty*$a['unit_kg']<=6000&&$used['m3']+$qty*0.00216<=8&&$used['pallets']+$qty/20<=60)return $loc;}
        throw new RuntimeException('Capacité du jeu insuffisante.');
    }
    public function move(int $article,int $item,int $loc,int $delta,string $kind,string $ref,string $time,array $lot,?int $pick=null):void
    {
        if(!$delta)return;$a=$this->articles[$article];$key=$item.':'.$loc;
        $received=$time;foreach($this->stock[$article]??[] as $point)if($point['item']===$item){$received=$point['received_at'];break;}
        $this->stock[$article][$key]??=['item'=>$item,'location'=>$loc,'qty'=>0,'lot'=>$lot,'received_at'=>$received];
        $this->stock[$article][$key]['qty']+=$delta;if($this->stock[$article][$key]['qty']<0)throw new RuntimeException('Stock simulé négatif.');
        $this->load[$loc]['kg']+=$delta*$a['unit_kg'];$this->load[$loc]['m3']+=$delta*0.00216;$this->load[$loc]['pallets']+=$delta/20;
        $this->insert('stock_movement',['operation_ref'=>$ref,'receipt_item_id'=>$item,'location_id'=>$loc,'delta'=>$delta,'kind'=>$kind,'pick_id'=>$pick,'reason'=>['entry'=>'Réception fictive validée','transfer'=>'Répartition de rangement fictive','shipment'=>'Chargement fictif confirmé','adjustment'=>'Comptage de contrôle fictif'][$kind],'actor_id'=>4,'created_at'=>$time]);
    }
    public function visit(int $carrier,int $dock,DateTimeImmutable $at,bool $out,bool $appointment=true,int $delay=0):int
    {
        $appt=null;$operation=$out?'expedition':'reception';
        if($appointment)$appt=$this->insert('appointment',['reference'=>$this->ref('RDV'),'dock_id'=>$dock,'driver_id'=>$this->drivers[$carrier],'vehicle_id'=>$this->vehicles[$carrier],'operation'=>$operation,'starts_at'=>$at->modify('-'.$delay.' minutes')->format('Y-m-d H:i:s'),'ends_at'=>$at->modify($out?'+17 minutes':'+40 minutes')->format('Y-m-d H:i:s')]);
        $id=$this->insert('truck_visit',['reference'=>$this->ref('PASS'),'appointment_id'=>$appt,'driver_id'=>$this->drivers[$carrier],'vehicle_id'=>$this->vehicles[$carrier],'operation'=>$operation,'dock_id'=>$dock,'status'=>'departed','document_note'=>'Contrôle documentaire fictif conforme']);
        $states=$out?['arrived'=>0,'checked'=>2,'called'=>4,'working'=>6,'finished'=>15,'departed'=>17]:['arrived'=>0,'checked'=>2,'parking'=>4,'called'=>8,'working'=>12,'finished'=>35,'departed'=>40];
        foreach($states as $state=>$minutes)$this->insert('visit_event',['visit_id'=>$id,'state'=>$state,'happened_at'=>$at->modify('+'.$minutes.' minutes')->format('Y-m-d H:i:s'),'actor_id'=>$state==='working'?4:3]);return $id;
    }
    public function cycle(int $index,DateTimeImmutable $at):void
    {
        $owner=$this->owners[$index%count($this->owners)];$carrier=$this->carriers[$index%count($this->carriers)];$preparer=$this->preparers[$index%count($this->preparers)];
        $visit=$this->visit($carrier,$this->docks[$index%3],$at,false,$index%5!==0,$index%4*2);
        $n=$this->insert('supplier_notice',['reference'=>$this->ref('AVIS'),'supplier_id'=>$this->suppliers[$index%20],'expected_on'=>$at->format('Y-m-d')]);
        $r=$this->insert('receipt',['reference'=>$this->ref('REC'),'notice_id'=>$n,'visit_id'=>$visit,'status'=>'validated','validated_at'=>$at->modify('+30 minutes')->format('Y-m-d H:i:s')]);
        $time=$at->modify('+30 minutes')->format('Y-m-d H:i:s');$articleIds=[];
        for($j=0;$j<6;$j++){
            $article=($owner-1)*10+(($index+$j)%10)+1;$articleIds[]=$article;$lot=$this->lots[$article][($index+$j)%4];$expected=30;
            $missing=($index+$j)%19===0?30:(($index+$j)%11===0?3:0);$excess=($index+$j)%17===0?2:0;$damage=$missing===30?0:(($index+$j)%13===0?2:0);$accepted=max(0,$expected-$missing+$excess-$damage);
            $nl=$this->insert('notice_line',['notice_id'=>$n,'article_id'=>$article,'expected_qty'=>$expected]);$rl=$this->insert('receipt_line',['receipt_id'=>$r,'notice_line_id'=>$nl,'expected_qty'=>$expected]);
            if($missing||$excess||$damage)$this->insert('receipt_reserve',['receipt_id'=>null,'line_id'=>$rl,'kind'=>$missing?'manquant':($excess?'excedent':'avarie'),'reason'=>'Écart fictif : manque '.$missing.', excédent '.$excess.', avarie '.$damage.'.','actor_id'=>$preparer,'created_at'=>$time]);
            if($accepted+$damage>0){$loc=$this->place($article,$accepted);$item=$this->insert('receipt_item',['line_id'=>$rl,'lot_id'=>$lot['id'],'pallet_code'=>$this->ref('PAL'),'accepted_qty'=>$accepted,'damaged_qty'=>$damage,'pallet_state'=>$damage?'abime':'bon','reservation'=>$damage?'Réserve avarie pédagogique':'','location_id'=>$loc]);$this->move($article,$item,$loc,$accepted,'entry','REC-'.$r,$time,$lot);
                if($accepted>5){$dest=$this->place($article,5,$loc);$ref=$this->ref('TRF');$when=$at->modify('+41 minutes')->format('Y-m-d H:i:s');$this->move($article,$item,$loc,-5,'transfer',$ref,$when,$lot);$this->move($article,$item,$dest,5,'transfer',$ref,$when,$lot);}
                if($j===0&&$accepted>2){$when=$at->modify('+41 minutes')->format('Y-m-d H:i:s');$this->move($article,$item,$loc,-1,'adjustment',$this->ref('INV'),$when,$lot);$this->move($article,$item,$loc,1,'adjustment',$this->ref('INV'),$when,$lot);}
            }
        }
        $this->db->run('UPDATE supplier_notice SET closed_at=?,closed_by=?,closure_note=? WHERE id=?',[$at->modify('+40 minutes')->format('Y-m-d H:i:s'),2,'Livraison fictive terminée ; écarts documentés.',$n]);
        $outAt=$at->modify('+42 minutes');$out=$this->visit($carrier,$this->docks[3+$index%3],$outAt,true,$index%3!==0);
        $o=$this->insert('customer_order',['reference'=>$this->ref('CMD'),'owner_id'=>$owner,'destination'=>'Agence client '.($owner).' — France (fictif)','desired_on'=>$at->format('Y-m-d'),'status'=>'shipped','preparer_id'=>$preparer,'picking_at'=>$at->modify('+41 minutes')->format('Y-m-d H:i:s'),'ready_at'=>$at->modify('+'.(46+$index%5).' minutes')->format('Y-m-d H:i:s')]);
        $packages=[];foreach(['colis','palette'] as $type)$packages[]=$this->insert('package',['order_id'=>$o,'code'=>$this->ref('COL'),'type'=>$type]);
        $shipmentRef=$this->ref('EXP');$shipped=$at->modify('+54 minutes')->format('Y-m-d H:i:s');$served=0;
        foreach($articleIds as $article){
            $points=array_values(array_filter($this->stock[$article]??[],fn($s)=>$s['qty']>0&&!$s['lot']['blocked']&&(!$s['lot']['expires_on']||$s['lot']['expires_on']>=$at->format('Y-m-d'))));
            if(array_sum(array_column($points,'qty'))<20)continue;
            usort($points,fn($a,$b)=>[$a['lot']['expires_on']??'9999-12-31',$a['received_at'],$a['item'],$a['location']]<=>[$b['lot']['expires_on']??'9999-12-31',$b['received_at'],$b['item'],$b['location']]);
            $ol=$this->insert('order_line',['order_id'=>$o,'article_id'=>$article,'qty'=>20]);$need=20;
            foreach($points as $point){$take=min($need,$point['qty']);$pick=$this->insert('pick',['order_line_id'=>$ol,'receipt_item_id'=>$point['item'],'location_id'=>$point['location'],'qty'=>$take,'status'=>'shipped','confirmed_at'=>$at->modify('+'.(46+$index%5).' minutes')->format('Y-m-d H:i:s')]);$first=(int)ceil($take/2);$this->insert('package_pick',['package_id'=>$packages[0],'pick_id'=>$pick,'qty'=>$first]);if($take>$first)$this->insert('package_pick',['package_id'=>$packages[1],'pick_id'=>$pick,'qty'=>$take-$first]);$this->move($article,$point['item'],$point['location'],-$take,'shipment',$shipmentRef,$shipped,$point['lot'],$pick);$need-=$take;if(!$need)break;}
            if(++$served===4)break;
        }
        if(!$served)throw new RuntimeException('Commande historique vide : revoir les scénarios.');
        $this->insert('shipment',['order_id'=>$o,'visit_id'=>$out,'reference'=>$shipmentRef,'shipped_at'=>$shipped,'actor_id'=>$preparer]);
    }
    public function live():void
    {
        $cat=new Catalog($this->db);$now=new DateTimeImmutable(Clock::now());
        // L'activité du jour reste manipulable : plusieurs états, sans écraser l'historique.
        for($i=0;$i<6;$i++){
            $carrier=$this->carriers[$i];$at=$now->modify('-'.(60-$i*5).' minutes');$w=new Warehouse($this->db,3,$at->format('Y-m-d H:i:s'));
            $v=$w->arrive(['reference'=>'ACTIF-'.($i+1),'driver_id'=>$this->drivers[$carrier],'vehicle_id'=>$this->vehicles[$carrier],'operation'=>'reception']);
            if($i===5){$w->transition($v,'rejected',null,'Document de transport manquant (cas fictif)');continue;}
            $w->transition($v,'checked',null,'Contrôle conforme');if($i===4){$w->transition($v,'parking');continue;}
            if($i===3)continue;
            $w->transition($v,'called',$this->docks[$i]);$w->transition($v,'working');
            $notice=$cat->save('supplier_notice',null,['reference'=>'AVIS-A-RECEVOIR-'.($i+1),'supplier_id'=>$this->suppliers[$i],'expected_on'=>Clock::today()],1);
            for($j=1;$j<=2;$j++)$cat->save('notice_line',null,['notice_id'=>$notice,'article_id'=>$i*10+$j,'expected_qty'=>20],1);
            $receipt=$w->openReceipt($notice,$v,'REC-A-COMPLETER-'.($i+1));
            if($i===0)$w->reserveReceipt($receipt,null,'autre','Livraison partielle attendue : réduire l’attendu de cette livraison avant validation.');
        }
        $w=new Warehouse($this->db,2);
        for($i=0;$i<24;$i++){
            $owner=$this->owners[$i%18];$id=$cat->save('customer_order',null,['reference'=>'CMD-EN-COURS-'.sprintf('%02d',$i+1),'owner_id'=>$owner,'destination'=>'Client fictif '.$owner.', France','desired_on'=>$now->modify('+'.($i%7).' days')->format('Y-m-d')],1);
            $candidates=$this->db->all('SELECT article_id,SUM(available_qty) available FROM v_stock WHERE owner_id=? GROUP BY article_id HAVING SUM(available_qty)>=4 ORDER BY article_id LIMIT 2',[$owner]);
            foreach($candidates as $a)$cat->save('order_line',null,['order_id'=>$id,'article_id'=>$a['article_id'],'qty'=>2],1);
            if($i%4===1&&$candidates)$w->prepare($id,$this->preparers[$i%12]);
            if($i%4===2&&$candidates){$w->prepare($id,$this->preparers[$i%12]);$w->confirmPick($id,2,'manager');}
            if($i%4===3)$w->cancelOrder($id);
        }
        for($i=0;$i<30;$i++){$carrier=$this->carriers[$i%20];$at=$now->setTime(8+($i%8),0)->modify('+'.(1+intdiv($i,8)).' days');$id=$w->appointment(['reference'=>'RDV-FUTUR-'.sprintf('%02d',$i+1),'dock_id'=>$this->docks[$i%3],'driver_id'=>$this->drivers[$carrier],'vehicle_id'=>$this->vehicles[$carrier],'trailer_id'=>null,'operation'=>'reception','starts_at'=>$at->format('Y-m-d H:i:s'),'ends_at'=>$at->modify('+45 minutes')->format('Y-m-d H:i:s')]);if($i%9===0)$w->cancelAppointment($id);}
        $this->insert('dock_downtime',['dock_id'=>$this->docks[8],'starts_at'=>$now->modify('-1 hour')->format('Y-m-d H:i:s'),'ends_at'=>$now->modify('+2 hours')->format('Y-m-d H:i:s'),'reason'=>'Maintenance du niveleur (fictive)']);
    }
}

$name=getenv('BD70_DATABASE')?:'';
if(!preg_match('/^bd70_(demo_rich|test_rich)[a-z0-9_]*$/',$name))die("Choisir une base neuve bd70_demo_rich* ou bd70_test_rich*.\n");
$db=new Database();if($db->scalar('SELECT COUNT(*) FROM user_account'))throw new RuntimeException('Génération refusée : base déjà alimentée.');
$reference=new DateTimeImmutable(Warehouse::date($argv[1]??Clock::today()).' 00:00:00',new DateTimeZone('Europe/Paris'));$days=max(1,min(180,(int)($argv[2]??90)));mt_srand(70);$dataset=new RichDataset($db,$reference);
// Première création de compte avant la transaction attribuée à l'administrateur.
$db->pdo->beginTransaction();try{$dataset->setup();$db->pdo->commit();}catch(Throwable $e){$db->pdo->rollBack();throw $e;}
$index=0;
for($day=$days;$day>=1;$day--){$date=$reference->modify('-'.$day.' days');$db->transaction(1,function()use($dataset,$date,&$index){for($hour=8;$hour<18;$hour++)$dataset->cycle($index++,$date->setTime($hour,0));});if($day%10===0)echo ($days-$day+1)." jours générés\n";}
$dataset->live();
$counts=[];foreach($db->all('SHOW FULL TABLES WHERE Table_type="BASE TABLE"') as $row){$t=array_values($row)[0];$counts[$t]=(int)$db->scalar('SELECT COUNT(*) FROM `'.$t.'`');}
file_put_contents(__DIR__.'/../docs/preuves/donnees-riches.json',json_encode(['database'=>$name,'reference_date'=>$reference->format('Y-m-d'),'timezone'=>'Europe/Paris','seed'=>70,'days'=>$days,'historical_data'=>'Simulation fictive cohérente ; scénarios actifs créés par Warehouse','volumes'=>$counts],JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
echo json_encode($counts,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE)."\n";
