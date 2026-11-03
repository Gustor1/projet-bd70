"""Corrected business model after teacher feedback; does not edit application rights."""
import importlib.util
from pathlib import Path
from copy import deepcopy
from io import BytesIO
import xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
from pypdf import PdfReader

spec=importlib.util.spec_from_file_location('renderer',Path(__file__).with_name('build-usecase-v2.py'))
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
OUT=r.ROOT/'livrables'/'correction-prof-use-case'
OUT.mkdir(parents=True,exist_ok=True)
STEM='UML-CAS-UTILISATION-BD70-CORRIGE'
p=deepcopy(r.p)
p.slug='01-vue-ensemble';p.title='BD70 · Cas d’utilisation — correction après retour enseignant'
p.nodes=[n for n in p.nodes if not n['id'].startswith('h-') and n['id'] not in ['hierarchy-title','legend','scope']]
p.edges=[e for e in p.edges if e['kind']!='generalization']
by={n['id']:n for n in p.nodes}
by['title']['label']=p.title
by['subtitle']['label']='Modèle métier corrigé · Responsabilités distinctes · Détails des quatre cas principaux dans les pages suivantes'
by['system']['h']=1535
by['orders']['label']='Préparer une commande affectée\nPrélèvements et constitution des colis'
by['actor-trace']['label']='Responsable'
by['actor-planning']['label']='Personnel métier'
by['G-title']['label']='G · Préparation et expédition (détail p. 3–4)'
by['D-title']['label']='D · Flux de camions (détail p. 2)'
by['H-title']['label']='H · Traçabilité et pilotage (détail p. 5)'
p.frame('transport-portal','Transporteur · Accès limité aux rendez-vous de sa société',310,1500,840,160)
p.use('request-rdv','Demander / modifier / annuler\nun rendez-vous de sa société',1600,'Transporteur')
p.frame('coordination','Responsable · Coordination des commandes',1250,1500,840,160)
p.use('assign','Gérer les commandes clients\nAffecter un préparateur (détail p. 3)',1600,'Responsable','right')
p.text('roles','Aucun héritage entre métiers. Le responsable coordonne ; le préparateur exécute ; l’administrateur gère les comptes et les droits.',70,1700,2260,30,22)
p.text('common','Personnel : fonctions de session communes aux profils internes. Personnel métier : responsable, accueil et magasinier / préparateur.',70,1740,2260,30,21)

def page(slug,title,sub):
    z=r.Page(slug,title,sub)
    z.frame('system','Système de gestion d’un entrepôt logistique',280,180,1840,1430)
    z.text('legend','« include » : comportement systématique, flèche vers le cas inclus. « extend » : complément conditionnel, flèche vers le cas de base.',70,1660,2260,35,22)
    z.text('note','Les relations expriment des dépendances fonctionnelles, pas un ordre chronologique. Une session et les droits du rôle sont requis.',70,1710,2260,35,22)
    return z

def case(z,id,label,x,y,w=600,h=130):z.node(id,label,x-w/2,y-h/2,w,h)
def actor(z,id,label,cy,target,tx=450):
    z.actor(id,label,125,cy);z.edge(id,target,[(147,cy),(tx,cy)])
def inc(z,source,target,sy,ty,lane):
    z.edge(source,target,[(750+300*(1-((sy-next(n for n in z.nodes if n['id']==source)['y']-65)/65)**2)**0.5,sy),(lane,sy),(lane,ty),(1440,ty)],'include','« include »',((lane+1440)/2,ty-26))

d=page('02-passages','BD70 · Suivre le passage d’un camion','Accueil : arrivée et sortie du site · Magasinier : début et fin de l’opération à quai')
case(d,'arrival','Enregistrer l’arrivée\nd’un camion',750,420)
actor(d,'gate1','Agent d’accueil',420,'arrival')
case(d,'docs','Contrôler les documents\nd’entrée',1740,420)
d.edge('arrival','docs',[(1050,420),(1440,420)],'include','« include »',(1240,394))
case(d,'walkin','Traiter une arrivée\nsans rendez-vous',750,690)
actor(d,'gate2','Agent d’accueil',690,'walkin')
d.edge('walkin','arrival',[(750,625),(750,485)],'extend','« extend »',(875,552))
d.text('condition','[aucun rendez-vous associé]',1040,550,700,35,22)
case(d,'queue','Appeler le camion à quai',750,970)
actor(d,'gate3','Agent d’accueil',970,'queue')
case(d,'dock','Vérifier la disponibilité\net la compatibilité du quai',1740,970)
d.edge('queue','dock',[(1050,970),(1440,970)],'include','« include »',(1240,944))
case(d,'work','Enregistrer le début / la fin\ndu chargement ou déchargement',750,1250)
actor(d,'wh','Magasinier /\npréparateur',1250,'work')
case(d,'leave','Enregistrer le départ du site',750,1490)
actor(d,'gate4','Agent d’accueil',1490,'leave')
d.text('scope','Ces cas détaillent « Suivre le passage d’un camion ». Les horodatages permettent le calcul des durées et des retards.',420,235,1600,35,22)

