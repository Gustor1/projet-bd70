<?php
// Compte pédagogique public : création/récupération exclusivement en CLI locale.
declare(strict_types=1);
if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
require __DIR__.'/../src/Database.php';
$config=require __DIR__.'/../config/local.php';
if(!preg_match('/(?:^|;)host=(127\.0\.0\.1|localhost)(?:;|$)/',preg_replace('/^mysql:/','',$config['dsn']))){
    fwrite(STDERR,"Commande réservée à une base MariaDB locale.\n");exit(1);
}
$db=new Database($config);
$name=(string)$db->scalar('SELECT DATABASE()');
if(!preg_match('/^bd70_(demo|test)[a-z0-9_]*$/',$name)){
    fwrite(STDERR,"Commande réservée aux bases pédagogiques bd70_demo* ou bd70_test*.\n");exit(1);
}
$email='admin@bd70.test';$password='Entrepot2026!';
$db->pdo->beginTransaction();
try{
    $lock=$db->run('CALL lock_site()');$lock->closeCursor();
    $user=$db->run('SELECT * FROM user_account WHERE email=? FOR UPDATE',[$email])->fetch();
    if(!$user){
        $db->run('SET @actor_id=NULL');
        $db->insert('user_account',['email'=>$email,'name'=>'Administrateur de test du groupe','password_hash'=>password_hash($password,PASSWORD_DEFAULT),'role'=>'admin','active'=>1]);
        $message='Compte administrateur de test créé';
    }elseif($user['role']!=='admin'||!$user['active']||!password_verify($password,$user['password_hash'])){
        $db->run('SET @actor_id=?',[$user['id']]);
        $db->run("UPDATE user_account SET role='admin',active=1,password_hash=? WHERE id=?",[password_hash($password,PASSWORD_DEFAULT),$user['id']]);
        $message='Accès administrateur de test rétabli';
    }else $message='Compte administrateur de test déjà disponible (aucune modification)';
    $db->pdo->commit();
    echo $message.' dans '.$name.".\nIdentifiants : voir COMPTES-TEST.md à la racine du projet.\n";
}catch(Throwable $e){
    if($db->pdo->inTransaction())$db->pdo->rollBack();
    fwrite(STDERR,"Impossible de préparer le compte de test. Vérifiez l’installation locale.\n");exit(1);
}
