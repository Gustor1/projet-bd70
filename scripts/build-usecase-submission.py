"""One-page, editable UML submission. Does not overwrite the earlier diagrams.

Requires reportlab. Geometry and labels are shared by Draw.io, SVG, HTML and PDF.
Re-running overwrites only the generated UML-CAS-UTILISATION-BD70 files.
"""
from pathlib import Path
from html import escape
import json
import math
import xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'livrables' / 'rendu-intermediaire'
OUT.mkdir(parents=True, exist_ok=True)
STEM = 'UML-CAS-UTILISATION-BD70'
W, H = 1960, 1386
INK, MUTED, FILL = '#20354b', '#46576a', '#ffffff'
fonts = Path('C:/Windows/Fonts')
pdfmetrics.registerFont(TTFont('Diagram', str(fonts / 'arial.ttf')))
pdfmetrics.registerFont(TTFont('DiagramBold', str(fonts / 'arialbd.ttf')))

actors = [
    dict(id='admin', cx=240, y=196, label=['Administrateur']),
    dict(id='manager', cx=610, y=196, label=['Responsable', 'd’exploitation']),
    dict(id='gate', cx=980, y=196, label=['Agent d’accueil']),
    dict(id='warehouse', cx=1350, y=196, label=['Magasinier / préparateur']),
    dict(id='staff', cx=1720, y=196, label=['Personnel', '(acteur général)']),
    dict(id='candidate', cx=240, y=1200, label=['Membre du personnel', 'non inscrit']),
]
cases = []
def case(ident, x, y, title, subtitle):
    cases.append(dict(id=ident, x=x, y=y, w=300, h=144,
                      title=title.split('\n'), subtitle=subtitle.split('\n')))

case('accounts', 90, 430, 'Administrer\nles comptes', 'Activer, désactiver,\nattribuer les droits')
case('register', 90, 794, 'S’inscrire', 'Demander un compte\nauprès de l’entrepôt')
case('transport', 460, 430, 'Gérer le référentiel\nde transport', 'Transporteurs, chauffeurs,\nvéhicules')
case('references', 460, 612, 'Gérer les données\nde l’entrepôt', 'Quais, articles, clients,\nstockage, fournisseurs')
case('reports', 460, 794, 'Piloter l’activité', 'Indicateurs, statistiques,\nrapports et exports')
case('appointments', 830, 430, 'Planifier les quais\net les rendez-vous', 'Créer, déplacer, annuler ;\ncontrôler leur faisabilité')
case('visits', 830, 698, 'Suivre le passage\nd’un camion', 'Arrivée, contrôle, attente,\nquai, opérations, départ')
case('receipts', 1200, 430, 'Réceptionner\net ranger les produits', 'Avis, lots, palettes ;\nécarts et réserves')
case('stock', 1200, 612, 'Gérer les stocks', 'Rechercher, transférer,\najuster l’inventaire')
case('orders', 1200, 794, 'Gérer et préparer\nles commandes', 'Affecter un préparateur ;\nprélever selon FEFO')
case('shipping', 1200, 976, 'Expédier\nles commandes', 'Colis, palettes, chargement ;\nBL et lettre de voiture')
case('login', 1570, 430, 'Se connecter', 'Compte actif\net identifiants valides')
case('logout', 1570, 612, 'Se déconnecter', 'Fermer sa session')
case('planning', 1570, 794, 'Consulter les quais\net le planning', 'Rendez-vous, occupation,\nindisponibilités')
case('trace', 1570, 976, 'Tracer un lot', 'Réception, emplacements,\ncommande, camion de sortie')

edges = []
def edge(source, target, points, kind='association', bridge=False):
    edges.append(dict(source=source, target=target, points=points, kind=kind, bridge=bridge))

# Generalization points to the more general functional role.
edge('admin', 'manager', [(270,235),(580,235)], 'generalization')
edge('manager', 'gate', [(640,235),(950,235)], 'generalization')
edge('manager', 'warehouse', [(610,196),(610,140),(1350,140),(1350,196)], 'generalization', True)
edge('gate', 'staff', [(980,196),(980,104),(1720,104),(1720,196)], 'generalization')
edge('warehouse', 'staff', [(1380,235),(1690,235)], 'generalization')

by_id = {n['id']: n for n in cases}
for actor_id, targets in [
    ('admin',['accounts']),
    ('manager',['transport','references','reports']),
    ('gate',['appointments','visits']),
    ('warehouse',['receipts','stock','orders','shipping']),
    ('staff',['login','logout','planning','trace'])
]:
    actor = next(a for a in actors if a['id'] == actor_id)
    for index, target in enumerate(targets):
        n = by_id[target]
        # Nested routes: the longest edge uses the outer corridor and highest exit.
        xroute = n['x'] - 14 * (index + 1)
        sy = 292 - index * 12
        edge(actor_id, target, [(actor['cx']-15,sy),(xroute,sy),
                               (xroute,n['y']+72),(n['x'],n['y']+72)])
