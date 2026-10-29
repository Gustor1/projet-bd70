"""Build the reviewed conceptual model without changing previous deliverables.

Usage: python scripts/build-mcd-final.py
Requires Python reportlab, svglib, pypdf and the bundled @viz-js/viz.
Generated Draw.io is native XML, not an embedded picture. Copy before manual edits.
"""
from pathlib import Path
import json, re, subprocess, hashlib, html, math
import xml.etree.ElementTree as ET
from io import BytesIO
from collections import Counter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, A2, A1, landscape
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'livrables' / 'mcd-final'
OUT.mkdir(exist_ok=True)
BUILD = OUT / 'sources'
BUILD.mkdir(exist_ok=True)
model = json.loads((ROOT/'docs/diagrammes/schema.json').read_text(encoding='utf-8'))
labels = json.loads((ROOT/'docs/diagrammes/labels.json').read_text(encoding='utf-8'))
sql = (ROOT/'sql/01_schema.sql').read_text(encoding='utf-8')
joins = {'driver_qualification','vehicle_equipment','dock_equipment','package_pick','dock_vehicle_type'}
technical = {'audit_log','site_lock'}
entities = {}
titles = {
 'user_account':'UTILISATEUR', 'carrier':'TRANSPORTEUR', 'carrier_contact':'CONTACT',
 'carrier_contract':'CONTRAT', 'qualification':'HABILITATION', 'driver':'CHAUFFEUR',
 'equipment':'ÉQUIPEMENT', 'vehicle':'VÉHICULE', 'dock':'QUAI', 'dock_downtime':'INDISPONIBILITÉ',
 'appointment':'RENDEZ-VOUS', 'truck_visit':'PASSAGE CAMION', 'visit_event':'ÉVÉNEMENT DE PASSAGE',
 'owner':'CLIENT PROPRIÉTAIRE', 'supplier':'FOURNISSEUR', 'article':'ARTICLE',
 'zone':'ZONE', 'aisle':'ALLÉE', 'rack':'RACK', 'rack_level':'NIVEAU', 'location':'EMPLACEMENT',
 'lot':'LOT', 'supplier_notice':'AVIS FOURNISSEUR', 'notice_line':"LIGNE D’AVIS",
 'receipt':'RÉCEPTION', 'receipt_line':'LIGNE DE RÉCEPTION', 'receipt_item':'FRACTION REÇUE',
 'customer_order':'COMMANDE', 'order_line':'LIGNE DE COMMANDE', 'pick':'PRÉLÈVEMENT',
 'package':'COLIS / PALETTE', 'shipment':'EXPÉDITION', 'stock_movement':'MOUVEMENT DE STOCK',
 'receipt_reserve':'RÉSERVE', 'vehicle_type':'TYPE DE VÉHICULE'}
overrides = {'password_hash':'Empreinte du mot de passe', 'reservation':'Observation sur avarie',
 'pallet_code':'Code de fraction / palette', 'document_note':'Contrôle des documents',
 'expires_on':'Date limite / validité', 'max_pallets':'Capacité (éq. palettes)',
 'operation_ref':'Référence d’opération', 'closed_at':'Date de clôture',
 'picking_at':'Début de préparation', 'ready_at':'Fin de préparation'}
for t,v in model.items():
 if t in joins|technical: continue
 fk = {f['COLUMN_NAME'] for f in v['foreign']}
 attrs=[]
 for c in v['columns']:
  k=c['Field']
  if k in fk or (t=='vehicle' and k=='type'): continue
  label='Identifiant' if k=='id' else overrides.get(k,labels.get(k,k)).replace('\\/','/')
  if c['Null']=='YES':label+=' (facultatif)'
  attrs.append({'key':k,'label':label,'id':k=='id'})
 entities[t]={'title':titles[t],'attrs':attrs,'table':t}
entities['vehicle_type']={'title':titles['vehicle_type'],'attrs':[{'key':'code','label':'Code type','id':True}], 'table':None}

