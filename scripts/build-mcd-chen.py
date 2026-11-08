"""MCD en notation de Chen, convention du cours BD70, généré depuis docs/mcd-chen/modele.json.

python scripts/build-mcd-chen.py [--layout dot|fdp] [--out chemin.dot]
Notation (cours BD70, diapositives 212 à 223) :
- entité : rectangle ; association : losange ; attribut : ovale ; identifiant souligné ;
- attribut porté par une association : ovale relié au losange ;
- cardinalités min,max écrites sur chaque trait entité–association, SANS parenthèses, et lues comme dans le cours :
  le couple placé du côté d’une entité indique combien de fois l’AUTRE entité peut lui être liée
  (« Client 1 — Possède — 0,N Facture » : un client possède 0 à N factures ; une facture appartient à 1 client).
Le contenu (entités, attributs, associations, cardinalités min,max) est celui de modele.json, contrôlé contre la base
par scripts/verify-models.py ; seule la présentation est produite ici. « (facultatif) » = colonne NULL dans le schéma réel.
"""
from pathlib import Path
import json, sys, html

root = Path(__file__).resolve().parents[1]
model = json.loads((root / 'docs/mcd-chen/modele.json').read_text(encoding='utf-8'))
schema = json.loads((root / 'docs/diagrammes/schema.json').read_text(encoding='utf-8'))
layout = sys.argv[sys.argv.index('--layout') + 1] if '--layout' in sys.argv else 'dot'
out = Path(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv else root / 'docs/mcd-chen/BD70-MCD-CHEN.dot'

ENT, ASSO, ATTR = '#dceaf4', '#fff0cf', '#ffffff'
q = lambda s: json.dumps(s, ensure_ascii=False)


def nullable(key):
    table, _, col = key.partition('.')
    for c in schema.get(table, {}).get('columns', []):
        if c['Field'] == col: return c['Null'] == 'YES'
    return False


def attr_label(table, a):
    key = a['key'] if '.' in a['key'] else f'{table}.{a["key"]}'
    text = a['label'] + (' (facultatif)' if not a.get('id') and nullable(key) and 'facultatif' not in a['label'] else '')
    return f'< <U>{html.escape(text)}</U> >' if a.get('id') else q(text)


# ------------------------------------------------------------------ post-traitement SVG
def postprocess(svg_path):
    """Décale les cardinalités superposées et dessine le soulignement des identifiants."""
    import re, itertools
    import xml.etree.ElementTree as ET
    from PIL import ImageFont
    NS = 'http://www.w3.org/2000/svg'; ET.register_namespace('', NS); ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    tree = ET.parse(svg_path); doc = tree.getroot(); ns = '{' + NS + '}'
    fonts = {}
    def width(text, size):
        size = float(size)
        if size not in fonts: fonts[size] = ImageFont.truetype('arial.ttf', max(1, round(size * 10)))
        return fonts[size].getlength(text) / 10
    shapes = []
    for g in doc.iter(ns + 'g'):
        if g.get('class') != 'node': continue
        for e in g.findall(ns + 'ellipse'):
            cx, cy, rx, ry = (float(e.get(k)) for k in ('cx', 'cy', 'rx', 'ry')); shapes.append((cx - rx, cy - ry, cx + rx, cy + ry))
        for pg in g.findall(ns + 'polygon'):
            pts = list(map(float, re.findall(r'-?\d+\.?\d*', pg.get('points')))); shapes.append((min(pts[0::2]), min(pts[1::2]), max(pts[0::2]), max(pts[1::2])))
    ov = lambda a, b: a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
    def box(t, dy=0):
        x, y, s = float(t.get('x')), float(t.get('y')) + dy, float(t.get('font-size', 13)); w = width(t.text or '', s)
        a = t.get('text-anchor'); x0 = x - w / 2 if a == 'middle' else (x - w if a == 'end' else x)
        return (x0 - 1, y - s * 0.8, x0 + w + 1, y + s * 0.15)
    placed = []; moved = 0
    for g in doc.iter(ns + 'g'):
        if g.get('class') != 'edge': continue
        for t in g.findall(ns + 'text'):
            s = float(t.get('font-size', 13))
            for dy in (0, s * 1.05, -s * 1.05, s * 2.1, -s * 2.1):
                b = box(t, dy)
                if not any(ov(b, p) for p in placed) and not any(ov(b, sh) for sh in shapes):
                    if dy: t.set('y', str(float(t.get('y')) + dy)); moved += 1
                    break
            else:
                b = box(t)
            placed.append(b)
    # Soulignement réel des identifiants (text-decoration est ignoré par plusieurs moteurs PDF).
    underlined = 0
    for g in doc.iter(ns + 'g'):
        for t in list(g.findall(ns + 'text')):
            if t.get('text-decoration') == 'underline':
                b = box(t); y = float(t.get('y')) + 2.2
                ET.SubElement(g, ns + 'line', {'x1': f'{b[0] + 1:.2f}', 'x2': f'{b[2] - 1:.2f}', 'y1': f'{y:.2f}', 'y2': f'{y:.2f}', 'stroke': '#17324d', 'stroke-width': '0.9'})
                underlined += 1
    tree.write(svg_path, encoding='utf-8', xml_declaration=True)
    remaining = sum(ov(a, b) for a, b in itertools.combinations(placed, 2))
    return underlined, moved, remaining


if '--postprocess' in sys.argv:
    print(postprocess(Path(sys.argv[sys.argv.index('--postprocess') + 1]))); sys.exit(0)

# ------------------------------------------------------------------ génération du DOT et rendu
title = ('Entrepôt logistique • Modèle entité-association (notation de Chen)\\n'
         'Rectangle : entité  |  Losange : association  |  Ovale : attribut  |  Souligné : identifiant  |  Ovale relié à un losange : attribut de l’association\\n'
         'Cardinalités min,max lues comme dans le cours : « Client 1 — Possède — 0,N Facture » = un client possède 0 à N factures, une facture appartient à 1 client.\\n'
         'Une sortie de stock référence uniquement son prélèvement ; les autres mouvements portent directement fraction, emplacement et variation (structures exclusives).')
g = ['graph MCD {']
if layout == 'dot':
    g.append(f'graph [rankdir=LR,nodesep=.3,ranksep=1.1,pad=.3,outputorder=edgesfirst,splines=true,labelloc=t,labeljust=l,fontname="Arial",fontsize=22,label="{title}"];')
else:
    g.append(f'graph [layout=fdp,K=.9,sep="+8",overlap=prism,overlap_scaling=-3,splines=true,pad=.3,outputorder=edgesfirst,labelloc=t,labeljust=l,fontname="Arial",fontsize=22,label="{title}"];')
g.append('node [fontname="Arial",fontsize=13,style=filled,color="#425c72",margin="0.06,0.03"]; edge [fontname="Arial",fontsize=13,fontcolor="#17324d",color="#627687",labeldistance=3,labelangle=20,labelfontsize=13];')
for name, e in model['entities'].items():
    label = e['title'] + ('\\n(domaine ENUM)' if not e.get('table') else '')
    g.append(f'{name} [shape=box,label={q(label)},fillcolor="{ENT}",penwidth=1.6];')
    attrs = sorted(e['attrs'], key=lambda a: not a.get('id'))   # identifiant en tête
    for i, a in enumerate(attrs):
        g.append(f'{name}_attr{i} [shape=ellipse,label={attr_label(e.get("table") or name, a)},fillcolor="{ATTR}",fontsize=11,height=.3];')
        g.append(f'{name} -- {name}_attr{i} [len=.6];')
    if '--stack' in sys.argv:
        g.append('{rank=same; ' + name + '; ' + '; '.join(f'{name}_attr{i}' for i in range(len(attrs))) + '}')
for r in model['associations']:
    g.append(f'{r["id"]} [shape=diamond,label={q(r["label"])},fillcolor="{ASSO}",fontsize=12];')
    for i, a in enumerate(r['attrs']):
        g.append(f'{r["id"]}_attr{i} [shape=ellipse,label={q(a["label"])},fillcolor="{ATTR}",fontsize=11,height=.3];')
        g.append(f'{r["id"]} -- {r["id"]}_attr{i} [style=solid,len=.6];')
    # Convention du cours : du côté de a, on écrit la cardinalité de b (et inversement).
    g.append(f'{r["a"]} -- {r["id"]} [taillabel="{r["cb"]}",len=1.2];')
    g.append(f'{r["id"]} -- {r["b"]} [headlabel="{r["ca"]}",len=1.2];')
g.append('}')
out.write_text('\n'.join(g) + '\n', encoding='utf-8')
print(out)
if '--no-render' not in sys.argv:
    import subprocess, shutil
    subprocess.run(['node', str(root / 'scripts/render-dot.cjs'), str(out)], check=True)
    print('SVG : %d identifiants soulignés, %d cardinalités décalées, %d chevauchements restants' % postprocess(out.with_suffix('.svg')))
    if out == root / 'docs/mcd-chen/BD70-MCD-CHEN.dot':
        shutil.copyfile(out.with_suffix('.svg'), root / 'livrables/entite-association/BD70-MCD-CHEN.svg')
