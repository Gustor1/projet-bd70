CREATE VIEW v_location AS
 SELECT l.*, z.id zone_id, z.name zone_name,z.storage, a.code aisle_code,r.code rack_code,n.code level_code,
 l.width_m*l.depth_m*l.height_m capacity_m3
 FROM location l JOIN rack_level n ON n.id=l.level_id JOIN rack r ON r.id=n.rack_id JOIN aisle a ON a.id=r.aisle_id JOIN zone z ON z.id=a.zone_id;
CREATE VIEW v_balance AS
 SELECT receipt_item_id,location_id,SUM(delta) qty FROM stock_movement GROUP BY receipt_item_id,location_id;
CREATE VIEW v_reserved AS
 SELECT receipt_item_id,location_id,SUM(qty) qty FROM pick WHERE status IN ('planned','confirmed') GROUP BY receipt_item_id,location_id;
CREATE VIEW v_stock AS
 SELECT b.receipt_item_id,b.location_id,b.qty,COALESCE(p.qty,0) reserved_qty,
 CASE WHEN t.blocked=1 OR (t.expires_on IS NOT NULL AND t.expires_on<CURRENT_DATE()) THEN 0 ELSE b.qty-COALESCE(p.qty,0) END available_qty,
 t.id lot_id,t.code lot_code,t.expires_on,t.blocked,a.id article_id,a.sku,a.name article_name,a.owner_id,o.name owner_name,a.storage,
 a.unit_kg,a.width_m*a.depth_m*a.height_m unit_m3,a.units_per_pallet,l.code location_code,l.zone_id,l.zone_name,
 i.pallet_code,c.validated_at received_at
 FROM v_balance b JOIN receipt_item i ON i.id=b.receipt_item_id JOIN lot t ON t.id=i.lot_id JOIN article a ON a.id=t.article_id
 JOIN owner o ON o.id=a.owner_id JOIN v_location l ON l.id=b.location_id JOIN receipt_line cl ON cl.id=i.line_id JOIN receipt c ON c.id=cl.receipt_id
 LEFT JOIN v_reserved p ON p.receipt_item_id=b.receipt_item_id AND p.location_id=b.location_id WHERE b.qty<>0;
CREATE VIEW v_location_usage AS
 SELECT l.id,COALESCE(SUM(s.qty*s.unit_kg),0) used_kg,COALESCE(SUM(s.qty*s.unit_m3),0) used_m3,COALESCE(SUM(s.qty/s.units_per_pallet),0) used_pallets
 FROM location l LEFT JOIN v_stock s ON s.location_id=l.id GROUP BY l.id;
CREATE VIEW v_visit AS
 SELECT v.*,c.id carrier_id,c.name carrier_name,d.name driver_name,ve.plate,
 MAX(CASE WHEN e.state='arrived' THEN e.happened_at END) arrived_at,
 MAX(CASE WHEN e.state='working' THEN e.happened_at END) working_at,
 MAX(CASE WHEN e.state='finished' THEN e.happened_at END) finished_at,
 MAX(CASE WHEN e.state='departed' THEN e.happened_at END) departed_at,
 TIMESTAMPDIFF(SECOND,MAX(CASE WHEN e.state='arrived' THEN e.happened_at END),MAX(CASE WHEN e.state='working' THEN e.happened_at END))/60 wait_minutes,
 TIMESTAMPDIFF(SECOND,MAX(CASE WHEN e.state='arrived' THEN e.happened_at END),MAX(CASE WHEN e.state='departed' THEN e.happened_at END))/60 immobilized_minutes
 FROM truck_visit v JOIN driver d ON d.id=v.driver_id JOIN vehicle ve ON ve.id=v.vehicle_id JOIN carrier c ON c.id=ve.carrier_id LEFT JOIN visit_event e ON e.visit_id=v.id GROUP BY v.id;
CREATE VIEW v_receipt_discrepancy AS
 SELECT rl.id,rl.receipt_id,rl.expected_qty,COALESCE(SUM(i.accepted_qty+i.damaged_qty),0) received_qty,COALESCE(SUM(i.damaged_qty),0) damaged_qty,
 GREATEST(rl.expected_qty-COALESCE(SUM(i.accepted_qty+i.damaged_qty),0),0) missing_qty,
 GREATEST(COALESCE(SUM(i.accepted_qty+i.damaged_qty),0)-rl.expected_qty,0) excess_qty
 FROM receipt_line rl LEFT JOIN receipt_item i ON i.line_id=rl.id GROUP BY rl.id;
