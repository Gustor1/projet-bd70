# Matrice CRUD et droits

A = administrateur, R = responsable, G = accueil, M = magasinier. Tous les contrôles sont faits côté serveur ; compte en attente sans accès. Administration des utilisateurs réservée à A.

| Entité | Création / modification / suppression | Profil |
|---|---|---|
| user_account | Créer/activer/modifier/désactiver ; pas de suppression de l’auteur historique. | A |
| carrier | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| carrier_contact | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| carrier_contract | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| qualification | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| driver | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| driver_qualification | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| equipment | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| vehicle | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| vehicle_equipment | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| dock | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| dock_equipment | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| dock_vehicle_type | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| dock_downtime | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R, G |
| appointment | Créer/déplacer sous contrôle ; annuler avant usage ; pas de suppression. | A, R, G |
| truck_visit | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R, G |
| visit_event | Actions métier uniquement ; historiques immuables, correction par mouvement ou annulation avant expédition. | A, R, G |
| owner | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| supplier | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| article | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| zone | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| aisle | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| rack | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| rack_level | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| location | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R |
| lot | CRUD de fiche inutilisée ; suppression référencée refusée ; propriétés structurelles protégées après usage. | A, R, M |
| supplier_notice | CRUD de brouillon ; FK protectrices ; validation ou préparation fige les données ; annulation métier. | A, R, M |
| notice_line | CRUD de brouillon ; FK protectrices ; validation ou préparation fige les données ; annulation métier. | A, R, M |
| receipt | CRUD de brouillon ; FK protectrices ; validation ou préparation fige les données ; annulation métier. | A, R, M |
| receipt_line | CRUD de brouillon ; FK protectrices ; validation ou préparation fige les données ; annulation métier. | A, R, M |
| receipt_item | CRUD de brouillon ; FK protectrices ; validation ou préparation fige les données ; annulation métier. | A, R, M |
| customer_order | CRUD de brouillon ; FK protectrices ; validation ou préparation fige les données ; annulation métier. | A, R, M |
| order_line | CRUD de brouillon ; FK protectrices ; validation ou préparation fige les données ; annulation métier. | A, R, M |
| pick | Actions métier uniquement ; historiques immuables, correction par mouvement ou annulation avant expédition. | A, R, M |
| package | CRUD de brouillon ; FK protectrices ; validation ou préparation fige les données ; annulation métier. | A, R, M |
| package_pick | CRUD de brouillon ; FK protectrices ; validation ou préparation fige les données ; annulation métier. | A, R, M |
| shipment | Actions métier uniquement ; historiques immuables, correction par mouvement ou annulation avant expédition. | A, R, M |
| stock_movement | Actions métier uniquement ; historiques immuables, correction par mouvement ou annulation avant expédition. | A, R, M |
| audit_log | Actions métier uniquement ; historiques immuables, correction par mouvement ou annulation avant expédition. | A |
| site_lock | Actions métier uniquement ; historiques immuables, correction par mouvement ou annulation avant expédition. | A |