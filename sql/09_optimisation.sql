-- Optimisation du calcul de stock (TD « Optimisation » et TD « Automatisation », exercice 2 : table de
-- statistiques tenue à jour par un déclencheur, mise à jour incrémentale en O(1)).
--
-- Avant : v_balance recalculait chaque solde par GROUP BY sur TOUT l'historique stock_movement, et v_reserved
-- sur toutes les lignes de pick ; MariaDB matérialisait ces deux vues (tables temporaires, lecture complète)
-- à chaque recherche de stock, sélection FEFO ou proposition d'emplacement.
-- Après : stock_balance garde, par fraction de réception et emplacement, la quantité physique et la quantité
-- réservée. Les déclencheurs la mettent à jour dans la même transaction que le mouvement ou la réservation ;
-- les vues v_balance et v_reserved lisent cette table par sa clé primaire.
-- Redondance contrôlée : la valeur de référence reste l'historique immuable ; v_balance_controle le recalcule
-- et scripts/validate-data.php vérifie que les deux sont identiques.

CREATE TABLE stock_balance (
 receipt_item_id INT NOT NULL,
 location_id INT NOT NULL,
 qty INT NOT NULL DEFAULT 0,
 reserved_qty INT NOT NULL DEFAULT 0,
 PRIMARY KEY (receipt_item_id, location_id),
 CHECK (reserved_qty >= 0),
 FOREIGN KEY (receipt_item_id) REFERENCES receipt_item(id),
 FOREIGN KEY (location_id) REFERENCES location(id)
) ENGINE=InnoDB;

-- Recalcul complet depuis l'historique (ancienne définition de v_balance), conservé pour le contrôle.
CREATE VIEW v_balance_controle AS
 SELECT receipt_item_id,location_id,SUM(delta) qty FROM v_stock_movement GROUP BY receipt_item_id,location_id;

CREATE OR REPLACE VIEW v_balance AS
 SELECT receipt_item_id,location_id,qty FROM stock_balance;
CREATE OR REPLACE VIEW v_reserved AS
 SELECT receipt_item_id,location_id,reserved_qty qty FROM stock_balance WHERE reserved_qty<>0;

DELIMITER $$
-- Chaque mouvement ajoute sa variation au solde. Une sortie (kind='shipment') ne porte que son prélèvement :
-- fraction, emplacement et quantité sont lus dans pick (normalize_shipment a vidé ces colonnes).
CREATE TRIGGER balance_movement_insert AFTER INSERT ON stock_movement FOR EACH ROW
BEGIN
 DECLARE v_item INT; DECLARE v_location INT; DECLARE v_delta INT;
 IF NEW.kind='shipment' THEN
  SELECT receipt_item_id,location_id,-qty INTO v_item,v_location,v_delta FROM pick WHERE id=NEW.pick_id;
 ELSE
  SET v_item=NEW.receipt_item_id, v_location=NEW.location_id, v_delta=NEW.delta;
 END IF;
 INSERT INTO stock_balance(receipt_item_id,location_id,qty) VALUES (v_item,v_location,v_delta)
 ON DUPLICATE KEY UPDATE qty=qty+VALUES(qty);
END$$

-- Réservations : seuls les prélèvements 'planned' et 'confirmed' comptent (même règle que l'ancienne v_reserved).
CREATE TRIGGER balance_pick_insert AFTER INSERT ON pick FOR EACH ROW
BEGIN
 IF NEW.status IN ('planned','confirmed') THEN
  INSERT INTO stock_balance(receipt_item_id,location_id,reserved_qty) VALUES (NEW.receipt_item_id,NEW.location_id,NEW.qty)
  ON DUPLICATE KEY UPDATE reserved_qty=reserved_qty+VALUES(reserved_qty);
 END IF;
END$$
CREATE TRIGGER balance_pick_update AFTER UPDATE ON pick FOR EACH ROW
BEGIN
 IF OLD.status IN ('planned','confirmed') THEN
  UPDATE stock_balance SET reserved_qty=reserved_qty-OLD.qty WHERE receipt_item_id=OLD.receipt_item_id AND location_id=OLD.location_id;
 END IF;
 IF NEW.status IN ('planned','confirmed') THEN
  INSERT INTO stock_balance(receipt_item_id,location_id,reserved_qty) VALUES (NEW.receipt_item_id,NEW.location_id,NEW.qty)
  ON DUPLICATE KEY UPDATE reserved_qty=reserved_qty+VALUES(reserved_qty);
 END IF;
END$$
CREATE TRIGGER balance_pick_delete AFTER DELETE ON pick FOR EACH ROW
BEGIN
 IF OLD.status IN ('planned','confirmed') THEN
  UPDATE stock_balance SET reserved_qty=reserved_qty-OLD.qty WHERE receipt_item_id=OLD.receipt_item_id AND location_id=OLD.location_id;
 END IF;
END$$
-- Une sortie a déjà été comptée avec la quantité du prélèvement : celui-ci est figé une fois expédié.
CREATE TRIGGER pick_shipped_frozen BEFORE UPDATE ON pick FOR EACH ROW
BEGIN
 IF OLD.status='shipped' AND (NEW.status<>'shipped' OR NEW.qty<>OLD.qty OR NEW.receipt_item_id<>OLD.receipt_item_id OR NEW.location_id<>OLD.location_id) THEN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Prelevement expedie : historique fige';
 END IF;
END$$

-- Fonction stockée : quantité disponible d'un article à une date (lots non bloqués, non périmés, hors réservations).
-- Utilisée par la préparation de commande pour refuser d'emblée une demande supérieure au stock disponible.
CREATE FUNCTION stock_disponible(p_article INT, p_jour DATE) RETURNS INT
READS SQL DATA
BEGIN
 RETURN (SELECT COALESCE(SUM(b.qty-b.reserved_qty),0)
         FROM stock_balance b JOIN receipt_item i ON i.id=b.receipt_item_id JOIN lot t ON t.id=i.lot_id
         WHERE t.article_id=p_article AND t.blocked=0 AND (t.expires_on IS NULL OR t.expires_on>=p_jour)
           AND b.qty-b.reserved_qty>0);
END$$
DELIMITER ;

-- Initialisation des soldes à partir de l'historique existant, en une seule transaction (tout ou rien,
-- TD « Automatisation », exercice 3, question 5). Sur une base neuve, aucune ligne n'est insérée.
START TRANSACTION;
INSERT INTO stock_balance(receipt_item_id,location_id,qty,reserved_qty)
 SELECT k.receipt_item_id,k.location_id,COALESCE(b.qty,0),COALESCE(r.qty,0)
 FROM (SELECT receipt_item_id,location_id FROM v_balance_controle
       UNION SELECT receipt_item_id,location_id FROM pick WHERE status IN ('planned','confirmed')) k
 LEFT JOIN v_balance_controle b ON b.receipt_item_id=k.receipt_item_id AND b.location_id=k.location_id
 LEFT JOIN (SELECT receipt_item_id,location_id,SUM(qty) qty FROM pick WHERE status IN ('planned','confirmed') GROUP BY receipt_item_id,location_id) r
        ON r.receipt_item_id=k.receipt_item_id AND r.location_id=k.location_id;
COMMIT;
