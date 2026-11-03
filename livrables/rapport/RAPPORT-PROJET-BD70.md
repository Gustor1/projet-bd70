# Transit - Gestion d’un entrepôt logistique

Auteurs : ELIOTT LE, SEMIH TASKIN et Thomas VUILLIN.

Projet BD70 - sujet A26. Réalisation après audit. Référence du jeu riche : 28 octobre 2026, Europe/Paris. Les contributions individuelles n’ont pas été communiquées.

## Introduction et démarche

Le système relie transporteurs, passages de camions, quais, réceptions, stocks et expéditions. Chaque quantité conserve sa provenance jusqu’au camion de sortie. Le sujet exige un modèle couvrant huit domaines et un minimum web de cinq domaines ; les huit ont ici une interface.

L’audit a confronté le sujet, la grille et le code, puis reproduit les anomalies. Six lots ont corrigé la fiabilité, les réceptions, les référentiels/planning, les commandes/colis, les données et la recette. Les sauvegardes précèdent les modifications ; les tests utilisent des bases distinctes.

Sources : A26_Site_Logistique.pdf, pages 1 à 3 ; Éléments dévaluation projet BD70.docx ; supports techniques A25 locaux. Les modalités A25 de soutenance ne sont pas supposées applicables à A26.

## Acteurs et cas d’utilisation

Administrateur : comptes et tous les traitements. Responsable : référentiels, planification, stocks, commandes et analyses. Accueil : rendez-vous et passages. Magasinier : réception, rangement, préparation et expédition. Les profils internes consultent la traçabilité et le planning ; les actions restent contrôlées côté serveur.

UC01-UC10 sont détaillés dans docs/02-cas-utilisation.md. L’authentification est une précondition des cas métier. Les modèles faisant référence sont indexés dans docs/modeles-reference.md : UML livré dans livrables/use-case-v2/, MCD dans livrables/mcd-final/, MLD dans docs/diagrammes/mld-*. L’annexe vectorielle historique ne contient pas le MCD final.

## F01 - Connexion et profils

**Objectif.** Permettre au personnel de s’inscrire, se connecter et agir selon son rôle.

**Travail réalisé.** Inscription en attente, activation administrative, sessions renouvelées, quatre profils, contrôles serveur, CSRF, mots de passe hachés.

**Conclusion.** Les accès interdits et l’élévation de rôle sont refusés. Le compte transporteur est explicitement facultatif dans le sujet.

Preuves : integration.json ; navigateur.json. Sources : Auth.php ; public/index.php.

## F02 - Transporteurs, chauffeurs et véhicules

**Objectif.** Maintenir sociétés, coordonnées, contacts, contrats et ressources de transport.

**Travail réalisé.** Chauffeurs, permis, habilitations datées ; tracteurs, remorques, porteurs et fourgons, plaques, capacités et équipements. Téléphone modifiable après utilisation, renouvellement d’une habilitation sans raccourcir son passé.

**Conclusion.** Les fiches inutilisées sont supprimables ; les caractéristiques structurelles utilisées sont protégées. Les valeurs avant/après sont historisées.

Preuves : completion.json ; navigateur.json. Sources : Catalog.php ; templates/catalog.php.

## F03 - Quais et rendez-vous

**Objectif.** Réserver des créneaux compatibles sans chevauchement et suivre les quais.

**Travail réalisé.** Types et équipements de quai, indisponibilités, création/déplacement/annulation. Compatibilité du véhicule et de la remorque ; disponibilité du chauffeur, du véhicule et de la remorque entre quais. États libre, réservé, occupé et hors service.

**Conclusion.** Les courses concurrentes sont contrôlées. Actualisation toutes les 30 secondes hors saisie, référence Paris commune à PHP/SQL.

Preuves : integration.json ; completion.json ; heure-paris.json. Sources : Warehouse::appointment/compatible ; Reports::docks.

## F04 - Flux de camions

**Objectif.** Tracer chaque étape, avec ou sans rendez-vous, et mesurer les durées.

**Travail réalisé.** Arrivée, contrôle documentaire, parking facultatif, appel à quai, début, fin et départ. Horodates, attente, immobilisation et retard par rapport au rendez-vous.

**Conclusion.** Transitions impossibles, rétrogrades et doubles occupations refusées. Les ressources constatées sont distinctes du planning.

Preuves : integration.json ; parcours.json. Sources : Warehouse::arrive/transition ; v_visit.

