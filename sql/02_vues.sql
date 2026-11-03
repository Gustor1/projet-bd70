CREATE VIEW v_stock_movement AS
 SELECT m.id,m.operation_ref,CASE WHEN m.kind='shipment' THEN p.receipt_item_id ELSE m.receipt_item_id END receipt_item_id,
 CASE WHEN m.kind='shipment' THEN p.location_id ELSE m.location_id END location_id,
 CASE WHEN m.kind='shipment' THEN -p.qty ELSE m.delta END delta,m.kind,m.pick_id,m.reason,m.actor_id,m.created_at
 FROM stock_movement m LEFT JOIN pick p ON p.id=m.pick_id;
CREATE VIEW v_location AS
 SELECT l.*, z.id zone_id, z.name zone_name,z.storage, a.code aisle_code,r.code rack_code,n.code level_code,
 l.width_m*l.depth_m*l.height_m capacity_m3
 FROM location l JOIN rack_level n ON n.id=l.level_id JOIN rack r ON r.id=n.rack_id JOIN aisle a ON a.id=r.aisle_id JOIN zone z ON z.id=a.zone_id;
CREATE VIEW v_balance AS
 SELECT receipt_item_id,location_id,SUM(delta) qty FROM v_stock_movement GROUP BY receipt_item_id,location_id;
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
 SELECT l.id,COALESCE(u.used_kg,0) used_kg,COALESCE(u.used_m3,0) used_m3,COALESCE(u.used_pallets,0) used_pallets
 FROM location l LEFT JOIN (
 SELECT b.location_id,SUM(b.qty*a.unit_kg) used_kg,SUM(b.qty*a.width_m*a.depth_m*a.height_m) used_m3,SUM(b.qty/a.units_per_pallet) used_pallets
 FROM v_balance b JOIN receipt_item i ON i.id=b.receipt_item_id JOIN lot t ON t.id=i.lot_id JOIN article a ON a.id=t.article_id
 GROUP BY b.location_id
 ) u ON u.location_id=l.id;
CREATE VIEW v_visit AS
 SELECT v.*,c.id carrier_id,c.name carrier_name,d.name driver_name,ve.plate,
 ea.happened_at arrived_at,ew.happened_at working_at,ef.happened_at finished_at,ed.happened_at departed_at,
 TIMESTAMPDIFF(SECOND,ea.happened_at,ew.happened_at)/60 wait_minutes,
 TIMESTAMPDIFF(SECOND,ea.happened_at,ed.happened_at)/60 immobilized_minutes
 FROM truck_visit v JOIN driver d ON d.id=v.driver_id JOIN vehicle ve ON ve.id=v.vehicle_id JOIN carrier c ON c.id=ve.carrier_id
 LEFT JOIN visit_event ea ON ea.visit_id=v.id AND ea.state='arrived'
 LEFT JOIN visit_event ew ON ew.visit_id=v.id AND ew.state='working'
 LEFT JOIN visit_event ef ON ef.visit_id=v.id AND ef.state='finished'
 LEFT JOIN visit_event ed ON ed.visit_id=v.id AND ed.state='departed';
CREATE VIEW v_receipt_discrepancy AS
 SELECT rl.id,rl.receipt_id,rl.expected_qty,COALESCE(SUM(i.accepted_qty+i.damaged_qty),0) received_qty,COALESCE(SUM(i.damaged_qty),0) damaged_qty,
 GREATEST(rl.expected_qty-COALESCE(SUM(i.accepted_qty+i.damaged_qty),0),0) missing_qty,
 GREATEST(COALESCE(SUM(i.accepted_qty+i.damaged_qty),0)-rl.expected_qty,0) excess_qty
 FROM receipt_line rl LEFT JOIN receipt_item i ON i.line_id=rl.id GROUP BY rl.id;

CREATE VIEW v_notice_line_progress AS
 SELECT n.*,COALESCE(r.allocated_qty,0) allocated_qty,COALESCE(r.received_qty,0) received_qty,
 COALESCE(r.damaged_qty,0) damaged_qty,GREATEST(n.expected_qty-COALESCE(r.allocated_qty,0),0) remaining_qty
 FROM notice_line n LEFT JOIN (
 SELECT l.notice_line_id,SUM(l.expected_qty) allocated_qty,SUM(d.received_qty) received_qty,SUM(d.damaged_qty) damaged_qty
 FROM receipt_line l JOIN receipt c ON c.id=l.receipt_id JOIN v_receipt_discrepancy d ON d.id=l.id
 WHERE c.status='validated' GROUP BY l.notice_line_id
 ) r ON r.notice_line_id=n.id;
