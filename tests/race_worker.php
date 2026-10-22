<?php
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';
putenv('BD70_DATABASE='.(getenv('BD70_TEST_DATABASE')?:'bd70_test'));$db=new Database();$w=new Warehouse($db,1,'2026-10-22 12:00:00');
$payload=json_decode(base64_decode($argv[2]),true);$at=(float)$argv[3];while(microtime(true)<$at)usleep(1000);
try {
 match($argv[1]){
  'appointment'=>$w->appointment($payload),
  'call'=>$w->transition((int)$payload['id'],'called',(int)$payload['dock']),
  'transfer'=>$w->transfer((int)$payload['item'],(int)$payload['source'],(int)$payload['dest'],(int)$payload['qty'],'Test concurrent'),
  'prepare'=>$w->prepare((int)$payload['order'],(int)$payload['preparer']),
 };
 echo json_encode(['ok'=>true,'connection'=>$db->scalar('SELECT CONNECTION_ID()')]);
}catch(Throwable $e){echo json_encode(['ok'=>false,'connection'=>$db->scalar('SELECT CONNECTION_ID()'),'error'=>$e->getMessage()]);}
