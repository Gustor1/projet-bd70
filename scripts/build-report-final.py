"""Rapport PDF depuis Markdown, figures vectorielles et recueil de diagrammes.

Lancer avec le Python des dépendances PDF (reportlab, svglib, pypdf dans .local/pdf-dependencies) :
  python scripts/build-report-final.py
Syntaxe Markdown prise en charge : ## section, paragraphes, **gras**, listes « - », tableaux, et
  ![Légende](chemin.svg|png){paysage}  -> figure (SVG en vectoriel), {paysage} = page A4 paysage dédiée.
Marqueurs remplacés depuis les sources réelles :
  {{SCHEMA_RELATIONNEL}} -> docs/diagrammes/schema.json (notation textuelle du schéma relationnel)
  {{PERFORMANCES}}, {{INDEX_AVANT}}, {{INDEX_APRES}} -> docs/preuves/performances*.json
  {{OPTIMISATION}}, {{INDEX_GAIN}}, {{ECRITURE_AVANT/APRES}} -> docs/preuves/performances-optimisation.json (avant/après, gain absolu et relatif)
"""
from pathlib import Path
import sys, re, html, json
local = Path('.local/pdf-dependencies')
if local.exists(): sys.path.insert(0, str(local.resolve()))
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, KeepTogether, NextPageTemplate, Flowable
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
from pypdf import PdfReader, PdfWriter
from PIL import Image as PILImage

out = Path('livrables/rapport'); proof = Path('docs/preuves')
AUTHORS = 'Eliott LE, Semih TASKIN, Thomas VUILLIN'
for name, file in [('Arial', 'arial.ttf'), ('Arial-Bold', 'arialbd.ttf'), ('Arial-Italic', 'ariali.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/' + file))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial-Italic', boldItalic='Arial-Bold')
navy = colors.HexColor('#17324d'); teal = colors.HexColor('#137c82'); styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Body', fontName='Arial', fontSize=10, leading=14, spaceAfter=7, textColor=navy))
styles.add(ParagraphStyle(name='Puce', parent=styles['Body'], leftIndent=14, bulletIndent=4, spaceAfter=3))
styles.add(ParagraphStyle(name='Section', parent=styles['Body'], fontName='Arial-Bold', fontSize=17, leading=21, spaceBefore=12, spaceAfter=12, keepWithNext=True, textColor=teal))
styles.add(ParagraphStyle(name='Cell', parent=styles['Body'], fontSize=8.5, leading=11, spaceAfter=0))
styles.add(ParagraphStyle(name='Schema', parent=styles['Body'], fontSize=8, leading=10.5, spaceAfter=3, leftIndent=8))
styles.add(ParagraphStyle(name='Caption', parent=styles['Body'], fontName='Arial-Italic', fontSize=8.5, leading=11, spaceBefore=3, spaceAfter=10, alignment=1))
styles.add(ParagraphStyle(name='Cover', parent=styles['Section'], fontSize=30, leading=36))
styles.add(ParagraphStyle(name='CoverSubtitle', parent=styles['Section']))

def markup(s):
    s = html.escape(s).replace(' → ', ' &rarr; ')
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s); s = re.sub(r'`([^`]+)`', r'\1', s)
    return s
def paragraph(s, style='Body'): return Paragraph(markup(s), styles[style])

class Report(BaseDocTemplate):
    def afterFlowable(self, flow):
        if isinstance(flow, Paragraph) and flow.style.name == 'Section':
            title = flow.getPlainText(); key = 's-' + str(self.seq.nextf('section'))
            self.canv.bookmarkPage(key); self.canv.addOutlineEntry(title, key, 0)
            self.notify('TOCEntry', (0, title, self.page, key))
def footer(c, doc):
    c.saveState(); w, h = c._pagesize
    c.setStrokeColor(colors.HexColor('#d8e3ed')); c.line(42, 39, w - 42, 39); c.setFont('Arial', 8); c.setFillColor(navy)
    c.drawString(42, 26, 'TRANSIT  /  BD70  /  Données fictives'); c.drawRightString(w - 42, 26, str(doc.page)); c.restoreState()

