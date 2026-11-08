"""Generate the complete relational schema from installed database metadata."""
import json,html,sys
from pathlib import Path
from collections import defaultdict
root=Path('docs/diagrammes');model=json.loads((root/'schema.json').read_text(encoding='utf-8'));labels=json.loads((root/'labels.json').read_text(encoding='utf-8'))
def dotquote(x):return json.dumps(x,ensure_ascii=False)
base='graph [fontname="Arial",bgcolor="white",pad="0.4",nodesep="0.6",ranksep="1",splines=polyline]; node [fontname="Arial",fontsize=12]; edge [fontname="Arial",fontsize=10,color="#617b94",fontcolor="#17324d"];\n'
# MLD : tous les attributs, PK, FK, clés candidates et nullabilité.
def mld(tables):
 s='digraph MLD {\nrankdir=LR;\n'+base
 parents={f['REFERENCED_TABLE_NAME'] for t in tables for f in model[t]['foreign']}
 for t in sorted(set(tables)|parents):
  if t not in tables:s+=f'{t} [shape=box,style="rounded,dashed",label={dotquote(model[t]["title"]+"\n"+t)},color="#a0aab5"];\n';continue
  rows=[];fk={f['COLUMN_NAME']:f['REFERENCED_TABLE_NAME'] for f in model[t]['foreign']}
  for c in model[t]['columns']:
   key=c['Field'];mark='PK ' if c['Key']=='PRI' else ('FK ' if key in fk else '')
   rows.append('<TR><TD ALIGN="LEFT">'+html.escape(mark+key)+'</TD><TD ALIGN="LEFT">'+html.escape(c['Type'])+'</TD><TD>'+('NULL' if c['Null']=='YES' else 'NN')+'</TD></TR>')
  unique=defaultdict(list)
  for idx in model[t]['indexes']:
   if not idx['Non_unique'] and idx['Key_name']!='PRIMARY':unique[idx['Key_name']].append(idx['Column_name'])
  for cols in unique.values():rows.append('<TR><TD COLSPAN="3" ALIGN="LEFT">UNIQUE ('+html.escape(', '.join(cols))+')</TD></TR>')
  s+=f'{t} [shape=plain,label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="6" COLOR="#8fa8be"><TR><TD COLSPAN="3" BGCOLOR="#17324d"><FONT COLOR="white"><B>{html.escape(t)}</B></FONT></TD></TR>'+''.join(rows)+ '</TABLE>>];\n'
 for t in tables:
  for f in model[t]['foreign']:
   optional=next(c['Null']=='YES' for c in model[t]['columns'] if c['Field']==f['COLUMN_NAME'])
   unique_fk=any(idx['Column_name']==f['COLUMN_NAME'] and not idx['Non_unique'] and sum(x['Key_name']==idx['Key_name'] for x in model[t]['indexes'])==1 for idx in model[t]['indexes'])
   s+=f'{t} -> {f["REFERENCED_TABLE_NAME"]} [label={dotquote(f["COLUMN_NAME"])},taillabel="'+('0..1' if unique_fk else '0..N')+'",headlabel="'+('0..1' if optional else '1')+'",labeldistance=2];\n'
 return s+'}'
(root/'mld-complet.dot').write_text(mld(list(model)),encoding='utf-8')
print("Schéma relationnel complet écrit dans docs/diagrammes/mld-complet.dot")
