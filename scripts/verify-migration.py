"""Restore the preserved baseline into a new database, migrate and compare old fields."""
import os, subprocess, json, re
from pathlib import Path
target=os.environ.get('BD70_MIGRATION_TARGET','bd70_restore_completion_final')
assert re.fullmatch(r'bd70_restore[a-z0-9_]*',target)
source='bd70_demo_final'
binary=Path(os.environ.get('BD70_MYSQL_BIN','C:/xampp2/mysql/bin'))
common=['--host=127.0.0.1','--port='+os.environ.get('BD70_PORT','3307'),'--user='+os.environ.get('BD70_ADMIN_USER','root'),'--default-character-set=utf8mb4','--batch','--skip-column-names']
env=os.environ.copy()
if env.get('BD70_ADMIN_PASSWORD'):env['MYSQL_PWD']=env['BD70_ADMIN_PASSWORD']
def query(sql,db=None):
    return subprocess.check_output([str(binary/'mysql.exe'),*common,*([db] if db else []),'--execute',sql],env=env)
if query(f"SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name='{target}'").strip()!=b'0':
    raise SystemExit('Cible existante : choisir BD70_MIGRATION_TARGET, aucune suppression automatique.')
backup=Path('.local/bd70-demo-final-before-completion.sql')
assert backup.is_file()
query(f'CREATE DATABASE `{target}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
with backup.open('rb') as stream:
    subprocess.run([str(binary/'mysql.exe'),*common,target],stdin=stream,env=env,check=True)
tables=[line.split('\t')[0] for line in query('SHOW FULL TABLES WHERE Table_type="BASE TABLE"',target).decode().splitlines()]
old={}
columns={}
audit_max=query('SELECT COALESCE(MAX(id),0) FROM audit_log',target).decode().strip()
for table in tables:
    columns[table]=[line.split('\t')[0] for line in query(f'SHOW COLUMNS FROM `{table}`',target).decode().splitlines()]
    cols=','.join('`'+c+'`' for c in columns[table])
    old[table]=query(f'SELECT {cols} FROM `{table}` ORDER BY id',target)
subprocess.run([os.environ.get('BD70_PHP','C:/xampp2/php/php.exe'),'scripts/migrate.php',target,str(backup)],check=True,env=env)
checks={}
for table in tables:
    cols=','.join('`'+c+'`' for c in columns[table])
    where=f' WHERE id<={audit_max}' if table=='audit_log' else ''
    checks[table]=old[table]==query(f'SELECT {cols} FROM `{table}`{where} ORDER BY id',target)
checks['allocations_historiques']=query('SELECT COUNT(*) FROM package_pick pp JOIN pick p ON p.id=pp.pick_id WHERE pp.qty<>p.qty',target).strip()==b'0'
checks['reserve_parent_exclusif']=b'receipt_id` is null' in query('SHOW CREATE TABLE receipt_reserve',target).lower()
Path('livrables/preuves/migration.json').write_text(json.dumps({'source':source,'backup':str(backup),'target':target,'checks':checks,'passed':all(checks.values())},ensure_ascii=False,indent=2),encoding='utf-8')
assert all(checks.values()),checks
print(f'Migration : {len(checks)} contrôles réussis ; colonnes préexistantes conservées.')