edge('candidate', 'register', [(240,1200),(240,938)])

texts = [
    dict(id='heading', x=40, y=44, text='BD70 · Diagramme de cas d’utilisation', size=34, bold=True),
    dict(id='subheading', x=40, y=77, text='Entrepôt logistique · Périmètre fonctionnel du projet', size=22),
    dict(id='system-title', x=980, y=1141, text='Système de gestion d’un entrepôt logistique', size=25, bold=True, anchor='middle'),
    dict(id='legend', x=440, y=1192, text='Trait simple : participation à un cas. Triangle creux : héritage vers le rôle général.', size=21),
    dict(id='inheritance-note', x=440, y=1224, text='Le Responsable reprend les fonctions Accueil et Magasinier ; l’Administrateur reprend celles du Responsable.', size=20),
    dict(id='session-note', x=440, y=1256, text='Session active et rôle autorisé pour les opérations métier. L’inscription et la connexion sont accessibles sans session.', size=20),
    dict(id='scope-note', x=440, y=1288, text='Portail Transporteur facultatif non retenu. « Gérer » comprend consultation, recherche et opérations autorisées.', size=20),
    dict(id='terms', x=440, y=1320, text='FEFO : premier périmé, premier sorti. BL : bon de livraison. Les sous-lignes précisent le contenu des cas.', size=20),
]

def width(text, size, bold=False):
    return pdfmetrics.stringWidth(text, 'DiagramBold' if bold else 'Diagram', size)

def case_lines(n):
    items = [(s,22,True) for s in n['title']] + [(s,19,False) for s in n['subtitle']]
    heights = [29 if bold else 24 for _,_,bold in items]
    start = n['y'] + (n['h']-sum(heights))/2 + 22
    lines=[]
    for (s,size,bold), step in zip(items,heights):
        lines.append((s, n['x']+n['w']/2, start, size, bold))
        start += step
    return lines

def validate():
    ids = {a['id'] for a in actors} | set(by_id)
    assert len(ids) == len(actors) + len(cases)
    for e in edges:
        assert e['source'] in ids and e['target'] in ids
        for (x1,y1),(x2,y2) in zip(e['points'],e['points'][1:]):
            assert x1 == x2 or y1 == y2
    for n in cases:
        assert 40 < n['x'] and n['x']+n['w'] < 1920
        assert 370 < n['y'] and n['y']+n['h'] < 1150
        # Check each text line fits inside the ellipse at its furthest vertical extent.
        for s,x,y,size,bold in case_lines(n):
            dy=max(abs(y-n['y']-n['h']/2), abs(y-size*.8-n['y']-n['h']/2))
            available=n['w']*math.sqrt(max(0,1-(dy/(n['h']/2))**2))
            assert width(s,size,bold)+12 < available, (n['id'],s,available)
    for i,a in enumerate(cases):
        for b in cases[i+1:]:
            assert a['x']+a['w'] <= b['x'] or b['x']+b['w'] <= a['x'] or a['y']+a['h'] <= b['y'] or b['y']+b['h'] <= a['y']
    for t in texts:
        tw=width(t['text'],t['size'],t.get('bold',False))
        assert t['x']+tw <= W-25 if t.get('anchor') != 'middle' else tw < W-80

def triangle(e):
    tip=e['points'][-1]; prev=e['points'][-2]
    dx,dy=tip[0]-prev[0],tip[1]-prev[1]
    length=math.hypot(dx,dy); ux,uy=dx/length,dy/length
    base=(tip[0]-18*ux,tip[1]-18*uy)
    return [tip,(base[0]-9*uy,base[1]+9*ux),(base[0]+9*uy,base[1]-9*ux)]

def svg_text(s,x,y,size,bold=False,anchor='middle'):
    return f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{INK}" text-anchor="{anchor}">{escape(s)}</text>'

