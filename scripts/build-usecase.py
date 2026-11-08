"""Diagramme de cas d'utilisation V2 : une seule page, un bonhomme par rôle, aucun héritage, cas éclatés avec include/extend.

Lancer avec le Python des dépendances PDF :
  python scripts/build-usecase.py
Répond aux remarques du professeur sur la V1 (docs/correction-prof-use-case/LIRE-MOI.md).
Réutilise les primitives de dessin de scripts/usecase_layout.py. Sorties dans livrables/use-case/ :
UML-CAS-UTILISATION-BD70-CORRIGE.pdf (vectoriel, A3 paysage), .svg (vectoriel), .drawio (modifiable).
"""
import importlib.util
from pathlib import Path
from io import BytesIO
import sys
import xml.etree.ElementTree as ET
local = Path(__file__).resolve().parents[1] / '.local' / 'pdf-dependencies'
if local.exists(): sys.path.insert(0, str(local))
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
from pypdf import PdfReader

spec = importlib.util.spec_from_file_location('renderer', Path(__file__).with_name('usecase_layout.py'))
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
r.W, r.H = 3400, 2580
OUT = r.ROOT / 'livrables' / 'use-case'
STEM = 'UML-CAS-UTILISATION-BD70-CORRIGE'
AL, AR = 125, 3275            # abscisses des acteurs
LB, LI = 620, 1380            # colonne gauche : cas de base, cas inclus
RB, RI = 2810, 2030           # colonne droite : cas de base, cas inclus
CW = 480                      # largeur des ellipses

p = r.Page('use-case-v2', 'BD70 · Diagramme de cas d’utilisation (V2)',
           'Système de gestion d’un entrepôt logistique · Un acteur par rôle, sans héritage · Cas éclatés en sous-cas avec « include » et « extend »')
geo = {}


S = 0                         # décalage vertical du cadre courant (marge sous les titres de cadres)


def case(ident, label, cx, cy, w=CW, h=66):
    cy += S
    p.node(ident, label, cx - w / 2, cy - h / 2, w, h, size=21)
    geo[ident] = (cx, cy, w, h)


def actor_link(actor, ay, side, lane, target):
    cx, cy, w, h = geo[target]
    start = (AL + 22, ay) if side == 'left' else (AR - 22, ay)
    end = (cx - w / 2, cy) if side == 'left' else (cx + w / 2, cy)
    pts = [start, (lane, ay), (lane, cy), end]
    out = [pts[0]]
    for q in pts[1:]:
        if q != out[-1]: out.append(q)
    simple = [out[0]]
    for i in range(1, len(out) - 1):
        a, b, c = simple[-1], out[i], out[i + 1]
        if not ((a[0] == b[0] == c[0]) or (a[1] == b[1] == c[1])): simple.append(b)
    simple.append(out[-1])
    p.edge(actor, target, simple)


def rel(src, dst, lane, kind='include'):
    """Relation orthogonale entre colonnes : part du centre du cas source (masqué par l'ellipse),
    aboutit au bord du cas cible. Étiquette au milieu du dernier segment horizontal."""
    sx, sy, sw, sh = geo[src]; tx, ty, tw, th = geo[dst]
    toward_right = tx > sx
    end = (tx - tw / 2 if toward_right else tx + tw / 2, ty)
    pts = [(sx, sy), (lane, sy), (lane, ty), end] if sy != ty else [(sx, sy), end]
    pts = [q for i, q in enumerate(pts) if i == 0 or q != pts[i - 1]]
    label = '« include »' if kind == 'include' else '« extend »'
    p.edge(src, dst, pts, kind, label, ((pts[-2][0] + end[0]) / 2, ty - 22))


# ------------------------------------------------------------ cadres
p.frame('system', 'Système de gestion d’un entrepôt logistique', 300, 165, 2800, 2200)
p.frame('A', 'A · Authentification et comptes', 330, 205, 2740, 235)
p.frame('B', 'B · Quais et rendez-vous', 330, 460, 1350, 330)
p.frame('C', 'C · Référentiels', 330, 810, 1350, 230)
p.frame('G1', 'G · Commandes : coordination', 330, 1060, 1350, 230)
p.frame('H', 'H · Pilotage et traçabilité', 330, 1310, 1350, 470)
p.frame('D', 'D · Suivi des flux de camions', 1720, 460, 1350, 630)
p.frame('E', 'E · Réception des marchandises', 1720, 1110, 1350, 235)
p.frame('F', 'F · Emplacements et stocks', 1720, 1365, 1350, 220)
p.frame('G2', 'G · Préparation et expédition', 1720, 1605, 1350, 710)