## F05 - Réception des marchandises

**Objectif.** Comparer l’annonce fournisseur à la réception et conserver les réserves.

**Travail réalisé.** Avis et lignes attendues, réceptions partielles, fiche guidée, fractions multilots, DLC, palettes, avaries, emplacements compatibles. Suivi attendu/alloué/reçu/reste et clôture motivée. Réserves générales ou de ligne, même sans marchandise.

**Conclusion.** Un manquant total ne crée aucune fausse palette. La validation est atomique et non rejouable. Réserves consultables dans la réception et la trace des lots concernés.

Preuves : completion.json ; completion-navigateur.json ; parcours.json. Sources : Warehouse::openReceipt/receiveItem/reserveReceipt/validateReceipt/closeNotice.

## F06 - Emplacements et stocks

**Objectif.** Connaître les quantités, les capacités et la provenance dans l’entrepôt.

**Travail réalisé.** Zones ambiant/froid/dangereux, allées, racks, niveaux, emplacements. Articles, propriétaires, dimensions, poids et conditionnement. Stock par article/lot/emplacement ; entrées, transferts, sorties, ajustements motivés ; propositions selon compatibilité et capacités restantes.

**Conclusion.** Le stock est calculé depuis les mouvements. Kg, m³ et équivalents palettes sont contrôlés séparément. Concurrence et conservation des quantités sont testées.

Preuves : integration.json ; integrite-donnees.json. Sources : Warehouse::capacity/suggestions/transfer/adjust ; Reports::stock.

## F07 - Préparation et expédition

**Objectif.** Servir les commandes, constituer les colis, charger et produire les documents.

**Travail réalisé.** Commandes et lignes avec date souhaitée, préparateur, réservation FEFO, confirmation par prélèvement. Affectations quantifiées dans plusieurs colis/palettes. Reprise motivée en brouillon avant expédition. Chargement sur camion sortant avec capacité ; bon de livraison et lettre de voiture avec totaux.

**Conclusion.** Couverture exacte des quantités, refus des suraffectations et doubles expéditions. FEFO satisfait l’alternative FIFO ou FEFO du sujet. Commandes expédiées intégralement.

Preuves : completion.json ; completion-navigateur.json ; parcours.json. Sources : Warehouse::prepare/confirmPickLine/resetPreparation/ship ; templates/order_detail.php.

## F08 - Traçabilité et tableaux de bord

**Objectif.** Retrouver l’historique du lot et fournir les indicateurs demandés.

**Travail réalisé.** Réceptions, réserves, emplacements successifs, commandes et camions sortants. Occupation des quais, attente/immobilisation par transporteur, remplissage par zone, taux d’écart, productivité, proximité DLC. Tableaux, graphiques, impressions et CSV filtrés.

**Conclusion.** Période vide acceptée. Activité sur la période choisie ; stock et DLC à la date actuelle du site, explicitement annoncée. Mouvements de trace paginés.

Preuves : integration.json ; heure-paris.json ; navigateur-riche.json. Sources : Reports.php ; templates/trace.php ; templates/reports.php.

## Conception et normalisation

41 tables, dont journal d’audit et verrou techniques. Les relations 1:N relient sociétés/chauffeurs, avis/lignes et commandes/lignes. Les N:N utilisent des jointures : habilitations, équipements et allocations de colis. PK techniques, clés métier, types, FK et CHECK sont extraits du moteur dans le dictionnaire.

Chaîne de provenance : fournisseur → avis → ligne de réception → fraction/lot → mouvements/emplacements → prélèvement → commande → expédition → camion sortant. Plusieurs réceptions peuvent fournir un lot ; une fraction peut servir plusieurs commandes.

Les descriptions restent dans leurs entités. (package_id, pick_id) détermine qty ; aucun des deux seuls ne suffit. Une réserve porte soit receipt_id soit line_id, jamais les deux (CHECK XOR), pour éviter la dépendance redondante line_id → receipt_id. Les soldes, capacités et durées sont calculés dans les vues.

Les états opérationnels sont des projections contrôlées. L’audit conserve volontairement des instantanés JSON historiques : cette redondance technique est explicitée, distincte du modèle métier normalisé. docs/normalisation-3nf.md expose clés et dépendances ; les propriétés du domaine, et non la seule présence d’une PK, justifient la normalisation.

## Transactions et sécurité