# All ordinary FK relationships are named and assigned to a readable domain view.
# Cardinalities are PARTICIPATIONS, written next to the participating entity.
spec = {
 'carrier_contact.carrier_id':(1,'possède un contact'),
 'carrier_contract.carrier_id':(1,'signe un contrat'),
 'driver.carrier_id':(1,'rattache un chauffeur'),
 'vehicle.carrier_id':(1,'exploite un véhicule'),
 'dock_downtime.dock_id':(2,'subit une indisponibilité'),
 'appointment.dock_id':(3,'est prévu pour'),
 'appointment.driver_id':(3,'est prévu pour'),
 'appointment.vehicle_id':(3,'est prévu comme principal'),
 'appointment.trailer_id':(3,'est prévue comme remorque'),
 'truck_visit.appointment_id':(3,'donne lieu à'),
 'truck_visit.driver_id':(4,'conduit le passage'),
 'truck_visit.vehicle_id':(4,'effectue (véhicule principal)'),
 'truck_visit.trailer_id':(4,'accompagne (remorque)'),
 'truck_visit.dock_id':(4,'dessert le passage'),
 'visit_event.visit_id':(4,'comporte une étape'),
 'visit_event.actor_id':(4,'enregistre une étape'),
 'article.owner_id':(5,'possède'),
 'lot.article_id':(5,'définit'),
 'aisle.zone_id':(5,'contient'),
 'rack.aisle_id':(5,'contient'),
 'rack_level.rack_id':(5,'contient'),
 'location.level_id':(5,'contient'),
 'supplier_notice.supplier_id':(6,'émet un avis'),
 'supplier_notice.closed_by':(6,'clôture un avis'),
 'notice_line.notice_id':(6,'détaille un avis'),
 'notice_line.article_id':(6,'figure dans'),
 'receipt.notice_id':(6,'livre tout ou partie'),
 'receipt.visit_id':(7,'achemine une réception'),
 'receipt_line.receipt_id':(7,'détaille une réception'),
 'receipt_line.notice_line_id':(7,'alloue un attendu local'),
 'receipt_item.line_id':(7,'se répartit en fractions'),
 'receipt_item.lot_id':(7,'identifie le lot reçu'),
 'receipt_item.location_id':(7,'rangement initial'),
 'receipt_reserve.receipt_id':(8,'porte une réserve générale'),
 'receipt_reserve.line_id':(8,'porte une réserve de ligne'),
 'receipt_reserve.actor_id':(8,'émet une réserve'),
 'stock_movement.receipt_item_id':(8,'fait l’objet de mouvements'),
 'stock_movement.location_id':(8,'est affecté par'),
 'stock_movement.pick_id':(8,'produit une sortie'),
 'stock_movement.actor_id':(8,'effectue un mouvement'),
 'customer_order.owner_id':(9,'passe une commande'),
 'customer_order.preparer_id':(9,'prépare une commande'),
 'order_line.order_id':(9,'détaille une commande'),
 'order_line.article_id':(9,'figure dans'),
 'pick.order_line_id':(9,'est servie par'),
 'pick.receipt_item_id':(9,'alimente le prélèvement'),
 'pick.location_id':(9,'est le lieu du prélèvement'),
 'package.order_id':(10,'est conditionnée en'),
 'shipment.order_id':(10,'donne lieu à'),
 'shipment.visit_id':(10,'emporte une expédition'),
 'shipment.actor_id':(10,'confirme une expédition'),
}
rels=[]
for t,v in model.items():
 if t in joins|technical:continue
 for f in v['foreign']:
  field=f['COLUMN_NAME']; key=f'{t}.{field}'
  group,label=spec[key]
  parent=f['REFERENCED_TABLE_NAME']
  column=next(c for c in v['columns'] if c['Field']==field)
  unique=any(not i['Non_unique'] and i['Column_name']==field and sum(j['Key_name']==i['Key_name'] for j in v['indexes'])==1 for i in v['indexes'])
  parent_card='0,1' if unique else '0,N'
  if key=='visit_event.visit_id':parent_card='1,N'
  child_card='0,1' if column['Null']=='YES' else '1,1'
  rels.append({'a':parent,'b':t,'ca':parent_card,'cb':child_card,'label':label,'group':group,'fields':[key],'attrs':[]})
