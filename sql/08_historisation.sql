-- Historisation, automatisation et cohérence métier (cours BD70 : déclencheurs, historisation, évènements).
-- 1. Les rendez-vous anciens et sans passage sont déplacés vers une table historique (archivage).
-- 2. Un évènement planifié lance cet archivage chaque nuit.
-- 3. Une vue UNION ALL réunit rendez-vous courants et historisés.
-- 4. Un déclencheur garantit en base l'absence de chevauchement sur un même quai.

CREATE TABLE appointment_archive (
 id INT PRIMARY KEY, reference VARCHAR(40) NOT NULL UNIQUE, dock_id INT NOT NULL, driver_id INT NOT NULL, vehicle_id INT NOT NULL, trailer_id INT NULL,
 operation ENUM('reception','expedition') NOT NULL, starts_at DATETIME NOT NULL, ends_at DATETIME NOT NULL, status ENUM('active','cancelled') NOT NULL,
 archived_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CHECK(ends_at>starts_at),
 FOREIGN KEY(dock_id) REFERENCES dock(id), FOREIGN KEY(driver_id) REFERENCES driver(id), FOREIGN KEY(vehicle_id) REFERENCES vehicle(id), FOREIGN KEY(trailer_id) REFERENCES vehicle(id),
 INDEX idx_archive_period(starts_at)
) ENGINE=InnoDB;

CREATE VIEW v_appointment_all AS
 SELECT id,reference,dock_id,driver_id,vehicle_id,trailer_id,operation,starts_at,ends_at,status,'courant' origine FROM appointment
 UNION ALL
 SELECT id,reference,dock_id,driver_id,vehicle_id,trailer_id,operation,starts_at,ends_at,status,'historique' origine FROM appointment_archive;

DELIMITER $$
-- Cohérence : deux rendez-vous actifs ne peuvent pas se chevaucher sur un même quai,
-- même si une écriture contourne l'application.
CREATE TRIGGER appointment_no_overlap_insert BEFORE INSERT ON appointment FOR EACH ROW
BEGIN
 IF NEW.status='active' AND EXISTS(SELECT 1 FROM appointment a WHERE a.dock_id=NEW.dock_id AND a.status='active' AND a.starts_at<NEW.ends_at AND a.ends_at>NEW.starts_at) THEN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Ce créneau chevauche un rendez-vous actif sur ce quai';
 END IF;
END$$
CREATE TRIGGER appointment_no_overlap_update BEFORE UPDATE ON appointment FOR EACH ROW
BEGIN
 IF NEW.status='active' AND EXISTS(SELECT 1 FROM appointment a WHERE a.id<>NEW.id AND a.dock_id=NEW.dock_id AND a.status='active' AND a.starts_at<NEW.ends_at AND a.ends_at>NEW.starts_at) THEN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Ce créneau chevauche un rendez-vous actif sur ce quai';
 END IF;
END$$

-- Archivage transactionnel : copie puis suppression, validées ensemble ou annulées ensemble.
-- Seuls les rendez-vous terminés depuis p_days jours et n'ayant donné lieu à aucun passage sont déplacés
-- (annulés ou non honorés) : les passages gardent ainsi leur clé étrangère vers appointment.
CREATE PROCEDURE archive_appointments(IN p_days INT)
SQL SECURITY DEFINER
BEGIN
 DECLARE v_limit DATETIME;
 DECLARE v_moved INT DEFAULT 0;
 DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
 IF p_days IS NULL OR p_days<30 THEN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Délai d archivage minimal : 30 jours';
 END IF;
 SET v_limit=NOW()-INTERVAL p_days DAY;
 START TRANSACTION;
 INSERT INTO appointment_archive(id,reference,dock_id,driver_id,vehicle_id,trailer_id,operation,starts_at,ends_at,status)
  SELECT a.id,a.reference,a.dock_id,a.driver_id,a.vehicle_id,a.trailer_id,a.operation,a.starts_at,a.ends_at,a.status
  FROM appointment a
  WHERE a.ends_at<v_limit AND NOT EXISTS(SELECT 1 FROM truck_visit v WHERE v.appointment_id=a.id);
 DELETE a FROM appointment a JOIN appointment_archive h ON h.id=a.id;
 SET v_moved=ROW_COUNT();
 COMMIT;
 SELECT v_moved rendez_vous_archives, COUNT(*) total_historique FROM appointment_archive;
END$$
DELIMITER ;

-- Exécution automatique chaque nuit (nécessite event_scheduler=ON côté serveur).
CREATE EVENT ev_archive_appointments
 ON SCHEDULE EVERY 1 DAY STARTS (CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 2 HOUR)
 ON COMPLETION PRESERVE ENABLE
 COMMENT 'Historise les rendez-vous terminés depuis plus d un an et sans passage'
 DO CALL archive_appointments(365);
