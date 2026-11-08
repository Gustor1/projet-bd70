"""Compare reviewed model sources with metadata exported from a NEW test database.

python scripts/verify-models.py path/to/schema-installe.json output.json
No database or artifact is changed, except the explicitly named JSON proof.
"""
from pathlib import Path
import json,sys,re,hashlib
root=Path(__file__).resolve().parents[1]
actual=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
snapshot=json.loads((root/'docs/diagrammes/schema.json').read_text(encoding='utf-8'))
mcd=json.loads((root/'docs/mcd-chen/modele.json').read_text(encoding='utf-8'))
checks={}
def canonical(v):
    cols=[{k:c[k] for k in ['Field','Type','Null','Default','Extra']} for c in v['columns']]
    indexes=sorted((i['Key_name'],i['Non_unique'],i['Seq_in_index'],i['Column_name']) for i in v['indexes'])
    foreign=sorted((f['COLUMN_NAME'],f['REFERENCED_TABLE_NAME'],f['REFERENCED_COLUMN_NAME']) for f in v['foreign'])
    return cols,indexes,foreign
checks['tables']=set(actual)==set(snapshot)
for t,v in actual.items():checks['schema_'+t]=t in snapshot and canonical(v)==canonical(snapshot[t])
technical={'audit_log','site_lock','appointment_archive'};joins={'driver_qualification','vehicle_equipment','dock_equipment','dock_vehicle_type','package_pick'}
represented={field for r in mcd['associations'] for field in r['fields']}
attrs={t+'.'+a['key'] for t,e in mcd['entities'].items() if e['table'] for a in e['attrs']}
attrs|={a['key'] for r in mcd['associations'] for a in r['attrs']}
expected_fk={t+'.'+f['COLUMN_NAME'] for t,v in actual.items() if t not in technical for f in v['foreign']}
expected_attrs={t+'.'+c['Field'] for t,v in actual.items() if t not in technical for c in v['columns'] if not(t in joins and c['Field']=='id')}
checks['mcd_fk_coverage']=expected_fk<=represented
checks['mcd_column_coverage']=expected_attrs<=represented|attrs
checks['mcd_entities']=set(mcd['entities'])==set(actual)-joins-technical|{'vehicle_type'}
checks['five_join_associations']={r.get('join') for r in mcd['associations'] if r.get('join')}==joins
for r in mcd['associations']:
    if r.get('join'):
        checks['cardinality_'+r['id']]=r['ca']==r['cb']=='0,N'
    elif len(r['fields'])==1:
        table,col=r['fields'][0].split('.')
        if table not in actual:continue
        v=actual[table];fk=next((f for f in v['foreign'] if f['COLUMN_NAME']==col),None)
        if not fk:continue
        optional=next(c['Null']=='YES' for c in v['columns'] if c['Field']==col)
        keys={}
        for i in v['indexes']:
            if not i['Non_unique']:keys.setdefault(i['Key_name'],[]).append(i['Column_name'])
        unique=[col] in keys.values()
        child_card='0,1' if optional else '1,1'
        parent_card='0,1' if unique else '0,N'
        # A mandatory first event is an application invariant beyond bare FK.
        a=r['ca'];b=r['cb']
        if table==r['a']:checks['cardinality_'+r['id']]=a==child_card and b==parent_card
        else:checks['cardinality_'+r['id']]=b==child_card and (a==parent_card or (table=='visit_event' and a=='1,N'))
chen=(root/'docs/mcd-chen/BD70-MCD-CHEN.dot').read_text(encoding='utf-8')
# Convention du cours : du côté de l'entité a figure la cardinalité de b, et inversement.
for relation in mcd['associations']:
    checks['chen_'+relation['id']+'_a']=f'{relation["a"]} -- {relation["id"]} [taillabel="{relation["cb"]}"' in chen
    checks['chen_'+relation['id']+'_b']=f'{relation["id"]} -- {relation["b"]} [headlabel="{relation["ca"]}"' in chen
dot=(root/'docs/diagrammes/mld-complet.dot').read_text(encoding='utf-8')
for t,v in actual.items():
    checks['mld_'+t]=all(c['Field'] in dot for c in v['columns']) and all(f'{t} -> {f["REFERENCED_TABLE_NAME"]}' in dot for f in v['foreign'])
files=['sql/01_schema.sql','docs/diagrammes/schema.json','docs/diagrammes/mld-complet.dot','docs/diagrammes/mld-complet.svg','docs/mcd-chen/BD70-MCD-CHEN.svg','docs/mcd-chen/modele.json','livrables/use-case/UML-CAS-UTILISATION-BD70-CORRIGE.pdf']
result={'checks':checks,'passed':all(checks.values()),'missing_mcd_columns':sorted(expected_attrs-(represented|attrs)),'missing_mcd_fk':sorted(expected_fk-represented),'business_fk':len(expected_fk),'business_columns':len(expected_attrs),'sha256':{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files}}
Path(sys.argv[2]).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':result['passed'],'failed':[k for k,v in checks.items() if not v],'business_fk':len(expected_fk),'business_columns':len(expected_attrs)},ensure_ascii=False))
raise SystemExit(0 if result['passed'] else 1)
