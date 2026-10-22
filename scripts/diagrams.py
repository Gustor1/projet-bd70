"""Sources DOT/SVG distinctes : UML, MCD conceptuel et MLD physique exhaustif."""
import json,html
from pathlib import Path
from collections import defaultdict
root=Path('docs/diagrammes');model=json.loads((root/'schema.json').read_text(encoding='utf-8'));labels=json.loads((root/'labels.json').read_text(encoding='utf-8'))
def dotquote(x):return json.dumps(x,ensure_ascii=False)
base='graph [fontname="Arial",bgcolor="white",pad="0.4",nodesep="0.6",ranksep="1",splines=polyline]; node [fontname="Arial",fontsize=12]; edge [fontname="Arial",fontsize=10,color="#617b94",fontcolor="#17324d"];\n'
groups={
 'personnel-transport':['user_account','carrier','carrier_contact','carrier_contract','qualification','driver','driver_qualification','equipment','vehicle','vehicle_equipment'],
 'quais-passages':['dock','dock_equipment','dock_vehicle_type','dock_downtime','appointment','truck_visit','visit_event','driver','vehicle','equipment'],
 'articles-stockage':['owner','article','lot','zone','aisle','rack','rack_level','location'],
 'receptions-stock':['supplier','supplier_notice','notice_line','receipt','receipt_line','receipt_item','stock_movement','lot','location','truck_visit'],
 'commandes-expeditions':['customer_order','order_line','pick','package','package_pick','shipment','receipt_item','location','truck_visit','user_account'],
 'historisation':['audit_log','site_lock','user_account','stock_movement','visit_event'],
}
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
for group,tables in groups.items():(root/f'mld-{group}.dot').write_text(mld(tables),encoding='utf-8')
# Concepts et associations (pas de types SQL ni de FK dans le MCD).
concepts={k:v['title'] for k,v in model.items() if k not in ['site_lock','audit_log']}
relations=[
 ('carrier','driver','emploie','1','0..N'),('carrier','vehicle','exploite','1','0..N'),('carrier','carrier_contact','possède','1','0..N'),('carrier','carrier_contract','signe','1','0..N'),
 ('driver','qualification','est habilité (validité)','0..N','0..N'),('vehicle','equipment','est équipé','0..N','0..N'),('dock','equipment','dispose de','0..N','0..N'),
 ('dock','dock_vehicle_type','accepte un type','1','0..N'),('dock','dock_downtime','est indisponible','1','0..N'),('dock','appointment','accueille au planning','1','0..N'),('vehicle','appointment','est prévu','1','0..N'),('driver','appointment','est attendu','1','0..N'),
 ('appointment','truck_visit','donne lieu à','0..1','0..1'),('vehicle','truck_visit','effectue / remorque optionnelle','1','0..N'),('driver','truck_visit','conduit','1','0..N'),('dock','truck_visit','sert effectivement','0..1','0..N'),('truck_visit','visit_event','est horodaté','1','1..N'),('user_account','visit_event','enregistre','1','0..N'),
 ('owner','article','possède','1','0..N'),('article','lot','identifie','1','0..N'),('zone','aisle','contient','1','0..N'),('aisle','rack','contient','1','0..N'),('rack','rack_level','contient','1','0..N'),('rack_level','location','contient','1','0..N'),
 ('supplier','supplier_notice','annonce','1','0..N'),('supplier_notice','notice_line','détaille','1','0..N'),('article','notice_line','est attendu (quantité)','1','0..N'),('supplier_notice','receipt','est livré partiellement','1','0..N'),('truck_visit','receipt','achemine','1','0..N'),('receipt','receipt_line','contient','1','0..N'),('notice_line','receipt_line','est reçu (attendu local)','1','0..N'),('receipt_line','receipt_item','est répartie en fractions','1','0..N'),('lot','receipt_item','est reçu plusieurs fois','1','0..N'),('location','receipt_item','rangement initial','1','0..N'),
 ('receipt_item','stock_movement','est déplacée (quantité)','1','0..N'),('location','stock_movement','reçoit/débite','1','0..N'),('user_account','stock_movement','réalise','1','0..N'),
 ('owner','customer_order','commande','1','0..N'),('user_account','customer_order','prépare','0..1','0..N'),('customer_order','order_line','détaille','1','0..N'),('article','order_line','est commandé','1','0..N'),('order_line','pick','est servie (quantité)','1','0..N'),('receipt_item','pick','fournit le lot reçu','1','0..N'),('location','pick','est prélevé à','1','0..N'),('customer_order','package','est conditionnée','1','0..N'),('package','pick','contient (affectation)','0..1','0..N'),('customer_order','shipment','est expédiée','1','0..1'),('truck_visit','shipment','charge','1','0..N'),('pick','stock_movement','produit la sortie','0..1','0..1')]
