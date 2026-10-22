-- Contrat relationnel BD70. MariaDB 10.4, InnoDB, utf8mb4.
-- Installer dans une base vide choisie par le script CLI, jamais dans la base système.
SET NAMES utf8mb4;
CREATE TABLE site_lock (id INT PRIMARY KEY, label VARCHAR(80) NOT NULL) ENGINE=InnoDB;
INSERT INTO site_lock VALUES (1,'Entrepôt de démonstration');
CREATE TABLE user_account (
 id INT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(190) NOT NULL UNIQUE,
 name VARCHAR(100) NOT NULL, password_hash VARCHAR(255) NOT NULL,
 role ENUM('pending','admin','manager','gate','warehouse') NOT NULL DEFAULT 'pending',
 active BOOLEAN NOT NULL DEFAULT 0, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, CHECK(active IN (0,1))
) ENGINE=InnoDB;
CREATE TABLE carrier (id INT AUTO_INCREMENT PRIMARY KEY, code VARCHAR(30) NOT NULL UNIQUE, name VARCHAR(100) NOT NULL, address VARCHAR(255) NOT NULL, phone VARCHAR(30) NOT NULL, email VARCHAR(190) NOT NULL) ENGINE=InnoDB;
CREATE TABLE carrier_contact (id INT AUTO_INCREMENT PRIMARY KEY, carrier_id INT NOT NULL, name VARCHAR(100) NOT NULL, phone VARCHAR(30) NOT NULL, email VARCHAR(190) NOT NULL, FOREIGN KEY(carrier_id) REFERENCES carrier(id)) ENGINE=InnoDB;
CREATE TABLE carrier_contract (id INT AUTO_INCREMENT PRIMARY KEY, carrier_id INT NOT NULL, reference VARCHAR(40) NOT NULL UNIQUE, starts_on DATE NOT NULL, ends_on DATE NOT NULL, terms TEXT NOT NULL, CHECK(ends_on>=starts_on), FOREIGN KEY(carrier_id) REFERENCES carrier(id)) ENGINE=InnoDB;
CREATE TABLE qualification (id INT AUTO_INCREMENT PRIMARY KEY, code VARCHAR(30) NOT NULL UNIQUE, name VARCHAR(100) NOT NULL) ENGINE=InnoDB;
CREATE TABLE driver (id INT AUTO_INCREMENT PRIMARY KEY, carrier_id INT NOT NULL, name VARCHAR(100) NOT NULL, phone VARCHAR(30) NOT NULL, license_number VARCHAR(60) NOT NULL UNIQUE, FOREIGN KEY(carrier_id) REFERENCES carrier(id)) ENGINE=InnoDB;
CREATE TABLE driver_qualification (id INT AUTO_INCREMENT PRIMARY KEY, driver_id INT NOT NULL, qualification_id INT NOT NULL, expires_on DATE NOT NULL, UNIQUE(driver_id,qualification_id), FOREIGN KEY(driver_id) REFERENCES driver(id), FOREIGN KEY(qualification_id) REFERENCES qualification(id)) ENGINE=InnoDB;
CREATE TABLE equipment (id INT AUTO_INCREMENT PRIMARY KEY, code VARCHAR(30) NOT NULL UNIQUE, name VARCHAR(100) NOT NULL) ENGINE=InnoDB;
CREATE TABLE vehicle (id INT AUTO_INCREMENT PRIMARY KEY, carrier_id INT NOT NULL, plate VARCHAR(30) NOT NULL UNIQUE, type ENUM('tracteur','remorque','porteur','fourgon') NOT NULL, max_kg DECIMAL(12,3) NOT NULL, max_pallets DECIMAL(10,3) NOT NULL, CHECK(max_kg>0 AND max_pallets>0), FOREIGN KEY(carrier_id) REFERENCES carrier(id)) ENGINE=InnoDB;
CREATE TABLE vehicle_equipment (id INT AUTO_INCREMENT PRIMARY KEY, vehicle_id INT NOT NULL, equipment_id INT NOT NULL, UNIQUE(vehicle_id,equipment_id), FOREIGN KEY(vehicle_id) REFERENCES vehicle(id), FOREIGN KEY(equipment_id) REFERENCES equipment(id)) ENGINE=InnoDB;
CREATE TABLE dock (id INT AUTO_INCREMENT PRIMARY KEY, code VARCHAR(30) NOT NULL UNIQUE, name VARCHAR(100) NOT NULL, type ENUM('reception','expedition','mixte') NOT NULL) ENGINE=InnoDB;
CREATE TABLE dock_equipment (id INT AUTO_INCREMENT PRIMARY KEY, dock_id INT NOT NULL, equipment_id INT NOT NULL, UNIQUE(dock_id,equipment_id), FOREIGN KEY(dock_id) REFERENCES dock(id), FOREIGN KEY(equipment_id) REFERENCES equipment(id)) ENGINE=InnoDB;
CREATE TABLE dock_vehicle_type (id INT AUTO_INCREMENT PRIMARY KEY, dock_id INT NOT NULL, vehicle_type ENUM('tracteur','remorque','porteur','fourgon') NOT NULL, UNIQUE(dock_id,vehicle_type), FOREIGN KEY(dock_id) REFERENCES dock(id)) ENGINE=InnoDB;
CREATE TABLE dock_downtime (id INT AUTO_INCREMENT PRIMARY KEY, dock_id INT NOT NULL, starts_at DATETIME NOT NULL, ends_at DATETIME NOT NULL, reason VARCHAR(255) NOT NULL, CHECK(ends_at>starts_at), FOREIGN KEY(dock_id) REFERENCES dock(id)) ENGINE=InnoDB;
CREATE TABLE appointment (
 id INT AUTO_INCREMENT PRIMARY KEY, reference VARCHAR(40) NOT NULL UNIQUE, dock_id INT NOT NULL, driver_id INT NOT NULL, vehicle_id INT NOT NULL, trailer_id INT NULL,
 operation ENUM('reception','expedition') NOT NULL, starts_at DATETIME NOT NULL, ends_at DATETIME NOT NULL, status ENUM('active','cancelled') NOT NULL DEFAULT 'active',
 CHECK(ends_at>starts_at), CHECK(trailer_id IS NULL OR trailer_id<>vehicle_id),
 FOREIGN KEY(dock_id) REFERENCES dock(id), FOREIGN KEY(driver_id) REFERENCES driver(id), FOREIGN KEY(vehicle_id) REFERENCES vehicle(id), FOREIGN KEY(trailer_id) REFERENCES vehicle(id)
) ENGINE=InnoDB;
CREATE TABLE truck_visit (
 id INT AUTO_INCREMENT PRIMARY KEY, reference VARCHAR(40) NOT NULL UNIQUE, appointment_id INT NULL UNIQUE,
 driver_id INT NOT NULL, vehicle_id INT NOT NULL, trailer_id INT NULL, operation ENUM('reception','expedition') NOT NULL,
 dock_id INT NULL, status ENUM('arrived','checked','parking','called','working','finished','departed','rejected') NOT NULL DEFAULT 'arrived',
 document_note VARCHAR(255) NOT NULL DEFAULT '',
 FOREIGN KEY(appointment_id) REFERENCES appointment(id), FOREIGN KEY(driver_id) REFERENCES driver(id), FOREIGN KEY(vehicle_id) REFERENCES vehicle(id), FOREIGN KEY(trailer_id) REFERENCES vehicle(id), FOREIGN KEY(dock_id) REFERENCES dock(id)
) ENGINE=InnoDB;
CREATE TABLE visit_event (
 id INT AUTO_INCREMENT PRIMARY KEY, visit_id INT NOT NULL, state ENUM('arrived','checked','parking','called','working','finished','departed','rejected') NOT NULL,
 happened_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, actor_id INT NOT NULL, UNIQUE(visit_id,state),
 FOREIGN KEY(visit_id) REFERENCES truck_visit(id), FOREIGN KEY(actor_id) REFERENCES user_account(id)
) ENGINE=InnoDB;
CREATE TABLE owner (id INT AUTO_INCREMENT PRIMARY KEY, code VARCHAR(30) NOT NULL UNIQUE, name VARCHAR(100) NOT NULL, address VARCHAR(255) NOT NULL, email VARCHAR(190) NOT NULL) ENGINE=InnoDB;
CREATE TABLE supplier (id INT AUTO_INCREMENT PRIMARY KEY, code VARCHAR(30) NOT NULL UNIQUE, name VARCHAR(100) NOT NULL, address VARCHAR(255) NOT NULL, phone VARCHAR(30) NOT NULL) ENGINE=InnoDB;
CREATE TABLE article (
 id INT AUTO_INCREMENT PRIMARY KEY, owner_id INT NOT NULL, sku VARCHAR(40) NOT NULL, name VARCHAR(100) NOT NULL,
 storage ENUM('ambiant','froid','dangereux') NOT NULL, packaging VARCHAR(80) NOT NULL,
 width_m DECIMAL(10,4) NOT NULL, depth_m DECIMAL(10,4) NOT NULL, height_m DECIMAL(10,4) NOT NULL,
 unit_kg DECIMAL(10,3) NOT NULL, units_per_pallet INT NOT NULL,
 UNIQUE(owner_id,sku), CHECK(width_m>0 AND depth_m>0 AND height_m>0 AND unit_kg>0 AND units_per_pallet>0), FOREIGN KEY(owner_id) REFERENCES owner(id)
) ENGINE=InnoDB;
CREATE TABLE zone (id INT AUTO_INCREMENT PRIMARY KEY, code VARCHAR(30) NOT NULL UNIQUE, name VARCHAR(100) NOT NULL, storage ENUM('ambiant','froid','dangereux') NOT NULL) ENGINE=InnoDB;
CREATE TABLE aisle (id INT AUTO_INCREMENT PRIMARY KEY, zone_id INT NOT NULL, code VARCHAR(30) NOT NULL UNIQUE, FOREIGN KEY(zone_id) REFERENCES zone(id)) ENGINE=InnoDB;
CREATE TABLE rack (id INT AUTO_INCREMENT PRIMARY KEY, aisle_id INT NOT NULL, code VARCHAR(30) NOT NULL UNIQUE, FOREIGN KEY(aisle_id) REFERENCES aisle(id)) ENGINE=InnoDB;
CREATE TABLE rack_level (id INT AUTO_INCREMENT PRIMARY KEY, rack_id INT NOT NULL, code VARCHAR(30) NOT NULL UNIQUE, FOREIGN KEY(rack_id) REFERENCES rack(id)) ENGINE=InnoDB;
CREATE TABLE location (
 id INT AUTO_INCREMENT PRIMARY KEY, level_id INT NOT NULL, code VARCHAR(30) NOT NULL UNIQUE,
 width_m DECIMAL(10,4) NOT NULL, depth_m DECIMAL(10,4) NOT NULL, height_m DECIMAL(10,4) NOT NULL,
 max_kg DECIMAL(12,3) NOT NULL, max_pallets DECIMAL(10,3) NOT NULL,
 CHECK(width_m>0 AND depth_m>0 AND height_m>0 AND max_kg>0 AND max_pallets>0), FOREIGN KEY(level_id) REFERENCES rack_level(id)
) ENGINE=InnoDB;
CREATE TABLE lot (id INT AUTO_INCREMENT PRIMARY KEY, article_id INT NOT NULL, code VARCHAR(40) NOT NULL, expires_on DATE NULL, blocked BOOLEAN NOT NULL DEFAULT 0, block_reason VARCHAR(255) NOT NULL DEFAULT '', CHECK(blocked IN (0,1)), UNIQUE(article_id,code), FOREIGN KEY(article_id) REFERENCES article(id)) ENGINE=InnoDB;
CREATE TABLE supplier_notice (id INT AUTO_INCREMENT PRIMARY KEY, reference VARCHAR(40) NOT NULL UNIQUE, supplier_id INT NOT NULL, expected_on DATE NOT NULL, FOREIGN KEY(supplier_id) REFERENCES supplier(id)) ENGINE=InnoDB;
CREATE TABLE notice_line (id INT AUTO_INCREMENT PRIMARY KEY, notice_id INT NOT NULL, article_id INT NOT NULL, expected_qty INT NOT NULL, UNIQUE(notice_id,article_id), CHECK(expected_qty>0), FOREIGN KEY(notice_id) REFERENCES supplier_notice(id), FOREIGN KEY(article_id) REFERENCES article(id)) ENGINE=InnoDB;
CREATE TABLE receipt (id INT AUTO_INCREMENT PRIMARY KEY, reference VARCHAR(40) NOT NULL UNIQUE, notice_id INT NOT NULL, visit_id INT NOT NULL, status ENUM('draft','validated') NOT NULL DEFAULT 'draft', validated_at DATETIME NULL, FOREIGN KEY(notice_id) REFERENCES supplier_notice(id), FOREIGN KEY(visit_id) REFERENCES truck_visit(id)) ENGINE=InnoDB;
CREATE TABLE receipt_line (id INT AUTO_INCREMENT PRIMARY KEY, receipt_id INT NOT NULL, notice_line_id INT NOT NULL, expected_qty INT NOT NULL, UNIQUE(receipt_id,notice_line_id), CHECK(expected_qty>0), FOREIGN KEY(receipt_id) REFERENCES receipt(id), FOREIGN KEY(notice_line_id) REFERENCES notice_line(id)) ENGINE=InnoDB;
CREATE TABLE receipt_item (
 id INT AUTO_INCREMENT PRIMARY KEY, line_id INT NOT NULL, lot_id INT NOT NULL, pallet_code VARCHAR(50) NOT NULL UNIQUE,
 accepted_qty INT NOT NULL, damaged_qty INT NOT NULL DEFAULT 0, pallet_state ENUM('bon','abime') NOT NULL DEFAULT 'bon', reservation VARCHAR(255) NOT NULL DEFAULT '', location_id INT NOT NULL,
 CHECK(accepted_qty>=0 AND damaged_qty>=0 AND accepted_qty+damaged_qty>0), CHECK(damaged_qty=0 OR CHAR_LENGTH(reservation)>0),
 FOREIGN KEY(line_id) REFERENCES receipt_line(id), FOREIGN KEY(lot_id) REFERENCES lot(id), FOREIGN KEY(location_id) REFERENCES location(id)
) ENGINE=InnoDB;
CREATE TABLE customer_order (id INT AUTO_INCREMENT PRIMARY KEY, reference VARCHAR(40) NOT NULL UNIQUE, owner_id INT NOT NULL, destination VARCHAR(255) NOT NULL, desired_on DATE NOT NULL, status ENUM('draft','picking','ready','shipped','cancelled') NOT NULL DEFAULT 'draft', preparer_id INT NULL, picking_at DATETIME NULL, ready_at DATETIME NULL, FOREIGN KEY(owner_id) REFERENCES owner(id), FOREIGN KEY(preparer_id) REFERENCES user_account(id)) ENGINE=InnoDB;
CREATE TABLE order_line (id INT AUTO_INCREMENT PRIMARY KEY, order_id INT NOT NULL, article_id INT NOT NULL, qty INT NOT NULL, UNIQUE(order_id,article_id), CHECK(qty>0), FOREIGN KEY(order_id) REFERENCES customer_order(id), FOREIGN KEY(article_id) REFERENCES article(id)) ENGINE=InnoDB;
CREATE TABLE pick (id INT AUTO_INCREMENT PRIMARY KEY, order_line_id INT NOT NULL, receipt_item_id INT NOT NULL, location_id INT NOT NULL, qty INT NOT NULL, status ENUM('planned','confirmed','shipped','cancelled') NOT NULL DEFAULT 'planned', confirmed_at DATETIME NULL, CHECK(qty>0), FOREIGN KEY(order_line_id) REFERENCES order_line(id), FOREIGN KEY(receipt_item_id) REFERENCES receipt_item(id), FOREIGN KEY(location_id) REFERENCES location(id)) ENGINE=InnoDB;
CREATE TABLE package (id INT AUTO_INCREMENT PRIMARY KEY, order_id INT NOT NULL, code VARCHAR(50) NOT NULL UNIQUE, type ENUM('colis','palette') NOT NULL, FOREIGN KEY(order_id) REFERENCES customer_order(id)) ENGINE=InnoDB;
CREATE TABLE package_pick (id INT AUTO_INCREMENT PRIMARY KEY, package_id INT NOT NULL, pick_id INT NOT NULL UNIQUE, FOREIGN KEY(package_id) REFERENCES package(id), FOREIGN KEY(pick_id) REFERENCES pick(id)) ENGINE=InnoDB;
CREATE TABLE shipment (id INT AUTO_INCREMENT PRIMARY KEY, order_id INT NOT NULL UNIQUE, visit_id INT NOT NULL, reference VARCHAR(40) NOT NULL UNIQUE, shipped_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, actor_id INT NOT NULL, FOREIGN KEY(order_id) REFERENCES customer_order(id), FOREIGN KEY(visit_id) REFERENCES truck_visit(id), FOREIGN KEY(actor_id) REFERENCES user_account(id)) ENGINE=InnoDB;
CREATE TABLE stock_movement (
 id INT AUTO_INCREMENT PRIMARY KEY, operation_ref VARCHAR(64) NOT NULL, receipt_item_id INT NOT NULL, location_id INT NOT NULL, delta INT NOT NULL,
 kind ENUM('entry','transfer','shipment','adjustment') NOT NULL, pick_id INT NULL UNIQUE, reason VARCHAR(255) NOT NULL, actor_id INT NOT NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CHECK(delta<>0), CHECK((kind='entry' AND delta>0 AND pick_id IS NULL) OR (kind='shipment' AND delta<0 AND pick_id IS NOT NULL) OR (kind IN ('transfer','adjustment') AND pick_id IS NULL)),
 FOREIGN KEY(receipt_item_id) REFERENCES receipt_item(id), FOREIGN KEY(location_id) REFERENCES location(id), FOREIGN KEY(pick_id) REFERENCES pick(id), FOREIGN KEY(actor_id) REFERENCES user_account(id)
) ENGINE=InnoDB;
CREATE TABLE audit_log (id BIGINT AUTO_INCREMENT PRIMARY KEY, entity VARCHAR(50) NOT NULL, entity_id INT NOT NULL, operation VARCHAR(12) NOT NULL, actor_id INT NULL, happened_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, details VARCHAR(255) NOT NULL, FOREIGN KEY(actor_id) REFERENCES user_account(id)) ENGINE=InnoDB;
