<?php
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';
ini_set('session.use_strict_mode','1');
session_name('bd70_session');
session_set_cookie_params(['httponly'=>true,'samesite'=>'Lax','secure'=>!empty($_SERVER['HTTPS']),'path'=>'/']);
session_start();
header("Content-Security-Policy: default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; frame-ancestors 'none'; form-action 'self'; base-uri 'none'");
header('X-Content-Type-Options: nosniff');header('Referrer-Policy: same-origin');header('Cache-Control: no-store');
$_SESSION['csrf']??=bin2hex(random_bytes(24));
$user=null;$error=null;$page=(string)($_GET['page']??'home');$message=$_SESSION['message']??null;unset($_SESSION['message']);
try {
    $db=new Database();$catalog=new Catalog($db);$reports=new Reports($db);
    if(isset($_SESSION['uid'])){
        $user=$db->run('SELECT id,name,email,role,active,carrier_id FROM user_account WHERE id=?',[$_SESSION['uid']])->fetch()?:null;
        if(!$user||!$user['active']||$user['role']==='pending'){unset($_SESSION['uid']);$user=null;}
    }
    if($user&&$user['role']==='carrier'&&$_SERVER['REQUEST_METHOD']==='POST')$page='carrier_portal';
    if($_SERVER['REQUEST_METHOD']==='POST'){
        if(!is_string($_POST['csrf']??null)||!hash_equals($_SESSION['csrf'],$_POST['csrf']))throw new RuntimeException('Formulaire expiré ou protection CSRF absente. Rechargez la page.',403);
        $action=(string)($_POST['action']??'');$w=$user?new Warehouse($db,(int)$user['id']):null;
        if($action==='login'){$user=Auth::login($db,(string)($_POST['email']??''),(string)($_POST['password']??''));$_SESSION['message']='Connexion réussie.';header('Location: /');exit;}
        if($action==='register'){Auth::register($db,$_POST);$_SESSION['message']='Compte créé en attente d’activation par un administrateur.';header('Location: /');exit;}
        if(!$user)throw new RuntimeException('Connexion requise.',401);
        if($user['role']==='carrier' && $action!=='logout'){
            require_once __DIR__.'/../src/CarrierPortal.php';
            (new CarrierPortal($db,$user))->act($action,$_POST);
            $_SESSION['message']='Rendez-vous enregistré.';header('Location: /?page=carrier_portal');exit;
        }
        if(in_array($action,['assign_preparer','reset_preparation','cancel_order'],true))Auth::demand($user,'manage_orders');
        if(in_array($action,['prepare','confirm','confirm_pick','ship'],true)&&$user['role']!=='warehouse')throw new RuntimeException('Action réservée au magasinier.',403);
        if(in_array($action,['prepare','confirm','ship'],true))Auth::orderAccess($db,$user,Warehouse::positive($_POST['id']??0));
        if($action==='confirm_pick')Auth::orderAccess($db,$user,(int)$db->scalar('SELECT l.order_id FROM pick p JOIN order_line l ON l.id=p.order_line_id WHERE p.id=?',[(int)($_POST['pick_id']??0)]));
        switch($action){
          case 'logout': $_SESSION=[];session_regenerate_id(true);header('Location: /');exit;
          case 'save': $t=(string)($_POST['table']??'');$catalog->check($t);Auth::catalogWrite($db,$user,$t,empty($_POST['id'])?null:(int)$_POST['id'],$_POST);$catalog->save($t,empty($_POST['id'])?null:(int)$_POST['id'],$_POST,(int)$user['id']);break;
          case 'delete': $t=(string)($_POST['table']??'');$catalog->check($t);Auth::catalogWrite($db,$user,$t,empty($_POST['id'])?null:(int)$_POST['id'],$_POST);$catalog->delete($t,Warehouse::positive($_POST['id']??0),(int)$user['id']);break;
          case 'cancel_appointment': Auth::demand($user,'planning');$w->cancelAppointment(Warehouse::positive($_POST['id']??0));break;
          case 'arrive': Auth::demand($user,'visits');$w->arrive($_POST);break;
          case 'transition': if(!Auth::transitionAllowed($user,(string)($_POST['next']??'')))throw new RuntimeException('Étape réservée au profil responsable de cette opération.',403);$w->transition(Warehouse::positive($_POST['id']??0),(string)($_POST['next']??''),empty($_POST['dock_id'])?null:(int)$_POST['dock_id'],trim((string)($_POST['document_note']??'')));break;
          case 'open_receipt': Auth::demand($user,'stock');$rid=$w->openReceipt(Warehouse::positive($_POST['notice_id']??0),Warehouse::positive($_POST['visit_id']??0),trim((string)($_POST['reference']??'')));$_POST['back']=url(['page'=>'receipt_detail','id'=>$rid]);break;
          case 'reserve_receipt': Auth::demand($user,'stock');$w->reserveReceipt(Warehouse::positive($_POST['receipt_id']??0),empty($_POST['line_id'])?null:Warehouse::positive($_POST['line_id']),(string)($_POST['kind']??''),(string)($_POST['reason']??''));break;
          case 'receive_item': Auth::demand($user,'stock');$w->receiveItem(Warehouse::positive($_POST['receipt_id']??0),$_POST);break;
          case 'close_notice': Auth::demand($user,'stock');$w->closeNotice(Warehouse::positive($_POST['notice_id']??0),(string)($_POST['reason']??''));break;
          case 'reset_preparation': Auth::demand($user,'orders');$w->resetPreparation(Warehouse::positive($_POST['id']??0),(string)($_POST['reason']??''));break;
          case 'confirm_pick': Auth::demand($user,'orders');$w->confirmPickLine(Warehouse::positive($_POST['pick_id']??0),(int)$user['id'],$user['role']);break;
          case 'receipt': Auth::demand($user,'stock');$w->validateReceipt(Warehouse::positive($_POST['id']??0));break;
          case 'transfer': Auth::demand($user,'stock');$w->transfer(Warehouse::positive($_POST['receipt_item_id']??0),Warehouse::positive($_POST['source_id']??0),Warehouse::positive($_POST['dest_id']??0),Warehouse::positive($_POST['qty']??0),trim((string)($_POST['reason']??'')));break;
          case 'adjust': Auth::demand($user,'stock');if(!preg_match('/^-?[1-9]\d*$/',(string)($_POST['delta']??'')))throw new DomainException('Variation entière non nulle requise.');$w->adjust(Warehouse::positive($_POST['receipt_item_id']??0),Warehouse::positive($_POST['location_id']??0),(int)$_POST['delta'],trim((string)($_POST['reason']??'')));break;
          case 'assign_preparer': Auth::demand($user,'manage_orders');$w->assignPreparer(Warehouse::positive($_POST['id']??0),Warehouse::positive($_POST['preparer_id']??0));break;
          case 'prepare': Auth::demand($user,'orders');$w->prepare(Warehouse::positive($_POST['id']??0),(int)$user['id']);break;
          case 'confirm': Auth::demand($user,'orders');$w->confirmPick(Warehouse::positive($_POST['id']??0),(int)$user['id'],$user['role']);break;
          case 'cancel_order': Auth::demand($user,'orders');$w->cancelOrder(Warehouse::positive($_POST['id']??0));break;
          case 'ship': Auth::demand($user,'orders');$w->ship(Warehouse::positive($_POST['id']??0),Warehouse::positive($_POST['visit_id']??0));break;
          default: throw new DomainException('Action inconnue.');
        }
        $_SESSION['message']='Opération enregistrée.';
        $back=(string)($_POST['back']??'/');if(!preg_match('~^/\?[^\r\n]*$~',$back))$back='/';header('Location: '.$back);exit;
    }
    if(!$user)$page='login';
    else {
        if($page==='home'&&$user['role']==='carrier')$page='carrier_portal';
        if($user['role']==='carrier'&&$page!=='carrier_portal')throw new RuntimeException('Accès limité aux rendez-vous de votre société.',403);
        if($user['role']==='admin'&&!in_array($page,['home','catalog'],true))throw new RuntimeException('Administrateur technique : accès métier interdit.',403);
        if($page==='visits') {if(!Auth::can($user,'visits')&&!Auth::can($user,'operations'))throw new RuntimeException('Accès interdit.',403);}
        if(in_array($page,['order_detail','document'],true))Auth::orderAccess($db,$user,(int)($_GET['id']??0));
        $right=match($page){'planning'=>'trace','carrier_portal'=>'carrier_portal','visits'=>null,'stock','receipts','receipt_detail','notices'=>'stock','orders','order_detail','document'=>'orders','reports','export'=>'reports','trace'=>'trace',default=>null};
        if($right)Auth::demand($user,$right);
        if($page==='catalog'){
            $table=(string)($_GET['t']??($user['role']==='admin'?'user_account':'carrier'));$catalog->check($table);
            Auth::catalogRead($user,$table);
        }
        if(!in_array($page,['home','catalog','planning','visits','stock','receipts','orders','reports','trace','document','export','receipt_detail','order_detail','notices','carrier_portal'],true))throw new RuntimeException('Page introuvable.',404);
        if($page==='export'){
            $kind=(string)($_GET['kind']??'stock');$res=match($kind){'stock'=>$reports->stock($_GET,true),'visits'=>$reports->visits($_GET,true),'receipts'=>$reports->receipts($_GET,true),default=>throw new DomainException('État inconnu.')};
            $rows=$res['rows'];if($kind==='stock')$rows=array_map(fn($r)=>['article'=>$r['sku'],'designation'=>$r['article_name'],'lot'=>$r['lot_code'],'proprietaire'=>$r['owner_name'],'zone'=>$r['zone_name'],'emplacement'=>$r['location_code'],'quantite'=>$r['qty'],'reserve'=>$r['reserved_qty'],'disponible'=>$r['available_qty'],'bloque'=>$r['blocked'],'dlc'=>$r['expires_on']],$rows);
            elseif($kind==='visits')$rows=array_map(fn($r)=>['passage'=>$r['reference'],'transporteur'=>$r['carrier_name'],'camion'=>$r['plate'],'etat'=>Catalog::VALUES[$r['status']]??$r['status'],'arrivee'=>$r['arrived_at'],'attente_min'=>$r['wait_minutes'],'immobilisation_min'=>$r['immobilized_minutes']],$rows);
            header('Content-Type: text/csv; charset=utf-8');header('Content-Disposition: attachment; filename="bd70-'.$kind.'.csv"');$f=fopen('php://output','w');fwrite($f,"\xEF\xBB\xBF");
            if($rows){fputcsv($f,array_keys($rows[0]),';','"','');foreach($rows as $r)fputcsv($f,array_map(fn($v)=>is_string($v)&&preg_match('/^[=+@\-]/',$v)?"'".$v:$v,$r),';','"','');}else fputcsv($f,['Aucun résultat pour ces filtres.'],';','"','');exit;
        }
    }
} catch(Throwable $e){
    $code=$e->getCode();if(in_array($code,[401,403,404],true))http_response_code($code);else http_response_code(422);
    if($e instanceof PDOException){$state=$e->errorInfo[0]??'';$error=$state==='23000'?'Référence déjà utilisée, relation manquante ou suppression protégée.':($state==='22001'?'Texte trop long.':'Opération refusée par les contraintes de données.');error_log('BD70 SQL '.$state.' / '.($e->errorInfo[1]??''));}
    elseif($e instanceof DomainException||in_array($code,[401,403,404],true))$error=$e->getMessage();
    else {$error='Service indisponible. Consultez le journal local du serveur.';error_log('BD70 '.get_class($e).': '.$e->getMessage());}
    if(in_array($code,[401,403,404],true))$page=$user?'error':'login';
    if(!isset($db))$page='error';
}
// Une erreur de formulaire anonyme ne doit jamais rendre un écran métier.
if(!$user&&isset($db))$page='login';
require __DIR__.'/../templates/layout.php';