for a,b,group,label,table,fields,attrs in [
 ('driver','qualification',1,'est habilité','driver_qualification',['driver_id','qualification_id'],[('expires_on','Date de fin de validité')]),
 ('vehicle','equipment',1,'est équipé de','vehicle_equipment',['vehicle_id','equipment_id'],[]),
 ('dock','equipment',2,'dispose de','dock_equipment',['dock_id','equipment_id'],[]),
 ('package','pick',10,'contient une quantité','package_pick',['package_id','pick_id'],[('qty','Quantité affectée')]),
 ('dock','vehicle_type',2,'accepte le type','dock_vehicle_type',['dock_id','vehicle_type'],[]),
]:
 rels.append({'a':a,'b':b,'ca':'0,N','cb':'0,N','label':label,'group':group,'fields':[f'{table}.{k}' for k in fields], 'attrs':[{'key':f'{table}.{k}','label':n} for k,n in attrs], 'join':table})
rels.append({'a':'vehicle_type','b':'vehicle','ca':'0,N','cb':'1,1','label':'caractérise le véhicule','group':2,'fields':['vehicle.type'],'attrs':[]})
for i,r in enumerate(rels,1):r['id']=f'R{i:02}'
groups={
 1:('Transporteurs, chauffeurs et véhicules', ['La validité appartient à l’association CHAUFFEUR / HABILITATION.', 'VÉHICULE représente aussi les remorques ; leurs rôles sont séparés dans les vues 3 et 4.']),
 2:('Quais, équipements et compatibilités', ['TYPE DE VÉHICULE : tracteur, remorque, porteur, fourgon.', 'Dans le SQL, le domaine est un ENUM ; la compatibilité utilise dock_vehicle_type.', 'Les indisponibilités et les réservations actives d’un quai ne doivent pas se chevaucher.']),
 3:('Rendez-vous et ressources prévues', ['Un rendez-vous a exactement un quai, un chauffeur et un véhicule principal ; la remorque est facultative.', 'Un passage peut être sans rendez-vous ; un rendez-vous est lié à zéro ou un passage.', 'Les affectations prévues et constatées sont des faits distincts. Absence de chevauchement contrôlée par le service.']),
 4:('Passages réels et chronologie', ['Les liens « véhicule principal » et « remorque » sont distincts. Le quai effectif est facultatif avant affectation.', 'Chaque passage créé par l’application possède au moins l’événement d’arrivée (minimum métier 1,N).', 'Une seule occurrence de chaque étape par passage ; les durées sont calculées depuis les horodatages.']),
 5:('Articles, propriétaires et structure de stockage', ['Un article appartient à un seul propriétaire. Un lot est défini pour un seul article.', 'Les capacités de zone, allée, rack et niveau se déduisent de leurs emplacements.', 'Compatibilité article / zone, dimensions, poids et capacité palettes sont contrôlés avant rangement.']),
 6:('Avis fournisseurs et livraisons partielles', ['Un avis peut être reçu en plusieurs réceptions. Les lignes décrivent l’attendu total par article.', 'L’auteur de clôture est facultatif tant que l’avis reste ouvert ; motif et date accompagnent la clôture.', 'Les brouillons peuvent être vides : les minima 0,N ne dispensent pas des contrôles à la validation.']),
 7:('Réceptions, lots et fractions reçues', ['Une ligne de réception alloue une partie de l’attendu d’une ligne d’avis ; plusieurs lots sont possibles.', 'Une fraction conserve sa provenance et son emplacement initial ; les positions suivantes proviennent des mouvements.', 'L’article du lot doit correspondre à l’article attendu. L’avis de chaque ligne doit être celui de la réception.']),
 8:('Réserves et journal des mouvements', ['Contrainte XOR totale : une réserve vise exactement une réception OU une ligne, jamais les deux ni aucune.', 'Un mouvement de sortie est lié à un prélèvement ; les autres mouvements ne le sont pas.', 'Stock physique = somme des variations par fraction et emplacement. Un transfert comporte deux écritures opposées.', 'Le texte d’avarie de la fraction (vue 7) complète les réserves structurées ; aucune quantité endommagée en stock disponible.']),
 9:('Commandes et préparation', ['Un préparateur est facultatif au brouillon, obligatoire à la préparation ; les articles appartiennent au propriétaire de la commande.', 'Chaque prélèvement désigne une ligne, une fraction reçue et un emplacement : la provenance est conservée.', 'FEFO exclut les lots bloqués ou périmés ; le disponible déduit les prélèvements encore réservés.']),
 10:('Colis, chargement et expédition', ['La quantité appartient à l’association COLIS / PRÉLÈVEMENT : un prélèvement peut être réparti entre plusieurs colis.', 'Une commande a zéro ou une expédition (pas d’expédition partielle dans cette version). Un passage peut en charger plusieurs.', 'Avant chargement : même commande pour le colis et le prélèvement ; couverture exacte des quantités prélevées.', 'Bon de livraison et lettre de voiture sont générés à partir de ces faits, sans entités documentaires supplémentaires.'])}

