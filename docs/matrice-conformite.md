# Matrice de conformité après réalisation

Références techniques consolidées : [index des modèles](modeles-reference.md). Le recueil PDF actualisé réunit le use case corrigé, le dernier MCD (retour enseignant attendu) et les MLD courants.

Les huit domaines obligatoires sont présents dans l’interface. Les preuves couvrent des scénarios ciblés ; charger une rubrique ne prouve pas tous ses CRUD. L’audit initial reste conservé dans livrables/audit-2026-10-28/.

## F01 - Connexion et profils

**Objectif.** Permettre au personnel de s’inscrire, se connecter et agir selon son rôle.

**Travail réalisé.** Inscription en attente, activation administrative, sessions renouvelées, cinq profils, contrôles serveur, CSRF, mots de passe hachés.

**Conclusion.** Les accès interdits et l’élévation de rôle sont refusés. Le compte transporteur est explicitement facultatif dans le sujet.

Implémentation : Auth.php ; public/index.php. Preuves : integration.json ; navigateur.json, dans livrables/preuves/.

## F02 - Transporteurs, chauffeurs et véhicules

**Objectif.** Maintenir sociétés, coordonnées, contacts, contrats et ressources de transport.

**Travail réalisé.** Chauffeurs, permis, habilitations datées ; tracteurs, remorques, porteurs et fourgons, plaques, capacités et équipements. Téléphone modifiable après utilisation, renouvellement d’une habilitation sans raccourcir son passé.

**Conclusion.** Les fiches inutilisées sont supprimables ; les caractéristiques structurelles utilisées sont protégées. Les valeurs avant/après sont historisées.

Implémentation : Catalog.php ; templates/catalog.php. Preuves : completion.json ; navigateur.json, dans livrables/preuves/.

## F03 - Quais et rendez-vous

**Objectif.** Réserver des créneaux compatibles sans chevauchement et suivre les quais.

**Travail réalisé.** Types et équipements de quai, indisponibilités, création/déplacement/annulation. Compatibilité du véhicule et de la remorque ; disponibilité du chauffeur, du véhicule et de la remorque entre quais. États libre, réservé, occupé et hors service.

**Conclusion.** Les courses concurrentes sont contrôlées. Actualisation toutes les 30 secondes hors saisie, référence Paris commune à PHP/SQL.

Implémentation : Warehouse::appointment/compatible ; Reports::docks. Preuves : integration.json ; completion.json ; heure-paris.json, dans livrables/preuves/.

## F04 - Flux de camions

**Objectif.** Tracer chaque étape, avec ou sans rendez-vous, et mesurer les durées.

**Travail réalisé.** Arrivée, contrôle documentaire, parking facultatif, appel à quai, début, fin et départ. Horodates, attente, immobilisation et retard par rapport au rendez-vous.

**Conclusion.** Transitions impossibles, rétrogrades et doubles occupations refusées. Les ressources constatées sont distinctes du planning.

Implémentation : Warehouse::arrive/transition ; v_visit. Preuves : integration.json ; parcours.json, dans livrables/preuves/.

## F05 - Réception des marchandises

**Objectif.** Comparer l’annonce fournisseur à la réception et conserver les réserves.

**Travail réalisé.** Avis et lignes attendues, réceptions partielles, fiche guidée, fractions multilots, DLC, palettes, avaries, emplacements compatibles. Suivi attendu/alloué/reçu/reste et clôture motivée. Réserves générales ou de ligne, même sans marchandise.

**Conclusion.** Un manquant total ne crée aucune fausse palette. La validation est atomique et non rejouable. Réserves consultables dans la réception et la trace des lots concernés.

Implémentation : Warehouse::openReceipt/receiveItem/reserveReceipt/validateReceipt/closeNotice. Preuves : completion.json ; completion-navigateur.json ; parcours.json, dans livrables/preuves/.

## F06 - Emplacements et stocks

**Objectif.** Connaître les quantités, les capacités et la provenance dans l’entrepôt.

**Travail réalisé.** Zones ambiant/froid/dangereux, allées, racks, niveaux, emplacements. Articles, propriétaires, dimensions, poids et conditionnement. Stock par article/lot/emplacement ; entrées, transferts, sorties, ajustements motivés ; propositions selon compatibilité et capacités restantes.

**Conclusion.** Le stock est calculé depuis les mouvements. Kg, m³ et équivalents palettes sont contrôlés séparément. Concurrence et conservation des quantités sont testées.

Implémentation : Warehouse::capacity/suggestions/transfer/adjust ; Reports::stock. Preuves : integration.json ; integrite-donnees.json, dans livrables/preuves/.

## F07 - Préparation et expédition

**Objectif.** Servir les commandes, constituer les colis, charger et produire les documents.

**Travail réalisé.** Commandes et lignes avec date souhaitée, préparateur, réservation FEFO, confirmation par prélèvement. Affectations quantifiées dans plusieurs colis/palettes. Reprise motivée en brouillon avant expédition. Chargement sur camion sortant avec capacité ; bon de livraison et lettre de voiture avec totaux.

**Conclusion.** Couverture exacte des quantités, refus des suraffectations et doubles expéditions. FEFO satisfait l’alternative FIFO ou FEFO du sujet. Commandes expédiées intégralement.

Implémentation : Warehouse::prepare/confirmPickLine/resetPreparation/ship ; templates/order_detail.php. Preuves : completion.json ; completion-navigateur.json ; parcours.json, dans livrables/preuves/.

## F08 - Traçabilité et tableaux de bord

**Objectif.** Retrouver l’historique du lot et fournir les indicateurs demandés.

**Travail réalisé.** Réceptions, réserves, emplacements successifs, commandes et camions sortants. Occupation des quais, attente/immobilisation par transporteur, remplissage par zone, taux d’écart, productivité, proximité DLC. Tableaux, graphiques, impressions et CSV filtrés.

**Conclusion.** Période vide acceptée. Activité sur la période choisie ; stock et DLC à la date actuelle du site, explicitement annoncée. Mouvements de trace paginés.

Implémentation : Reports.php ; templates/trace.php ; templates/reports.php. Preuves : integration.json ; heure-paris.json ; navigateur-riche.json, dans livrables/preuves/.

## Exigences générales et grille

| Critère | Réalisation |
|---|---|
| UML, MCD, MLD | Diagrammes DOT/SVG, recueil PDF et dictionnaire du moteur réel |
| PK, types, 1:N, N:N, normalisation | 41 tables ; FK, CHECK, clés métier et dépendances documentées |
| Ajout, édition, suppression | Formulaires de référentiels/brouillons ; correction et annulation métier des faits protégés |
| Contrôle de saisie et recherches | Validation PHP/SQL, filtres multicritères, pagination et recherche des références |
| Statistiques, graphiques et états | Six familles d’indicateurs, trois exports CSV et documents imprimables |
| Multi-utilisateurs et automatisation | Cinq rôles ; courses à deux connexions ; 120 triggers et deux procédures |
| Données factices en quantité | SQL riche, 90 jours simulés ; 82 contrôles métier/FK |
| Rapport et performance | Auteurs, objectifs/travail/conclusion ; huit requêtes, dix mesures et EXPLAIN |
