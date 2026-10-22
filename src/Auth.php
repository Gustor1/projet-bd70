<?php
declare(strict_types=1);

final class Auth
{
    public const RIGHTS = [
        'admin'=>['catalog','accounts','planning','visits','stock','orders','reports','trace'],
        'manager'=>['catalog','planning','visits','stock','orders','reports','trace'],
        'gate'=>['planning','visits','trace'],
        'warehouse'=>['stock','orders','trace'], 'pending'=>[],
    ];
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
