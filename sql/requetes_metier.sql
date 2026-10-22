-- Requêtes réellement mesurées, paramètres dans performances.json.

-- disponibilite_quai
SELECT reference FROM appointment WHERE dock_id=? AND status='active' AND starts_at<? AND ends_at>?;

-- recherche_passages
SELECT reference,carrier_name,status,arrived_at FROM v_visit WHERE arrived_at>=? AND arrived_at<? AND carrier_id=? AND status=? ORDER BY arrived_at DESC LIMIT 20;

-- recherche_stock
SELECT sku,lot_code,location_code,qty,available_qty FROM v_stock WHERE article_id=? AND owner_id=? AND zone_id=? ORDER BY lot_code,location_code LIMIT 20;

-- emplacements
SELECT l.code,u.used_kg,u.used_pallets FROM v_location l JOIN v_location_usage u ON u.id=l.id JOIN article a ON a.id=? WHERE l.storage=a.storage AND l.width_m>=a.width_m AND l.height_m>=a.height_m AND l.depth_m>=a.depth_m AND u.used_kg+?*a.unit_kg<=l.max_kg AND u.used_m3+?*a.width_m*a.height_m*a.depth_m<=l.capacity_m3 AND u.used_pallets+?/a.units_per_pallet<=l.max_pallets;

-- historique_lot
SELECT m.operation_ref,m.created_at,m.delta,l.code FROM stock_movement m JOIN receipt_item i ON i.id=m.receipt_item_id JOIN location l ON l.id=m.location_id WHERE i.lot_id=? ORDER BY m.created_at,m.id LIMIT 20;

-- selection_fefo
SELECT receipt_item_id,location_id,available_qty,expires_on FROM v_stock WHERE article_id=? AND available_qty>0 AND blocked=0 AND (expires_on IS NULL OR expires_on>=?) ORDER BY expires_on IS NULL,expires_on,received_at,receipt_item_id,location_id LIMIT 20;

-- statistiques_transporteur
SELECT carrier_name,COUNT(*) passages,AVG(wait_minutes),AVG(immobilized_minutes) FROM v_visit WHERE arrived_at>=? AND arrived_at<? GROUP BY carrier_id,carrier_name;

-- remplissage_zone
SELECT l.zone_name,SUM(u.used_kg),SUM(l.max_kg),SUM(u.used_pallets),SUM(l.max_pallets) FROM v_location l JOIN v_location_usage u ON u.id=l.id GROUP BY l.zone_id,l.zone_name;
