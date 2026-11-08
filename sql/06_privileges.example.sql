-- Gestion des accès (DCL) : moindre privilège, un compte SQL par usage.
-- À exécuter séparément avec le compte d'administration, après avoir remplacé
-- bd70_demo par le nom de la base et chaque secret par une valeur locale.
-- scripts/install.php crée automatiquement le compte applicatif avec un secret aléatoire
-- stocké hors dépôt (config/local.php) ; aucun mot de passe réel n'est versionné.
--
-- Les profils métier (administrateur, responsable, accueil, magasinier, transporteur)
-- sont des lignes de user_account contrôlées par l'application. La base ne connaît
-- que des comptes techniques, chacun limité à son usage :
--   bd70_app      : l'application web (lecture, écritures métier limitées) ;
--   bd70_reporting: un outil de reporting (lecture des vues d'indicateurs uniquement) ;
--   bd70_backup   : la sauvegarde nocturne (lecture et verrouillage, aucune écriture).
-- Seul l'administrateur de la base (root, mot de passe défini à l'installation du serveur)
-- peut modifier la structure (CREATE, ALTER, DROP).

-- 1. Application web, connexions locales uniquement (liste blanche d'adresse).
CREATE USER 'bd70_app'@'127.0.0.1' IDENTIFIED BY 'REMPLACER_PAR_UN_SECRET_LOCAL';
GRANT SELECT, EXECUTE ON bd70_demo.* TO 'bd70_app'@'127.0.0.1';
GRANT INSERT, UPDATE, DELETE ON bd70_demo.carrier TO 'bd70_app'@'127.0.0.1';
GRANT INSERT, UPDATE, DELETE ON bd70_demo.appointment TO 'bd70_app'@'127.0.0.1';
-- (install.php répète ce GRANT pour chaque table éditable.)
-- Les historiques n'acceptent que l'ajout : jamais de correction ni de suppression.
GRANT INSERT ON bd70_demo.stock_movement TO 'bd70_app'@'127.0.0.1';
GRANT INSERT ON bd70_demo.visit_event TO 'bd70_app'@'127.0.0.1';
GRANT INSERT ON bd70_demo.shipment TO 'bd70_app'@'127.0.0.1';
GRANT INSERT ON bd70_demo.receipt_reserve TO 'bd70_app'@'127.0.0.1';
-- audit_log, site_lock, appointment_archive et stock_balance ne sont alimentés que par triggers et procédures
-- (SQL SECURITY DEFINER) : l'application n'a aucun droit d'écriture direct dessus.

-- 2. Reporting : uniquement les vues d'indicateurs, aucune donnée personnelle des comptes.
CREATE USER 'bd70_reporting'@'127.0.0.1' IDENTIFIED BY 'REMPLACER_PAR_UN_AUTRE_SECRET';
GRANT SELECT ON bd70_demo.v_visit TO 'bd70_reporting'@'127.0.0.1';
GRANT SELECT ON bd70_demo.v_stock TO 'bd70_reporting'@'127.0.0.1';
GRANT SELECT ON bd70_demo.v_location_usage TO 'bd70_reporting'@'127.0.0.1';
GRANT SELECT ON bd70_demo.v_receipt_discrepancy TO 'bd70_reporting'@'127.0.0.1';
GRANT SELECT ON bd70_demo.v_appointment_all TO 'bd70_reporting'@'127.0.0.1';

-- 3. Sauvegarde : lecture cohérente, vues, procédures et évènements pour mysqldump.
CREATE USER 'bd70_backup'@'127.0.0.1' IDENTIFIED BY 'REMPLACER_PAR_UN_TROISIEME_SECRET';
GRANT SELECT, LOCK TABLES, SHOW VIEW, TRIGGER, EVENT ON bd70_demo.* TO 'bd70_backup'@'127.0.0.1';

-- REVOKE : retrait d'un droit devenu inutile.
-- Exemple : la vue v_visit expose les noms des chauffeurs ; si le reporting
-- ne doit plus voir de données nominatives, on lui retire ce droit.
REVOKE SELECT ON bd70_demo.v_visit FROM 'bd70_reporting'@'127.0.0.1';
-- Autre exemple : le journal d'audit ne doit jamais être modifiable par l'application.
-- REVOKE UPDATE, DELETE ON bd70_demo.audit_log FROM 'bd70_app'@'127.0.0.1';

-- Contrôle des droits effectifs :
SHOW GRANTS FOR 'bd70_app'@'127.0.0.1';
SHOW GRANTS FOR 'bd70_reporting'@'127.0.0.1';