Les services PHP prennent le verrou site_lock puis réalisent les mutations atomiques. Les opérations imbriquées utilisent des points de sauvegarde. Deux procédures assurent verrou et trace ; 119 déclencheurs assurent audit et immuabilité. Le compte applicatif n’a pas de droit DDL ni d’édition du journal.

Requêtes paramétrées, validation serveur/SQL, échappement HTML, sessions renouvelées, CSRF et mots de passe hachés sont contrôlés dans les parcours. Les instantanés excluent password_hash. Configuration et sauvegardes privées sont exclues du dépôt.

## Données fictives en quantité

Graine 70, 90 jours simulés et situations en cours. L’historique est généré directement sous contrôles ; les scénarios actifs utilisent les services métier. Cela ne représente pas 900 cycles saisis dans un navigateur.

| Entité | Nombre |
|---|---:|
| carrier | 20 |
| driver | 80 |
| vehicle | 100 |
| owner | 18 |
| supplier | 20 |
| article | 180 |
| lot | 720 |
| location | 360 |
| appointment | 1350 |
| truck_visit | 1806 |
| receipt | 903 |
| receipt_item | 5130 |
| receipt_reserve | 1365 |
| customer_order | 924 |
| pick | 7873 |
| package | 1800 |
| package_pick | 15541 |
| shipment | 900 |
| stock_movement | 24917 |
| audit_log | 92512 |

L’export sql/07_donnees_demo_riches.sql se charge après la structure. Les triggers recréent l’audit lors de l’import ; ses instantanés diffèrent donc de ceux de la génération. Le jeu réduit reste réservé aux oracles ; un jeu séparé de 10 000 passages sert aux performances.

## Vérification et résultats

Résultats exécutés par les scripts livrés. Bases mutantes dédiées ; démonstration riche consultée en lecture.

| Vérification | Réussis | Échecs | Preuve |
|---|---:|---:|---|
| Intégration métier/SQL | 64 | 0 | integration.json |
| Nouveaux cas métier | 23 | 0 | completion.json |
| Navigateur général | 71 | 0 | navigateur.json |
| Parcours complet | 31 | 0 | parcours.json |
| Parcours guidés ajoutés | 34 | 0 | completion-navigateur.json |
| Base riche en lecture | 16 | 0 | navigateur-riche.json |

Horloge Paris : 8 contrôles. Intégrité riche : 82 contrôles métier/FK. Migration : 42 contrôles des colonnes préexistantes et allocations.

Restauration : 41 tables comparées par comptes et checksums, 119 déclencheurs et 2 procédures. Une mutation vérifie l’audit dans la copie.

Installation propre : configuration et compte SQL neufs, trois refus de booléens invalides, CRUD d’une relation inutilisée et huit routes authentifiées.

Les 64 assertions initiales incluent quatre courses entre deux connexions, la conservation du stock, les rollbacks et les oracles des indicateurs. Les 23 nouveaux cas couvrent réserves, restes, clôtures, ressources, modifications permises, reprise et colis. Les contrôles mobiles sont effectués dans Edge à 390 px, pas sur appareil physique.

Reproduction : installer une base neuve, charger scripts/seed.php. integration.php utilise BD70_TEST_DATABASE ; completion.php utilise BD70_DATABASE. Les tests fixent le 22/10/2026 à midi ; le serveur navigateur dédié doit recevoir BD70_NOW=2026-10-22 12:00:00 et une base bd70_test*. Ne jamais figer la démonstration.

## Analyse des performances

Environnement : 10.4.32-MariaDB, PHP 8.2.12, Windows ; base isolée bd70_perf_completion. Chauffe puis dix exécutions PDO avec récupération des résultats. Paramètres, EXPLAIN, index et observations dans performances.json.

| Requête | Médiane ms | Min ms | Max ms |
|---|---:|---:|---:|
| disponibilite_quai | 1.940 | 1.427 | 3.231 |
| recherche_passages | 8.927 | 4.302 | 13.486 |
| recherche_stock | 61.910 | 46.158 | 75.219 |
| emplacements | 50.225 | 37.541 | 61.628 |
| historique_lot | 56.277 | 45.494 | 65.249 |
| selection_fefo | 74.066 | 67.637 | 89.753 |
| statistiques_transporteur | 25.255 | 19.178 | 30.299 |
| remplissage_zone | 49.243 | 35.433 | 60.719 |

