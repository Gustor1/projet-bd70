-- Journal automatique sans mot de passe ni valeur sensible.
DELIMITER $$
CREATE TRIGGER audit_user_account_insert AFTER INSERT ON user_account FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('user_account',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'email',NEW.`email`,'name',NEW.`name`,'role',NEW.`role`,'active',NEW.`active`,'created_at',NEW.`created_at`)));
END$$
CREATE TRIGGER audit_user_account_update AFTER UPDATE ON user_account FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('user_account',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'email',OLD.`email`,'name',OLD.`name`,'role',OLD.`role`,'active',OLD.`active`,'created_at',OLD.`created_at`),'apres',JSON_OBJECT('id',NEW.`id`,'email',NEW.`email`,'name',NEW.`name`,'role',NEW.`role`,'active',NEW.`active`,'created_at',NEW.`created_at`)));
END$$
CREATE TRIGGER audit_user_account_delete AFTER DELETE ON user_account FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('user_account',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'email',OLD.`email`,'name',OLD.`name`,'role',OLD.`role`,'active',OLD.`active`,'created_at',OLD.`created_at`),'apres',NULL));
END$$
CREATE TRIGGER audit_carrier_insert AFTER INSERT ON carrier FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'code',NEW.`code`,'name',NEW.`name`,'address',NEW.`address`,'phone',NEW.`phone`,'email',NEW.`email`)));
END$$
CREATE TRIGGER audit_carrier_update AFTER UPDATE ON carrier FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'code',OLD.`code`,'name',OLD.`name`,'address',OLD.`address`,'phone',OLD.`phone`,'email',OLD.`email`),'apres',JSON_OBJECT('id',NEW.`id`,'code',NEW.`code`,'name',NEW.`name`,'address',NEW.`address`,'phone',NEW.`phone`,'email',NEW.`email`)));
END$$
CREATE TRIGGER audit_carrier_delete AFTER DELETE ON carrier FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'code',OLD.`code`,'name',OLD.`name`,'address',OLD.`address`,'phone',OLD.`phone`,'email',OLD.`email`),'apres',NULL));
END$$
CREATE TRIGGER audit_carrier_contact_insert AFTER INSERT ON carrier_contact FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier_contact',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'carrier_id',NEW.`carrier_id`,'name',NEW.`name`,'phone',NEW.`phone`,'email',NEW.`email`)));
END$$
CREATE TRIGGER audit_carrier_contact_update AFTER UPDATE ON carrier_contact FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier_contact',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'carrier_id',OLD.`carrier_id`,'name',OLD.`name`,'phone',OLD.`phone`,'email',OLD.`email`),'apres',JSON_OBJECT('id',NEW.`id`,'carrier_id',NEW.`carrier_id`,'name',NEW.`name`,'phone',NEW.`phone`,'email',NEW.`email`)));
END$$
CREATE TRIGGER audit_carrier_contact_delete AFTER DELETE ON carrier_contact FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier_contact',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'carrier_id',OLD.`carrier_id`,'name',OLD.`name`,'phone',OLD.`phone`,'email',OLD.`email`),'apres',NULL));
END$$
CREATE TRIGGER audit_carrier_contract_insert AFTER INSERT ON carrier_contract FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier_contract',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'carrier_id',NEW.`carrier_id`,'reference',NEW.`reference`,'starts_on',NEW.`starts_on`,'ends_on',NEW.`ends_on`,'terms',NEW.`terms`)));
END$$
CREATE TRIGGER audit_carrier_contract_update AFTER UPDATE ON carrier_contract FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier_contract',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'carrier_id',OLD.`carrier_id`,'reference',OLD.`reference`,'starts_on',OLD.`starts_on`,'ends_on',OLD.`ends_on`,'terms',OLD.`terms`),'apres',JSON_OBJECT('id',NEW.`id`,'carrier_id',NEW.`carrier_id`,'reference',NEW.`reference`,'starts_on',NEW.`starts_on`,'ends_on',NEW.`ends_on`,'terms',NEW.`terms`)));
END$$
CREATE TRIGGER audit_carrier_contract_delete AFTER DELETE ON carrier_contract FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('carrier_contract',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'carrier_id',OLD.`carrier_id`,'reference',OLD.`reference`,'starts_on',OLD.`starts_on`,'ends_on',OLD.`ends_on`,'terms',OLD.`terms`),'apres',NULL));
END$$
CREATE TRIGGER audit_qualification_insert AFTER INSERT ON qualification FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('qualification',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'code',NEW.`code`,'name',NEW.`name`)));
END$$
CREATE TRIGGER audit_qualification_update AFTER UPDATE ON qualification FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('qualification',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'code',OLD.`code`,'name',OLD.`name`),'apres',JSON_OBJECT('id',NEW.`id`,'code',NEW.`code`,'name',NEW.`name`)));
END$$
CREATE TRIGGER audit_qualification_delete AFTER DELETE ON qualification FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('qualification',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'code',OLD.`code`,'name',OLD.`name`),'apres',NULL));
END$$
CREATE TRIGGER audit_driver_insert AFTER INSERT ON driver FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('driver',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'carrier_id',NEW.`carrier_id`,'name',NEW.`name`,'phone',NEW.`phone`,'license_number',NEW.`license_number`)));
END$$
CREATE TRIGGER audit_driver_update AFTER UPDATE ON driver FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('driver',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'carrier_id',OLD.`carrier_id`,'name',OLD.`name`,'phone',OLD.`phone`,'license_number',OLD.`license_number`),'apres',JSON_OBJECT('id',NEW.`id`,'carrier_id',NEW.`carrier_id`,'name',NEW.`name`,'phone',NEW.`phone`,'license_number',NEW.`license_number`)));
END$$
CREATE TRIGGER audit_driver_delete AFTER DELETE ON driver FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('driver',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'carrier_id',OLD.`carrier_id`,'name',OLD.`name`,'phone',OLD.`phone`,'license_number',OLD.`license_number`),'apres',NULL));
END$$
CREATE TRIGGER audit_driver_qualification_insert AFTER INSERT ON driver_qualification FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('driver_qualification',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'driver_id',NEW.`driver_id`,'qualification_id',NEW.`qualification_id`,'expires_on',NEW.`expires_on`)));
END$$
CREATE TRIGGER audit_driver_qualification_update AFTER UPDATE ON driver_qualification FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('driver_qualification',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'driver_id',OLD.`driver_id`,'qualification_id',OLD.`qualification_id`,'expires_on',OLD.`expires_on`),'apres',JSON_OBJECT('id',NEW.`id`,'driver_id',NEW.`driver_id`,'qualification_id',NEW.`qualification_id`,'expires_on',NEW.`expires_on`)));
END$$
CREATE TRIGGER audit_driver_qualification_delete AFTER DELETE ON driver_qualification FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('driver_qualification',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'driver_id',OLD.`driver_id`,'qualification_id',OLD.`qualification_id`,'expires_on',OLD.`expires_on`),'apres',NULL));
END$$
CREATE TRIGGER audit_equipment_insert AFTER INSERT ON equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('equipment',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'code',NEW.`code`,'name',NEW.`name`)));
END$$
CREATE TRIGGER audit_equipment_update AFTER UPDATE ON equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('equipment',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'code',OLD.`code`,'name',OLD.`name`),'apres',JSON_OBJECT('id',NEW.`id`,'code',NEW.`code`,'name',NEW.`name`)));
END$$
CREATE TRIGGER audit_equipment_delete AFTER DELETE ON equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('equipment',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'code',OLD.`code`,'name',OLD.`name`),'apres',NULL));
END$$
CREATE TRIGGER audit_vehicle_insert AFTER INSERT ON vehicle FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('vehicle',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'carrier_id',NEW.`carrier_id`,'plate',NEW.`plate`,'type',NEW.`type`,'max_kg',NEW.`max_kg`,'max_pallets',NEW.`max_pallets`)));
END$$
CREATE TRIGGER audit_vehicle_update AFTER UPDATE ON vehicle FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('vehicle',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'carrier_id',OLD.`carrier_id`,'plate',OLD.`plate`,'type',OLD.`type`,'max_kg',OLD.`max_kg`,'max_pallets',OLD.`max_pallets`),'apres',JSON_OBJECT('id',NEW.`id`,'carrier_id',NEW.`carrier_id`,'plate',NEW.`plate`,'type',NEW.`type`,'max_kg',NEW.`max_kg`,'max_pallets',NEW.`max_pallets`)));
END$$
CREATE TRIGGER audit_vehicle_delete AFTER DELETE ON vehicle FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('vehicle',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'carrier_id',OLD.`carrier_id`,'plate',OLD.`plate`,'type',OLD.`type`,'max_kg',OLD.`max_kg`,'max_pallets',OLD.`max_pallets`),'apres',NULL));
END$$
CREATE TRIGGER audit_vehicle_equipment_insert AFTER INSERT ON vehicle_equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('vehicle_equipment',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'vehicle_id',NEW.`vehicle_id`,'equipment_id',NEW.`equipment_id`)));
END$$
CREATE TRIGGER audit_vehicle_equipment_update AFTER UPDATE ON vehicle_equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('vehicle_equipment',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'vehicle_id',OLD.`vehicle_id`,'equipment_id',OLD.`equipment_id`),'apres',JSON_OBJECT('id',NEW.`id`,'vehicle_id',NEW.`vehicle_id`,'equipment_id',NEW.`equipment_id`)));
END$$
CREATE TRIGGER audit_vehicle_equipment_delete AFTER DELETE ON vehicle_equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('vehicle_equipment',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'vehicle_id',OLD.`vehicle_id`,'equipment_id',OLD.`equipment_id`),'apres',NULL));
END$$
CREATE TRIGGER audit_dock_insert AFTER INSERT ON dock FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'code',NEW.`code`,'name',NEW.`name`,'type',NEW.`type`)));
END$$
CREATE TRIGGER audit_dock_update AFTER UPDATE ON dock FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'code',OLD.`code`,'name',OLD.`name`,'type',OLD.`type`),'apres',JSON_OBJECT('id',NEW.`id`,'code',NEW.`code`,'name',NEW.`name`,'type',NEW.`type`)));
END$$
CREATE TRIGGER audit_dock_delete AFTER DELETE ON dock FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'code',OLD.`code`,'name',OLD.`name`,'type',OLD.`type`),'apres',NULL));
END$$
CREATE TRIGGER audit_dock_equipment_insert AFTER INSERT ON dock_equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_equipment',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'dock_id',NEW.`dock_id`,'equipment_id',NEW.`equipment_id`)));
END$$
CREATE TRIGGER audit_dock_equipment_update AFTER UPDATE ON dock_equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_equipment',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'dock_id',OLD.`dock_id`,'equipment_id',OLD.`equipment_id`),'apres',JSON_OBJECT('id',NEW.`id`,'dock_id',NEW.`dock_id`,'equipment_id',NEW.`equipment_id`)));
END$$
CREATE TRIGGER audit_dock_equipment_delete AFTER DELETE ON dock_equipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_equipment',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'dock_id',OLD.`dock_id`,'equipment_id',OLD.`equipment_id`),'apres',NULL));
END$$
CREATE TRIGGER audit_dock_vehicle_type_insert AFTER INSERT ON dock_vehicle_type FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_vehicle_type',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'dock_id',NEW.`dock_id`,'vehicle_type',NEW.`vehicle_type`)));
END$$
CREATE TRIGGER audit_dock_vehicle_type_update AFTER UPDATE ON dock_vehicle_type FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_vehicle_type',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'dock_id',OLD.`dock_id`,'vehicle_type',OLD.`vehicle_type`),'apres',JSON_OBJECT('id',NEW.`id`,'dock_id',NEW.`dock_id`,'vehicle_type',NEW.`vehicle_type`)));
END$$
CREATE TRIGGER audit_dock_vehicle_type_delete AFTER DELETE ON dock_vehicle_type FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_vehicle_type',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'dock_id',OLD.`dock_id`,'vehicle_type',OLD.`vehicle_type`),'apres',NULL));
END$$
CREATE TRIGGER audit_dock_downtime_insert AFTER INSERT ON dock_downtime FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_downtime',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'dock_id',NEW.`dock_id`,'starts_at',NEW.`starts_at`,'ends_at',NEW.`ends_at`,'reason',NEW.`reason`)));
END$$
CREATE TRIGGER audit_dock_downtime_update AFTER UPDATE ON dock_downtime FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_downtime',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'dock_id',OLD.`dock_id`,'starts_at',OLD.`starts_at`,'ends_at',OLD.`ends_at`,'reason',OLD.`reason`),'apres',JSON_OBJECT('id',NEW.`id`,'dock_id',NEW.`dock_id`,'starts_at',NEW.`starts_at`,'ends_at',NEW.`ends_at`,'reason',NEW.`reason`)));
END$$
CREATE TRIGGER audit_dock_downtime_delete AFTER DELETE ON dock_downtime FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('dock_downtime',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'dock_id',OLD.`dock_id`,'starts_at',OLD.`starts_at`,'ends_at',OLD.`ends_at`,'reason',OLD.`reason`),'apres',NULL));
END$$
CREATE TRIGGER audit_appointment_insert AFTER INSERT ON appointment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('appointment',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'reference',NEW.`reference`,'dock_id',NEW.`dock_id`,'driver_id',NEW.`driver_id`,'vehicle_id',NEW.`vehicle_id`,'trailer_id',NEW.`trailer_id`,'operation',NEW.`operation`,'starts_at',NEW.`starts_at`,'ends_at',NEW.`ends_at`,'status',NEW.`status`)));
END$$
CREATE TRIGGER audit_appointment_update AFTER UPDATE ON appointment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('appointment',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'reference',OLD.`reference`,'dock_id',OLD.`dock_id`,'driver_id',OLD.`driver_id`,'vehicle_id',OLD.`vehicle_id`,'trailer_id',OLD.`trailer_id`,'operation',OLD.`operation`,'starts_at',OLD.`starts_at`,'ends_at',OLD.`ends_at`,'status',OLD.`status`),'apres',JSON_OBJECT('id',NEW.`id`,'reference',NEW.`reference`,'dock_id',NEW.`dock_id`,'driver_id',NEW.`driver_id`,'vehicle_id',NEW.`vehicle_id`,'trailer_id',NEW.`trailer_id`,'operation',NEW.`operation`,'starts_at',NEW.`starts_at`,'ends_at',NEW.`ends_at`,'status',NEW.`status`)));
END$$
CREATE TRIGGER audit_appointment_delete AFTER DELETE ON appointment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('appointment',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'reference',OLD.`reference`,'dock_id',OLD.`dock_id`,'driver_id',OLD.`driver_id`,'vehicle_id',OLD.`vehicle_id`,'trailer_id',OLD.`trailer_id`,'operation',OLD.`operation`,'starts_at',OLD.`starts_at`,'ends_at',OLD.`ends_at`,'status',OLD.`status`),'apres',NULL));
END$$
CREATE TRIGGER audit_truck_visit_insert AFTER INSERT ON truck_visit FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('truck_visit',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'reference',NEW.`reference`,'appointment_id',NEW.`appointment_id`,'driver_id',NEW.`driver_id`,'vehicle_id',NEW.`vehicle_id`,'trailer_id',NEW.`trailer_id`,'operation',NEW.`operation`,'dock_id',NEW.`dock_id`,'status',NEW.`status`,'document_note',NEW.`document_note`)));
END$$
CREATE TRIGGER audit_truck_visit_update AFTER UPDATE ON truck_visit FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('truck_visit',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'reference',OLD.`reference`,'appointment_id',OLD.`appointment_id`,'driver_id',OLD.`driver_id`,'vehicle_id',OLD.`vehicle_id`,'trailer_id',OLD.`trailer_id`,'operation',OLD.`operation`,'dock_id',OLD.`dock_id`,'status',OLD.`status`,'document_note',OLD.`document_note`),'apres',JSON_OBJECT('id',NEW.`id`,'reference',NEW.`reference`,'appointment_id',NEW.`appointment_id`,'driver_id',NEW.`driver_id`,'vehicle_id',NEW.`vehicle_id`,'trailer_id',NEW.`trailer_id`,'operation',NEW.`operation`,'dock_id',NEW.`dock_id`,'status',NEW.`status`,'document_note',NEW.`document_note`)));
END$$
CREATE TRIGGER audit_truck_visit_delete AFTER DELETE ON truck_visit FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('truck_visit',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'reference',OLD.`reference`,'appointment_id',OLD.`appointment_id`,'driver_id',OLD.`driver_id`,'vehicle_id',OLD.`vehicle_id`,'trailer_id',OLD.`trailer_id`,'operation',OLD.`operation`,'dock_id',OLD.`dock_id`,'status',OLD.`status`,'document_note',OLD.`document_note`),'apres',NULL));
END$$
CREATE TRIGGER audit_visit_event_insert AFTER INSERT ON visit_event FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('visit_event',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'visit_id',NEW.`visit_id`,'state',NEW.`state`,'happened_at',NEW.`happened_at`,'actor_id',NEW.`actor_id`)));
END$$
CREATE TRIGGER audit_owner_insert AFTER INSERT ON owner FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('owner',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'code',NEW.`code`,'name',NEW.`name`,'address',NEW.`address`,'email',NEW.`email`)));
END$$
CREATE TRIGGER audit_owner_update AFTER UPDATE ON owner FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('owner',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'code',OLD.`code`,'name',OLD.`name`,'address',OLD.`address`,'email',OLD.`email`),'apres',JSON_OBJECT('id',NEW.`id`,'code',NEW.`code`,'name',NEW.`name`,'address',NEW.`address`,'email',NEW.`email`)));
END$$
CREATE TRIGGER audit_owner_delete AFTER DELETE ON owner FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('owner',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'code',OLD.`code`,'name',OLD.`name`,'address',OLD.`address`,'email',OLD.`email`),'apres',NULL));
END$$
CREATE TRIGGER audit_supplier_insert AFTER INSERT ON supplier FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('supplier',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'code',NEW.`code`,'name',NEW.`name`,'address',NEW.`address`,'phone',NEW.`phone`)));
END$$
CREATE TRIGGER audit_supplier_update AFTER UPDATE ON supplier FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('supplier',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'code',OLD.`code`,'name',OLD.`name`,'address',OLD.`address`,'phone',OLD.`phone`),'apres',JSON_OBJECT('id',NEW.`id`,'code',NEW.`code`,'name',NEW.`name`,'address',NEW.`address`,'phone',NEW.`phone`)));
END$$
CREATE TRIGGER audit_supplier_delete AFTER DELETE ON supplier FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('supplier',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'code',OLD.`code`,'name',OLD.`name`,'address',OLD.`address`,'phone',OLD.`phone`),'apres',NULL));
END$$
CREATE TRIGGER audit_article_insert AFTER INSERT ON article FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('article',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'owner_id',NEW.`owner_id`,'sku',NEW.`sku`,'name',NEW.`name`,'storage',NEW.`storage`,'packaging',NEW.`packaging`,'width_m',NEW.`width_m`,'depth_m',NEW.`depth_m`,'height_m',NEW.`height_m`,'unit_kg',NEW.`unit_kg`,'units_per_pallet',NEW.`units_per_pallet`)));
END$$
CREATE TRIGGER audit_article_update AFTER UPDATE ON article FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('article',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'owner_id',OLD.`owner_id`,'sku',OLD.`sku`,'name',OLD.`name`,'storage',OLD.`storage`,'packaging',OLD.`packaging`,'width_m',OLD.`width_m`,'depth_m',OLD.`depth_m`,'height_m',OLD.`height_m`,'unit_kg',OLD.`unit_kg`,'units_per_pallet',OLD.`units_per_pallet`),'apres',JSON_OBJECT('id',NEW.`id`,'owner_id',NEW.`owner_id`,'sku',NEW.`sku`,'name',NEW.`name`,'storage',NEW.`storage`,'packaging',NEW.`packaging`,'width_m',NEW.`width_m`,'depth_m',NEW.`depth_m`,'height_m',NEW.`height_m`,'unit_kg',NEW.`unit_kg`,'units_per_pallet',NEW.`units_per_pallet`)));
END$$
CREATE TRIGGER audit_article_delete AFTER DELETE ON article FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('article',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'owner_id',OLD.`owner_id`,'sku',OLD.`sku`,'name',OLD.`name`,'storage',OLD.`storage`,'packaging',OLD.`packaging`,'width_m',OLD.`width_m`,'depth_m',OLD.`depth_m`,'height_m',OLD.`height_m`,'unit_kg',OLD.`unit_kg`,'units_per_pallet',OLD.`units_per_pallet`),'apres',NULL));
END$$
CREATE TRIGGER audit_zone_insert AFTER INSERT ON zone FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('zone',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'code',NEW.`code`,'name',NEW.`name`,'storage',NEW.`storage`)));
END$$
CREATE TRIGGER audit_zone_update AFTER UPDATE ON zone FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('zone',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'code',OLD.`code`,'name',OLD.`name`,'storage',OLD.`storage`),'apres',JSON_OBJECT('id',NEW.`id`,'code',NEW.`code`,'name',NEW.`name`,'storage',NEW.`storage`)));
END$$
CREATE TRIGGER audit_zone_delete AFTER DELETE ON zone FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('zone',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'code',OLD.`code`,'name',OLD.`name`,'storage',OLD.`storage`),'apres',NULL));
END$$
CREATE TRIGGER audit_aisle_insert AFTER INSERT ON aisle FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('aisle',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'zone_id',NEW.`zone_id`,'code',NEW.`code`)));
END$$
CREATE TRIGGER audit_aisle_update AFTER UPDATE ON aisle FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('aisle',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'zone_id',OLD.`zone_id`,'code',OLD.`code`),'apres',JSON_OBJECT('id',NEW.`id`,'zone_id',NEW.`zone_id`,'code',NEW.`code`)));
END$$
CREATE TRIGGER audit_aisle_delete AFTER DELETE ON aisle FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('aisle',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'zone_id',OLD.`zone_id`,'code',OLD.`code`),'apres',NULL));
END$$
CREATE TRIGGER audit_rack_insert AFTER INSERT ON rack FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('rack',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'aisle_id',NEW.`aisle_id`,'code',NEW.`code`)));
END$$
CREATE TRIGGER audit_rack_update AFTER UPDATE ON rack FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('rack',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'aisle_id',OLD.`aisle_id`,'code',OLD.`code`),'apres',JSON_OBJECT('id',NEW.`id`,'aisle_id',NEW.`aisle_id`,'code',NEW.`code`)));
END$$
CREATE TRIGGER audit_rack_delete AFTER DELETE ON rack FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('rack',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'aisle_id',OLD.`aisle_id`,'code',OLD.`code`),'apres',NULL));
END$$
CREATE TRIGGER audit_rack_level_insert AFTER INSERT ON rack_level FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('rack_level',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'rack_id',NEW.`rack_id`,'code',NEW.`code`)));
END$$
CREATE TRIGGER audit_rack_level_update AFTER UPDATE ON rack_level FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('rack_level',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'rack_id',OLD.`rack_id`,'code',OLD.`code`),'apres',JSON_OBJECT('id',NEW.`id`,'rack_id',NEW.`rack_id`,'code',NEW.`code`)));
END$$
CREATE TRIGGER audit_rack_level_delete AFTER DELETE ON rack_level FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('rack_level',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'rack_id',OLD.`rack_id`,'code',OLD.`code`),'apres',NULL));
END$$
CREATE TRIGGER audit_location_insert AFTER INSERT ON location FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('location',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'level_id',NEW.`level_id`,'code',NEW.`code`,'width_m',NEW.`width_m`,'depth_m',NEW.`depth_m`,'height_m',NEW.`height_m`,'max_kg',NEW.`max_kg`,'max_pallets',NEW.`max_pallets`)));
END$$
CREATE TRIGGER audit_location_update AFTER UPDATE ON location FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('location',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'level_id',OLD.`level_id`,'code',OLD.`code`,'width_m',OLD.`width_m`,'depth_m',OLD.`depth_m`,'height_m',OLD.`height_m`,'max_kg',OLD.`max_kg`,'max_pallets',OLD.`max_pallets`),'apres',JSON_OBJECT('id',NEW.`id`,'level_id',NEW.`level_id`,'code',NEW.`code`,'width_m',NEW.`width_m`,'depth_m',NEW.`depth_m`,'height_m',NEW.`height_m`,'max_kg',NEW.`max_kg`,'max_pallets',NEW.`max_pallets`)));
END$$
CREATE TRIGGER audit_location_delete AFTER DELETE ON location FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('location',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'level_id',OLD.`level_id`,'code',OLD.`code`,'width_m',OLD.`width_m`,'depth_m',OLD.`depth_m`,'height_m',OLD.`height_m`,'max_kg',OLD.`max_kg`,'max_pallets',OLD.`max_pallets`),'apres',NULL));
END$$
CREATE TRIGGER audit_lot_insert AFTER INSERT ON lot FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('lot',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'article_id',NEW.`article_id`,'code',NEW.`code`,'expires_on',NEW.`expires_on`,'blocked',NEW.`blocked`,'block_reason',NEW.`block_reason`)));
END$$
CREATE TRIGGER audit_lot_update AFTER UPDATE ON lot FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('lot',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'article_id',OLD.`article_id`,'code',OLD.`code`,'expires_on',OLD.`expires_on`,'blocked',OLD.`blocked`,'block_reason',OLD.`block_reason`),'apres',JSON_OBJECT('id',NEW.`id`,'article_id',NEW.`article_id`,'code',NEW.`code`,'expires_on',NEW.`expires_on`,'blocked',NEW.`blocked`,'block_reason',NEW.`block_reason`)));
END$$
CREATE TRIGGER audit_lot_delete AFTER DELETE ON lot FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('lot',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'article_id',OLD.`article_id`,'code',OLD.`code`,'expires_on',OLD.`expires_on`,'blocked',OLD.`blocked`,'block_reason',OLD.`block_reason`),'apres',NULL));
END$$
CREATE TRIGGER audit_supplier_notice_insert AFTER INSERT ON supplier_notice FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('supplier_notice',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'reference',NEW.`reference`,'supplier_id',NEW.`supplier_id`,'expected_on',NEW.`expected_on`,'closed_at',NEW.`closed_at`,'closed_by',NEW.`closed_by`,'closure_note',NEW.`closure_note`)));
END$$
CREATE TRIGGER audit_supplier_notice_update AFTER UPDATE ON supplier_notice FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('supplier_notice',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'reference',OLD.`reference`,'supplier_id',OLD.`supplier_id`,'expected_on',OLD.`expected_on`,'closed_at',OLD.`closed_at`,'closed_by',OLD.`closed_by`,'closure_note',OLD.`closure_note`),'apres',JSON_OBJECT('id',NEW.`id`,'reference',NEW.`reference`,'supplier_id',NEW.`supplier_id`,'expected_on',NEW.`expected_on`,'closed_at',NEW.`closed_at`,'closed_by',NEW.`closed_by`,'closure_note',NEW.`closure_note`)));
END$$
CREATE TRIGGER audit_supplier_notice_delete AFTER DELETE ON supplier_notice FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('supplier_notice',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'reference',OLD.`reference`,'supplier_id',OLD.`supplier_id`,'expected_on',OLD.`expected_on`,'closed_at',OLD.`closed_at`,'closed_by',OLD.`closed_by`,'closure_note',OLD.`closure_note`),'apres',NULL));
END$$
CREATE TRIGGER audit_notice_line_insert AFTER INSERT ON notice_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('notice_line',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'notice_id',NEW.`notice_id`,'article_id',NEW.`article_id`,'expected_qty',NEW.`expected_qty`)));
END$$
CREATE TRIGGER audit_notice_line_update AFTER UPDATE ON notice_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('notice_line',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'notice_id',OLD.`notice_id`,'article_id',OLD.`article_id`,'expected_qty',OLD.`expected_qty`),'apres',JSON_OBJECT('id',NEW.`id`,'notice_id',NEW.`notice_id`,'article_id',NEW.`article_id`,'expected_qty',NEW.`expected_qty`)));
END$$
CREATE TRIGGER audit_notice_line_delete AFTER DELETE ON notice_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('notice_line',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'notice_id',OLD.`notice_id`,'article_id',OLD.`article_id`,'expected_qty',OLD.`expected_qty`),'apres',NULL));
END$$
CREATE TRIGGER audit_receipt_insert AFTER INSERT ON receipt FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'reference',NEW.`reference`,'notice_id',NEW.`notice_id`,'visit_id',NEW.`visit_id`,'status',NEW.`status`,'validated_at',NEW.`validated_at`)));
END$$
CREATE TRIGGER audit_receipt_update AFTER UPDATE ON receipt FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'reference',OLD.`reference`,'notice_id',OLD.`notice_id`,'visit_id',OLD.`visit_id`,'status',OLD.`status`,'validated_at',OLD.`validated_at`),'apres',JSON_OBJECT('id',NEW.`id`,'reference',NEW.`reference`,'notice_id',NEW.`notice_id`,'visit_id',NEW.`visit_id`,'status',NEW.`status`,'validated_at',NEW.`validated_at`)));
END$$
CREATE TRIGGER audit_receipt_delete AFTER DELETE ON receipt FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'reference',OLD.`reference`,'notice_id',OLD.`notice_id`,'visit_id',OLD.`visit_id`,'status',OLD.`status`,'validated_at',OLD.`validated_at`),'apres',NULL));
END$$
CREATE TRIGGER audit_receipt_line_insert AFTER INSERT ON receipt_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt_line',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'receipt_id',NEW.`receipt_id`,'notice_line_id',NEW.`notice_line_id`,'expected_qty',NEW.`expected_qty`)));
END$$
CREATE TRIGGER audit_receipt_line_update AFTER UPDATE ON receipt_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt_line',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'receipt_id',OLD.`receipt_id`,'notice_line_id',OLD.`notice_line_id`,'expected_qty',OLD.`expected_qty`),'apres',JSON_OBJECT('id',NEW.`id`,'receipt_id',NEW.`receipt_id`,'notice_line_id',NEW.`notice_line_id`,'expected_qty',NEW.`expected_qty`)));
END$$
CREATE TRIGGER audit_receipt_line_delete AFTER DELETE ON receipt_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt_line',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'receipt_id',OLD.`receipt_id`,'notice_line_id',OLD.`notice_line_id`,'expected_qty',OLD.`expected_qty`),'apres',NULL));
END$$
CREATE TRIGGER audit_receipt_item_insert AFTER INSERT ON receipt_item FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt_item',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'line_id',NEW.`line_id`,'lot_id',NEW.`lot_id`,'pallet_code',NEW.`pallet_code`,'accepted_qty',NEW.`accepted_qty`,'damaged_qty',NEW.`damaged_qty`,'pallet_state',NEW.`pallet_state`,'reservation',NEW.`reservation`,'location_id',NEW.`location_id`)));
END$$
CREATE TRIGGER audit_receipt_item_update AFTER UPDATE ON receipt_item FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt_item',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'line_id',OLD.`line_id`,'lot_id',OLD.`lot_id`,'pallet_code',OLD.`pallet_code`,'accepted_qty',OLD.`accepted_qty`,'damaged_qty',OLD.`damaged_qty`,'pallet_state',OLD.`pallet_state`,'reservation',OLD.`reservation`,'location_id',OLD.`location_id`),'apres',JSON_OBJECT('id',NEW.`id`,'line_id',NEW.`line_id`,'lot_id',NEW.`lot_id`,'pallet_code',NEW.`pallet_code`,'accepted_qty',NEW.`accepted_qty`,'damaged_qty',NEW.`damaged_qty`,'pallet_state',NEW.`pallet_state`,'reservation',NEW.`reservation`,'location_id',NEW.`location_id`)));
END$$
CREATE TRIGGER audit_receipt_item_delete AFTER DELETE ON receipt_item FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt_item',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'line_id',OLD.`line_id`,'lot_id',OLD.`lot_id`,'pallet_code',OLD.`pallet_code`,'accepted_qty',OLD.`accepted_qty`,'damaged_qty',OLD.`damaged_qty`,'pallet_state',OLD.`pallet_state`,'reservation',OLD.`reservation`,'location_id',OLD.`location_id`),'apres',NULL));
END$$
CREATE TRIGGER audit_customer_order_insert AFTER INSERT ON customer_order FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('customer_order',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'reference',NEW.`reference`,'owner_id',NEW.`owner_id`,'destination',NEW.`destination`,'revision_note',NEW.`revision_note`,'desired_on',NEW.`desired_on`,'status',NEW.`status`,'preparer_id',NEW.`preparer_id`,'picking_at',NEW.`picking_at`,'ready_at',NEW.`ready_at`)));
END$$
CREATE TRIGGER audit_customer_order_update AFTER UPDATE ON customer_order FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('customer_order',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'reference',OLD.`reference`,'owner_id',OLD.`owner_id`,'destination',OLD.`destination`,'revision_note',OLD.`revision_note`,'desired_on',OLD.`desired_on`,'status',OLD.`status`,'preparer_id',OLD.`preparer_id`,'picking_at',OLD.`picking_at`,'ready_at',OLD.`ready_at`),'apres',JSON_OBJECT('id',NEW.`id`,'reference',NEW.`reference`,'owner_id',NEW.`owner_id`,'destination',NEW.`destination`,'revision_note',NEW.`revision_note`,'desired_on',NEW.`desired_on`,'status',NEW.`status`,'preparer_id',NEW.`preparer_id`,'picking_at',NEW.`picking_at`,'ready_at',NEW.`ready_at`)));
END$$
CREATE TRIGGER audit_customer_order_delete AFTER DELETE ON customer_order FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('customer_order',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'reference',OLD.`reference`,'owner_id',OLD.`owner_id`,'destination',OLD.`destination`,'revision_note',OLD.`revision_note`,'desired_on',OLD.`desired_on`,'status',OLD.`status`,'preparer_id',OLD.`preparer_id`,'picking_at',OLD.`picking_at`,'ready_at',OLD.`ready_at`),'apres',NULL));
END$$
CREATE TRIGGER audit_order_line_insert AFTER INSERT ON order_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('order_line',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'order_id',NEW.`order_id`,'article_id',NEW.`article_id`,'qty',NEW.`qty`)));
END$$
CREATE TRIGGER audit_order_line_update AFTER UPDATE ON order_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('order_line',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'order_id',OLD.`order_id`,'article_id',OLD.`article_id`,'qty',OLD.`qty`),'apres',JSON_OBJECT('id',NEW.`id`,'order_id',NEW.`order_id`,'article_id',NEW.`article_id`,'qty',NEW.`qty`)));
END$$
CREATE TRIGGER audit_order_line_delete AFTER DELETE ON order_line FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('order_line',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'order_id',OLD.`order_id`,'article_id',OLD.`article_id`,'qty',OLD.`qty`),'apres',NULL));
END$$
CREATE TRIGGER audit_pick_insert AFTER INSERT ON pick FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('pick',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'order_line_id',NEW.`order_line_id`,'receipt_item_id',NEW.`receipt_item_id`,'location_id',NEW.`location_id`,'qty',NEW.`qty`,'status',NEW.`status`,'confirmed_at',NEW.`confirmed_at`)));
END$$
CREATE TRIGGER audit_pick_update AFTER UPDATE ON pick FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('pick',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'order_line_id',OLD.`order_line_id`,'receipt_item_id',OLD.`receipt_item_id`,'location_id',OLD.`location_id`,'qty',OLD.`qty`,'status',OLD.`status`,'confirmed_at',OLD.`confirmed_at`),'apres',JSON_OBJECT('id',NEW.`id`,'order_line_id',NEW.`order_line_id`,'receipt_item_id',NEW.`receipt_item_id`,'location_id',NEW.`location_id`,'qty',NEW.`qty`,'status',NEW.`status`,'confirmed_at',NEW.`confirmed_at`)));
END$$
CREATE TRIGGER audit_pick_delete AFTER DELETE ON pick FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('pick',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'order_line_id',OLD.`order_line_id`,'receipt_item_id',OLD.`receipt_item_id`,'location_id',OLD.`location_id`,'qty',OLD.`qty`,'status',OLD.`status`,'confirmed_at',OLD.`confirmed_at`),'apres',NULL));
END$$
CREATE TRIGGER audit_package_insert AFTER INSERT ON package FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('package',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'order_id',NEW.`order_id`,'code',NEW.`code`,'type',NEW.`type`)));
END$$
CREATE TRIGGER audit_package_update AFTER UPDATE ON package FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('package',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'order_id',OLD.`order_id`,'code',OLD.`code`,'type',OLD.`type`),'apres',JSON_OBJECT('id',NEW.`id`,'order_id',NEW.`order_id`,'code',NEW.`code`,'type',NEW.`type`)));
END$$
CREATE TRIGGER audit_package_delete AFTER DELETE ON package FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('package',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'order_id',OLD.`order_id`,'code',OLD.`code`,'type',OLD.`type`),'apres',NULL));
END$$
CREATE TRIGGER audit_package_pick_insert AFTER INSERT ON package_pick FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('package_pick',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'package_id',NEW.`package_id`,'pick_id',NEW.`pick_id`,'qty',NEW.`qty`)));
END$$
CREATE TRIGGER audit_package_pick_update AFTER UPDATE ON package_pick FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('package_pick',NEW.id,'UPDATE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'package_id',OLD.`package_id`,'pick_id',OLD.`pick_id`,'qty',OLD.`qty`),'apres',JSON_OBJECT('id',NEW.`id`,'package_id',NEW.`package_id`,'pick_id',NEW.`pick_id`,'qty',NEW.`qty`)));
END$$
CREATE TRIGGER audit_package_pick_delete AFTER DELETE ON package_pick FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('package_pick',OLD.id,'DELETE',@actor_id,JSON_OBJECT('avant',JSON_OBJECT('id',OLD.`id`,'package_id',OLD.`package_id`,'pick_id',OLD.`pick_id`,'qty',OLD.`qty`),'apres',NULL));
END$$
CREATE TRIGGER audit_shipment_insert AFTER INSERT ON shipment FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('shipment',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'order_id',NEW.`order_id`,'visit_id',NEW.`visit_id`,'reference',NEW.`reference`,'shipped_at',NEW.`shipped_at`,'actor_id',NEW.`actor_id`)));
END$$
CREATE TRIGGER audit_stock_movement_insert AFTER INSERT ON stock_movement FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('stock_movement',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'operation_ref',NEW.`operation_ref`,'receipt_item_id',NEW.`receipt_item_id`,'location_id',NEW.`location_id`,'delta',NEW.`delta`,'kind',NEW.`kind`,'pick_id',NEW.`pick_id`,'reason',NEW.`reason`,'actor_id',NEW.`actor_id`,'created_at',NEW.`created_at`)));
END$$
CREATE TRIGGER audit_receipt_reserve_insert AFTER INSERT ON receipt_reserve FOR EACH ROW
BEGIN
 INSERT INTO audit_log(entity,entity_id,operation,actor_id,details) VALUES ('receipt_reserve',NEW.id,'INSERT',@actor_id,JSON_OBJECT('avant',NULL,'apres',JSON_OBJECT('id',NEW.`id`,'receipt_id',NEW.`receipt_id`,'line_id',NEW.`line_id`,'kind',NEW.`kind`,'reason',NEW.`reason`,'actor_id',NEW.`actor_id`,'created_at',NEW.`created_at`)));
END$$
CREATE TRIGGER immutable_stock_movement_update BEFORE UPDATE ON stock_movement FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
CREATE TRIGGER immutable_stock_movement_delete BEFORE DELETE ON stock_movement FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
CREATE TRIGGER immutable_visit_event_update BEFORE UPDATE ON visit_event FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
CREATE TRIGGER immutable_visit_event_delete BEFORE DELETE ON visit_event FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
CREATE TRIGGER immutable_shipment_update BEFORE UPDATE ON shipment FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
CREATE TRIGGER immutable_shipment_delete BEFORE DELETE ON shipment FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
CREATE TRIGGER immutable_audit_log_update BEFORE UPDATE ON audit_log FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
CREATE TRIGGER immutable_audit_log_delete BEFORE DELETE ON audit_log FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
CREATE TRIGGER immutable_receipt_reserve_update BEFORE UPDATE ON receipt_reserve FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
CREATE TRIGGER immutable_receipt_reserve_delete BEFORE DELETE ON receipt_reserve FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Historique immuable : utiliser une correction métier'$$
DELIMITER ;