assoc_tables={'driver_qualification','vehicle_equipment','dock_equipment','package_pick'}
def mcd(tables):
 ts=set(tables)-assoc_tables-{'site_lock','audit_log'};s='graph MCD {\nrankdir=LR;\n'+base
 for t in sorted(ts):
  attrs=[labels.get(c['Field'],c['Field']) for c in model[t]['columns'] if c['Field']!='id' and not c['Field'].endswith('_id') and c['Field']!='password_hash'][:4]
  s+=f'{t} [shape=box,style="rounded,filled",fillcolor="#edf4fa",color="#5b82a6",label={dotquote(concepts[t]+chr(10)+chr(10).join(attrs))}];\n'
 for n,(a,b,label,ca,cb) in enumerate(relations):
  if a not in ts or b not in ts:continue
  s+=f'assoc{n} [shape=diamond,fontsize=10,label={dotquote(label)},color="#7693ad"];{a} -- assoc{n} [taillabel={dotquote(ca)},labeldistance=2];assoc{n} -- {b} [headlabel={dotquote(cb)},labeldistance=2];\n'
 return s+'}'
(root/'mcd-complet.dot').write_text(mcd(list(concepts)),encoding='utf-8')
for group,tables in groups.items():
 if group!='historisation':(root/f'mcd-{group}.dot').write_text(mcd(tables),encoding='utf-8')
# UML de cas d'utilisation : acteurs, frontière système et ellipses, include/extend.
uml='digraph UML {\nrankdir=LR;\n'+base
for actor,label in [('admin','Administrateur'),('manager','Responsable'),('gate','Accueil'),('warehouse','Magasinier')]:uml+=f'{actor} [shape=plaintext,label={dotquote("◯\n/|\\\n/ \\\n"+label)}];\n'
uml+='subgraph cluster_system { label="Transit - Système de gestion d’un entrepôt";color="#6c8aa4";style=rounded;\n'
for uc,label in [('auth','UC01 Accéder au système'),('refs','UC02 Gérer les référentiels'),('reserve','UC03 Planifier les quais'),('flow','UC04 Suivre les camions'),('receive','UC05 Réceptionner / ranger'),('stock','UC06 Déplacer / corriger le stock'),('pick','UC07 Préparer en FEFO'),('ship','UC08 Charger et expédier'),('trace','UC09 Tracer un lot'),('report','UC10 Analyser / exporter'),('rights','Vérifier les droits'),('availability','Vérifier la disponibilité'),('walkin','Traiter sans rendez-vous')]:uml+=f'{uc} [shape=ellipse,label={dotquote(label)},style=filled,fillcolor="#edf4fa",color="#6b8dac"];\n'
uml+='}\n'
for actor,ucs in {'admin':[],'manager':['refs','report'],'gate':['auth','reserve','flow','trace'],'warehouse':['auth','receive','stock','pick','ship','trace']}.items():
 for uc in ucs:uml+=f'{actor} -> {uc} [dir=none];\n'
