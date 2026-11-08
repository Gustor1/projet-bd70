# Rapport d’analyse des performances

Fichier généré par `scripts/build-performances-md.py` à partir des preuves JSON. Mesures du 2026-11-07 (base volumétrique) et du 2026-11-07 (jeu de démonstration). Moteur : 10.4.32-MariaDB ; PHP 8.2.12 ; Windows.

## Méthode

- Chaque requête est exécutée une fois pour chauffer le cache, puis **dix fois** depuis PHP/PDO avec récupération de toutes les lignes. On retient la **médiane**, plus robuste que la moyenne face à une mesure isolée lente ; minimum et maximum sont dans les JSON.
- Le plan d’exécution est obtenu avec `EXPLAIN` sur la même requête et les mêmes paramètres.
- **Base volumétrique** `bd70_perf_revue` : 10003 passages, 22011 mouvements de stock, créée par `scripts/performance.php`.
- **Jeu de démonstration** `bd70_test_hist` : 1806 passages, 24917 mouvements, 7873 prélèvements, chargé par `scripts/import-demo.php`.
- Les temps mesurent le travail SQL sur une machine de développement ; ils ne prédisent ni le temps d’affichage d’une page, ni un comportement sous forte charge.

## Temps d’exécution des requêtes principales (médianes, ms)

| Requête | Écran qui l’utilise | Base volumétrique | Jeu de démonstration | Lignes (démo) |
|---|---|---:|---:|---:|
| Disponibilité d’un quai | Planning : refus des chevauchements | 0,497 | 0,360 | 0 |
| Recherche de passages | Passages camions : filtres période, transporteur, état | 33,689 | 0,987 | 20 |
| Recherche de stock | Stocks : filtres article, propriétaire, zone | 30,488 | 28,437 | 20 |
| Emplacements compatibles | Réception : proposition de rangement | 34,046 | 47,007 | 120 |
| Historique d’un lot | Traçabilité | 23,380 | 36,502 | 20 |
| Sélection FEFO | Préparation : réservation des prélèvements | 34,644 | 35,849 | 5 |
| Statistiques par transporteur (GROUP BY) | Indicateurs | 35,363 | 14,641 | 20 |
| Transporteurs au-dessus du seuil (HAVING) | Indicateurs | 34,959 | 10,713 | 20 |
| Rendez-vous courants et historisés (UNION ALL) | Rendez-vous historisés | 12,733 | 1,993 | 20 |
| Remplissage par zone | Indicateurs | 23,356 | 41,513 | 6 |

Le texte SQL exact et les paramètres de chaque requête sont dans `sql/requetes_metier.sql` et dans les deux JSON.

## Effet d’un index : recherche de chevauchement de créneaux

```sql
SELECT reference FROM appointment
WHERE dock_id=? AND status='active' AND starts_at<? AND ends_at>?;
```

Comparaison sur la base volumétrique, même requête et mêmes paramètres : index simple sur `dock_id` (avant) puis index composé `idx_appointment_slot(dock_id, status, starts_at, ends_at)` (après). Médiane **3,997 ms → 0,905 ms**.

Avant :

| table | type | index utilisé | lignes estimées | Extra |
|---|---|---|---:|---|
| appointment | ref | idx_appt_dock_baseline | 3335 | Using where |

Après :

| table | type | index utilisé | lignes estimées | Extra |
|---|---|---|---:|---|
| appointment | range | idx_appointment_slot | 971 | Using index condition |

Lecture : le type passe de `ref` (toutes les lignes du quai) à `range` (plage sur les horaires) et le nombre de lignes estimées diminue. `Using index condition` signifie que le filtre sur le statut et les horaires est appliqué dans l’index avant de lire la table.
Contrepartie mesurée : une insertion de rendez-vous (trigger compris, puis ROLLBACK) prend 11,960 ms avant et 8,570 ms après. Ces deux séries ne montrent pas de surcoût mesurable de l’index composé à ce volume ; l’index reste un coût de stockage et de mise à jour, d’où un nombre limité d’index (8 index secondaires, en plus des index créés automatiquement par MariaDB sur les clés primaires, UNIQUE et étrangères).

