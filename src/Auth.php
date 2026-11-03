<?php
declare(strict_types=1);

final class Auth
{
    public const RIGHTS = [
        'admin'=>['accounts'],
        'manager'=>['catalog','planning','manage_orders','reports','trace','orders'],
        'gate'=>['visits','trace'],
        'warehouse'=>['stock','orders','operations','trace'],
        'carrier'=>['carrier_portal'], 'pending'=>[],
    ];
    public static function transitionAllowed(array $user,string $next): bool
    { return self::can($user,in_array($next,['working','finished'],true)?'operations':'visits'); }
    public static function orderAccess(Database $db,array $user,int $id): void
    {
        self::demand($user,'orders');
        if($user['role']==='warehouse' && (int)$db->scalar('SELECT preparer_id FROM customer_order WHERE id=?',[$id])!==(int)$user['id'])
            throw new RuntimeException('Commande non affectée à cet utilisateur.',403);
    }
    public static function catalogRead(array $user,string $table): void
    {
        if($user['role']==='admin'){if(!in_array($table,['user_account','audit_log'],true))throw new RuntimeException('Accès métier interdit.',403);return;}
        if($user['role']==='carrier')throw new RuntimeException('Utilisez votre espace transporteur.',403);
        if(in_array($table,['user_account','audit_log'],true))throw new RuntimeException('Accès interdit pour ce profil.',403);
        if($user['role']==='gate'&&!in_array($table,['carrier','driver','vehicle','equipment','qualification','driver_qualification','vehicle_equipment','dock','dock_equipment','dock_vehicle_type','appointment','truck_visit','visit_event','dock_downtime'],true))throw new RuntimeException('Accès interdit pour ce profil.',403);
        if($user['role']==='warehouse'&&in_array($table,['customer_order','order_line','pick','package','package_pick','shipment'],true))throw new RuntimeException('Utilisez vos commandes affectées.',403);
    }
    public static function catalogWrite(Database $db,array $user,string $table,?int $id,array $input): void
    {
        self::demand($user,(new Catalog($db))->right($table));
        if(in_array($table,['package','package_pick'],true)&&$user['role']!=='warehouse')throw new RuntimeException('Conditionnement réservé au magasinier affecté.',403);
        if($user['role']==='warehouse'&&in_array($table,['package','package_pick'],true)){
            if($table==='package'){
                $order=$id?$db->scalar('SELECT order_id FROM package WHERE id=?',[$id]):($input['order_id']??0);
            }else{
                $package=$id?$db->scalar('SELECT package_id FROM package_pick WHERE id=?',[$id]):($input['package_id']??0);
                $order=$db->scalar('SELECT order_id FROM package WHERE id=?',[(int)$package]);
            }
            self::orderAccess($db,$user,(int)$order);
            // Also check the proposed parent when editing an allocation.
            if(isset($input['order_id']))self::orderAccess($db,$user,(int)$input['order_id']);
            if(isset($input['package_id']))self::orderAccess($db,$user,(int)$db->scalar('SELECT order_id FROM package WHERE id=?',[(int)$input['package_id']]));
        }
    }
    public static function can(array $user,string $right): bool { return (bool)$user['active'] && in_array($right,self::RIGHTS[$user['role']]??[],true); }
    public static function demand(array $user,string $right): void { if (!self::can($user,$right)) throw new RuntimeException('Accès interdit pour ce profil.',403); }
    public static function register(Database $db,array $data): void
    {
        $email=trim($data['email']??''); $name=trim($data['name']??''); $pass=$data['password']??'';
        if (!filter_var($email,FILTER_VALIDATE_EMAIL)||mb_strlen($email)>190||$name===''||mb_strlen($name)>100||strlen($pass)<10||strlen($pass)>72) throw new DomainException('Nom et email valides, mot de passe de 10 à 72 caractères requis.');
        $db->insert('user_account',['email'=>$email,'name'=>$name,'password_hash'=>password_hash($pass,PASSWORD_DEFAULT),'role'=>'pending','active'=>0]);
    }
    public static function login(Database $db,string $email,string $password): array
    {
        $u=$db->run('SELECT * FROM user_account WHERE email=?',[trim($email)])->fetch();
        if (!$u || !password_verify($password,$u['password_hash']) || !$u['active'] || $u['role']==='pending') throw new DomainException('Connexion refusée. Vérifiez vos identifiants et l’activation du compte.');
        session_regenerate_id(true); $_SESSION['uid']=$u['id']; $_SESSION['csrf']=bin2hex(random_bytes(24)); return $u;
    }
}