# Validate the stored schema metadata against the actual repository SQL first.
sql_tables=dict(re.findall(r'CREATE TABLE (\w+)\s*\((.*?)\) ENGINE=InnoDB;',sql,re.S))
assert set(sql_tables)==set(model), 'SQL/model table drift'
for t,body in sql_tables.items():
 cols=re.findall(r'(?:^|,)\s*(\w+)\s+(?:INT|BIGINT|VARCHAR|TEXT|DATE|DATETIME|BOOLEAN|DECIMAL|ENUM)\b',body,re.I)
 assert cols==[c['Field'] for c in model[t]['columns']], (t,'column drift')
 sql_fk=set(re.findall(r'FOREIGN KEY\((\w+)\) REFERENCES (\w+)\(id\)',body))
 assert sql_fk=={(f['COLUMN_NAME'],f['REFERENCED_TABLE_NAME']) for f in model[t]['foreign']}, (t,'FK drift')
expected_fk={f'{t}.{f["COLUMN_NAME"]}' for t,v in model.items() if t not in technical for f in v['foreign']}
covered=[k for r in rels for k in r['fields']]
assert expected_fk<=set(covered)
assert all(n==1 for n in Counter(covered).values())
covered_attrs={f'{t}.{a["key"]}' for t,v in entities.items() if v['table'] for a in v['attrs']}
covered_attrs|={a['key'] for r in rels for a in r['attrs']}|set(covered)
expected_attrs={f'{t}.{c["Field"]}' for t,v in model.items() if t not in technical for c in v['columns'] if not(t in joins and c['Field']=='id')}
assert expected_attrs<=covered_attrs, expected_attrs-covered_attrs

def dot_source(selected):
 ts=sorted({r[k] for r in selected for k in ('a','b')})
 s=['graph MCD {','graph [rankdir=LR, bgcolor="white", pad="0.32", nodesep="0.50", ranksep="0.55", splines=polyline, outputorder=edgesfirst];',
    'node [fontname="Arial", fontsize=15, color="#48647c", penwidth=1.3];',
    'edge [fontname="Arial", fontsize=14, color="#6c7d8c", fontcolor="#203c54", penwidth=1.1];']
 for t in ts:
  e=entities[t]
  rows=[]
  for a in e['attrs']:
   tx=html.escape(a['label'])
   if a['id']:tx='<U>'+tx+'</U>'
   rows.append(f'<TR><TD ALIGN="LEFT">{tx}</TD></TR>')
  label=f'<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="6" COLOR="#48647c"><TR><TD BGCOLOR="#e7eff6"><B>{html.escape(e["title"])}</B></TD></TR>'+''.join(rows)+'</TABLE>'
  s.append(f'{t} [shape=plain,label=<{label}>];')
 for r in selected:
  lines=[r['id'],r['label']]+[a['label'] for a in r['attrs']]
  # Wrap long names inside the diamond, without hiding any association attribute.
  import textwrap
  text='\n'.join('\n'.join(textwrap.wrap(x,16,break_long_words=False)) for x in lines)
  s.append(f'{r["id"]} [shape=diamond, style=filled, fillcolor="#fff7e8", margin="0.12,0.08", fontsize=14, label={json.dumps(text,ensure_ascii=False)}];')
  s.append(f'{r["a"]} -- {r["id"]} [taillabel="{r["ca"]}", labeldistance=2.0, labelangle=25];')
  s.append(f'{r["id"]} -- {r["b"]} [headlabel="{r["cb"]}", labeldistance=2.0, labelangle=-25];')
 s.append('}')
 return '\n'.join(s),ts