class Svg(Flowable):
    """Dessin SVG vectoriel mis à l'échelle pour tenir dans le cadre."""
    def __init__(self, path, max_w, max_h):
        super().__init__(); self.d = svg2rlg(str(path)); s = min(max_w / self.d.width, max_h / self.d.height)
        self.s = s; self.width = self.d.width * s; self.height = self.d.height * s
    def draw(self):
        self.canv.saveState(); self.canv.scale(self.s, self.s); renderPDF.draw(self.d, self.canv, 0, 0); self.canv.restoreState()

def figure(path, caption, max_w, max_h):
    p = Path(path)
    if p.suffix == '.svg': f = Svg(p, max_w, max_h)
    else:
        im = PILImage.open(p); s = min(max_w / im.width, max_h / im.height); f = Image(str(p), width=im.width * s, height=im.height * s)
    f.hAlign = 'CENTER'
    return [f, paragraph(caption, 'Caption')]

def schema_relationnel():
    model = json.loads(Path('docs/diagrammes/schema.json').read_text(encoding='utf-8'))
    items = []
    for t in sorted(model):
        v = model[t]; fk = {f['COLUMN_NAME']: f['REFERENCED_TABLE_NAME'] for f in v['foreign']}
        uniq = {i['Column_name'] for i in v['indexes'] if not i['Non_unique'] and i['Key_name'] != 'PRIMARY' and sum(x['Key_name'] == i['Key_name'] for x in v['indexes']) == 1}
        composite = {}
        for i in v['indexes']:
            if not i['Non_unique'] and i['Key_name'] != 'PRIMARY': composite.setdefault(i['Key_name'], []).append(i['Column_name'])
        cols = []
        for c in v['columns']:
            n = html.escape(c['Field'])
            if c['Key'] == 'PRI': n = '<u>' + n + '</u>'
            if c['Field'] in fk: n = '#' + n + ' &rarr; ' + fk[c['Field']]
            if c['Field'] in uniq: n += ' [U]'
            if c['Null'] == 'YES': n += ' [NULL]'
            cols.append(n)
        extra = ''.join(' ; UNIQUE(' + ', '.join(cs) + ')' for cs in composite.values() if len(cs) > 1)
        items.append(Paragraph('<b>' + t + '</b> (' + ', '.join(cols) + ')' + extra, styles['Schema']))
    return items

vol = json.loads((proof / 'performances.json').read_text(encoding='utf-8'))
demo = json.loads((proof / 'performances-demo.json').read_text(encoding='utf-8'))
opti = json.loads((proof / 'performances-optimisation.json').read_text(encoding='utf-8'))
OPTI = [('recherche_stock', 'Recherche de stock'), ('selection_fefo', 'Sélection FEFO'), ('emplacements', 'Emplacements compatibles'),
        ('remplissage_zone', 'Remplissage par zone'), ('stock_libre', 'Contrôle du stock libre (transfert)')]
PERF = [('disponibilite_quai', 'Disponibilité d’un quai'), ('recherche_passages', 'Recherche de passages'), ('recherche_stock', 'Recherche de stock'),
        ('emplacements', 'Emplacements compatibles'), ('historique_lot', 'Historique d’un lot'), ('selection_fefo', 'Sélection FEFO'),
        ('statistiques_transporteur', 'Statistiques par transporteur (GROUP BY)'), ('transporteurs_lents', 'Transporteurs au-dessus du seuil (HAVING)'),
        ('historique_rendez_vous', 'Rendez-vous courants et historisés (UNION ALL)'), ('remplissage_zone', 'Remplissage par zone')]
fr = lambda x: f'{x:.2f}'.replace('.', ',')

def table(rows, total_w, widths=None):
    count = len(rows[0])
    if widths is None:
        # Largeur proportionnelle à la longueur moyenne du texte de chaque colonne (minimum lisible).
        avg = [max(10, sum(len(r[c].getPlainText()) for r in rows) / len(rows)) for c in range(count)]
        widths = [a / sum(avg) for a in avg]
        widths = [max(w, .18) for w in widths]; widths = [w / sum(widths) for w in widths]
    t = Table(rows, colWidths=[total_w * w for w in widths], repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e4eef5')), ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f8fb')]),
                           ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6), ('TOPPADDING', (0, 0), (-1, -1), 5),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 5), ('LINEBELOW', (0, 0), (-1, 0), .5, navy)]))
    return t