# A
S = 30
case('register', 'S’inscrire (compte en attente)', LB, 255)
case('accounts', 'Gérer les comptes et les profils\nConsulter le journal d’audit', LB, 360, CW, 74)
case('session', 'Se connecter / se déconnecter', 1700, 308, 560)
# B
S = 60
case('docks', 'Gérer les quais\net leurs indisponibilités', LB, 500, CW, 74)
case('plan', 'Planifier un rendez-vous\nCréer, déplacer, annuler', LB, 620, CW, 74)
case('compat', 'Vérifier la compatibilité\nvéhicule / quai', LI, 575, CW, 74)
case('slot', 'Vérifier la disponibilité\ndu créneau', LI, 670, CW, 74)
rel('plan', 'compat', 990); rel('plan', 'slot', 1040)
# C
S = 90
case('transport', 'Gérer transporteurs, chauffeurs\net véhicules', LB, 815, CW, 74)
case('refs', 'Gérer articles, clients, fournisseurs\net structure de l’entrepôt', 820, 900, 880, 74)
# G1
S = 120
case('orders', 'Gérer les commandes clients\nCréer, modifier, annuler', LB, 1040, CW, 74)
case('assign', 'Affecter / réaffecter\nun préparateur', LB, 1125, CW, 74)
# H
S = 150
case('reports', 'Consulter les indicateurs\net les rapports', LB, 1260, CW, 74)
case('trace', 'Tracer un lot', LB, 1460)
case('identify', 'Rechercher / identifier le lot', LI, 1300)
case('origin', 'Consulter sa réception\net sa provenance', LI, 1390, CW, 74)
case('moves', 'Consulter les emplacements\net les mouvements', LI, 1480, CW, 74)
case('dest', 'Consulter les commandes\net les expéditions', LI, 1570, CW, 74)
rel('trace', 'identify', 950); rel('trace', 'origin', 990); rel('trace', 'moves', 1030); rel('trace', 'dest', 1070)

# D
S = 60
case('arrival', 'Enregistrer l’arrivée\nd’un camion', RB, 500, CW, 74)
case('docs-in', 'Contrôler les documents\nd’entrée', RI, 500, CW, 74)
rel('arrival', 'docs-in', 0)
case('walkin', 'Traiter une arrivée\nsans rendez-vous', RB, 640, CW, 74)
p.edge('walkin', 'arrival', [(RB, 640 + S), (RB, 537 + S)], 'extend', '« extend »', (2665, 570 + S))
p.text('walkin-cond', '[aucun rendez-vous]', 2410, 598 + S, 230, 30, 19)
case('parking', 'Mettre en attente sur le parking', RB, 745)
case('call', 'Appeler le camion à quai', RB, 835)
case('dock-check', 'Vérifier la disponibilité\net la compatibilité du quai', RI, 835, CW, 74)
rel('call', 'dock-check', 0)
case('ops', 'Enregistrer début / fin\ndu (dé)chargement', RB, 925, CW, 74)
case('leave', 'Enregistrer le départ du site', RB, 1000)
p.text('d-note', 'Les horodatages calculent attente, immobilisation et retards.', 1760, 1040, 700, 30, 19)
# E
S = 90
case('receive', 'Réceptionner les marchandises\n(lots, quantités, état)', RB, 1120, CW, 74)
case('locate', 'Affecter un emplacement\ncompatible', RI, 1120, CW, 74)
rel('receive', 'locate', 0)
case('reserve', 'Déclarer un écart,\némettre une réserve', RI, 1210, CW, 74)
p.edge('reserve', 'receive', [(RI, 1210 + S), (RB, 1210 + S), (RB, 1157 + S)], 'extend', '« extend »', (2420, 1188 + S))
p.text('reserve-cond', '[écart constaté]', 2585, 1218 + S, 200, 30, 19)
# F
S = 120
case('stock', 'Rechercher et consulter le stock', RB, 1340)
case('move', 'Transférer, ajuster l’inventaire', RB, 1425)
# G2
S = 150
case('prepare', 'Préparer une commande\naffectée', RB, 1640, CW, 74)
case('fefo', 'Réserver le stock selon FEFO\n(liste de prélèvement)', RI, 1555, CW, 74)
case('pick', 'Prélever et confirmer\nles articles', RI, 1640, CW, 74)
case('pack', 'Constituer les colis\net les palettes', RI, 1725, CW, 74)
rel('prepare', 'fefo', 2470); rel('prepare', 'pick', 0); rel('prepare', 'pack', 2470)
case('ship', 'Expédier une commande', RB, 1900)
case('load-check', 'Contrôler colis, lots\net capacité du camion', RI, 1815, CW, 74)
case('load', 'Confirmer le chargement\ndans le camion sortant', RI, 1900, CW, 74)
case('exit', 'Enregistrer la sortie\nde stock', RI, 1985, CW, 74)
rel('ship', 'load-check', 2470); rel('ship', 'load', 0); rel('ship', 'exit', 2470)
case('documents', 'Éditer bon de livraison\net lettre de voiture', RB, 2100, CW, 74)

