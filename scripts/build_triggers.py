"""Produit le SQL explicite livré ; ne nécessite pas le moteur pour la génération."""
from pathlib import Path
import re
schema=Path('sql/01_schema.sql').read_text(encoding='utf-8')
tables=re.findall(r'CREATE TABLE (\w+)',schema)
parts=['-- Journal automatique sans mot de passe ni valeur sensible.\nDELIMITER $$']
for table in tables:
 if table in ('audit_log','site_lock'): continue
 for event in ('INSERT','UPDATE','DELETE'):
  if table in ('stock_movement','visit_event','shipment','receipt_reserve') and event!='INSERT': continue
  ref='OLD' if event=='DELETE' else 'NEW'
  definition=re.search(r'CREATE TABLE '+table+r'\s*\((.*?)\) ENGINE=',schema,re.S).group(1)
  columns=re.findall(r'(?:^|,)\s*(\w+)\s+(?:INT|BIGINT|VARCHAR|TEXT|DATETIME|DATE|ENUM|BOOLEAN|DECIMAL)\b',definition,re.M)
  columns=[c for c in columns if c!='password_hash']
  def obj(prefix):return 'JSON_OBJECT('+','.join("'"+c+"',"+prefix+'.`'+c+'`' for c in columns)+')'
  detail="JSON_OBJECT('avant',"+(obj('OLD') if event!='INSERT' else 'NULL')+",'apres',"+(obj('NEW') if event!='DELETE' else 'NULL')+")"
  parts.append(f"CREATE TRIGGER audit_{table}_{event.lower()} AFTER {event} ON {table} FOR EACH ROW\nBEGIN\n INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('{table}',{ref}.id,'{event}',@actor_id,{detail});\nEND$$")
for table in ('stock_movement','visit_event','shipment','audit_log','receipt_reserve'):
 for event in ('UPDATE','DELETE'):
  parts.append(f"CREATE TRIGGER immutable_{table}_{event.lower()} BEFORE {event} ON {table} FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$")
parts.append("""CREATE TRIGGER normalize_shipment BEFORE INSERT ON stock_movement FOR EACH ROW
BEGIN
 IF NEW.kind='shipment' THEN
  IF (NEW.receipt_item_id IS NOT NULL AND NEW.receipt_item_id<>(SELECT receipt_item_id FROM pick WHERE id=NEW.pick_id)) OR
     (NEW.location_id IS NOT NULL AND NEW.location_id<>(SELECT location_id FROM pick WHERE id=NEW.pick_id)) OR
     (NEW.delta IS NOT NULL AND NEW.delta<>-(SELECT qty FROM pick WHERE id=NEW.pick_id)) THEN
   SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Sortie incoherente avec le prelevement';
  END IF;
  SET NEW.receipt_item_id=NULL, NEW.location_id=NULL, NEW.delta=NULL;
 END IF;
END$$""")
parts.append('DELIMITER ;\n')
Path('sql/04_triggers.sql').write_text('\n'.join(parts),encoding='utf-8')
