"""Produit le SQL explicite livré ; ne nécessite pas le moteur pour la génération."""
from pathlib import Path
import re
schema=Path('sql/01_schema.sql').read_text(encoding='utf-8')
tables=re.findall(r'CREATE TABLE (\w+)',schema)
parts=['-- Journal automatique sans mot de passe ni valeur sensible.\nDELIMITER $$']
for table in tables:
 if table in ('audit_log','site_lock'): continue
 for event in ('INSERT','UPDATE','DELETE'):
  if table in ('stock_movement','visit_event','shipment') and event!='INSERT': continue
  ref='OLD' if event=='DELETE' else 'NEW'
  parts.append(f"CREATE TRIGGER audit_{table}_{event.lower()} AFTER {event} ON {table} FOR EACH ROW\nBEGIN\n INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('{table}',{ref}.id,'{event}',@actor_id,'Modification métier');\nEND$$")
for table in ('stock_movement','visit_event','shipment','audit_log'):
 for event in ('UPDATE','DELETE'):
  parts.append(f"CREATE TRIGGER immutable_{table}_{event.lower()} BEFORE {event} ON {table} FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$")
parts.append('DELIMITER ;\n')
Path('sql/04_triggers.sql').write_text('\n'.join(parts),encoding='utf-8')