S = 0
# ------------------------------------------------------------ acteurs (un seul exemplaire chacun)
p.actor('a-new', 'Utilisateur\nnon inscrit', AL, 240)
p.actor('a-admin', 'Administrateur', AL, 380)
p.actor('a-carrier', 'Transporteur', AL, 760)
p.actor('a-manager', 'Responsable\nd’exploitation', AL, 1250)
p.actor('a-gate', 'Agent d’accueil', AR, 820)
p.actor('a-wh', 'Magasinier /\npréparateur', AR, 1850)
actor_link('a-new', 240, 'left', 190, 'register')
actor_link('a-admin', 380, 'left', 190, 'accounts')
actor_link('a-admin', 380, 'left', 215, 'session')
actor_link('a-carrier', 760, 'left', 215, 'session')
actor_link('a-carrier', 760, 'left', 215, 'plan')
for t in ['session', 'docks', 'plan', 'transport', 'refs', 'orders', 'assign', 'reports', 'trace']:
    actor_link('a-manager', 1250, 'left', 255, t)
for t in ['session', 'arrival', 'walkin', 'parking', 'call', 'leave']:
    actor_link('a-gate', 820, 'right', 3150, t)
for t in ['session', 'ops', 'receive', 'stock', 'move', 'prepare', 'ship', 'documents']:
    actor_link('a-wh', 1850, 'right', 3200, t)
# « Tracer un lot » est aussi ouvert à l'accueil et au magasinier (droit trace de l'application).
# Tracés par le bas du système et le couloir entre les deux colonnes : aucun croisement.
tcx, tcy, tw, th = geo['trace']; tb = tcy + th / 2
p.edge('a-wh', 'trace', [(AR - 22, 1850), (3200, 1850), (3200, 2355), (1710, 2355), (1710, 1795), (tcx + 20, 1795), (tcx + 20, tb)])
p.edge('a-gate', 'trace', [(AR + 22, 820), (3370, 820), (3370, 2380), (1690, 2380), (1690, 1812), (tcx - 20, 1812), (tcx - 20, tb)])

# ------------------------------------------------------------ légende dans la zone libre
p.frame('legend', 'Lecture du diagramme', 330, 1830, 1350, 515)
for i, line in enumerate([
    'Un acteur = un rôle : chaque acteur est dessiné une seule fois et relié',
    'aux seuls cas qu’il réalise. Aucun héritage entre acteurs.',
    'Le responsable coordonne et affecte ; le magasinier / préparateur exécute',
    'les commandes qui lui sont affectées ; l’administrateur gère les comptes.',
    'Le transporteur planifie uniquement les rendez-vous de sa société.',
    '« include » : comportement systématique ; la flèche pointe vers le cas inclus.',
    '« extend » : complément conditionnel [condition] ; la flèche pointe vers le cas de base.',
    'Tous les cas métier exigent une session ; ils sont implémentés dans l’interface web.',
]):
    p.text(f'leg{i}', line, 360, 1880 + i * 54, 1290, 32, 22)
p.text('foot', 'V2 · répond aux remarques sur la V1 : héritage supprimé, transporteur ajouté, rôles des commandes répartis, cas éclatés avec leurs relations.', 70, 2410, 3260, 34, 23)

# ------------------------------------------------------------ sorties et contrôles
r.PAGES = [p]; r.OUT = OUT
r.validate(); r.drawio()
(OUT / 'BD70-USE-CASE-V2.drawio').replace(OUT / (STEM + '.drawio'))
sv = r.svg(p)
(OUT / (STEM + '.svg')).write_text(sv, encoding='utf-8')
for old in OUT.glob(STEM + '-p*.svg'): old.unlink()
pw, ph = landscape(A3); c = canvas.Canvas(str(OUT / (STEM + '.pdf')), pagesize=(pw, ph))
c.setTitle('BD70 - Diagramme de cas d’utilisation (V2)'); c.setAuthor('Eliott LE, Semih TASKIN, Thomas VUILLIN')
drawing = svg2rlg(BytesIO(sv.encode())); drawing.scale(r.W / drawing.width, r.H / drawing.height)
scale = min((pw - 24) / r.W, (ph - 24) / r.H)
c.translate((pw - r.W * scale) / 2, (ph - r.H * scale) / 2); c.scale(scale, scale)
renderPDF.draw(drawing, c, 0, 0); c.showPage(); c.save()
assert len(PdfReader(OUT / (STEM + '.pdf')).pages) == 1
tree = ET.parse(OUT / (STEM + '.drawio'))
for diag in tree.findall('diagram'):
    cells = diag.findall('.//mxCell'); ids = {x.get('id') for x in cells}
    assert len(ids) == len(cells)
    for cell in cells:
        if cell.get('edge') == '1': assert cell.get('source') in ids and cell.get('target') in ids
assert not any(e['kind'] == 'generalization' for e in p.edges)
names = [n['label'] for n in p.nodes if n['kind'] == 'actor']
assert len(names) == len(set(names)) == 6, names
print('OK : 1 page, 6 acteurs uniques, aucun héritage,',
      sum(e['kind'] == 'include' for e in p.edges), 'include,', sum(e['kind'] == 'extend' for e in p.edges), 'extend,',
      sum(n['kind'] == 'ellipse' for n in p.nodes), 'cas')