o=page('03-commandes','BD70 · Gérer et préparer les commandes','Le responsable affecte le travail ; le préparateur traite uniquement les commandes qui lui sont affectées')
case(o,'manage','Gérer les commandes clients\nCréer / modifier / annuler',750,390)
actor(o,'manager1','Responsable\nd’exploitation',390,'manage')
case(o,'assign','Affecter / réaffecter\nun préparateur',750,620)
actor(o,'manager2','Responsable\nd’exploitation',620,'assign')
o.text('pre','Précondition de la préparation : commande validée pour préparation et préparateur affecté.',420,770,1600,35,23)
case(o,'prepare','Préparer une commande\naffectée',750,1100)
actor(o,'prep','Préparateur',1100,'prepare')
for id,label,cy in [('reserve','Réserver le stock selon FEFO\net obtenir la liste de prélèvement',900),('pick','Prélever et confirmer\nles articles',1160),('pack','Constituer les colis\net les palettes',1420)]:
    case(o,id,label,1740,cy)
for target,sy,ty,lane in [('reserve',1070,900,1160),('pick',1100,1160,1230),('pack',1130,1420,1100)]:inc(o,'prepare',target,sy,ty,lane)

s=page('04-expedition','BD70 · Expédier une commande','Magasinier / préparateur : contrôler et confirmer l’expédition · Documents consultables séparément après expédition')
case(s,'ship','Expédier une commande',750,750)
actor(s,'wh','Magasinier /\npréparateur',750,'ship')
for id,label,cy in [('check','Contrôler les colis, les lots\net la capacité du camion',400),('load','Confirmer le chargement\ndans le camion sortant',750),('exit','Enregistrer la sortie de stock\net le statut expédié',1100)]:case(s,id,label,1740,cy)
for target,sy,ty,lane in [('check',720,400,1120),('load',750,750,1190),('exit',780,1100,1260)]:inc(s,'ship',target,sy,ty,lane)
case(s,'documents','Éditer les documents de transport\nBon de livraison / lettre de voiture',750,1400)
actor(s,'wh2','Magasinier /\npréparateur',1400,'documents')
s.text('pre','Préconditions : commande préparée, colis constitués, camion sortant en opération à quai.',420,235,1600,35,23)
s.text('doc-note','Documents : expédition existante ; impression possible à nouveau sans refaire le chargement.',1100,1440,950,65,21)

t=page('05-tracabilite','BD70 · Tracer un lot','Responsable d’exploitation : retrouver l’historique et la destination des marchandises')
case(t,'trace','Tracer un lot',750,850)
actor(t,'manager','Responsable\nd’exploitation',850,'trace')
for id,label,cy in [('identify','Rechercher / identifier le lot',350),('receipt','Consulter sa réception\net sa provenance',650),('moves','Consulter les emplacements\net les mouvements successifs',950),('out','Consulter les commandes\net les expéditions associées',1250)]:case(t,id,label,1740,cy)
for target,sy,ty,lane in [('identify',810,350,1110),('receipt',835,650,1170),('moves',860,950,1290),('out',885,1250,1230)]:inc(t,'trace',target,sy,ty,lane)
t.text('empty','Chaque consultation peut retourner « aucun résultat » : un lot non expédié ne possède pas encore de commande / camion de sortie.',420,1460,1600,70,23)

r.PAGES=[p,d,o,s,t];r.OUT=OUT
for z in r.PAGES:
    for e in z.edges:
        e['pts']=[pt for i,pt in enumerate(e['pts']) if i==0 or pt!=e['pts'][i-1]]
r.validate();r.drawio()
(OUT/'BD70-USE-CASE-V2.drawio').replace(OUT/(STEM+'.drawio'))
svgs=[r.svg(z) for z in r.PAGES]
pw,ph=landscape(A3);c=canvas.Canvas(str(OUT/(STEM+'.pdf')),pagesize=(pw,ph))
c.setTitle('BD70 - Cas d’utilisation corrigés après retour enseignant')
for z,svg in zip(r.PAGES,svgs):
    (OUT/(z.slug+'.svg')).write_text(svg,encoding='utf-8')
    drawing=svg2rlg(BytesIO(svg.encode()));drawing.scale(r.W/drawing.width,r.H/drawing.height)
    scale=min((pw-24)/r.W,(ph-24)/r.H)
    c.saveState();c.translate((pw-r.W*scale)/2,(ph-r.H*scale)/2);c.scale(scale,scale)
    renderPDF.draw(drawing,c,0,0);c.restoreState();c.showPage()
c.save()
(OUT/(STEM+'.html')).write_text('<!doctype html><html lang="fr"><meta charset="utf-8"><title>BD70 corrigé</title><style>body{margin:0}.diagram-container{overflow-x:auto}svg{min-width:2400px;width:100%;height:auto}</style>'+''.join('<div class="diagram-container">'+v+'</div>' for v in svgs)+'</html>',encoding='utf-8')
assert len(PdfReader(OUT/(STEM+'.pdf')).pages)==5
tree=ET.parse(OUT/(STEM+'.drawio'))
for diag in tree.findall('diagram'):
    cells=diag.findall('.//mxCell'); ids={c.get('id') for c in cells}
    assert len(ids)==len(cells)
    for cell in cells:
        if cell.get('edge')=='1':assert cell.get('source') in ids and cell.get('target') in ids
assert not any(e['kind']=='generalization' for z in r.PAGES for e in z.edges)
print('OK: 5 pages, native Draw.io, no actor inheritance, geometry and PDF verified')