def build_svg():
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="uml-cas-utilisation-bd70-title uml-cas-utilisation-bd70-desc">',
         '<title id="uml-cas-utilisation-bd70-title">Cas d’utilisation de l’entrepôt logistique BD70</title>',
         '<desc id="uml-cas-utilisation-bd70-desc">Les rôles du personnel et leurs capacités héritées participent aux quinze cas couvrant les huit domaines du sujet.</desc>',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         f'<rect x="40" y="370" width="1880" height="780" fill="white" stroke="{INK}" stroke-width="2"/>']
    # One bridge makes the unrelated crossing of the two generalizations explicit.
    for e in sorted(edges,key=lambda e:e['bridge']):
        pts=' '.join(f'{x},{y}' for x,y in e['points'])
        if e['bridge']:
            path='M610,196 L610,140 L969,140 Q980,118 991,140 L1350,140 L1350,196'
            svg += [f'<path d="{path}" fill="none" stroke="white" stroke-width="7"/>',f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="2"/>']
        else:
            svg.append(f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="2"/>')
        if e['kind']=='generalization':
            svg.append(f'<polygon points="'+ ' '.join(f'{x},{y}' for x,y in triangle(e))+f'" fill="white" stroke="{INK}" stroke-width="2"/>')
    for a in actors:
        x,y=a['cx'],a['y']
        svg += [f'<g stroke="{INK}" stroke-width="2.4" fill="none"><circle cx="{x}" cy="{y+14}" r="14" fill="white"/><path d="M{x},{y+28} V{y+66} M{x-30},{y+39} H{x+30} M{x},{y+66} L{x-30},{y+104} M{x},{y+66} L{x+30},{y+104}"/></g>']
        for i,s in enumerate(a['label']):
            svg.append(svg_text(s,x,y+130+i*25,23,i==0))
    for n in cases:
        svg.append(f'<ellipse cx="{n["x"]+150}" cy="{n["y"]+72}" rx="150" ry="72" fill="white" stroke="{INK}" stroke-width="2"/>')
        for s,x,y,size,bold in case_lines(n): svg.append(svg_text(s,x,y,size,bold))
    for t in texts: svg.append(svg_text(t['text'],t['x'],t['y'],t['size'],t.get('bold',False),t.get('anchor','start')))
    svg.append('</svg>')
    return '\n'.join(svg)

def build_drawio():
    doc=ET.Element('mxfile',host='app.diagrams.net',agent='BD70')
    diagram=ET.SubElement(doc,'diagram',id='bd70-rendu',name='Cas d’utilisation - rendu')
    model=ET.SubElement(diagram,'mxGraphModel',grid='1',gridSize='10',page='1',pageScale='1',pageWidth=str(W),pageHeight=str(H),connect='1',arrows='1')
    root=ET.SubElement(model,'root')
    ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
    geo={}
    def cell(ident,value,x,y,w,h,style):
        c=ET.SubElement(root,'mxCell',id=ident,value=value,style=style,vertex='1',parent='1')
        ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
        geo[ident]=(x,y,w,h)
    common=f'fontFamily=Arial;fontColor={INK};strokeColor={INK};strokeWidth=2;fillColor=#ffffff;'
    cell('system','',40,370,1880,780,'rounded=0;'+common)
    for a in actors:
        cell(a['id'],'',a['cx']-30,a['y'],60,104,'shape=umlActor;'+common)
        label='\n'.join(a['label'])
        cell(a['id']+'-label',label,a['cx']-160,a['y']+112,320,54,'text;whiteSpace=wrap;html=0;align=center;verticalAlign=top;fontSize=23;fontStyle=1;strokeColor=none;fillColor=none;fontFamily=Arial;')
    for n in cases:
        val='<div style="font-size:22px;line-height:1.2;font-weight:bold">'+'<br>'.join(escape(s) for s in n['title'])+'</div><div style="font-size:19px;line-height:1.25;font-weight:normal">'+'<br>'.join(escape(s) for s in n['subtitle'])+'</div>'
        cell(n['id'],val,n['x'],n['y'],n['w'],n['h'],'ellipse;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;spacing=0;'+common)
    for i,e in enumerate(edges):
        style='edgeStyle=none;rounded=0;endArrow=none;html=0;strokeWidth=2;strokeColor='+INK+';'
        if e['kind']=='generalization': style+='endArrow=block;endFill=0;endSize=18;'
        if e['bridge']: style+='jumpStyle=arc;jumpSize=12;jumpDirection=left;'
        for pref,ident,pt in [('exit',e['source'],e['points'][0]),('entry',e['target'],e['points'][-1])]:
            x,y,w,h=geo[ident]
            style+=f'{pref}X={(pt[0]-x)/w};{pref}Y={(pt[1]-y)/h};{pref}Perimeter=0;'
        c=ET.SubElement(root,'mxCell',id=f'edge-{i}',style=style,edge='1',parent='1',source=e['source'],target=e['target'])
        g=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
        if len(e['points'])>2:
            arr=ET.SubElement(g,'Array',attrib={'as':'points'})
            for x,y in e['points'][1:-1]: ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
    for t in texts:
        tw=width(t['text'],t['size'],t.get('bold',False))+12
        x=t['x']-tw/2 if t.get('anchor')=='middle' else t['x']
        cell(t['id'],t['text'],x,t['y']-t['size'],tw,t['size']+8,f'text;html=0;align=left;verticalAlign=middle;whiteSpace=wrap;fontFamily=Arial;fontSize={t["size"]};fontStyle={1 if t.get("bold") else 0};strokeColor=none;fillColor=none;fontColor={INK};')
    ET.indent(doc)
    ET.ElementTree(doc).write(OUT/(STEM+'.drawio'),encoding='utf-8',xml_declaration=True)

def build_pdf():
    pagew,pageh=landscape(A3)
    c=canvas.Canvas(str(OUT/(STEM+'.pdf')),pagesize=(pagew,pageh))
    c.setTitle('BD70 - Diagramme UML de cas d’utilisation - Entrepôt logistique')
    c.setAuthor('Projet BD70')
    scale=min((pagew-32)/W,(pageh-32)/H)
    c.translate((pagew-W*scale)/2,(pageh-H*scale)/2)
    c.scale(scale,scale)
    def poly(points,close=False,fill=False):
        p=c.beginPath();p.moveTo(points[0][0],H-points[0][1])
        for x,y in points[1:]: p.lineTo(x,H-y)
        if close:p.close()
        c.drawPath(p,stroke=1,fill=int(fill))
    def txt(s,x,y,size,bold=False,anchor='middle'):
        c.setFillColor(INK);c.setFont('DiagramBold' if bold else 'Diagram',size)
        if anchor=='middle':c.drawCentredString(x,H-y,s)
        else:c.drawString(x,H-y,s)
    c.setStrokeColor(INK);c.setLineWidth(2);c.setFillColor('white')
    c.rect(40,H-1150,1880,780,stroke=1,fill=1)
    for e in sorted(edges,key=lambda e:e['bridge']):
        if e['bridge']:
            p=c.beginPath();p.moveTo(610,H-196);p.lineTo(610,H-140);p.lineTo(969,H-140)
            p.curveTo(976,H-125,984,H-125,991,H-140)
            p.lineTo(1350,H-140);p.lineTo(1350,H-196)
            c.setStrokeColor('white');c.setLineWidth(7);c.drawPath(p)
            c.setStrokeColor(INK);c.setLineWidth(2);c.drawPath(p)
        else:poly(e['points'])
        if e['kind']=='generalization':c.setFillColor('white');poly(triangle(e),True,True)
    for a in actors:
        x,y=a['cx'],a['y'];c.setFillColor('white');c.setLineWidth(2.4)
        c.circle(x,H-y-14,14,stroke=1,fill=1)
        poly([(x,y+28),(x,y+66)])
        poly([(x-30,y+39),(x+30,y+39)])
        poly([(x-30,y+104),(x,y+66),(x+30,y+104)])
        for i,s in enumerate(a['label']):txt(s,x,y+130+i*25,23,i==0)
    c.setLineWidth(2)
    for n in cases:
        c.setFillColor('white');c.ellipse(n['x'],H-n['y']-n['h'],n['x']+n['w'],H-n['y'],stroke=1,fill=1)
        for s,x,y,size,bold in case_lines(n):txt(s,x,y,size,bold)
    for t in texts:txt(t['text'],t['x'],t['y'],t['size'],t.get('bold',False),t.get('anchor','start'))
    c.showPage();c.save()

if __name__=='__main__':
    validate()
    svg=build_svg()
    html=f'<!doctype html><html lang="fr"><meta charset="utf-8"><title>BD70 - Cas d’utilisation</title><style>body{{margin:0;background:#eee}}.diagram-container{{overflow-x:auto;width:100%}}svg{{display:block;width:100%;min-width:{W}px}}@media print{{body{{background:white}}svg{{min-width:0;width:100%}}@page{{size:A3 landscape;margin:5mm}}}}</style><div class="diagram-container">{svg}</div></html>'
    (OUT/(STEM+'.html')).write_text(html,encoding='utf-8')
    (OUT/(STEM+'.svg')).write_text(svg,encoding='utf-8')
    build_drawio();build_pdf()
    # Structural verification after writing, including native editability.
    tree=ET.parse(OUT/(STEM+'.drawio'));cells=tree.findall('.//mxCell')
    assert len(tree.findall('./diagram'))==1
    assert sum('ellipse;' in c.get('style','') for c in cells)==15
    assert sum('shape=umlActor;' in c.get('style','') for c in cells)==6
    assert sum(c.get('edge')=='1' for c in cells)==20
    print(json.dumps({'pages':1,'use_cases':15,'actors':6,'associations':15,'generalizations':5,'pdf':'A3 landscape','status':'geometry, labels and native XML verified'},ensure_ascii=False))
