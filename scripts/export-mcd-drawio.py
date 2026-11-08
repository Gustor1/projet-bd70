"""Convertit le MCD Chen (SVG produit par scripts/build-mcd-chen.py) en Draw.io natif et modifiable.

python scripts/export-mcd-drawio.py
Entités : rectangles ; associations : losanges ; attributs : ellipses (identifiant souligné, fontStyle=4).
Les traits sont des connecteurs reliés à leurs formes (ils suivent un déplacement) ; les cardinalités sont des
étiquettes attachées à leur connecteur, placées à la même position que dans le SVG.
Sortie : livrables/entite-association/BD70-MCD-CHEN.drawio
"""
from pathlib import Path
import re, math
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
src = root / 'docs/mcd-chen/BD70-MCD-CHEN.svg'
dst = root / 'livrables/entite-association/BD70-MCD-CHEN.drawio'
NS = '{http://www.w3.org/2000/svg}'
svg = ET.parse(src).getroot()
W, H = (float(v) for v in svg.get('viewBox').split()[2:])
graph = svg.find(NS + 'g')
tx, ty = map(float, re.search(r'translate\(([^)]+)\)', graph.get('transform')).group(1).split())
nums = lambda s: list(map(float, re.findall(r'-?\d+(?:\.\d+)?', s)))

mx = ET.Element('mxfile', host='app.diagrams.net', agent='BD70')
diagram = ET.SubElement(mx, 'diagram', id='mcd-chen', name='MCD (notation de Chen)')
model = ET.SubElement(diagram, 'mxGraphModel', grid='1', gridSize='10', page='1', pageWidth=str(int(W)), pageHeight=str(int(H)), connect='1')
cells = ET.SubElement(model, 'root')
ET.SubElement(cells, 'mxCell', id='0'); ET.SubElement(cells, 'mxCell', id='1', parent='0')
FONT = 'fontFamily=Arial;fontColor=#17324d;'


def vertex(ident, value, style, x, y, w, h, parent='1'):
    c = ET.SubElement(cells, 'mxCell', id=ident, value=value, style=style, vertex='1', parent=parent)
    ET.SubElement(c, 'mxGeometry', x=f'{x:.1f}', y=f'{y:.1f}', width=f'{w:.1f}', height=f'{h:.1f}', attrib={'as': 'geometry'})
    return c


# Titre et légende du graphe.
title = [t.text for t in graph.findall(NS + 'text')]
if title:
    ys = [float(t.get('y')) + ty for t in graph.findall(NS + 'text')]
    vertex('titre', '\n'.join(title), FONT + 'text;align=center;verticalAlign=top;whiteSpace=wrap;fontSize=22;', 20, min(ys) - 25, W - 40, len(title) * 28 + 10)

bounds = {}
for g in graph.findall(NS + 'g'):
    if g.get('class') != 'node': continue
    name = g.findtext(NS + 'title')
    texts = g.findall(NS + 'text')
    label = '\n'.join(t.text or '' for t in texts)
    size = float(texts[0].get('font-size', 13)) if texts else 13
    underline = any(t.get('text-decoration') == 'underline' for t in texts)
    e = g.find(NS + 'ellipse')
    if e is not None:
        cx, cy, rx, ry = (float(e.get(k)) for k in ('cx', 'cy', 'rx', 'ry'))
        x, y, w, h = cx - rx + tx, cy - ry + ty, 2 * rx, 2 * ry
        style = FONT + f'ellipse;whiteSpace=wrap;fillColor=#ffffff;strokeColor=#425c72;fontSize={size:g};' + ('fontStyle=4;' if underline else '')
    else:
        pts = nums(g.find(NS + 'polygon').get('points'))
        xs, ys = pts[0::2], pts[1::2]
        x, y, w, h = min(xs) + tx, min(ys) + ty, max(xs) - min(xs), max(ys) - min(ys)
        if re.fullmatch(r'R\d+', name):
            style = FONT + f'rhombus;whiteSpace=wrap;fillColor=#fff0cf;strokeColor=#425c72;fontSize={size:g};'
        else:
            style = FONT + f'rounded=0;whiteSpace=wrap;fillColor=#dceaf4;strokeColor=#425c72;strokeWidth=1.6;fontSize={size:g};'
    vertex(name, label, style, x, y, w, h)
    bounds[name] = (x, y, w, h)

edges = 0
for i, g in enumerate(graph.findall(NS + 'g')):
    if g.get('class') != 'edge': continue
    a, b = g.findtext(NS + 'title').split('--')
    path = g.find(NS + 'path')
    pts = nums(path.get('d'))
    pairs = [(pts[k] + tx, pts[k + 1] + ty) for k in range(0, len(pts), 2)]
    eid = f'e{i}'
    c = ET.SubElement(cells, 'mxCell', id=eid, style='endArrow=none;html=0;curved=1;strokeColor=#627687;' + FONT + 'fontSize=13;labelBackgroundColor=#ffffff;',
                      edge='1', parent='1', source=a, target=b)
    geo = ET.SubElement(c, 'mxGeometry', relative='1', attrib={'as': 'geometry'})
    inner = pairs[3:-3:3]                     # points de passage de la courbe de Bézier
    if inner:
        arr = ET.SubElement(geo, 'Array', attrib={'as': 'points'})
        for x, y in inner: ET.SubElement(arr, 'mxPoint', x=f'{x:.1f}', y=f'{y:.1f}')
    # Cardinalités : étiquettes enfants du connecteur, positionnées en coordonnées absolues décalées.
    for k, t in enumerate(g.findall(NS + 'text')):
        x, y = float(t.get('x')) + tx, float(t.get('y')) + ty
        lab = ET.SubElement(cells, 'mxCell', id=f'{eid}-c{k}', value=t.text or '', vertex='1', connectable='0', parent='1',
                            style=FONT + 'text;align=center;verticalAlign=middle;fontSize=13;labelBackgroundColor=#ffffff;')
        ET.SubElement(lab, 'mxGeometry', x=f'{x - 18:.1f}', y=f'{y - 12:.1f}', width='36', height='16', attrib={'as': 'geometry'})
    edges += 1

ET.indent(mx)
ET.ElementTree(mx).write(dst, encoding='utf-8', xml_declaration=True)
# Contrôles : identifiants uniques, extrémités des connecteurs existantes.
ids = [c.get('id') for c in cells.findall('mxCell')]
assert len(ids) == len(set(ids))
for c in cells.findall('mxCell'):
    if c.get('edge') == '1': assert c.get('source') in bounds and c.get('target') in bounds, c.get('id')
shapes = {k: sum(1 for c in cells.findall('mxCell') if k in (c.get('style') or '')) for k in ('rhombus', 'ellipse', 'rounded=0')}
print(f'Draw.io : {len(bounds)} formes ({shapes["rounded=0"]} entités, {shapes["rhombus"]} associations, {shapes["ellipse"]} attributs), {edges} connecteurs -> {dst}')
