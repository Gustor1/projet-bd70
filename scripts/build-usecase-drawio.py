"""Generate editable native Draw.io objects and matching SVG previews (stdlib only)."""
from pathlib import Path
import xml.etree.ElementTree as ET
from html import escape
import json

OUT = Path(__file__).resolve().parents[1] / 'livrables' / 'uml-use-case'
OUT.mkdir(parents=True, exist_ok=True)
INK = '#20354b'
COLORS = {'blue': ('#eef5fc', '#537ea6'), 'green': ('#eef8f3', '#568873'),
          'orange': ('#fff5e9', '#b6874b'), 'purple': ('#f4effa', '#8c72aa'),
          'gray': ('#f4f6f8', '#8291a1')}
pages = []

class Page:
    def __init__(self, name, slug, width, height, title, subtitle):
        self.name, self.slug, self.width, self.height = name, slug, width, height
        self.nodes, self.edges = [], []
        pages.append(self)
        self.text('title', title, 60, 35, width-120, 50, 34, True)
        self.text('subtitle', subtitle, 60, 95, width-120, 50, 19)

    def node(self, ident, label, x, y, w, h, kind='ellipse', color='blue', size=21, bold=False):
        n = dict(id=ident, label=label, x=x, y=y, w=w, h=h, kind=kind, color=color, size=size, bold=bold)
        self.nodes.append(n)
        return ident

    def text(self, ident, label, x, y, w, h, size=19, bold=False):
        return self.node(ident, label, x, y, w, h, 'text', 'gray', size, bold)

    def actor(self, ident, label, x, y):
        return self.node(ident, label, x, y, 64, 100, 'actor')

    def edge(self, a, b, points, kind='association', label='', labelxy=None):
        self.edges.append(dict(a=a, b=b, points=points, kind=kind, label=label, labelxy=labelxy))

    def frame(self, label, x, y, w, h):
        self.node('frame'+str(len(self.nodes)), '', x, y, w, h, 'frame')
        self.text('frame-title'+str(len(self.nodes)), label, x+22, y+15, w-44, 35, 21, True)


p = Page('01 - Vue d’ensemble', '01-vue-ensemble', 1800, 1770,
         'TRANSIT · Diagramme de cas d’utilisation',
         'Projet BD70 — Entrepôt logistique · Vue fonctionnelle de l’application réalisée')
p.frame('Système Transit — gestion de l’entrepôt', 340, 185, 1120, 1245)
p.text('left-title', 'ADMINISTRATION & FLUX CAMIONS', 375, 245, 460, 35, 18, True)
p.text('right-title', 'MARCHANDISES & COMMANDES', 960, 245, 460, 35, 18, True)
for ident, label, y, color in [
    ('accounts', 'UC11 · Administrer les comptes\nActiver, attribuer un rôle, désactiver', 310, 'purple'),
    ('refs', 'UC02 · Gérer les référentiels\nTransport, articles, propriétaires, stockage', 490, 'purple'),
    ('reports', 'UC10 · Piloter l’activité\nIndicateurs, rapports et exports', 670, 'purple'),
    ('planning', 'UC03 · Planifier les quais\nCréer, déplacer, annuler un rendez-vous', 900, 'orange'),
    ('visits', 'UC04 · Suivre les camions\nDe l’arrivée au départ du site', 1080, 'orange')]:
    p.node(ident, label, 400, y, 420, 110, color=color)
for ident, label, y in [
    ('receipt', 'UC05 · Réceptionner et ranger\nAvis, lots, palettes, écarts et réserves', 310),
    ('stock', 'UC06 · Gérer les stocks\nRechercher, transférer, ajuster', 550),
    ('picking', 'UC07 · Préparer les commandes\nLignes, affectation et prélèvements FEFO', 790),
    ('shipping', 'UC08 · Charger et expédier\nColis, palettes et documents de transport', 1030)]:
    p.node(ident, label, 980, y, 420, 110, color='green')
p.actor('admin', 'Administrateur', 130, 315)
p.actor('manager', 'Responsable\nd’exploitation', 130, 570)
p.actor('gate', 'Agent d’accueil', 130, 990)
p.actor('warehouse', 'Magasinier /\npréparateur', 1605, 675)
p.edge('admin','accounts',[(194,365),(400,365)])
p.edge('manager','refs',[(194,620),(280,620),(280,545),(400,545)])
p.edge('manager','reports',[(194,620),(280,620),(280,725),(400,725)])
p.edge('gate','planning',[(194,1040),(280,1040),(280,955),(400,955)])
p.edge('gate','visits',[(194,1040),(280,1040),(280,1135),(400,1135)])
for target, y in [('receipt',365),('stock',605),('picking',845),('shipping',1085)]:
    p.edge('warehouse',target,[(1605,725),(1515,725),(1515,y),(1400,y)])
