<?php
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';$db=new Database();$cat=new Catalog($db);$model=[];
foreach([...array_keys(Catalog::TITLES),'site_lock'] as $t){
 $model[$t]=['title'=>Catalog::TITLES[$t]??'Verrou du site','columns'=>$db->all('SHOW COLUMNS FROM `'.$t.'`'),'indexes'=>$db->all('SHOW INDEX FROM `'.$t.'`'),'foreign'=>$db->all('SELECT COLUMN_NAME,REFERENCED_TABLE_NAME,REFERENCED_COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=? AND REFERENCED_TABLE_NAME IS NOT NULL',[$t])];
}
file_put_contents(__DIR__.'/../docs/diagrammes/schema.json',json_encode($model,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
file_put_contents(__DIR__.'/../docs/diagrammes/labels.json',json_encode(Catalog::LABELS,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
echo count($model)." tables exportées depuis le moteur réel.\n";
