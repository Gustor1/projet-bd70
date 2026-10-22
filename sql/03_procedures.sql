-- Appelées dans une transaction PHP ; aucun START/COMMIT implicite.
DELIMITER $$
CREATE PROCEDURE lock_site()
SQL SECURITY DEFINER
BEGIN
 SELECT id FROM site_lock WHERE id=1 FOR UPDATE;
END$$
CREATE PROCEDURE trace_lot(IN p_lot INT, IN p_offset INT)
SQL SECURITY DEFINER
BEGIN
 SELECT m.operation_ref,m.kind,m.delta,m.created_at,l.code emplacement,c.reference reception,i.pallet_code,
 o.reference commande,s.reference expedition,v.reference passage,ve.plate camion
 FROM stock_movement m JOIN receipt_item i ON i.id=m.receipt_item_id JOIN receipt_line rl ON rl.id=i.line_id
 JOIN receipt c ON c.id=rl.receipt_id JOIN location l ON l.id=m.location_id
 LEFT JOIN pick p ON p.id=m.pick_id LEFT JOIN order_line ol ON ol.id=p.order_line_id LEFT JOIN customer_order o ON o.id=ol.order_id
 LEFT JOIN shipment s ON s.order_id=o.id LEFT JOIN truck_visit v ON v.id=s.visit_id LEFT JOIN vehicle ve ON ve.id=v.vehicle_id
 WHERE i.lot_id=p_lot ORDER BY m.created_at,m.id LIMIT 20 OFFSET p_offset;
END$$
DELIMITER ;