pages=[{'slug':'00-modele-complet','title':'Modèle entité-association complet','rels':rels,'notes':['Vue globale vectorielle à lire avec zoom ; les pages suivantes détaillent toutes les associations.', 'Identifiant souligné ; rectangles = entités ; losanges = associations ; cardinalité près de l’entité = nombre de participations.', 'Les entités répétées dans les vues détaillées sont les mêmes concepts. Les règles complémentaires figurent dans ANALYSE-MCD.md.']}]
for g,(title,notes) in groups.items(): pages.append({'slug':f'{g:02}-'+['transport','quais','rendez-vous','passages','articles-stockage','avis','receptions','reserves-mouvements','commandes','expeditions'][g-1], 'title':title,'rels':[r for r in rels if r['group']==g], 'notes':notes})
for p in pages:
 text,ts=dot_source(p['rels']);p['entities']=ts
 (BUILD/(p['slug']+'.dot')).write_text(text,encoding='utf-8')
renderer=BUILD/'render.cjs'
renderer.write_text('''const fs=require('fs'),path=require('path');
const {instance}=require(process.env.BD70_VIZ||'C:/Users/eliot/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@viz-js/viz');
(async()=>{const v=await instance();for(const f of fs.readdirSync(__dirname).filter(x=>x.endsWith('.dot'))){const s=fs.readFileSync(path.join(__dirname,f),'utf8');for(const fmt of ['svg','json'])fs.writeFileSync(path.join(__dirname,f.replace(/\\.dot$/,'.'+fmt)),v.renderString(s,{format:fmt,engine:'dot'}));}})().catch(e=>{console.error(e);process.exit(1)});
''',encoding='utf-8')
subprocess.run(['node',str(renderer)],check=True)

for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold')

def finish_svg(p):
 """Preserve key underlines in svglib and keep cardinalities clear of boxes."""
 path=BUILD/(p['slug']+'.svg')
 svg=ET.fromstring(path.read_text(encoding='utf-8'))
 ns='{http://www.w3.org/2000/svg}'
 layout=json.loads((BUILD/(p['slug']+'.json')).read_text(encoding='utf-8'))
 objects={o['_gvid']:o for o in layout['objects']}
 boxes=[];diamonds=[]
 for o in objects.values():
  x,y=map(float,o['pos'].split(','));w,h=float(o['width'])*72,float(o['height'])*72
  if o['name'] in entities:boxes.append((x-w/2-2,y-h/2-2,x+w/2+2,y+h/2+2))
  else:diamonds.append((x,y,w/2+2,h/2+2))
 _,_,gw,gh=map(float,layout['bb'].split(','))
 def collision(box,other):return box[0]<other[2] and box[2]>other[0] and box[1]<other[3] and box[3]>other[1]
 occupied=[]
 edgegroups={g.find(ns+'title').text:g for g in svg.findall('.//'+ns+'g') if g.get('class')=='edge'}
 for edge in layout['edges']:
  group=edgegroups[objects[edge['tail']]['name']+'--'+objects[edge['head']]['name']]
  textnodes=group.findall(ns+'text')
  for kind in ('head','tail'):
   if kind+'label' not in edge:continue
   x,y=map(float,edge[kind+'_lp'].split(','))
   found=None
   for distance in (0,4,8,12,16,20,24,32,40,48,64,80):
    for angle in (0,180,90,270,45,135,225,315):
     nx=x+distance*math.cos(math.radians(angle));ny=y+distance*math.sin(math.radians(angle))
     box=(nx-20,ny-10,nx+20,ny+10)
     in_diamond=any(max(abs(nx-cx)-20,0)/rx+max(abs(ny-cy)-10,0)/ry<1 for cx,cy,rx,ry in diamonds)
     if box[0]>=0 and box[1]>=0 and box[2]<=gw and box[3]<=gh and not in_diamond and not any(collision(box,b) for b in boxes+occupied):found=(nx,ny,box);break
    if found:break
   assert found,(p['slug'],'cardinality layout',edge)
   nx,ny,box=found;occupied.append(box)
   textnode=next(t for t in textnodes if t.text==edge[kind+'label'])
   textnodes.remove(textnode)
   textnode.set('x',str(float(textnode.get('x'))+nx-x));textnode.set('y',str(float(textnode.get('y'))-ny+y))
   width=pdfmetrics.stringWidth(textnode.text,'Arial',14)
   mask=ET.Element(ns+'rect',x=str(nx-width/2-2),y=str(-ny-8),width=str(width+4),height='17',fill='white',stroke='none')
   group.insert(list(group).index(textnode),mask)
   edge[kind+'_lp']=f'{nx},{ny}'
 for group in svg.findall('.//'+ns+'g'):
  for t in list(group):
   if t.tag!=ns+'text':continue
   if t.get('font-weight')=='bold':t.set('font-family','Arial-Bold');t.attrib.pop('font-weight',None)
   if t.get('text-decoration')=='underline':
    t.attrib.pop('text-decoration')
    x,y=float(t.get('x')),float(t.get('y'));w=pdfmetrics.stringWidth(t.text or '', 'Arial',float(t.get('font-size')))
    ET.SubElement(group,ns+'line',x1=str(x),x2=str(x+w),y1=str(y+2),y2=str(y+2),stroke='#203c54',attrib={'stroke-width':'0.8'})
 ET.register_namespace('',ns[1:-1]);ET.ElementTree(svg).write(path,encoding='utf-8',xml_declaration=True)
 (BUILD/(p['slug']+'.json')).write_text(json.dumps(layout,ensure_ascii=False),encoding='utf-8')

