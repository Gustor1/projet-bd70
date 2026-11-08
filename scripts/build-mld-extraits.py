"""Extraits lisibles du schéma relationnel, par domaine, pour le rapport.

python scripts/build-mld-extraits.py
Réutilise la fonction mld() de scripts/diagrams.py (métadonnées réelles de docs/diagrammes/schema.json) :
colonnes, types, PK, FK, NULL/NN et UNIQUE identiques au MLD complet. Les tables référencées hors
extrait apparaissent en pointillés. Sorties vectorielles : docs/diagrammes/extraits/*.dot et *.svg.
"""
from pathlib import Path
import importlib.util, subprocess

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('diagrams', root / 'scripts/diagrams.py')
diagrams = importlib.util.module_from_spec(spec)
import os
os.chdir(root)
spec.loader.exec_module(diagrams)
DOMAINS = {
    'mld-1-transport-quais': ['carrier', 'carrier_contact', 'carrier_contract', 'driver', 'qualification', 'driver_qualification', 'vehicle', 'equipment', 'vehicle_equipment', 'dock', 'dock_equipment', 'dock_vehicle_type', 'dock_downtime', 'appointment', 'appointment_archive', 'truck_visit', 'visit_event'],
    'mld-2-reception-stock': ['supplier', 'supplier_notice', 'notice_line', 'receipt', 'receipt_line', 'receipt_item', 'receipt_reserve', 'lot', 'article', 'owner', 'zone', 'aisle', 'rack', 'rack_level', 'location', 'stock_movement'],
    'mld-3-commandes-comptes': ['customer_order', 'order_line', 'pick', 'package', 'package_pick', 'shipment', 'user_account', 'audit_log', 'site_lock'],
}
out = root / 'docs/diagrammes/extraits'
out.mkdir(exist_ok=True)
for slug, tables in DOMAINS.items():
    (out / f'{slug}.dot').write_text(diagrams.mld(tables), encoding='utf-8')
covered = set().union(*DOMAINS.values())
missing = set(diagrams.model) - covered
assert not missing, f'Tables absentes des extraits : {missing}'
subprocess.run(['node', str(root / 'scripts/render-dot.cjs'), *[str(out / f'{s}.dot') for s in DOMAINS]], check=True)