## Plan d’une agrégation : statistiques par transporteur

| table | type | index utilisé | lignes estimées | Extra |
|---|---|---|---:|---|
| c | ALL | — | 20 | Using temporary; Using filesort |
| ve | ref | carrier_id | 2 | Using index |
| v | ref | vehicle_id | 1 |  |
| ea | eq_ref | visit_id | 1 | Using index condition; Using where |
| d | eq_ref | PRIMARY | 1 | Using index |
| ew | eq_ref | visit_id | 1 | Using where |
| ed | eq_ref | visit_id | 1 | Using where |

La vue `v_visit` est fusionnée dans la requête (`SIMPLE`) : chaque passage rejoint ses événements par l’index unique `(visit_id, state)` (`eq_ref`, une ligne). `Using temporary; Using filesort` correspond au regroupement par transporteur, sur 20 lignes seulement. La version avec `HAVING` a le même plan : le filtre s’applique après le regroupement, sans coût de lecture supplémentaire.

## Limite identifiée : le stock calculé depuis les mouvements

| table | type | index utilisé | lignes estimées | Extra |
|---|---|---|---:|---|
| a | const | PRIMARY | 1 | Using temporary; Using filesort |
| o | const | PRIMARY | 1 | Using index |
| z | const | PRIMARY | 1 | Using index |
| t | ref | article_id | 4 |  |
| i | ref | lot_id | 1 |  |
| cl | eq_ref | PRIMARY | 1 |  |
| c | eq_ref | PRIMARY | 1 | Using index |
| <derived3> | ref | key0 | 10 | Using where |
| l | eq_ref | PRIMARY | 1 |  |
| n | eq_ref | PRIMARY | 1 |  |
| r | eq_ref | PRIMARY | 1 |  |
| a | eq_ref | PRIMARY | 1 | Using where |
| <derived6> | ref | key0 | 10 | Using where |
| pick | ALL | — | 8116 | Using where; Using temporary; Using filesort |
| m | ALL | — | 24934 | Using temporary; Using filesort |
| p | eq_ref | PRIMARY | 1 | Using where |

Les lignes `DERIVED` montrent que la vue `v_balance`, qui contient un `GROUP BY`, est matérialisée en table temporaire : MariaDB lit **tout** l’historique `stock_movement` (`ALL`) et toutes les réservations `pick` avant d’appliquer le filtre sur l’article. Le temps reste de quelques dizaines de millisecondes avec le jeu actuel, mais il augmentera avec la taille de l’historique.

Ce coût est le prix d’un choix de conception : le solde n’est jamais stocké, il est toujours recalculé depuis des mouvements immuables, ce qui évite deux valeurs à synchroniser (3NF). Si le volume l’exigeait, deux pistes : (1) une table de soldes par fraction et emplacement, mise à jour dans la même transaction que chaque mouvement ; (2) l’historisation des mouvements anciens, sur le modèle de `appointment_archive`, avec un solde d’ouverture.

## Autres optimisations appliquées

- Requêtes paginées (`LIMIT 20`) et colonnes sélectionnées explicitement dans les requêtes mesurées.
- `v_visit` joint les événements uniques `(passage, état)` au lieu d’agréger tout l’historique ; `v_location_usage` calcule l’occupation sans les jointures de `v_stock`.
- L’archivage des rendez-vous (`archive_appointments`, évènement nocturne) allège la table consultée par le planning ; la vue `v_appointment_all` garde l’accès à l’ensemble avec `UNION ALL`.
- Écritures concurrentes : le verrou `lock_site` (`SELECT … FOR UPDATE`) garantit la cohérence des contrôles portant sur plusieurs lignes, mais sérialise les écritures. Pour un site très actif, il faudrait des verrous par quai ou par emplacement.
