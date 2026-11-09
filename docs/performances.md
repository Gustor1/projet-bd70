# Rapport d’analyse des performances

Fichier généré par `scripts/build-performances-md.py` à partir des preuves JSON. Mesures du 2026-11-08 (base volumétrique) et du 2026-11-08 (jeu de démonstration). Moteur : 10.4.32-MariaDB ; PHP 8.2.12 ; Windows.

## Méthode

- Chaque requête est exécutée une fois pour chauffer le cache, puis **dix fois** depuis PHP/PDO avec récupération de toutes les lignes. On retient la **médiane**, plus robuste que la moyenne face à une mesure isolée lente ; minimum et maximum sont dans les JSON.
- Le plan d’exécution est obtenu avec `EXPLAIN` sur la même requête et les mêmes paramètres.
- **Base volumétrique** `bd70_perf_opti` : 10003 passages, 22011 mouvements de stock, créée par `scripts/performance.php`.
- **Jeu de démonstration** `bd70_test_opti1` : 1806 passages, 24917 mouvements, 7873 prélèvements, chargé par `scripts/import-demo.php`.
- Les temps mesurent le travail SQL sur une machine de développement ; ils ne prédisent ni le temps d’affichage d’une page, ni un comportement sous forte charge.

## Temps d’exécution des requêtes principales (médianes, ms)

| Requête | Écran qui l’utilise | Base volumétrique | Jeu de démonstration | Lignes (démo) |
|---|---|---:|---:|---:|
| Disponibilité d’un quai | Planning : refus des chevauchements | 0,936 | 1,207 | 0 |
| Recherche de passages | Passages camions : filtres période, transporteur, état | 67,859 | 2,238 | 20 |
| Recherche de stock | Stocks : filtres article, propriétaire, zone | 31,890 | 2,110 | 20 |
| Emplacements compatibles | Réception : proposition de rangement | 16,653 | 22,271 | 120 |
| Historique d’un lot | Traçabilité | 51,330 | 52,727 | 20 |
| Sélection FEFO | Préparation : réservation des prélèvements | 54,669 | 1,755 | 5 |
| Statistiques par transporteur (GROUP BY) | Indicateurs | 62,456 | 25,401 | 20 |
| Transporteurs au-dessus du seuil (HAVING) | Indicateurs | 58,254 | 17,124 | 20 |
| Rendez-vous courants et historisés (UNION ALL) | Rendez-vous historisés | 31,029 | 3,525 | 20 |
| Remplissage par zone | Indicateurs | 19,966 | 36,097 | 6 |

Le texte SQL exact et les paramètres de chaque requête sont dans `sql/requetes_metier.sql` et dans les deux JSON.

## Effet d’un index : recherche de chevauchement de créneaux

```sql
SELECT reference FROM appointment
WHERE dock_id=? AND status='active' AND starts_at<? AND ends_at>?;
```

Comparaison sur la base volumétrique, même requête et mêmes paramètres : index simple sur `dock_id` (avant) puis index composé `idx_appointment_slot(dock_id, status, starts_at, ends_at)` (après). Médiane **7,220 ms → 1,405 ms**, soit un gain absolu de 5,815 ms et un gain relatif de 81 %.

Avant :

| table | type | index utilisé | lignes estimées | Extra |
|---|---|---|---:|---|
| appointment | ref | idx_appt_dock_baseline | 3335 | Using where |

Après :

| table | type | index utilisé | lignes estimées | Extra |
|---|---|---|---:|---|
| appointment | range | idx_appointment_slot | 971 | Using index condition |

Lecture : le type passe de `ref` (toutes les lignes du quai) à `range` (plage sur les horaires) et le nombre de lignes estimées diminue. `Using index condition` signifie que le filtre sur le statut et les horaires est appliqué dans l’index avant de lire la table.
Contrepartie mesurée : une insertion de rendez-vous (trigger compris, puis ROLLBACK) prend 17,842 ms avant et 21,265 ms après. Ces deux séries ne montrent pas de surcoût mesurable de l’index composé à ce volume ; l’index reste un coût de stockage et de mise à jour, d’où un nombre limité d’index (8 index secondaires, en plus des index créés automatiquement par MariaDB sur les clés primaires, UNIQUE et étrangères).

## Plan d’une agrégation : statistiques par transporteur

| table | type | index utilisé | lignes estimées | Extra |
|---|---|---|---:|---|
| v | ALL | — | 1806 | Using temporary; Using filesort |
| d | eq_ref | PRIMARY | 1 | Using index |
| ve | eq_ref | PRIMARY | 1 |  |
| ea | eq_ref | visit_id | 1 | Using index condition; Using where |
| ew | eq_ref | visit_id | 1 | Using where |
| ed | eq_ref | visit_id | 1 | Using where |
| c | ALL | — | 20 | Using where; Using join buffer (flat, BNL join) |

La vue `v_visit` est fusionnée dans la requête (`SIMPLE`) : chaque passage rejoint ses événements par l’index unique `(visit_id, state)` (`eq_ref`, une ligne). `Using temporary; Using filesort` correspond au regroupement par transporteur, sur 20 lignes seulement. La version avec `HAVING` a le même plan : le filtre s’applique après le regroupement, sans coût de lecture supplémentaire.

## Optimisation du stock : table de soldes tenue à jour par triggers

