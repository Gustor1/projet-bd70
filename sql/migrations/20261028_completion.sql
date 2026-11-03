-- Appliquer avec scripts/migrate.php sur une sauvegarde restaurée avant utilisation réelle.
ALTER TABLE supplier_notice ADD closed_at DATETIME NULL, ADD closed_by INT NULL, ADD closure_note VARCHAR(255) NOT NULL DEFAULT '', ADD FOREIGN KEY(closed_by) REFERENCES user_account(id);
ALTER TABLE customer_order ADD revision_note VARCHAR(255) NOT NULL DEFAULT '';
ALTER TABLE package_pick ADD qty INT NOT NULL DEFAULT 1;
UPDATE package_pick pp JOIN pick p ON p.id=pp.pick_id SET pp.qty=p.qty;
ALTER TABLE package_pick ADD INDEX idx_package_pick_pick(pick_id);
ALTER TABLE package_pick DROP INDEX pick_id, ADD UNIQUE KEY uq_package_pick(package_id,pick_id), ADD CHECK(qty>0);
ALTER TABLE audit_log MODIFY details TEXT NOT NULL;
CREATE TABLE receipt_reserve (
 id INT AUTO_INCREMENT PRIMARY KEY, receipt_id INT NULL, line_id INT NULL,
 kind ENUM('manquant','excedent','avarie','autre') NOT NULL, reason VARCHAR(255) NOT NULL,
 actor_id INT NOT NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CHECK(CHAR_LENGTH(TRIM(reason))>0), CHECK((receipt_id IS NULL) <> (line_id IS NULL)), FOREIGN KEY(receipt_id) REFERENCES receipt(id),
 FOREIGN KEY(line_id) REFERENCES receipt_line(id), FOREIGN KEY(actor_id) REFERENCES user_account(id)
) ENGINE=InnoDB;
