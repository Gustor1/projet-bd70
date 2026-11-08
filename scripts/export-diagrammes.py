"""Publie chaque diagramme dans les trois formats du rendu : SVG vectoriel, PDF vectoriel et Draw.io.

python scripts/export-diagrammes.py
- Use case : le SVG est produit par scripts/build-usecase.py et seulement vérifiés ici.
- MCD et MLD : les SVG générés par viz.js sont copiés à côté de leur PDF et de leur Draw.io.
Aucun contenu de diagramme n'est modifié. Le script échoue si un SVG contient une image raster.
"""
from pathlib import Path
import shutil, json, sys
import fitz

root = Path(__file__).resolve().parents[1]
out = []
# Use case : SVG natifs écrits par scripts/build-usecase.py ; ici seulement vérifiés.
out.append(root / 'livrables/use-case/UML-CAS-UTILISATION-BD70-CORRIGE.svg')
for source, target in [
    ('docs/mcd-chen/BD70-MCD-CHEN.svg', 'livrables/entite-association/BD70-MCD-CHEN.svg'),
    ('docs/diagrammes/mld-complet.svg', 'livrables/schema-relationnel/mld-complet.svg'),
]:
    shutil.copyfile(root / source, root / target)
    out.append(root / target)
report = []
for f in out:
    text = f.read_text(encoding='utf-8')
    report.append({'file': str(f.relative_to(root)).replace('\\', '/'), 'raster_images': text.count('<image'), 'text_elements': text.count('<text'), 'bytes': f.stat().st_size})
print(json.dumps(report, ensure_ascii=False, indent=1))
if any(r['raster_images'] or not r['text_elements'] for r in report):
    sys.exit('Diagramme non vectoriel ou sans texte.')