p.text('common', 'FONCTIONS COMMUNES AU PERSONNEL', 450, 1220, 900, 35, 18, True)
for ident,label,x in [('auth','UC01 · Se connecter\net se déconnecter',385),
                      ('trace','UC09 · Tracer un lot\nDe la réception à l’expédition',755),
                      ('readplan','Consulter le planning\net l’état des quais',1125)]:
    p.node(ident,label,x,1290,290,95,color='blue',size=19)
p.actor('staff','Personnel\n(acteur général)',868,1500)
for target,x in [('auth',530),('trace',900),('readplan',1270)]:
    p.edge('staff',target,[(900,1500),(900,1465),(x,1465),(x,1385)])
p.text('note','Lecture : les associations propres à chaque profil sont affichées ici ; les droits hérités sont détaillés page 2.\nSession active et rôle autorisé requis pour les cas métier. Les relations « include / extend » figurent page 3.',90,1665,1620,65,19)

p = Page('02 - Acteurs et accès', '02-acteurs-acces', 1800, 1400,
         'Acteurs · Généralisation et accès',
         'La pointe du triangle désigne le rôle général dont les cas d’utilisation sont hérités.')
for ident,label,x,y in [('staff','Personnel\n(acteur général)',678,225),
                        ('gate','Agent d’accueil',378,500),
                        ('warehouse','Magasinier /\npréparateur',978,500),
                        ('manager','Responsable\nd’exploitation',678,795),
                        ('admin','Administrateur',678,1090)]:
    p.actor(ident,label,x,y)
p.edge('gate','staff',[(410,500),(410,275),(678,275)],'generalization')
p.edge('warehouse','staff',[(1010,500),(1010,275),(742,275)],'generalization')
p.edge('manager','gate',[(678,840),(310,840),(310,550),(378,550)],'generalization')
p.edge('manager','warehouse',[(742,840),(1120,840),(1120,550),(1042,550)],'generalization')
p.edge('admin','manager',[(742,1140),(820,1140),(820,845),(742,845)],'generalization')
p.text('common','Connexion / déconnexion\nTraçabilité des lots\nConsultation du planning',60,235,430,100,21)
p.text('gate-note','Rendez-vous\nPassages des camions',80,630,450,70,21)
p.text('warehouse-note','Réceptions · stocks\nPréparation · expédition',850,660,240,80,21)
p.text('manager-note','Référentiels et pilotage\n+ fonctions Accueil et Magasinier',80,900,540,80,21)
p.text('admin-note','Gestion des comptes\n+ toutes les fonctions du Responsable',80,1135,540,80,21)
p.frame('Transit — accès initial',1200,185,540,420)
p.actor('candidate','Membre du personnel\nnon inscrit',1480,775)
p.node('register','UC01a · S’inscrire\nDemander un compte',1270,285,400,110,color='blue')
p.edge('candidate','register',[(1544,825),(1710,825),(1710,340),(1670,340)])
p.text('pending','Compte créé en attente.\nActivation par l’administrateur (UC11)\navant toute connexion.',1220,445,500,100,19)
p.text('notes','Cette généralisation exprime les capacités fonctionnelles, pas la hiérarchie des personnes.\nLe transporteur et le chauffeur sont gérés comme données : aucun portail transporteur n’est implémenté.\nUC01 à UC10 reprennent la documentation ; UC01a détaille l’inscription et UC11 explicite l’administration des comptes.',60,1270,1680,100,19)

p = Page('03 - Include et extend', '03-relations-metier', 1800, 1610,
         'Cas d’utilisation · Relations métier',
         'Vue partielle : les acteurs et leurs associations sont ceux des pages 1 et 2.')