Index comparé : idx_appointment_slot uniquement ; index FK simple maintenu. Lecture avant 10.481 ms, après 1.361 ms. Les dix observations et le coût INSERT + ROLLBACK sont publiés dans le JSON.

v_visit joint les événements uniques (passage, état) au lieu d’agréger tout l’historique. v_location_usage calcule les capacités physiques sans toutes les jointures de v_stock. La seconde correction répond à une expiration de 30 secondes observée avec les données riches.

Les navigations riches ont été rejouées après correction : navigateur-riche.json contient des observations uniques, avec rendu et ressources, distinctes des dix mesures PDO. La page Indicateurs a alors chargé en environ 2,2 s dans ce relevé. Le jeu volumétrique de 10 000 passages et le catalogue riche de 180 articles sont complémentaires.

Ces mesures locales ne sont pas une certification de charge industrielle. Les comparaisons historiques de réécriture ne contrôlent pas cache et charge à l’identique. Le verrou global limite le parallélisme.

## Installation et conservation des données

scripts/start.ps1 démarre MariaDB et PHP localement ; une nouvelle installation charge le SQL riche. Le README décrit les commandes et comptes fictifs. Une configuration existante n’est pas écrasée.

La migration additive est testée sur une restauration distincte : colonnes anciennes et allocations conservées ; les nouvelles entrées d’audit dues à la migration sont normales. L’ancienne base bd70_demo_final est conservée. La démonstration active est bd70_demo_rich_final.

La restauration compare les 41 tables par comptes/checksums, vérifie 119 déclencheurs et deux procédures, puis provoque une historisation dans la copie. Installation sur copie propre également testée.

## Limites et bilan

Tous les domaines obligatoires ont un accès web. Le rôle transporteur externe est facultatif et non retenu ; FEFO est une stratégie autorisée. Les commandes sont expédiées intégralement.

Application monosite, locale, PHP 8.2.12 / MariaDB 10.4.32 / Windows / Edge. Pas de déploiement public ni de test sur téléphone physique. Le planning se rafraîchit toutes les 30 secondes hors saisie.

SQL DATETIME stocke les heures civiles de Paris. Seules les heures locales ambiguës/inexistantes des changements saisonniers sont refusées. Changer le fuseau ne corrige pas une horloge système physiquement fausse.

Les invariants entre lignes reposent sur les services transactionnels et le verrou global. Un administrateur SQL peut les contourner. L’historique riche est simulé directement puis vérifié ; il ne représente pas 900 cycles saisis au navigateur.

Les sélecteurs sont limités à 2 000 propositions, avec une recherche préalable. Les mouvements de trace sont paginés ; ses réceptions et commandes restent des tableaux complets. Les propriétés structurelles utilisées et les historiques sont protégés ; corrections par reprise, annulation ou ajustement selon l’état.

Les documents consultent les libellés actuels ; ils ne constituent pas une archive réglementaire figée. GPS, EDI, facturation, signature électronique et chargement géométrique ne sont pas demandés ni réalisés.

Auteurs : ELIOTT LE, SEMIH TASKIN et Thomas VUILLIN. Répartition individuelle non communiquée, donc non inventée. Date de remise et modalités de soutenance A26 à confirmer par le groupe.


Les fonctionnalités obligatoires des huit domaines sont présentes, avec des preuves ciblées métier, SQL et navigateur. Les corrections renforcent les cas non nominaux et les données riches ont révélé une requête trop coûteuse, corrigée avant livraison. Les tests ne constituent pas une certification exhaustive ou industrielle.

L’IA a aidé à l’audit, à l’implémentation, au jeu fictif et à la vérification. Les auteurs doivent pouvoir expliquer le modèle, les règles, les requêtes et les limites du projet.

## Index des livrables

docs/matrice-conformite.md : couverture. docs/02-cas-utilisation.md : scénarios. docs/diagrammes/ : DOT/SVG et métadonnées. Dictionnaire, normalisation et matrice CRUD : conception. sql/ : structure, procédures, triggers, index, migration et données. tests/ et livrables/preuves/ : scripts et résultats. README.md : lancement.

DIAGRAMMES-BD70.pdf est un recueil historique, conservé sans être régénéré : ses MCD sont incomplets et il ne constitue pas la référence finale. Le PDF de ce rapport est antérieur à la consolidation du 3 novembre ; pour les références techniques actuelles, utiliser docs/modeles-reference.md et la présente source Markdown.