**Constat (mesure avant).** Le solde n’était pas conservé : la vue `v_balance` recalculait chaque solde par `GROUP BY` sur tout l’historique `stock_movement` (24917 mouvements dans le jeu de démonstration) et `v_reserved` sur les 7873 prélèvements. Comme ces vues contiennent un `GROUP BY`, MariaDB les matérialise en tables temporaires (lignes `<derived…>` du plan) et lit ces tables **en entier** (`ALL`) avant d’appliquer le filtre sur l’article :

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
| <derived6> | ref | key0 | 2 | Using where |
| pick | ref | location_id | 1 | Using index condition; Using where |
| m | ALL | — | 24997 | Using temporary; Using filesort |
| p | eq_ref | PRIMARY | 1 | Using where |

**Optimisation (`sql/09_optimisation.sql`).** Même démarche que le TD « Automatisation » (table de statistiques hebdomadaires mise à jour par un déclencheur) :

- table `stock_balance(receipt_item_id, location_id, qty, reserved_qty)`, clé primaire composée ;
- trigger `balance_movement_insert` : chaque mouvement ajoute sa variation au solde (`INSERT … ON DUPLICATE KEY UPDATE`, coût constant) ; une sortie lit fraction, emplacement et quantité dans son prélèvement ;
- triggers `balance_pick_insert/update/delete` : la quantité réservée suit les prélèvements prévus ou confirmés ; `pick_shipped_frozen` interdit de modifier un prélèvement déjà expédié ;
- vues `v_balance` et `v_reserved` réécrites sur `stock_balance` : sans `GROUP BY`, elles sont fusionnées dans la requête et lues par clé ;
- fonction stockée `stock_disponible(article, date)`, utilisée par la préparation de commande ;
- initialisation des soldes existants dans une seule transaction (`START TRANSACTION … COMMIT`), par `scripts/migrate-optimisation.php`.

Plan après optimisation, même requête :

| table | type | index utilisé | lignes estimées | Extra |
|---|---|---|---:|---|
| a | const | PRIMARY | 1 | Using temporary; Using filesort |
| o | const | PRIMARY | 1 | Using index |
| z | const | PRIMARY | 1 | Using index |
| t | ref | article_id | 4 |  |
| i | ref | lot_id | 1 |  |
| cl | eq_ref | PRIMARY | 1 |  |
| c | eq_ref | PRIMARY | 1 | Using index |
| stock_balance | ref | PRIMARY | 1 | Using where |
| l | eq_ref | PRIMARY | 1 |  |
| n | eq_ref | PRIMARY | 1 |  |
| r | eq_ref | PRIMARY | 1 |  |
| a | eq_ref | PRIMARY | 1 | Using where |
| stock_balance | eq_ref | PRIMARY | 1 | Using where |

**Résultats** (`scripts/performance-optimisation.php`, base `bd70_test_opti1`, mêmes données ; « avant » = anciennes vues et pas de trigger de solde ; médiane de 15 mesures) :

| Requête | Écran | Avant (ms) | Après (ms) | Gain absolu (ms) | Gain relatif |
|---|---|---:|---:|---:|---:|
| Recherche de stock | Stocks : filtres article, propriétaire, zone | 72,289 | 1,986 | 70,303 | 97 % |
| Sélection FEFO | Préparation : réservation FEFO | 75,124 | 1,984 | 73,141 | 97 % |
| Emplacements compatibles | Réception : emplacements compatibles | 96,236 | 25,454 | 70,781 | 74 % |
| Remplissage par zone | Indicateurs : remplissage par zone | 101,392 | 19,980 | 81,412 | 80 % |
| Contrôle du stock libre | Transfert et ajustement : contrôle du stock libre | 63,809 | 0,375 | 63,434 | 99 % |

**Contrepartie.** Chaque écriture de mouvement exécute un trigger de plus : 5,225 ms avant, 5,864 ms après (insertion puis ROLLBACK). L’écart est de l’ordre du bruit de mesure : pas de surcoût mesurable à ce volume. Le solde devient une **redondance contrôlée** : la référence reste l’historique immuable, la vue `v_balance_controle` le recalcule et `scripts/validate-data.php` vérifie que les deux sont égaux (0 écart après la mesure). `stock_balance` n’est modifiable que par les triggers (aucun droit d’écriture pour le compte applicatif).

## Autres optimisations appliquées

- Requêtes paginées (`LIMIT 20`) et colonnes sélectionnées explicitement dans les requêtes mesurées.
- `v_visit` joint les événements uniques `(passage, état)` au lieu d’agréger tout l’historique ; `v_location_usage` calcule l’occupation sans les jointures de `v_stock`.
- Contrôle du stock libre avant transfert ou ajustement : une ligne de `stock_balance` lue par clé primaire au lieu de deux agrégations.
- L’archivage des rendez-vous (`archive_appointments`, évènement nocturne) allège la table consultée par le planning ; la vue `v_appointment_all` garde l’accès à l’ensemble avec `UNION ALL`.
- Écritures concurrentes : le verrou `lock_site` (`SELECT … FOR UPDATE`) garantit la cohérence des contrôles portant sur plusieurs lignes, mais sérialise les écritures. Pour un site très actif, il faudrait des verrous par quai ou par emplacement.