p.frame('Système Transit — détails des comportements',100,190,1600,1150)
rows = [
    ('rdv','Créer / déplacer\nun rendez-vous (UC03)','quai','Vérifier la disponibilité\net la compatibilité du quai',300,'include',''),
    ('walkin','Traiter une arrivée\nsans rendez-vous','flow','Suivre un camion (UC04)\nPoint d’extension : arrivée',480,'extend','[sans rendez-vous]'),
    ('reception','Valider une réception (UC05)\navec quantités acceptées','capacity','Contrôler la compatibilité\net la capacité des emplacements',660,'include',''),
    ('transfer','Transférer du stock (UC06)','free','Contrôler le stock libre\net la destination',840,'include',''),
    ('prepare','Préparer une commande (UC07)','fefo','Réserver le stock disponible\nselon la règle FEFO',1020,'include',''),
    ('ship','Expédier une commande (UC08)','loading','Vérifier colis, lots\net capacité du camion',1200,'include','')]
for a,la,b,lb,y,kind,condition in rows:
    p.node(a,la,180,y,510,105,color='orange' if y<600 else 'green')
    p.node(b,lb,1100,y,510,105,color='orange' if y<600 else 'green')
    p.edge(a,b,[(690,y+52.5),(1100,y+52.5)],kind,'«'+kind+'»'+ ('\n'+condition if condition else ''),(895,y+24))
p.text('legend','« include » : comportement systématiquement exécuté par le cas source ; flèche vers le cas inclus.\n« extend » : comportement conditionnel ajouté au cas de base ; flèche vers le cas étendu.\nFEFO : les lots dont la date de péremption arrive en premier sont prélevés en priorité.',100,1380,1600,110,21)
p.text('auth-note','L’authentification est une précondition de session, pas un « include » répété à chaque opération.',100,1515,1600,45,19)


def render_xml():
    doc = ET.Element('mxfile', host='app.diagrams.net', agent='BD70', version='24.7.17')
    for page in pages:
        diag = ET.SubElement(doc,'diagram',id=page.slug,name=page.name)
        model = ET.SubElement(diag,'mxGraphModel',dx='1800',dy='1800',grid='1',gridSize='10',guides='1',tooltips='1',connect='1',arrows='1',fold='1',page='1',pageScale='1',pageWidth=str(page.width),pageHeight=str(page.height),math='0',shadow='0')
        root = ET.SubElement(model,'root')
        ET.SubElement(root,'mxCell',id='0')
        ET.SubElement(root,'mxCell',id='1',parent='0')
        for n in page.nodes:
            fill,stroke = COLORS[n['color']]
            style=f"whiteSpace=wrap;html=0;fontFamily=Arial;fontSize={n['size']};fontColor={INK};strokeWidth=2;"
            if n['kind']=='ellipse': style+=f'ellipse;fillColor={fill};strokeColor={stroke};'
            elif n['kind']=='actor': style+='shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;align=center;fillColor=#ffffff;strokeColor='+INK+';'
            elif n['kind']=='frame': style+='rounded=0;fillColor=#ffffff;strokeColor=#a5b2be;'
            else: style+='text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;'
            if n['bold']: style+='fontStyle=1;'
            c=ET.SubElement(root,'mxCell',id=n['id'],value=n['label'],style=style,vertex='1',parent='1')
            ET.SubElement(c,'mxGeometry',x=str(n['x']),y=str(n['y']),width=str(n['w']),height=str(n['h']),attrib={'as':'geometry'})
        nodes={n['id']:n for n in page.nodes}
        for i,e in enumerate(page.edges):
            a,b=nodes[e['a']],nodes[e['b']]
            start,end=e['points'][0],e['points'][-1]
            style=f'edgeStyle=none;rounded=0;html=0;strokeWidth=2;strokeColor={INK};fontColor={INK};fontSize=19;fontFamily=Arial;labelBackgroundColor=#ffffff;'
            for prefix,n,pt in [('exit',a,start),('entry',b,end)]:
                style+=f"{prefix}X={(pt[0]-n['x'])/n['w']};{prefix}Y={(pt[1]-n['y'])/n['h']};{prefix}Perimeter=0;"
            style+=('endArrow=block;endFill=0;endSize=18;' if e['kind']=='generalization' else
                    'dashed=1;dashPattern=8 5;endArrow=open;endSize=14;' if e['kind'] in ['include','extend'] else 'endArrow=none;')
            c=ET.SubElement(root,'mxCell',id='edge'+str(i),value=e['label'],style=style,edge='1',parent='1',source=e['a'],target=e['b'])
            g=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
            if e['label']: ET.SubElement(g,'mxPoint',x='0',y='-28',attrib={'as':'offset'})
            if len(e['points'])>2:
                arr=ET.SubElement(g,'Array',attrib={'as':'points'})
                for x,y in e['points'][1:-1]: ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
    ET.indent(doc)
    ET.ElementTree(doc).write(OUT/'Transit-Use-Case.drawio',encoding='utf-8',xml_declaration=True)