for a,b,label in [('reserve','availability','include'),('stock','availability','include'),('receive','rights','include'),('ship','rights','include'),('walkin','flow','extend')]:uml+=f'{a} -> {b} [style=dashed,arrowhead=empty,label="«{label}»"];\n'
uml+='admin -> manager [arrowhead=empty,label="hérite",constraint=false];manager -> gate [arrowhead=empty,label="hérite",constraint=false];manager -> warehouse [arrowhead=empty,label="hérite",constraint=false];\n'
uml+='}'
(root/'cas-utilisation.dot').write_text(uml,encoding='utf-8')
# Dictionnaire exhaustif et dépendances fonctionnelles vérifiables table par table.
d=['# Dictionnaire des données','\nGénéré depuis les métadonnées du moteur exécuté. NN = obligatoire ; NULL = facultatif. Quantités : unités entières ; dimensions : m ; poids : kg ; capacité palettes : équivalents. Dates/heures civiles du site Europe/Paris. Les clés et FK ci-dessous sont réellement installées.\n']
n=['# Normalisation et dépendances fonctionnelles','\nLes relations représentent les faits décrits dans le contrat de conception. Pour chaque table, toutes les valeurs sont atomiques (1NF). Les associations N:N portent des unicités composées ; leurs attributs dépendent de la totalité de ces clés (2NF). Les attributs descriptifs du parent restent dans le parent : aucun nom de transporteur, d’article ou de propriétaire n’est recopié dans les lignes (3NF). Une PK artificielle ne constitue pas à elle seule cette justification.\n','Les clés UNIQUE contenant NULL sont des unicités conditionnelles, pas des clés candidates totales (appointment_id d’un passage, pick_id d’un mouvement). Le passage conserve les faits réels distincts du planning ; ses copies initiales constituent un instantané de l’affectation réelle. `status` est une projection opérationnelle conservée, vérifiée par les transitions ; durées, totaux et soldes ne sont pas stockés. L’attendu local d’une ligne de réception est l’allocation de la livraison partielle, et non la copie de l’attendu total de l’avis.\n']
crud=['# Matrice CRUD et droits','\nA = administrateur, R = responsable, G = accueil, M = magasinier. Tous les contrôles sont faits côté serveur ; compte en attente sans accès. Administration des utilisateurs réservée à A.\n','| Entité | Création / modification / suppression | Profil |\n|---|---|---|']
for t,v in model.items():
 unique=defaultdict(list)
 for idx in v['indexes']:
  if not idx['Non_unique']:unique[idx['Key_name']].append(idx['Column_name'])
 fk={f['COLUMN_NAME']:f['REFERENCED_TABLE_NAME']+'.'+f['REFERENCED_COLUMN_NAME'] for f in v['foreign']}
 d+=['\n## '+t+' - '+v['title'],'\nUnicités : '+ '; '.join('('+', '.join(cols)+')' for cols in unique.values())+'.','\n| Attribut | Sens | Type | NULL | Relation |\n|---|---|---|---|---|']
 for c in v['columns']:d.append('| '+c['Field']+' | '+labels.get(c['Field'],('Identifiant interne' if c['Field']=='id' else 'Valeur interne documentée dans SQL'))+' | '+c['Type']+' | '+c['Null']+' | '+fk.get(c['Field'],'')+' |')
 keys=['('+', '.join(cols)+')' for cols in unique.values() if all(next(c['Null']=='NO' for c in v['columns'] if c['Field']==col) for col in cols)]
 attrs=[c['Field'] for c in v['columns'] if c['Field']!='id']
 n+=['\n## '+t,'Clés candidates : '+', '.join(keys)+'. DF : chaque clé candidate → '+', '.join(attrs)+'.']
 if len(keys)>1:n+=['La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.']
 if fk:n+=['Les déterminants externes ('+', '.join(fk)+') ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.']
 n+=['Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.']
 if t in ['site_lock','audit_log','stock_movement','visit_event','shipment','pick']:rule='Actions métier uniquement ; historiques immuables, correction par mouvement ou annulation avant expédition.'
 elif t=='user_account':rule='Créer/activer/modifier/désactiver ; pas de suppression de l’auteur historique.'
 elif t=='appointment':rule='Créer/déplacer sous contrôle ; annuler avant usage ; pas de suppression.'
 elif t in ['receipt','receipt_line','receipt_item','notice_line','supplier_notice','customer_order','order_line','package','package_pick']:rule='CRUD de brouillon ; FK protectrices ; validation ou préparation fige les données ; annulation métier.'
 else:rule='CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage.'
 role='A' if t in ['user_account','audit_log','site_lock'] else ('A, R, G' if t in ['appointment','truck_visit','visit_event','dock_downtime'] else ('A, R, M' if t in ['supplier_notice','notice_line','receipt','receipt_line','receipt_item','lot','customer_order','order_line','package','package_pick','pick','shipment','stock_movement'] else 'A, R'))
 crud.append('| '+t+' | '+rule+' | '+role+' |')
(Path('docs')/'dictionnaire-donnees.md').write_text('\n'.join(d),encoding='utf-8');(Path('docs')/'normalisation-3nf.md').write_text('\n'.join(n),encoding='utf-8');(Path('docs')/'matrice-crud-droits.md').write_text('\n'.join(crud),encoding='utf-8')
print('Sources DOT, dictionnaire, DF et matrice CRUD écrits.')
