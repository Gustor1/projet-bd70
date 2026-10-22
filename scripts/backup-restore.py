"""Sauvegarde binaire SQL et restauration isolée ; ne remplace jamais une base existante."""
import subprocess,json,os,datetime
from pathlib import Path
binary=Path(os.environ.get('BD70_MYSQL_BIN','C:/xampp2/mysql/bin'))
source=os.environ.get('BD70_BACKUP_SOURCE','bd70_demo_final');target=os.environ.get('BD70_RESTORE_TARGET','bd70_restore_verifiee')
import re
assert re.fullmatch(r'bd70_demo[a-z0-9_]*',source)
assert re.fullmatch(r'bd70_restore[a-z0-9_]*',target)
common=['--host=127.0.0.1','--port=3307','--user='+os.environ.get('BD70_ADMIN_USER','root'),'--default-character-set=utf8mb4']
# Un éventuel secret est transmis via l'environnement du client, jamais dans la commande ou le rapport.
env=os.environ.copy()
if os.environ.get('BD70_ADMIN_PASSWORD'):env['MYSQL_PWD']=os.environ['BD70_ADMIN_PASSWORD']
def sql(query,db=None):
 cmd=[str(binary/'mysql.exe'),*common,'--batch','--skip-column-names',*([db] if db else []),'--execute',query]
 return subprocess.check_output(cmd,env=env).decode('utf-8').strip()
exists=sql(f"SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name='{target}'")
if exists!='0':raise SystemExit('Restauration refusée : cible existante. Choisir un nouveau nom bd70_restore*.')
file=Path('.local')/(source+'-sauvegarde.sql')
with file.open('wb') as output:subprocess.run([str(binary/'mysqldump.exe'),*common,'--single-transaction','--routines','--triggers',source],stdout=output,env=env,check=True)
sql(f'CREATE DATABASE `{target}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
with file.open('rb') as data:subprocess.run([str(binary/'mysql.exe'),*common,target],stdin=data,env=env,check=True)
tables=sql('SHOW FULL TABLES WHERE Table_type="BASE TABLE"',source).splitlines();results=[]
for line in tables:
 table=line.split('\t')[0]
 left=sql(f'SELECT COUNT(*) FROM `{table}`',source);right=sql(f'SELECT COUNT(*) FROM `{table}`',target)
 checksum_left=sql(f'CHECKSUM TABLE `{table}`',source).split('\t')[-1];checksum_right=sql(f'CHECKSUM TABLE `{table}`',target).split('\t')[-1]
 results.append({'table':table,'source_count':int(left),'restored_count':int(right),'checksum_identical':checksum_left==checksum_right,'ok':left==right and checksum_left==checksum_right})
triggers=int(sql("SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema=DATABASE()",target))
procedures=int(sql("SELECT COUNT(*) FROM information_schema.routines WHERE routine_schema=DATABASE()",target))
old_audit=int(sql('SELECT COUNT(*) FROM audit_log',target))
sql("SET @actor_id=1; UPDATE carrier SET phone='000-RESTORE-TEST' WHERE id=1",target)
automatic=int(sql('SELECT COUNT(*) FROM audit_log',target))==old_audit+1
checks={'data':all(x['ok'] for x in results),'triggers_restored':triggers>0,'procedures_restored':procedures==2,'historisation_after_restore':automatic}
report={'date':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':source,'target':target,'tables':results,'triggers':triggers,'procedures':procedures,'checks':checks,'backup_bytes':file.stat().st_size}
Path('livrables/preuves/restauration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(results)} tables restaurées, {triggers} déclencheurs, {procedures} procédures. Contrôles : {checks}')
assert all(checks.values())
