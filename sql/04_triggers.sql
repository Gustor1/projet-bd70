-- Journal automatique sans mot de passe ni valeur sensible.
DELIMITER $$
CREATE TRIGGER audit_user_account_insert AFTER INSERT ON user_account FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('user_account',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_user_account_update AFTER UPDATE ON user_account FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('user_account',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_user_account_delete AFTER DELETE ON user_account FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('user_account',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_carrier_insert AFTER INSERT ON carrier FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_carrier_update AFTER UPDATE ON carrier FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_carrier_delete AFTER DELETE ON carrier FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_carrier_contact_insert AFTER INSERT ON carrier_contact FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier_contact',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_carrier_contact_update AFTER UPDATE ON carrier_contact FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier_contact',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_carrier_contact_delete AFTER DELETE ON carrier_contact FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier_contact',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_carrier_contract_insert AFTER INSERT ON carrier_contract FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier_contract',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_carrier_contract_update AFTER UPDATE ON carrier_contract FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier_contract',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_carrier_contract_delete AFTER DELETE ON carrier_contract FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier_contract',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_qualification_insert AFTER INSERT ON qualification FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('qualification',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_qualification_update AFTER UPDATE ON qualification FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('qualification',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_qualification_delete AFTER DELETE ON qualification FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('qualification',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_driver_insert AFTER INSERT ON driver FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('driver',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_driver_update AFTER UPDATE ON driver FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('driver',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_driver_delete AFTER DELETE ON driver FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('driver',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_driver_qualification_insert AFTER INSERT ON driver_qualification FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('driver_qualification',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_driver_qualification_update AFTER UPDATE ON driver_qualification FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('driver_qualification',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_driver_qualification_delete AFTER DELETE ON driver_qualification FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('driver_qualification',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_equipment_insert AFTER INSERT ON equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('equipment',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_equipment_update AFTER UPDATE ON equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('equipment',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_equipment_delete AFTER DELETE ON equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('equipment',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_vehicle_insert AFTER INSERT ON vehicle FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('vehicle',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_vehicle_update AFTER UPDATE ON vehicle FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('vehicle',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_vehicle_delete AFTER DELETE ON vehicle FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('vehicle',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_vehicle_equipment_insert AFTER INSERT ON vehicle_equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('vehicle_equipment',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_vehicle_equipment_update AFTER UPDATE ON vehicle_equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('vehicle_equipment',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_vehicle_equipment_delete AFTER DELETE ON vehicle_equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('vehicle_equipment',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_dock_insert AFTER INSERT ON dock FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_dock_update AFTER UPDATE ON dock FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_dock_delete AFTER DELETE ON dock FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_dock_equipment_insert AFTER INSERT ON dock_equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_equipment',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_dock_equipment_update AFTER UPDATE ON dock_equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_equipment',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_dock_equipment_delete AFTER DELETE ON dock_equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_equipment',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_dock_vehicle_type_insert AFTER INSERT ON dock_vehicle_type FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_vehicle_type',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_dock_vehicle_type_update AFTER UPDATE ON dock_vehicle_type FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_vehicle_type',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_dock_vehicle_type_delete AFTER DELETE ON dock_vehicle_type FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_vehicle_type',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_dock_downtime_insert AFTER INSERT ON dock_downtime FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_downtime',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_dock_downtime_update AFTER UPDATE ON dock_downtime FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_downtime',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_dock_downtime_delete AFTER DELETE ON dock_downtime FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_downtime',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_appointment_insert AFTER INSERT ON appointment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('appointment',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_appointment_update AFTER UPDATE ON appointment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('appointment',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_appointment_delete AFTER DELETE ON appointment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('appointment',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_truck_visit_insert AFTER INSERT ON truck_visit FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('truck_visit',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_truck_visit_update AFTER UPDATE ON truck_visit FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('truck_visit',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_truck_visit_delete AFTER DELETE ON truck_visit FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('truck_visit',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_visit_event_insert AFTER INSERT ON visit_event FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('visit_event',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_owner_insert AFTER INSERT ON owner FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('owner',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_owner_update AFTER UPDATE ON owner FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('owner',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_owner_delete AFTER DELETE ON owner FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('owner',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_supplier_insert AFTER INSERT ON supplier FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('supplier',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_supplier_update AFTER UPDATE ON supplier FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('supplier',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_supplier_delete AFTER DELETE ON supplier FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('supplier',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_article_insert AFTER INSERT ON article FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('article',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_article_update AFTER UPDATE ON article FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('article',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_article_delete AFTER DELETE ON article FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('article',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_zone_insert AFTER INSERT ON zone FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('zone',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_zone_update AFTER UPDATE ON zone FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('zone',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_zone_delete AFTER DELETE ON zone FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('zone',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_aisle_insert AFTER INSERT ON aisle FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('aisle',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_aisle_update AFTER UPDATE ON aisle FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('aisle',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_aisle_delete AFTER DELETE ON aisle FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('aisle',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_rack_insert AFTER INSERT ON rack FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('rack',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_rack_update AFTER UPDATE ON rack FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('rack',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_rack_delete AFTER DELETE ON rack FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('rack',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_rack_level_insert AFTER INSERT ON rack_level FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('rack_level',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_rack_level_update AFTER UPDATE ON rack_level FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('rack_level',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_rack_level_delete AFTER DELETE ON rack_level FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('rack_level',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_location_insert AFTER INSERT ON location FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('location',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_location_update AFTER UPDATE ON location FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('location',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_location_delete AFTER DELETE ON location FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('location',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_lot_insert AFTER INSERT ON lot FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('lot',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_lot_update AFTER UPDATE ON lot FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('lot',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_lot_delete AFTER DELETE ON lot FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('lot',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_supplier_notice_insert AFTER INSERT ON supplier_notice FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('supplier_notice',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_supplier_notice_update AFTER UPDATE ON supplier_notice FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('supplier_notice',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_supplier_notice_delete AFTER DELETE ON supplier_notice FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('supplier_notice',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_notice_line_insert AFTER INSERT ON notice_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('notice_line',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_notice_line_update AFTER UPDATE ON notice_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('notice_line',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_notice_line_delete AFTER DELETE ON notice_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('notice_line',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_receipt_insert AFTER INSERT ON receipt FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_receipt_update AFTER UPDATE ON receipt FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_receipt_delete AFTER DELETE ON receipt FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_receipt_line_insert AFTER INSERT ON receipt_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt_line',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_receipt_line_update AFTER UPDATE ON receipt_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt_line',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_receipt_line_delete AFTER DELETE ON receipt_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt_line',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_receipt_item_insert AFTER INSERT ON receipt_item FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt_item',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_receipt_item_update AFTER UPDATE ON receipt_item FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt_item',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_receipt_item_delete AFTER DELETE ON receipt_item FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt_item',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_customer_order_insert AFTER INSERT ON customer_order FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('customer_order',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_customer_order_update AFTER UPDATE ON customer_order FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('customer_order',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_customer_order_delete AFTER DELETE ON customer_order FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('customer_order',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_order_line_insert AFTER INSERT ON order_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('order_line',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_order_line_update AFTER UPDATE ON order_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('order_line',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_order_line_delete AFTER DELETE ON order_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('order_line',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_pick_insert AFTER INSERT ON pick FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('pick',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_pick_update AFTER UPDATE ON pick FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('pick',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_pick_delete AFTER DELETE ON pick FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('pick',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_package_insert AFTER INSERT ON package FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('package',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_package_update AFTER UPDATE ON package FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('package',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_package_delete AFTER DELETE ON package FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('package',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_package_pick_insert AFTER INSERT ON package_pick FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('package_pick',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_package_pick_update AFTER UPDATE ON package_pick FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('package_pick',NEW.id,'UPDATE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_package_pick_delete AFTER DELETE ON package_pick FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('package_pick',OLD.id,'DELETE',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_shipment_insert AFTER INSERT ON shipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('shipment',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER audit_stock_movement_insert AFTER INSERT ON stock_movement FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('stock_movement',NEW.id,'INSERT',@actor_id,'Modification métier');
END$$
CREATE TRIGGER immutable_stock_movement_update BEFORE UPDATE ON stock_movement FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
CREATE TRIGGER immutable_stock_movement_delete BEFORE DELETE ON stock_movement FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
CREATE TRIGGER immutable_visit_event_update BEFORE UPDATE ON visit_event FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
CREATE TRIGGER immutable_visit_event_delete BEFORE DELETE ON visit_event FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
CREATE TRIGGER immutable_shipment_update BEFORE UPDATE ON shipment FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
CREATE TRIGGER immutable_shipment_delete BEFORE DELETE ON shipment FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
CREATE TRIGGER immutable_audit_log_update BEFORE UPDATE ON audit_log FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
CREATE TRIGGER immutable_audit_log_delete BEFORE DELETE ON audit_log FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
DELIMITER ;
