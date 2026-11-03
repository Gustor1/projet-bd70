"""Recette isolée. Aucune base existante supprimée, aucune preuve ancienne écrasée.

Usage: python scripts/verify-finalisation.py
BD70_RUN_ID permet une nouvelle exécution ; sorties dans livrables/preuves/<id>.
BD70_PYTHON/BD70_NODE/BD70_PLAYWRIGHT permettent de choisir les outils.
"""
from pathlib import Path
import os, subprocess, shutil, json, datetime, re, hashlib, time, socket

ROOT=Path(__file__).resolve().parents[1]
for port in [8071,8072]:
    with socket.socket() as probe:
        try:probe.bind(('127.0.0.1',port))
        except OSError:raise SystemExit(f'Port de recette {port} déjà occupé ; arrêter le serveur concerné avant de continuer.')
run=os.environ.get('BD70_RUN_ID','finalisation-'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
assert re.fullmatch(r'[a-z0-9_-]+',run)
work=ROOT/'.local'/run
proof=ROOT/'livrables/preuves'/run
if work.exists() or proof.exists():raise SystemExit('Choisir un nouvel identifiant BD70_RUN_ID ; aucune réutilisation.')
work.mkdir(parents=True);proof.mkdir(parents=True)
for folder in ['src','templates','public','sql','scripts','tests','config']:shutil.copytree(ROOT/folder,work/folder)
(work/'.local').mkdir();(work/'livrables/preuves').mkdir(parents=True)
baseline=ROOT/'.local/bd70-demo-final-before-completion.sql'
if baseline.exists():shutil.copy2(baseline,work/'.local'/baseline.name)
php=os.environ.get('BD70_PHP','C:/xampp2/php/php.exe')
node=os.environ.get('BD70_NODE','node');python=os.environ.get('BD70_PYTHON','python')
env=os.environ.copy();env.pop('BD70_NOW',None);env.pop('BD70_DATABASE',None);env.pop('BD70_TEST_DATABASE',None)
suffix=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
results=[]
def call(args,custom=None,label=None,timeout=900):
    label=label or Path(args[-1]).stem
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        r=subprocess.run(args,cwd=work,env=custom or env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
        output=r.stdout.decode('utf-8',errors='replace');code=r.returncode
    except subprocess.TimeoutExpired:
        output='Timeout';code=-1
    (proof/(label+'.log')).write_text(output,encoding='utf-8')
    results.append({'command':args,'label':label,'started_at':started,'exit_code':code})
    (proof/'execution.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(label,code,flush=True)
    return code==0
def install(kind,seed=True):
    name='bd70_test_'+kind+'_'+suffix
    if kind=='perf':name='bd70_perf_'+suffix
    if not call([php,'scripts/install.php',name],label='install-'+kind):raise RuntimeError('Installation '+kind)
    e={**env,'BD70_DATABASE':name,'BD70_TEST_DATABASE':name}
    if seed:
        if not call([php,'scripts/seed.php'],e,label='seed-'+kind):raise RuntimeError('Seed '+kind)
    return e
def collect():
    for f in (work/'livrables/preuves').iterdir():
        if f.is_file():shutil.copy2(f,proof/f.name)
def demo_snapshot():
    code="require 'src/bootstrap.php';$db=new Database();$out=['database'=>$db->scalar('SELECT DATABASE()'),'tables'=>[]];foreach($db->all('SHOW FULL TABLES WHERE Table_type=\"BASE TABLE\"') as $r){$t=array_values($r)[0];$out['tables'][$t]=[$db->scalar('SELECT COUNT(*) FROM `'.$t.'`'),$db->all('CHECKSUM TABLE `'.$t.'`')];}echo json_encode($out);"
    return json.loads(subprocess.check_output([php,'-r',code],cwd=work,env=env))
demo_before=demo_snapshot()
try:
    lint=[]
    for folder in ['src','templates','public','scripts','tests']:
        for f in (work/folder).rglob('*.php'):
            r=subprocess.run([php,'-l',str(f)],capture_output=True)
            lint.append({'file':str(f.relative_to(work)),'ok':r.returncode==0})
    (proof/'syntaxe.json').write_text(json.dumps(lint,indent=2),encoding='utf-8')
    e=install('integration');call([php,'tests/integration.php'],e,'integration')
    e=install('completion');call([php,'tests/completion.php'],e,'completion')
    e=install('regression');call([php,'tests/finalisation.php'],e,'regression')
    call([php,'tests/time.php'],e,'heure')
    e=install('riche',False)
    call([php,'scripts/import-demo.php'],e,'import-riche')
    call([php,'scripts/validate-data.php'],e,'integrite')
    call([python,'scripts/backup-restore.py'],{**env,'BD70_BACKUP_SOURCE':e['BD70_DATABASE'],'BD70_RESTORE_TARGET':'bd70_restore_backup_'+suffix},'restauration')
    # Capture the actual freshly installed schema without rewriting repository metadata.
    (work/'docs/diagrammes').mkdir(parents=True)
    call([php,'scripts/model.php'],e,'schema')
    shutil.copy2(work/'docs/diagrammes/schema.json',proof/'schema-installe.json')
    e=install('ui');e['BD70_NOW']='2026-10-22 12:00:00'
    call([php,'tests/corrections.php'],e,'corrections')
    log=(work/'.local/web.log').open('wb')
    server=subprocess.Popen([php,'-S','127.0.0.1:8071','-t','public'],cwd=work,env=e,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        time.sleep(1)
        if server.poll() is not None:raise RuntimeError('Le serveur dédié ne démarre pas ; aucun test navigateur exécuté.')
        for test in ['corrections-browser','parcours']:
            call([node,'tests/'+test+'.cjs'],{**e,'BD70_URL':'http://127.0.0.1:8071'},test,600)
    finally:server.terminate();server.wait(timeout=10);log.close()
    e=install('perf',False);call([php,'scripts/performance.php','10000'],e,'performances')
    call([python,'scripts/clean-install.py'],{**env,'BD70_CLEAN_DIR':'installation-'+suffix,'BD70_CLEAN_DB':'bd70_test_install_'+suffix},'installation-propre')
    # Current copy migration: scripts/migrate-corrections.php, tested against the preserved rich demo.
    # Historical verify-migration.py remains available for the pre-correction schema.
finally:
    collect()
    demo_after=demo_snapshot()
    (proof/'demonstration-preservee.json').write_text(json.dumps({'unchanged':demo_before==demo_after,'before':demo_before,'after':demo_after},indent=2),encoding='utf-8')
    manifest={'executed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'run':run,'working_copy':str(work),'commands':results,'all_commands_passed':all(x['exit_code']==0 for x in results),'sources_sha256':{str(f.relative_to(work)):hashlib.sha256(f.read_bytes()).hexdigest() for folder in ['src','templates','tests','sql'] for f in (work/folder).rglob('*') if f.is_file()}}
    (proof/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Preuves :',proof,flush=True)

raise SystemExit(0 if all(x["exit_code"]==0 for x in results) and all(x["ok"] for x in lint) and demo_before==demo_after else 1)