def svg_text(label,x,y,size,anchor='middle',bold=False):
    lines=label.split('\n')
    start=y-(len(lines)-1)*size*0.64
    return '<text fill="'+INK+'" font-family="Arial, sans-serif" font-size="'+str(size)+'" text-anchor="'+anchor+'"'+(' font-weight="bold"' if bold else '')+'>'+''.join(f'<tspan x="{x}" y="{start+i*size*1.28}">{escape(line)}</tspan>' for i,line in enumerate(lines))+'</text>'


def render_svg(page):
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{page.width}" height="{page.height}" viewBox="0 0 {page.width} {page.height}">',
       '<defs><marker id="open" markerWidth="14" markerHeight="14" refX="13" refY="7" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L13 7 L1 13" fill="none" stroke="'+INK+'" stroke-width="2"/></marker><marker id="triangle" markerWidth="21" markerHeight="20" refX="20" refY="10" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L20 10 L1 19 Z" fill="white" stroke="'+INK+'" stroke-width="2"/></marker></defs>',
       '<rect width="100%" height="100%" fill="white"/>']
    for n in page.nodes:
        if n['kind']=='frame': s.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" fill="white" stroke="#a5b2be" stroke-width="2"/>')
    for e in page.edges:
        extra=' stroke-dasharray="8 5" marker-end="url(#open)"' if e['kind'] in ['include','extend'] else ' marker-end="url(#triangle)"' if e['kind']=='generalization' else ''
        s.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in e['points'])+'" fill="none" stroke="'+INK+'" stroke-width="2"'+extra+'/>')
        if e['label']:
            x,y=e['labelxy']; s.append(svg_text(e['label'],x,y,19))
    for n in page.nodes:
        x,y,w,h=n['x'],n['y'],n['w'],n['h']
        if n['kind']=='frame': continue
        if n['kind']=='ellipse':
            fill,stroke=COLORS[n['color']]
            s.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        elif n['kind']=='actor':
            cx=x+w/2
            s.append(f'<g stroke="{INK}" stroke-width="2.4" fill="white"><circle cx="{cx}" cy="{y+14}" r="14"/><path d="M{cx} {y+28} V{y+65} M{x} {y+43} H{x+w} M{cx} {y+65} L{x} {y+100} M{cx} {y+65} L{x+w} {y+100}" fill="none"/></g>')
            lines=n['label'].count('\n')+1
            s.append(svg_text(n['label'],cx,y+h+26+(lines-1)*13,21))
            continue
        s.append(svg_text(n['label'],x if n['kind']=='text' else x+w/2,y+h/2+n['size']*.35,n['size'],'start' if n['kind']=='text' else 'middle',n['bold']))
    s.append('</svg>')
    (OUT/(page.slug+'.svg')).write_text('\n'.join(s),encoding='utf-8')


def validate():
    tree=ET.parse(OUT/'Transit-Use-Case.drawio')
    assert len(tree.findall('diagram'))==3
    for page,diag in zip(pages,tree.findall('diagram')):
        ids={c.attrib['id'] for c in diag.findall('.//mxCell')}
        assert len(ids)==len(diag.findall('.//mxCell'))
        for e in page.edges: assert e['a'] in ids and e['b'] in ids
        cases=[n for n in page.nodes if n['kind']=='ellipse']
        for i,a in enumerate(cases):
            assert 0<=a['x']<a['x']+a['w']<=page.width
            assert 0<=a['y']<a['y']+a['h']<=page.height
            for b in cases[i+1:]:
                assert a['x']+a['w']<=b['x'] or b['x']+b['w']<=a['x'] or a['y']+a['h']<=b['y'] or b['y']+b['h']<=a['y'], (a['id'],b['id'])
        ET.parse(OUT/(page.slug+'.svg'))
    print(json.dumps({'pages':len(pages),'native_use_cases':sum(n['kind']=='ellipse' for p in pages for n in p.nodes),'status':'XML valid; references and spacing checked'},ensure_ascii=False))


render_xml()
for page in pages: render_svg(page)
validate()
