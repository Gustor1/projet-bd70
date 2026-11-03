"""Rapport depuis Markdown et recueil vectoriel ; contrôle pypdf, rendu Poppler séparé."""
from pathlib import Path
import sys,re,html,json
local=Path('.local/pdf-dependencies')
if local.exists():sys.path.insert(0,str(local.resolve()))
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Image,KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
from pypdf import PdfReader, PdfWriter
from PIL import Image as PILImage
out=Path('livrables/rapport');proof=Path('livrables/preuves')
for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf'),('Arial-Italic','ariali.ttf')]:pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic',boldItalic='Arial-Bold')
navy=colors.HexColor('#17324d');teal=colors.HexColor('#137c82');styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Body',fontName='Arial',fontSize=10,leading=14,spaceAfter=8,textColor=navy))
styles.add(ParagraphStyle(name='Section',parent=styles['Body'],fontName='Arial-Bold',fontSize=17,leading=21,spaceBefore=17,spaceAfter=12,keepWithNext=True,textColor=teal))
styles.add(ParagraphStyle(name='Cell',parent=styles['Body'],fontSize=8.5,leading=11,spaceAfter=0))
styles.add(ParagraphStyle(name='Cover',parent=styles['Section'],fontSize=30,leading=36))
styles.add(ParagraphStyle(name='CoverSubtitle',parent=styles['Section']))
def markup(s):
 s=html.escape(s).replace(' → ',' &rarr; ')
 s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s);s=re.sub(r'`([^`]+)`',r'\1',s)
 return s
def paragraph(s,style='Body'):return Paragraph(markup(s),styles[style])
class Report(SimpleDocTemplate):
 def afterFlowable(self,flow):
  if isinstance(flow,Paragraph) and flow.style.name=='Section':
   title=flow.getPlainText();key='s-'+str(self.seq.nextf('section'));self.canv.bookmarkPage(key);self.canv.addOutlineEntry(title,key,0)
   self.notify('TOCEntry',(0,title,self.page,key))
def footer(c,doc):
 c.saveState();w,h=A4;c.setStrokeColor(colors.HexColor('#d8e3ed'));c.line(42,39,w-42,39);c.setFont('Arial',8);c.setFillColor(navy);c.drawString(42,26,'TRANSIT  /  BD70 A26  /  Données fictives');c.drawRightString(w-42,26,str(doc.page));c.restoreState()
source=(out/'RAPPORT-PROJET-BD70.md').read_text(encoding='utf-8');lines=source.splitlines();story=[]
first_section=next(i for i,l in enumerate(lines) if l.startswith('## '))
story += [Spacer(1,75),paragraph('TRANSIT','Cover'),paragraph('Gestion d’un entrepôt logistique','CoverSubtitle'),Spacer(1,25)]
for l in lines[1:first_section]:
 if l.strip():story.append(paragraph(l))
story += [Spacer(1,35),paragraph('Conception, fonctionnalités, données et vérification'),paragraph('Rapport final actualisé le 3 novembre 2026 après application du retour enseignant sur les cas d’utilisation.'),PageBreak(),paragraph('Table des matières','Cover'),Spacer(1,15)]
toc=TableOfContents();toc.levelStyles=[ParagraphStyle(name='toc',fontName='Arial',fontSize=10,leading=14,spaceBefore=4)];story += [toc,PageBreak()]
i=first_section
while i<len(lines):
 line=lines[i].strip()
 if not line:i+=1;continue
 if line.startswith('## '):story.append(paragraph(line[3:],'Section'));i+=1;continue
 if line.startswith('|'):
  rows=[]
  while i<len(lines) and (not lines[i].strip() or lines[i].strip().startswith('|')):
   row=lines[i].strip();i+=1
   if not row or re.fullmatch(r'[|:\- ]+',row):continue
   rows.append([paragraph(c.strip(),'Cell') for c in row.strip('|').split('|')])
  count=len(rows[0]);width=A4[0]-84
  widths=([width*.73,width*.27] if count==2 else ([width*.36,width*.12,width*.12,width*.40] if count==4 else [width/count]*count))
  table=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT');table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4eef5')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f8fb')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.5,navy)]));story += [table,Spacer(1,10)];continue
 story.append(paragraph(line));i+=1
# Two genuine browser captures, cropped only for legibility in the report.
story += [PageBreak(),paragraph('Écrans de la version livrée','Section')]
for name,caption in [('parcours-reception.png','Réception avec avarie validée par le magasinier pendant le parcours navigateur de la version corrigée.'),('corrections-portail.png','Portail transporteur : ressources et rendez-vous limités à la société du compte connecté.')]:
 image=PILImage.open(proof/'corrections-rendu-2026-11-03'/name);target=Path('.local')/('rapport-'+name);image.save(target)
 w=A4[0]-84;story += [KeepTogether([paragraph(caption),Image(str(target),width=w,height=w*image.height/image.width),Spacer(1,18)])]
doc=Report(str(out/'RAPPORT-PROJET-BD70.pdf'),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=53,title='Transit - Rapport de projet BD70',author='ELIOTT LE, SEMIH TASKIN, Thomas VUILLIN')
doc.multiBuild(story,onFirstPage=footer,onLaterPages=footer)
dc=canvas.Canvas(str(Path('.local')/'mld-courant.pdf'));dc.setTitle('BD70 - UML, MCD et MLD');dc.setAuthor('ELIOTT LE, SEMIH TASKIN, Thomas VUILLIN')
for file in sorted(Path('docs/diagrammes').glob('mld-*.svg')):
 drawing=svg2rlg(str(file));w,h=drawing.width,drawing.height;dc.setPageSize((w+60,h+100));dc.setFont('Arial-Bold',15);dc.setFillColor(navy);dc.drawString(30,h+70,file.stem);dc.setFont('Arial',10);dc.drawString(30,h+50,'Vectoriel à taille native : lire avec zoom. Source DOT modifiable dans docs/diagrammes/.');renderPDF.draw(drawing,dc,30,25);dc.showPage()
dc.save()
writer=PdfWriter()
for path in [Path('livrables/correction-prof-use-case/UML-CAS-UTILISATION-BD70-CORRIGE.pdf'),Path('livrables/mcd-final/BD70-MCD-FINAL.pdf'),Path('.local/mld-courant.pdf')]:
 writer.append(path)
writer.add_metadata({'/Title':'BD70 - UML corrigé, dernier MCD et MLD courant','/Author':'ELIOTT LE, SEMIH TASKIN, Thomas VUILLIN'})
with (out/'DIAGRAMMES-BD70.pdf').open('wb') as f:writer.write(f)
files=[]
for name in ['RAPPORT-PROJET-BD70.pdf','DIAGRAMMES-BD70.pdf']:
 reader=PdfReader(out/name);assert len(reader.pages)>0
 files.append({'file':str(out/name),'pages':len(reader.pages),'all_pages_have_text':all(bool(p.extract_text().strip()) for p in reader.pages)})
assert 'ELIOTT LE' in PdfReader(out/'RAPPORT-PROJET-BD70.pdf').pages[0].extract_text()
(proof/'verification-pdf.json').write_text(json.dumps({'files':files,'authors_present':True,'visual_review':'Rendus Poppler à inspecter séparément'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(files,ensure_ascii=False))