PW, PH = A4; LW, LH = landscape(A4); M = 42
portrait_w = PW - 2 * M; portrait_h = PH - M - 53
land_w = LW - 2 * M; land_h = LH - M - 53
source = (out / 'RAPPORT-PROJET-BD70.md').read_text(encoding='utf-8-sig')
source = source.replace('{{INDEX_AVANT}}', fr(vol['comparison']['before']['median_ms'])).replace('{{INDEX_APRES}}', fr(vol['comparison']['after']['median_ms']))
_b, _a = vol['comparison']['before']['median_ms'], vol['comparison']['after']['median_ms']
source = source.replace('{{INDEX_GAIN}}', f'gain absolu {fr(_b - _a)} ms, gain relatif {100 * (_b - _a) / _b:.0f} %')
source = source.replace('{{ECRITURE_AVANT}}', fr(opti['mesures']['ecriture_mouvement']['avant_ms'])).replace('{{ECRITURE_APRES}}', fr(opti['mesures']['ecriture_mouvement']['apres_ms']))
lines = source.splitlines(); story = []
first_section = next(i for i, l in enumerate(lines) if l.startswith('## '))
story += [Spacer(1, 75), paragraph('TRANSIT', 'Cover'), paragraph('Gestion d’un entrepôt logistique', 'CoverSubtitle'), Spacer(1, 25)]
for l in lines[1:first_section]:
    if l.strip(): story.append(paragraph(l))
story += [PageBreak(), paragraph('Table des matières', 'Cover'), Spacer(1, 15)]
toc = TableOfContents(); toc.levelStyles = [ParagraphStyle(name='toc', fontName='Arial', fontSize=10, leading=14, spaceBefore=4)]
story += [toc, PageBreak()]
i = first_section; first = True; figures = 0; in_land = False
while i < len(lines):
    line = lines[i].strip()
    if not line: i += 1; continue
    m = re.fullmatch(r'!\[(.+?)\]\((.+?)\)(\{paysage\})?', line)
    land_fig = bool(m and m.group(3))
    if in_land and not land_fig:
        # Retour au portrait : sauf début de section (qui ajoute déjà son saut de page).
        story.append(NextPageTemplate('portrait'))
        if not line.startswith('## '): story.append(PageBreak())
        in_land = False
    if line.startswith('## '):
        if not first: story.append(PageBreak())
        first = False; story.append(paragraph(line[3:], 'Section')); i += 1; continue
    if m:
        figures += 1
        if land_fig:
            story += ([PageBreak()] if in_land else [NextPageTemplate('paysage'), PageBreak()]) + figure(m.group(2), m.group(1), land_w, land_h - 30)
            in_land = True
        else:
            story.append(KeepTogether(figure(m.group(2), m.group(1), portrait_w * .92, portrait_h * .42)))
        i += 1; continue
    if line == '{{SCHEMA_RELATIONNEL}}': story += schema_relationnel(); i += 1; continue
    if line == '{{OPTIMISATION}}':
        rows = [[paragraph(x, 'Cell') for x in ['Requête', 'Avant (ms)', 'Après (ms)', 'Gain absolu (ms)', 'Gain relatif']]]
        for k, label in OPTI:
            x = opti['mesures'][k]
            rows.append([paragraph(label, 'Cell'), paragraph(fr(x['avant_ms']), 'Cell'), paragraph(fr(x['apres_ms']), 'Cell'),
                         paragraph(fr(x['gain_absolu_ms']), 'Cell'), paragraph(f"{x['gain_relatif_pct']:.0f} %", 'Cell')])
        story += [table(rows, portrait_w, [.40, .15, .15, .16, .14]), Spacer(1, 10)]; i += 1; continue
    if line == '{{PERFORMANCES}}':
        rows = [[paragraph(x, 'Cell') for x in ['Requête', 'Base de 10 000 passages (ms)', 'Jeu de démonstration (ms)']]]
        for k, label in PERF:
            v = vol['queries'].get(k); d = demo['queries'][k]
            rows.append([paragraph(label, 'Cell'), paragraph(fr(v['median_ms']) if v else '—', 'Cell'), paragraph(fr(d['median_ms']), 'Cell')])
        story += [table(rows, portrait_w, [.56, .22, .22]), Spacer(1, 10)]; i += 1; continue
    if line.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].strip().startswith('|'):
            row = lines[i].strip(); i += 1
            if re.fullmatch(r'[|:\- ]+', row): continue
            rows.append([paragraph(c.strip(), 'Cell') for c in row.strip('|').split('|')])
        story += [table(rows, portrait_w), Spacer(1, 10)]; continue
    if line.startswith('- '):
        story.append(Paragraph(markup(line[2:]), styles['Puce'], bulletText='•')); i += 1; continue
    story.append(paragraph(line)); i += 1

