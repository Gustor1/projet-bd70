"""Extraits lisibles du MCD Chen, par domaine, pour le rapport.

python scripts/build-mcd-extraits.py
Chaque extrait est un sous-graphe EXACT de docs/mcd-chen/BD70-MCD-CHEN.dot (référence validée) :
mêmes entités, attributs, associations et cardinalités ; seule la mise en page est recalculée.
Une association n'est retenue que si toutes ses entités appartiennent à l'extrait.
Sorties : docs/mcd-chen/extraits/*.dot et *.svg (vectoriels), rendus par viz.js (scripts/render-dot.cjs).
"""
from pathlib import Path
import re, subprocess, sys

root = Path(__file__).resolve().parents[1]
src = (root / 'docs/mcd-chen/BD70-MCD-CHEN.dot').read_text(encoding='utf-8')
DOMAINS = {
    'mcd-1-quais-passages': ('Quais, rendez-vous et passages', {'carrier', 'driver', 'vehicle', 'dock', 'appointment', 'truck_visit', 'visit_event', 'dock_downtime', 'equipment', 'vehicle_type'}),
    'mcd-2-reception-stock': ('Réception, emplacements et stock', {'supplier_notice', 'notice_line', 'receipt', 'receipt_line', 'receipt_item', 'lot', 'article', 'location', 'stock_movement', 'receipt_reserve', 'supplier'}),
    'mcd-3-preparation-expedition': ('Préparation et expédition', {'owner', 'customer_order', 'order_line', 'article', 'pick', 'package', 'shipment', 'receipt_item', 'stock_movement', 'truck_visit'}),
}
lines = src.splitlines()
header = [l for l in lines if l.startswith(('node [', 'graph [', 'edge [')) or l.lstrip().startswith(('node [', 'edge ['))]
nodes = {}
edges = []
for l in lines:
    m = re.match(r'^(\w+) -- (\w+) \[(.*)\];$', l)
    if m:
        edges.append((m.group(1), m.group(2), l)); continue
    m = re.match(r'^(\w+) \[', l)
    if m and not l.startswith(('graph', 'node', 'edge')):
        nodes[m.group(1)] = l
assoc = {n for n in nodes if re.fullmatch(r'R\d+', n)}
out = root / 'docs/mcd-chen/extraits'
out.mkdir(exist_ok=True)
for slug, (title, ents) in DOMAINS.items():
    keep = set(ents)
    # Associations entièrement internes à l'extrait.
    for r in assoc:
        ends = {a if b == r else b for a, b, _ in edges if r in (a, b) and not (a.startswith(r + '_') or b.startswith(r + '_'))}
        ends = {e for e in ends if e in nodes and not e.startswith(r + '_')}
        if ends and ends <= ents:
            keep.add(r)
    keep |= {n for n in nodes if any(n.startswith(k + '_attr') for k in keep)}
    body = [nodes[n] for n in nodes if n in keep]
    body += [l for a, b, l in edges if a in keep and b in keep]
    g = ('graph G {\n'
         f'graph [rankdir=LR,nodesep=.3,ranksep=.9,pad=.3,outputorder=edgesfirst,labelloc=t,labeljust=l,fontname="Arial",fontsize=18,'
         f'label="Extrait du MCD (notation de Chen) : {title}\\nSous-ensemble exact du MCD complet ; identifiants soulignés ; cardinalités lues comme dans le cours (Client 1 — Possède — 0,N Facture)."];\n'
         'node [fontname="Arial",fontsize=13,style=filled,color="#425c72",margin="0.06,0.03"]; edge [fontname="Arial",fontsize=13,fontcolor="#17324d",color="#627687",labeldistance=3,labelangle=20,labelfontsize=13];\n'
         + '\n'.join(body) + '\n}\n')
    (out / f'{slug}.dot').write_text(g, encoding='utf-8')
    print(slug, len([n for n in keep if n in ents]), 'entités,', len([n for n in keep if n in assoc]), 'associations')
subprocess.run(['node', str(root / 'scripts/render-dot.cjs'), *[str(out / f'{s}.dot') for s in DOMAINS]], check=True)
# Soulignement réel des identifiants et décalage des cardinalités superposées (même traitement que le MCD complet).
for slug in DOMAINS:
    subprocess.run([sys.executable, str(root / 'scripts/build-mcd-chen.py'), '--postprocess', str(out / f'{slug}.svg')], check=True)
