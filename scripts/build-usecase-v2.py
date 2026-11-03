"""Generate the revised two-page native Draw.io and vector PDF use-case diagram.

Run from any directory: python scripts/build-usecase-v2.py
Dependencies: reportlab, svglib, pypdf. Existing versions are never overwritten.
The files in livrables/use-case-v2 are generated; copy the Draw.io before editing.
"""
from pathlib import Path
from html import escape
from io import BytesIO
import json
import math
import xml.etree.ElementTree as ET
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'livrables' / 'use-case-v2'
W, H = 2400, 1800
INK, RULE, FILL = '#20354b', '#8395a5', '#f1f6fa'
for name, file in [('Arial', 'arial.ttf'), ('Arial-Bold', 'arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(Path('C:/Windows/Fonts') / file)))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold')


class Page:
    def __init__(self, slug, title, subtitle):
        self.slug, self.title, self.nodes, self.edges = slug, title, [], []
        self.text('title', title, 70, 45, 2260, 55, 38, True)
        self.text('subtitle', subtitle, 70, 105, 2260, 32, 23)

    def node(self, ident, label, x, y, w, h, kind='ellipse', size=24, fill=FILL):
        self.nodes.append(dict(id=ident, label=label, x=x, y=y, w=w, h=h,
                               kind=kind, size=size, fill=fill, bold=False))
        return ident

    def text(self, ident, label, x, y, w, h, size=22, bold=False):
        self.node(ident, label, x, y, w, h, 'text', size, 'none')
        self.nodes[-1]['bold'] = bold

    def frame(self, ident, title, x, y, w, h):
        self.node(ident, '', x, y, w, h, 'frame', fill='white')
        self.text(ident+'-title', title, x+20, y+10, w-40, 30, 23, True)

    def actor(self, ident, label, cx, cy):
        return self.node(ident, label, cx-22, cy-35, 44, 64, 'actor', 18, 'white')

    def edge(self, a, b, pts, kind='association', label='', labelxy=None, bridge=False):
        self.edges.append(dict(a=a, b=b, pts=pts, kind=kind, label=label,
                               labelxy=labelxy, bridge=bridge))

    def use(self, ident, label, cy, role, side='left', h=92):
        cx = 800 if side == 'left' else 1600
        self.node(ident, label, cx-310, cy-h/2, 620, h)
        ax = 125 if side == 'left' else 2275
        actor = self.actor('actor-'+ident, role, ax, cy)
        pts = [(ax+22, cy), (cx-310, cy)] if side == 'left' else [(ax-22, cy), (cx+310, cy)]
        self.edge(actor, ident, pts)


p = Page('01-vue-generale', 'BD70 · Cas d’utilisation — vue générale',
         'Application réalisée · Huit domaines du sujet · Les droits hérités sont précisés en bas de page')
p.frame('system', 'Système de gestion d’un entrepôt logistique', 280, 150, 1840, 1350)
for args in [
    ('A', 'A · Authentification et comptes', 310, 205, 840, 365),
    ('B', 'B · Quais et rendez-vous', 310, 600, 840, 365),
    ('C', 'C · Transporteurs, chauffeurs et véhicules', 310, 995, 840, 185),
    ('H', 'H · Traçabilité et tableaux de bord', 310, 1210, 840, 260),
    ('D', 'D · Suivi des flux de camions', 1250, 205, 840, 245),
    ('E', 'E · Réception des marchandises', 1250, 480, 840, 245),
    ('F', 'F · Emplacements et stocks', 1250, 755, 840, 290),
    ('G', 'G · Préparation et expédition', 1250, 1075, 840, 395),
]: p.frame(*args)
p.use('register', 'S’inscrire\nDemander un compte', 295, 'Personnel\nnon inscrit')
p.use('session', 'Se connecter / se déconnecter', 405, 'Personnel')
p.use('accounts', 'Administrer les comptes et les rôles\nActiver, désactiver, attribuer les droits', 515, 'Administrateur')
p.use('docks', 'Gérer les quais\nCaractéristiques et équipements', 690, 'Responsable')
p.use('appointments', 'Gérer les rendez-vous\nCréer, déplacer, annuler ; indisponibilités', 800, 'Accueil')
p.use('planning', 'Consulter les quais et le planning', 910, 'Personnel')
p.use('transport', 'Gérer le référentiel de transport\nTransporteurs, chauffeurs, véhicules', 1110, 'Responsable')
p.use('trace', 'Tracer un lot et ses mouvements', 1310, 'Personnel')
p.use('reports', 'Piloter l’activité\nIndicateurs, rapports et exports', 1420, 'Responsable')
p.use('visits', 'Suivre le passage d’un camion\nDe l’arrivée au départ ; opérations à quai', 345, 'Accueil', 'right', 110)
p.use('receipt', 'Réceptionner et ranger les marchandises\nAvis, lots, écarts, réserves, emplacements', 620, 'Magasinier /\npréparateur', 'right', 110)
p.use('references', 'Gérer les référentiels de stockage\nStructure, articles, clients, fournisseurs', 855, 'Responsable', 'right')
p.use('stock', 'Consulter et gérer les stocks\nRechercher, transférer, ajuster', 965, 'Magasinier /\npréparateur', 'right')
p.use('orders', 'Gérer et préparer les commandes\nAffectation, prélèvements FEFO, colis', 1180, 'Magasinier /\npréparateur', 'right')
p.use('shipping', 'Expédier une commande\nConfirmer le chargement et la sortie', 1290, 'Magasinier /\npréparateur', 'right')
p.use('documents', 'Éditer les documents de transport\nBon de livraison, lettre de voiture', 1400, 'Magasinier /\npréparateur', 'right')
p.text('hierarchy-title', 'Héritage des fonctions — le triangle pointe vers le rôle dont on reprend les possibilités', 70, 1520, 2260, 35, 23, True)
for ident, label, cx in [('admin', 'Administrateur', 180), ('manager', 'Responsable', 650),
                         ('gate', 'Accueil', 1120), ('warehouse', 'Magasinier / préparateur', 1590),
                         ('staff', 'Personnel', 2060)]:
    p.actor('h-'+ident, label, cx, 1645)
p.edge('h-admin', 'h-manager', [(202,1645),(628,1645)], 'generalization')
p.edge('h-manager', 'h-gate', [(672,1645),(1098,1645)], 'generalization')
p.edge('h-warehouse', 'h-staff', [(1612,1645),(2038,1645)], 'generalization')
p.edge('h-gate', 'h-staff', [(1120,1610),(1120,1570),(2060,1570),(2060,1610)], 'generalization')
p.edge('h-manager', 'h-warehouse', [(650,1610),(650,1590),(1590,1590),(1590,1610)], 'generalization', bridge=True)
p.text('legend', 'Trait simple : participation. Un acteur répété désigne toujours le même rôle. « Personnel » regroupe les fonctions communes.', 70, 1710, 2260, 30, 22)
p.text('scope', 'Session et droits requis pour les cas métier ; inscription et connexion sans session. Compte à activer par l’administrateur. Portail transporteur non retenu.', 70, 1748, 2260, 30, 21)

q = Page('02-relations-metier', 'BD70 · Cas d’utilisation — relations détaillées',
         'Vue complémentaire · Les associations et les droits de la page 1 restent applicables · Les flèches ne représentent pas un ordre chronologique')
q.frame('system', 'Système de gestion d’un entrepôt logistique — sélection de cas détaillés', 280, 155, 1840, 1390)

def detail_actor(ident, label, cy):
    return q.actor(ident, label, 125, cy)

def case(ident, label, cx, cy, w=570, h=110):
    q.node(ident, label, cx-w/2, cy-h/2, w, h)

q.frame('b', 'B · Rendez-vous — les vérifications concernent la création et le déplacement', 310, 210, 1780, 330)
case('create', 'Créer / déplacer\nun rendez-vous', 700, 335)
case('compat', 'Vérifier la compatibilité\nvéhicule / quai', 1740, 300)
case('available', 'Vérifier la disponibilité\ndu créneau', 1740, 450)
detail_actor('gate-b', 'Accueil', 335)
q.edge('gate-b','create',[(147,335),(415,335)])
q.edge('create','compat',[(968,315),(1200,315),(1200,300),(1455,300)],'include','« include »',(1315,274))
q.edge('create','available',[(968,355),(1100,355),(1100,450),(1455,450)],'include','« include »',(1280,424))
case('cancel', 'Annuler un rendez-vous', 700, 450, 570, 80)
detail_actor('gate-cancel', 'Accueil', 450)
q.edge('gate-cancel','cancel',[(147,450),(415,450)])
q.text('cancel-note', 'Annuler un rendez-vous reste un cas distinct : aucune recherche de créneau libre n’est nécessaire.', 350, 492, 1650, 30, 22)

q.frame('d', 'D · Arrivée — une variante conditionnelle', 310, 565, 1780, 260)
case('walkin', 'Traiter une arrivée\nsans rendez-vous', 700, 700)
case('arrival', 'Enregistrer l’arrivée d’un camion\nPoint d’extension : saisie de l’arrivée', 1740, 700, 620, 120)
detail_actor('gate-d', 'Accueil', 700)
q.edge('gate-d','walkin',[(147,700),(415,700)])
q.edge('walkin','arrival',[(985,700),(1430,700)],'extend','« extend »',(1200,674))
q.text('walkin-condition', '[aucun rendez-vous associé]', 990, 714, 440, 40, 21)

q.frame('e', 'E · Réception — un complément éventuel', 310, 850, 1780, 260)
case('reserve', 'Émettre une réserve', 700, 985)
case('receive', 'Réceptionner les marchandises\nPoint d’extension : constat à réception', 1740, 985, 620, 120)
detail_actor('warehouse-e', 'Magasinier /\npréparateur', 985)
q.edge('warehouse-e','reserve',[(147,985),(415,985)])
q.edge('reserve','receive',[(985,985),(1430,985)],'extend','« extend »',(1200,959))
q.text('reserve-condition', '[réserve à consigner]', 1010, 999, 400, 40, 21)

q.frame('g', 'G · Préparation et expédition — des comportements systématiques', 310, 1135, 1780, 380)
case('prepare', 'Lancer la préparation\nd’une commande', 700, 1240)
case('fefo', 'Réserver le stock disponible\nselon la règle FEFO', 1740, 1240)
detail_actor('warehouse-g1', 'Magasinier /\npréparateur', 1240)
q.edge('warehouse-g1','prepare',[(147,1240),(415,1240)])
q.edge('prepare','fefo',[(985,1240),(1455,1240)],'include','« include »',(1210,1214))
case('ship', 'Expédier une commande', 700, 1410)
case('check', 'Contrôler le chargement\nColis, lots, capacité du camion', 1740, 1410)
detail_actor('warehouse-g2', 'Magasinier /\npréparateur', 1410)
q.edge('warehouse-g2','ship',[(147,1410),(415,1410)])
q.edge('ship','check',[(985,1410),(1455,1410)],'include','« include »',(1210,1384))
q.text('include', '« include » : le cas source exécute obligatoirement le comportement inclus ; la flèche pointe vers ce comportement.', 70, 1580, 2260, 35, 24)
q.text('extend', '« extend » : un comportement complète le cas de base sous une condition ; la flèche pointe vers le cas de base.', 70, 1630, 2260, 35, 24)
q.text('documents-note', 'Les documents de transport peuvent être consultés / imprimés séparément : aucune inclusion automatique depuis « charger » n’est imposée.', 70, 1680, 2260, 35, 22)
q.text('fefo-note', 'FEFO : les lots dont la date de péremption arrive en premier sont prélevés en priorité. Les étapes de travail sont détaillées dans les scénarios.', 70, 1730, 2260, 35, 22)
PAGES = [p, q]


def text_svg(text, x, cy, size, bold=False, anchor='middle'):
    lines = text.split('\n')
    start = cy - (len(lines)-1)*size*.65 + size*.34
    return f'<text fill="{INK}" font-family="Arial" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">' + ''.join(
        f'<tspan x="{x}" y="{start+i*size*1.3}">{escape(line)}</tspan>' for i,line in enumerate(lines)) + '</text>'


def arrow_points(edge):
    tip, prev = edge['pts'][-1], edge['pts'][-2]
    dx,dy = tip[0]-prev[0], tip[1]-prev[1]
    length = math.hypot(dx,dy)
    ux,uy = dx/length,dy/length
    return [(tip[0]-18*ux-9*uy, tip[1]-18*uy+9*ux), tip,
            (tip[0]-18*ux+9*uy, tip[1]-18*uy-9*ux)]


def rounded_path(points):
    parts=[f'M{points[0][0]} {points[0][1]}']
    for a,b,c in zip(points,points[1:],points[2:]):
        before,after=math.dist(a,b),math.dist(b,c)
        r=min(8,before/2,after/2)
        entry=(b[0]+(a[0]-b[0])*r/before,b[1]+(a[1]-b[1])*r/before)
        leave=(b[0]+(c[0]-b[0])*r/after,b[1]+(c[1]-b[1])*r/after)
        parts.append(f'L{entry[0]} {entry[1]} Q{b[0]} {b[1]} {leave[0]} {leave[1]}')
    parts.append(f'L{points[-1][0]} {points[-1][1]}')
    return ' '.join(parts)


def svg(page):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="{page.slug}-title {page.slug}-desc">',
         f'<title id="{page.slug}-title">{escape(page.title)}</title>',
         f'<desc id="{page.slug}-desc">Fonctions du logiciel et relations entre les acteurs et les cas du projet BD70.</desc>',
         f'<rect width="{W}" height="{H}" fill="white"/>']
    for n in page.nodes:
        if n['kind']=='frame':
            s.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" fill="white" stroke="{RULE}" stroke-width="2"/>')
    for e in page.edges:
        pts = ' '.join(f'{x},{y}' for x,y in e['pts'])
        dashed = ' stroke-dasharray="8 6"' if e['kind'] in ('include','extend') else ''
        if e['bridge']:
            path='M650 1610 L650 1590 L1108 1590 Q1120 1568 1132 1590 L1590 1590 L1590 1610'
            s.append(f'<path d="{path}" fill="none" stroke="white" stroke-width="8"/>')
            s.append(f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="2"/>')
        else: s.append(f'<path d="{rounded_path(e["pts"])}" fill="none" stroke="{INK}" stroke-width="2"{dashed}/>')
        if e['kind']!='association':
            tag='polygon' if e['kind']=='generalization' else 'polyline'
            fill='white' if tag=='polygon' else 'none'
            s.append(f'<{tag} points="'+ ' '.join(f'{x},{y}' for x,y in arrow_points(e))+f'" fill="{fill}" stroke="{INK}" stroke-width="2"/>')
        if e['label']:
            x,y=e['labelxy']
            s.append(f'<rect x="{x-85}" y="{y-15}" width="170" height="30" fill="white"/>')
            s.append(text_svg(e['label'],x,y,22))
    for n in page.nodes:
        x,y,w,h=n['x'],n['y'],n['w'],n['h']
        if n['kind']=='frame': continue
        if n['kind']=='ellipse':
            s.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" fill="{n["fill"]}" stroke="{INK}" stroke-width="2"/>')
        if n['kind']=='actor':
            cx=x+w/2
            s.append(f'<g stroke="{INK}" stroke-width="2.2" fill="none"><circle cx="{cx}" cy="{y+10}" r="10" fill="white"/><path d="M{cx} {y+20} V{y+42} M{x} {y+35} H{x+w} M{x} {y+h} L{cx} {y+42} L{x+w} {y+h}"/></g>')
            lines=n['label'].count('\n')+1
            s.append(text_svg(n['label'],cx,y+h+12+(lines-1)*9,n['size']))
        else:
            s.append(text_svg(n['label'],x if n['kind']=='text' else x+w/2,y+h/2,n['size'],n['bold'],'start' if n['kind']=='text' else 'middle'))
    return '\n'.join(s+['</svg>'])


def drawio():
    doc=ET.Element('mxfile',host='app.diagrams.net',agent='BD70')
    for page in PAGES:
        diagram=ET.SubElement(doc,'diagram',id=page.slug,name=page.title.split('— ')[-1])
        model=ET.SubElement(diagram,'mxGraphModel',grid='1',gridSize='10',page='1',pageScale='1',pageWidth=str(W),pageHeight=str(H),connect='1')
        root=ET.SubElement(model,'root')
        ET.SubElement(root,'mxCell',id='0'); ET.SubElement(root,'mxCell',id='1',parent='0')
        for n in page.nodes:
            style=f'whiteSpace=wrap;html=0;fontFamily=Arial;fontSize={n["size"]};fontColor={INK};strokeColor={INK};strokeWidth=2;fillColor={n["fill"]};'
            if n['kind']=='ellipse': style+='ellipse;align=center;verticalAlign=middle;'
            elif n['kind']=='actor': style+='shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;align=center;spacingTop=5;'
            elif n['kind']=='frame': style+=f'rounded=0;strokeColor={RULE};'
            else: style+='text;align=left;verticalAlign=middle;strokeColor=none;fillColor=none;'
            if n['bold']: style+='fontStyle=1;'
            c=ET.SubElement(root,'mxCell',id=n['id'],value=n['label'],style=style,vertex='1',parent='1')
            ET.SubElement(c,'mxGeometry',x=str(n['x']),y=str(n['y']),width=str(n['w']),height=str(n['h']),attrib={'as':'geometry'})
        byid={n['id']:n for n in page.nodes}
        for i,e in enumerate(page.edges):
            style=f'edgeStyle=none;rounded=1;arcSize=8;html=0;strokeWidth=2;strokeColor={INK};endArrow=none;fontFamily=Arial;fontSize=22;labelBackgroundColor=#ffffff;'
            if e['kind']=='generalization':style+='endArrow=block;endFill=0;endSize=18;'
            elif e['kind'] in ('include','extend'):style+='dashed=1;dashPattern=8 6;endArrow=open;endSize=18;'
            if e['bridge']:style+='jumpStyle=arc;jumpSize=12;'
            for prefix,ident,pt in [('exit',e['a'],e['pts'][0]),('entry',e['b'],e['pts'][-1])]:
                n=byid[ident]
                style+=f'{prefix}X={(pt[0]-n["x"])/n["w"]};{prefix}Y={(pt[1]-n["y"])/n["h"]};{prefix}Perimeter=0;'
            c=ET.SubElement(root,'mxCell',id=f'edge-{i}',style=style,edge='1',parent='1',source=e['a'],target=e['b'])
            g=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
            if len(e['pts'])>2:
                arr=ET.SubElement(g,'Array',attrib={'as':'points'})
                for x,y in e['pts'][1:-1]: ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
            if e['label']:
                x,y=e['labelxy']
                label=ET.SubElement(root,'mxCell',id=f'edge-label-{i}',value=e['label'],vertex='1',parent='1',style=f'text;html=0;align=center;verticalAlign=middle;fillColor=#ffffff;strokeColor=none;fontFamily=Arial;fontSize=22;fontColor={INK};')
                ET.SubElement(label,'mxGeometry',x=str(x-85),y=str(y-15),width='170',height='30',attrib={'as':'geometry'})
    ET.indent(doc)
    ET.ElementTree(doc).write(OUT/'BD70-USE-CASE-V2.drawio',encoding='utf-8',xml_declaration=True)


def validate():
    for page in PAGES:
        ids=[n['id'] for n in page.nodes]
        assert len(set(ids))==len(ids)
        cases=[n for n in page.nodes if n['kind']=='ellipse']
        for n in page.nodes:
            assert 0<=n['x']<n['x']+n['w']<=W and 0<=n['y']<n['y']+n['h']<=H,n['id']
            if n['kind'] in ('text','ellipse'):
                lines=n['label'].split('\n')
                for i,line in enumerate(lines):
                    tw=pdfmetrics.stringWidth(line,'Arial-Bold' if n['bold'] else 'Arial',n['size'])
                    available=n['w']
                    if n['kind']=='ellipse':
                        dy=abs((i-(len(lines)-1)/2)*n['size']*1.3)+n['size']*.65
                        available*=math.sqrt(max(0,1-(dy/(n['h']/2))**2))
                    assert tw+8<available,(page.slug,n['id'],line,tw,available)
        for i,a in enumerate(cases):
            for b in cases[i+1:]:
                assert a['x']+a['w']<=b['x'] or b['x']+b['w']<=a['x'] or a['y']+a['h']<=b['y'] or b['y']+b['h']<=a['y'],(a['id'],b['id'])
        for e in page.edges:
            assert e['a'] in ids and e['b'] in ids
            for (x1,y1),(x2,y2) in zip(e['pts'],e['pts'][1:]):
                assert x1==x2 or y1==y2


def main():
    validate()
    OUT.mkdir(parents=True,exist_ok=True)
    drawio()
    rendered=[svg(page) for page in PAGES]
    for page,content in zip(PAGES,rendered):
        (OUT/(page.slug+'.svg')).write_text(content,encoding='utf-8')
    html='<!doctype html><html lang="fr"><meta charset="utf-8"><title>BD70 - Cas d’utilisation V2</title><style>body{margin:0;background:#e9edf0;font-family:Arial}header{padding:20px}a{color:#20354b}.diagram-container{overflow-x:auto;width:100%;margin-bottom:24px}svg{display:block;min-width:2400px;width:100%;height:auto}@media print{header{display:none}.diagram-container{break-after:page;margin:0;overflow:visible}svg{min-width:0;width:100%}@page{size:A3 landscape;margin:5mm}}</style><header><strong>BD70 · Version révisée</strong> — <a href="BD70-USE-CASE-V2.drawio">Draw.io modifiable</a> · <a href="BD70-USE-CASE-V2.pdf">PDF 2 pages</a></header>'+''.join('<div class="diagram-container">'+s+'</div>' for s in rendered)+'</html>'
    (OUT/'BD70-USE-CASE-V2.html').write_text(html,encoding='utf-8')
    pw,ph=landscape(A3)
    c=canvas.Canvas(str(OUT/'BD70-USE-CASE-V2.pdf'),pagesize=(pw,ph))
    c.setTitle('BD70 - Cas d’utilisation UML - Version révisée')
    for content in rendered:
        drawing=svg2rlg(BytesIO(content.encode('utf-8')))
        drawing.scale(W/drawing.width,H/drawing.height)
        drawing.width,drawing.height=W,H
        scale=min((pw-24)/W,(ph-24)/H)
        c.saveState();c.translate((pw-W*scale)/2,(ph-H*scale)/2);c.scale(scale,scale)
        renderPDF.draw(drawing,c,0,0)
        c.restoreState();c.showPage()
    c.save()
    tree=ET.parse(OUT/'BD70-USE-CASE-V2.drawio')
    assert len(tree.findall('diagram'))==2
    for d in tree.findall('diagram'):
        cells=d.findall('.//mxCell'); ids={c.get('id') for c in cells}
        assert len(ids)==len(cells)
        for cell in cells:
            if cell.get('edge')=='1': assert cell.get('source') in ids and cell.get('target') in ids
        assert not any('image=' in cell.get('style','') for cell in cells)
    pdf=PdfReader(OUT/'BD70-USE-CASE-V2.pdf')
    assert len(pdf.pages)==2
    for page in pdf.pages: assert len(page.extract_text())>1000
    result={'pages':2,'overview_use_cases':sum(n['kind']=='ellipse' for n in p.nodes),'detail_use_cases':sum(n['kind']=='ellipse' for n in q.nodes),'include':4,'extend':2,'native_drawio':True,'pdf':'A3 paysage','checks':'geometry, text widths, references, native shapes, PDF text'}
    (OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__': main()