for p in pages:finish_svg(p)
pdf=canvas.Canvas(str(OUT/'BD70-MCD-FINAL.pdf'))
pdf.setTitle('BD70 - Modèle conceptuel entité-association final')
mxfile=ET.Element('mxfile',host='app.diagrams.net',type='device')

def cell(root,id,value,style,x,y,w,h,parent='1'):
 c=ET.SubElement(root,'mxCell',id=id,value=value,style=style,vertex='1',parent=parent)
 ET.SubElement(c,'mxGeometry',x=str(round(x,2)),y=str(round(y,2)),width=str(round(w,2)),height=str(round(h,2)),attrib={'as':'geometry'})
 return c

for index,p in enumerate(pages):
 raw=(BUILD/(p['slug']+'.svg')).read_text(encoding='utf-8')
 drawing=svg2rlg(BytesIO(raw.encode()))
 dw,dh=drawing.width,drawing.height
 if index==0:pw,ph=dw+80,dh+200;scale=1.0;fmt='grand format, zoom'
 else:
  for size,name in [(A3,'A3'),(A2,'A2'),(A1,'A1')]:
   candidates=[]
   for (cw,ch),orient in [(landscape(size),'paysage'),(size,'portrait')]:
    candidates.append((min(1,(cw-70)/dw,(ch-215)/dh),cw,ch,orient))
   scale,pw,ph,orient=max(candidates)
   if scale>=0.72:break
  name+=' '+orient
  fmt=name
 p.update(format=fmt,scale=scale)
 pdf.setPageSize((pw,ph));pdf.setFillColorRGB(.09,.19,.28)
 pdf.setFont('Arial-Bold',22);pdf.drawString(35,ph-38,f'BD70 | {p["title"]}')
 pdf.setFont('Arial',11);pdf.drawString(35,ph-60,f'{index+1:02} / {len(pages):02}   •   {fmt}   •   29 octobre 2026   •   Modèle cohérent avec le SQL local')
 pdf.bookmarkPage(p['slug']);pdf.addOutlineEntry(p['title'],p['slug'],0)
 pdf.saveState();pdf.translate((pw-dw*scale)/2,ph-85-dh*scale);pdf.scale(scale,scale);renderPDF.draw(drawing,pdf,0,0);pdf.restoreState()
 pdf.setFont('Arial-Bold',10);pdf.drawString(35,112,'LECTURE ET CONTRAINTES')
 pdf.setFont('Arial',10)
 for j,note in enumerate(p['notes']):pdf.drawString(35,95-j*15,note)
 pdf.setStrokeColorRGB(.72,.77,.81);pdf.line(35,30,pw-35,30)
 pdf.setFont('Arial',9);pdf.drawString(35,17,'Rectangles : entités  |  Losanges : associations  |  Identifiant souligné  |  Cardinalités de participation : 0,1 / 1,1 / 0,N / 1,N')
 pdf.showPage()

 # Draw.io coordinates follow the Graphviz layout. All vertices, labels and edges stay editable.
 layout=json.loads((BUILD/(p['slug']+'.json')).read_text(encoding='utf-8'))
 _,_,gw,gh=map(float,layout['bb'].split(','))
 diagram=ET.SubElement(mxfile,'diagram',id=p['slug'],name=f'{index:02} - '+p['title'])
 graph=ET.SubElement(diagram,'mxGraphModel',dx='1600',dy='1000',grid='1',gridSize='10',page='1',pageScale='1',pageWidth=str(math.ceil(max(gw+80,1200))),pageHeight=str(math.ceil(gh+240)),math='0',shadow='0')
 root=ET.SubElement(graph,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
 base='html=1;whiteSpace=wrap;fontFamily=Arial;fontColor=#203c54;'
 cell(root,'title',html.escape('BD70 | '+p['title']),base+'text;align=left;fontSize=23;fontStyle=1;',35,15,gw,40)
 cell(root,'legend','Identifiant souligné ; cardinalités de participation près de l’entité. Mêmes concepts dans toutes les vues.',base+'text;align=left;fontSize=13;',35,55,gw,30)
 objects={o['_gvid']:o for o in layout['objects']}
 for o in objects.values():
  name=o['name'];x,y=map(float,o['pos'].split(','));w,h=float(o['width'])*72,float(o['height'])*72
  if name in entities:
   e=entities[name]
   value='<b>'+html.escape(e['title'])+'</b><hr>'+ '<br>'.join(('<u>'+html.escape(a['label'])+'</u>') if a['id'] else html.escape(a['label']) for a in e['attrs'])
   style=base+'shape=rectangle;rounded=0;fillColor=#eef4f9;strokeColor=#48647c;fontSize=15;align=left;verticalAlign=middle;spacing=8;'
  else:
   r=next(r for r in p['rels'] if r['id']==name)
   value='<b>'+name+'</b><br>'+html.escape(r['label'])+''.join('<br><i>'+html.escape(a['label'])+'</i>' for a in r['attrs'])
   style=base+'shape=rhombus;fillColor=#fff7e8;strokeColor=#48647c;fontSize=14;align=center;spacing=4;'
  cell(root,name,value,style,x-w/2+40,gh-y-h/2+100,w,h)
 for j,e in enumerate(layout['edges']):
  a=objects[e['tail']]['name'];b=objects[e['head']]['name'];pts=[]
  for op in e.get('_draw_',[]):
   if op['op'] in ('b','B','L'):pts=op['points'];break
  c=ET.SubElement(root,'mxCell',id=f'edge{j}',style='edgeStyle=none;rounded=0;html=1;endArrow=none;startArrow=none;strokeColor=#6c7d8c;strokeWidth=1.1;',edge='1',source=a,target=b,parent='1')
  geom=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
  arr=ET.SubElement(geom,'Array',attrib={'as':'points'})
  # Graphviz polyline coordinates repeat Bezier control points: keep distinct vertices.
  last=None
  for x,y in pts[1:-1]:
   pair=(round(x+40,2),round(gh-y+100,2))
   if pair!=last:ET.SubElement(arr,'mxPoint',x=str(pair[0]),y=str(pair[1]));last=pair
  for kind in ('tail','head'):
   if kind+'label' in e:
    x,y=map(float,e[kind+'_lp'].split(','))
    cell(root,f'card{j}{kind}',e[kind+'label'],base+'text;align=center;fontSize=14;fillColor=#ffffff;',x+20,gh-y+90,40,20)
 for j,note in enumerate(p['notes']):cell(root,f'note{j}',html.escape(note),base+'text;align=left;fontSize=13;',35,gh+120+j*23,max(gw,1100),23)
 print(p['slug'],fmt,'scale',round(scale,3),'entities',len(p['entities']),'relations',len(p['rels']))
pdf.save()
ET.ElementTree(mxfile).write(OUT/'BD70-MCD-FINAL.drawio',encoding='utf-8',xml_declaration=True)

source_paths=['document projet/A26_Site_Logistique.pdf','document projet/Éléments dévaluation projet BD70.docx','document cours/BD70_A25 (4).pptx','sql/01_schema.sql','docs/diagrammes/schema.json','scripts/diagrams.py','src/Warehouse.php']
source_paths += [str(x.relative_to(ROOT)).replace('\\','/') for x in (ROOT/'docs/diagrammes').glob('mcd-*.*')]
evidence={'date':'2026-10-29','entities':len(entities),'associations':len(rels),'business_foreign_keys_covered':len(expected_fk),'business_columns_covered':len(expected_attrs),'physical_tables':len(model),'join_tables':sorted(joins),'excluded_technical_tables':sorted(technical),'pdf_pages':len(PdfReader(OUT/'BD70-MCD-FINAL.pdf').pages),'native_drawio_pages':len(mxfile),'sources_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in source_paths},'views':[{'name':p['slug'],'format':p['format'],'scale':p['scale'],'entities':p['entities'],'relations':[r['id'] for r in p['rels']]} for p in pages]}
assert evidence['pdf_pages']==len(pages)==evidence['native_drawio_pages']
(OUT/'verification.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
(BUILD/'modele.json').write_text(json.dumps({'entities':entities,'associations':rels},ensure_ascii=False,indent=2),encoding='utf-8')

# Human-readable model/SQL correspondence and candidate keys, separate from diagram geometry.
md=['# Correspondance MCD / SQL','', 'Les cardinalités se lisent comme des participations : près de CLIENT, 0,N signifie qu’un client participe à zéro ou plusieurs occurrences de l’association. Les identifiants conceptuels sont soulignés ; leurs valeurs sont les id du modèle physique, sauf le type de véhicule (domaine énuméré).','', '## Associations','', '| Repère | Entité A | Participation A | Association | Entité B | Participation B | Traduction SQL |','|---|---|---|---|---|---|---|']
for r in rels:md.append('| '+' | '.join([r['id'],titles[r['a']],r['ca'],r['label']+(' : '+', '.join(a['label'] for a in r['attrs']) if r['attrs'] else ''),titles[r['b']],r['cb'],', '.join(r['fields'])])+ ' |')
md+=['','## Unicités complémentaires','', 'Les id identifient les entités. Les unicités ci-dessous complètent le diagramme ; une association N:N est identifiée par le couple de ses participants. Les identifiants id des tables de jointure sont des choix techniques.','', '| Table | Attributs uniques hors id |','|---|---|']
for t,v in model.items():
 if t in technical:continue
 indexes={}
 for i in v['indexes']:
  if not i['Non_unique'] and i['Key_name']!='PRIMARY':indexes.setdefault(i['Key_name'],[]).append(i['Column_name'])
 if indexes:md.append(f'| {t} | '+ ' ; '.join(' + '.join(cols) for cols in indexes.values())+' |')
md+=['','Les unicités sur appointment_id et pick_id sont conditionnelles lorsque la valeur est NULL : elles ne sont pas des identifiants totaux. shipment.order_id est obligatoire et unique.','', '## Périmètre technique','', 'audit_log et site_lock restent dans le MLD : journal d’audit générique et verrou de sérialisation. Les événements de passage et mouvements de stock restent dans le MCD car ce sont des faits métier demandés. Le rôle utilisateur et le statut sont des domaines finis ; aucune table ROLE n’est inventée. TYPE DE VÉHICULE est réalisé par les ENUM vehicle.type et dock_vehicle_type.vehicle_type, sans table supplémentaire.']
(OUT/'CORRESPONDANCE-SQL.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in evidence.items() if k not in ('sources_sha256','views')},ensure_ascii=False))
