<?php
declare(strict_types=1);
require __DIR__.'/../src/bootstrap.php';
$name=getenv('BD70_DATABASE')?:'';
if(!preg_match('/^bd70_(demo|test)[a-z0-9_]*$/',$name)){fwrite(STDERR,"Définir BD70_DATABASE vers une base de démonstration/test neuve, déjà installée.\n");exit(1);}
$db=new Database();
foreach($db->all('SHOW FULL TABLES WHERE Table_type="BASE TABLE"') as $row){$t=array_values($row)[0];if($t!=='site_lock'&&(int)$db->scalar('SELECT COUNT(*) FROM `'.$t.'`'))throw new RuntimeException('Import refusé : base non vide ('.$t.').');}
$path=__DIR__.'/../sql/07_donnees_demo_riches.sql';$handle=fopen($path,'rb');if(!$handle)throw new RuntimeException('Export SQL absent.');
$db->pdo->beginTransaction();$buffer='';
try{
 while(($line=fgets($handle))!==false){if(trim($line)===''||str_starts_with(ltrim($line),'--'))continue;$buffer.=$line;if(str_ends_with(trim($line),';')){$db->pdo->exec($buffer);$buffer='';}}
 if(trim($buffer)!=='')throw new RuntimeException('Export SQL incomplet.');
 $db->pdo->commit();echo 'Données fictives importées dans '.$name.". Vérifier avec scripts/validate-data.php.\n";
}catch(Throwable $e){if($db->pdo->inTransaction())$db->pdo->rollBack();throw $e;}finally{fclose($handle);$db->pdo->exec('SET FOREIGN_KEY_CHECKS=1');}
