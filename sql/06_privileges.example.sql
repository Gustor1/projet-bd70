-- À adapter et exécuter séparément avec le compte d'installation.
-- scripts/install.php génère les droits par table et un secret aléatoire hors dépôt.
CREATE USER 'bd70_app'@'127.0.0.1' IDENTIFIED BY 'REMPLACER_PAR_UN_SECRET_LOCAL';
GRANT SELECT, EXECUTE ON bd70_demo.* TO 'bd70_app'@'127.0.0.1';
-- INSERT/UPDATE/DELETE uniquement sur les tables éditables (voir install.php).
-- Exemple :
GRANT INSERT, UPDATE, DELETE ON bd70_demo.carrier TO 'bd70_app'@'127.0.0.1';
GRANT INSERT ON bd70_demo.stock_movement TO 'bd70_app'@'127.0.0.1';
GRANT INSERT ON bd70_demo.visit_event TO 'bd70_app'@'127.0.0.1';
GRANT INSERT ON bd70_demo.shipment TO 'bd70_app'@'127.0.0.1';
-- Aucun DDL, aucun UPDATE/DELETE sur les historiques, aucune écriture directe dans audit_log.