doc = Report(str(out / 'RAPPORT-PROJET-BD70.pdf'), pagesize=A4, title='Transit - Rapport de projet BD70', author=AUTHORS)
doc.addPageTemplates([
    PageTemplate(id='portrait', pagesize=A4, frames=[Frame(M, 53, portrait_w, portrait_h, id='p')], onPage=footer),
    PageTemplate(id='paysage', pagesize=landscape(A4), frames=[Frame(M, 53, land_w, land_h, id='l')], onPage=footer),
])
doc.multiBuild(story)

# PDF vectoriels des diagrammes générés (MCD et MLD complets), à partir de leurs SVG.
for src, target in [(Path('docs/mcd-chen/BD70-MCD-CHEN.svg'), Path('livrables/entite-association/BD70-MCD-CHEN.pdf')),
                    (Path('docs/diagrammes/mld-complet.svg'), Path('livrables/schema-relationnel/mld-complet.pdf'))]:
    drawing = svg2rlg(str(src)); w, h = drawing.width, drawing.height
    dc = canvas.Canvas(str(target), pagesize=(w + 60, h + 100)); dc.setTitle('BD70 - ' + src.stem); dc.setAuthor(AUTHORS)
    dc.setFont('Arial-Bold', 15); dc.drawString(30, h + 70, src.stem)
    dc.setFont('Arial', 10); dc.drawString(30, h + 50, 'Diagramme vectoriel à lire avec zoom. Sources modifiables : SVG et Draw.io dans le même dossier.')
    renderPDF.draw(drawing, dc, 30, 25); dc.showPage(); dc.save()
# Extraits par domaine : une page vectorielle chacun.
extraits = Path('livrables/rapport/EXTRAITS-MCD-MLD.pdf'); dc = canvas.Canvas(str(extraits)); dc.setTitle('BD70 - Extraits du MCD et du schéma relationnel'); dc.setAuthor(AUTHORS)
for src in sorted(Path('docs/mcd-chen/extraits').glob('*.svg')) + sorted(Path('docs/diagrammes/extraits').glob('*.svg')):
    drawing = svg2rlg(str(src)); w, h = drawing.width, drawing.height
    dc.setPageSize((w + 60, h + 80)); dc.setFont('Arial-Bold', 15); dc.drawString(30, h + 50, src.stem)
    renderPDF.draw(drawing, dc, 30, 25); dc.showPage()
dc.save()
writer = PdfWriter()
for path in [Path('livrables/use-case/UML-CAS-UTILISATION-BD70-CORRIGE.pdf'), Path('livrables/entite-association/BD70-MCD-CHEN.pdf'), Path('livrables/schema-relationnel/mld-complet.pdf'), extraits]:
    writer.append(path)
writer.add_metadata({'/Title': 'BD70 - Cas d’utilisation, MCD (Chen) et schéma relationnel', '/Author': AUTHORS})
with (out / 'DIAGRAMMES-BD70.pdf').open('wb') as f: writer.write(f)
extraits.unlink()
files = []
for name in ['RAPPORT-PROJET-BD70.pdf', 'DIAGRAMMES-BD70.pdf']:
    reader = PdfReader(out / name); assert len(reader.pages) > 0
    files.append({'file': str(out / name), 'pages': len(reader.pages), 'all_pages_have_text': all(bool(p.extract_text().strip()) for p in reader.pages)})
cover = PdfReader(out / 'RAPPORT-PROJET-BD70.pdf').pages[0].extract_text().upper()
assert all(a in cover for a in ['ELIOTT LE', 'SEMIH TASKIN', 'THOMAS VUILLIN'])
(proof / 'verification-pdf.json').write_text(json.dumps({'files': files, 'figures': figures, 'authors_present': True, 'visual_review': 'Rendus à inspecter séparément'}, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(files, ensure_ascii=False), 'figures:', figures)
