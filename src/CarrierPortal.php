<?php
declare(strict_types=1);

/** All carrier data access stays in this service, including forged identifiers. */
final class CarrierPortal
{
    public function __construct(private Database $db,private array $user) { Auth::demand($user,'carrier_portal');if(empty($user['carrier_id']))throw new RuntimeException('Société non configurée.',403); }
    public function appointments(): array
    { return $this->db->all('SELECT a.*,d.code dock_code,v.plate FROM appointment a JOIN vehicle v ON v.id=a.vehicle_id JOIN dock d ON d.id=a.dock_id WHERE v.carrier_id=? ORDER BY a.starts_at DESC LIMIT 200',[$this->user['carrier_id']]); }
    public function resources(string $table): array
    {
        if(!in_array($table,['vehicle','driver','dock'],true))throw new DomainException('Ressource inconnue.');
        $label=match($table){'vehicle'=>'plate','driver'=>'name',default=>'code'};
        return $this->db->all('SELECT id,'.$label.' label FROM '.$table.($table==='dock'?'':' WHERE carrier_id=?').' ORDER BY label',$table==='dock'?[]:[$this->user['carrier_id']]);
    }
    public function act(string $action,array $input): void
    {
        if(!in_array($action,['carrier_save','carrier_cancel'],true))throw new RuntimeException('Action interdite.',403);
        $this->db->transaction((int)$this->user['id'],function()use($action,$input){
            $id=empty($input['id'])?null:Warehouse::positive($input['id']);
            if($id&&!$this->db->scalar('SELECT a.id FROM appointment a JOIN vehicle v ON v.id=a.vehicle_id WHERE a.id=? AND v.carrier_id=?',[$id,$this->user['carrier_id']]))throw new RuntimeException('Rendez-vous inaccessible.',403);
            $w=new Warehouse($this->db,(int)$this->user['id']);
            if($action==='carrier_cancel'){if(!$id)throw new DomainException('Rendez-vous requis.');$w->cancelAppointment($id);return;}
            $d=[];foreach(['reference','dock_id','driver_id','vehicle_id','trailer_id','operation','starts_at','ends_at'] as $key)$d[$key]=$input[$key]??'';
            foreach(['driver_id'=>'driver','vehicle_id'=>'vehicle','trailer_id'=>'vehicle'] as $key=>$table){
                if($key==='trailer_id'&&$d[$key]===''){$d[$key]=null;continue;}
                $d[$key]=Warehouse::positive($d[$key]);
                if(!$this->db->scalar('SELECT id FROM '.$table.' WHERE id=? AND carrier_id=?',[$d[$key],$this->user['carrier_id']]))throw new RuntimeException('Ressource d’une autre société interdite.',403);
            }
            $d['dock_id']=Warehouse::positive($d['dock_id']);$d['starts_at']=Warehouse::datetime((string)$d['starts_at']);$d['ends_at']=Warehouse::datetime((string)$d['ends_at']);
            $w->saveAppointmentInside($id,$d);
        });
    }
}
