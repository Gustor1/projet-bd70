# Rapport de performances

Mesures réelles locales, moteur 10.4.32-MariaDB, PHP 8.2.12. Machine : voir livrables/preuves/machine.json. Buffer pool 128 Mio, isolation READ COMMITTED. Le temps publié est un aller-retour PDO avec récupération des résultats, pas un temps CPU serveur isolé.

Protocole : chauffe puis dix exécutions sur le même jeu et les mêmes paramètres, horloge hrtime. Les résultats bruts, EXPLAIN, index et volumes exhaustifs sont dans livrables/preuves/performances.json. Aucune charge utilisateur simultanée contrôlée n’a été appliquée pendant les mesures ; dispersion et contexte local à prendre en compte.

| Requête | Médiane ms | Min ms | Max ms | Lignes |
|---|---:|---:|---:|---:|
| disponibilite_quai | 1.553 | 1.327 | 1.826 | 0 |
| recherche_passages | 539.618 | 508.200 | 590.012 | 20 |
| recherche_stock | 88.402 | 85.454 | 109.745 | 20 |
| emplacements | 89.460 | 86.974 | 102.198 | 2 |
| historique_lot | 56.541 | 55.112 | 60.425 | 20 |
| selection_fefo | 158.653 | 155.135 | 208.038 | 20 |
| statistiques_transporteur | 586.225 | 522.160 | 840.049 | 2 |
| remplissage_zone | 87.453 | 84.906 | 89.983 | 3 |

## Jeu mesuré
10003 passages, 60019 événements, 2004 lignes de réception, 22011 mouvements, 112180 entrées d’audit. Graine 70, référence 22/10/2026. Stock non négatif, capacités et transferts conservatifs contrôlés. Les lignes volumétriques sont simulées par SQL sur une base dédiée, pas saisies dans le navigateur.

## Comparaison contrôlée
Index changé : idx_appointment_slot uniquement ; index FK simple maintenu. Lecture avant 5.909 ms, après 1.563 ms. Index quai/état/début/fin adapté aux filtres du planning. Plans complets avant et après dans le JSON.
Écriture : INSERT de rendez-vous avec trigger puis ROLLBACK, une chauffe et dix répétitions ; avant 5.554 ms, après 6.738 ms. Ce protocole inclut journal et rollback ; il ne mesure pas un débit durable de commits. Une petite différence inférieure à la dispersion ne permet pas de conclure à un coût universel.

## Temps HTTP distincts
Démonstration : un appel de chauffe puis dix réponses authentifiées par route ; temps Playwright request jusqu’à réception du corps, sans les ressources CSS/JS et sans exécution/rendu du navigateur. Jeu petit, donc non comparable directement aux mesures volumétriques PDO.

| Page | Médiane ms | Min–max ms |
|---|---:|---|
| planning | 60.273 | 43.835–91.331 |
| stock | 345.892 | 332.739–564.234 |
| reports | 364.123 | 349.713–585.302 |

## Analyse
Les vues de passages agrègent encore l’ensemble de l’historique avant certains filtres : elles dominent la durée. Le verrou global privilégie la compréhension et la sûreté ; une vraie mesure de débit concurrent serait nécessaire avant de le remplacer par des verrous par ressource. Les FK/PK, jointures et index de dates sont justifiés par les accès réels. Aucun partitionnement ou réplication artificiel.

## SQL et paramètres

### disponibilite_quai
```sql
SELECT reference FROM appointment WHERE dock_id=? AND status='active' AND starts_at<? AND ends_at>?;
```
Paramètres ordonnés : `[1, "2025-05-02 09:00:00", "2025-05-02 08:00:00"]`.
Index/plans : se reporter à l’entrée correspondante du JSON brut ; les métadonnées complètes y sont conservées.

### recherche_passages
```sql
SELECT reference,carrier_name,status,arrived_at FROM v_visit WHERE arrived_at>=? AND arrived_at<? AND carrier_id=? AND status=? ORDER BY arrived_at DESC LIMIT 20;
```
Paramètres ordonnés : `["2025-05-01", "2025-06-01", 1, "departed"]`.
Index/plans : se reporter à l’entrée correspondante du JSON brut ; les métadonnées complètes y sont conservées.

### recherche_stock
```sql
SELECT sku,lot_code,location_code,qty,available_qty FROM v_stock WHERE article_id=? AND owner_id=? AND zone_id=? ORDER BY lot_code,location_code LIMIT 20;
```
Paramètres ordonnés : `[1, 1, 1]`.
Index/plans : se reporter à l’entrée correspondante du JSON brut ; les métadonnées complètes y sont conservées.

### emplacements
```sql
SELECT l.code,u.used_kg,u.used_pallets FROM v_location l JOIN v_location_usage u ON u.id=l.id JOIN article a ON a.id=? WHERE l.storage=a.storage AND l.width_m>=a.width_m AND l.height_m>=a.height_m AND l.depth_m>=a.depth_m AND u.used_kg+?*a.unit_kg<=l.max_kg AND u.used_m3+?*a.width_m*a.height_m*a.depth_m<=l.capacity_m3 AND u.used_pallets+?/a.units_per_pallet<=l.max_pallets;
```
Paramètres ordonnés : `[1, 5, 5, 5]`.
Index/plans : se reporter à l’entrée correspondante du JSON brut ; les métadonnées complètes y sont conservées.

### historique_lot
```sql
SELECT m.operation_ref,m.created_at,m.delta,l.code FROM stock_movement m JOIN receipt_item i ON i.id=m.receipt_item_id JOIN location l ON l.id=m.location_id WHERE i.lot_id=? ORDER BY m.created_at,m.id LIMIT 20;
```
Paramètres ordonnés : `[7]`.
Index/plans : se reporter à l’entrée correspondante du JSON brut ; les métadonnées complètes y sont conservées.

### selection_fefo
```sql
SELECT receipt_item_id,location_id,available_qty,expires_on FROM v_stock WHERE article_id=? AND available_qty>0 AND blocked=0 AND (expires_on IS NULL OR expires_on>=?) ORDER BY expires_on IS NULL,expires_on,received_at,receipt_item_id,location_id LIMIT 20;
```
Paramètres ordonnés : `[1, "2026-10-22"]`.
Index/plans : se reporter à l’entrée correspondante du JSON brut ; les métadonnées complètes y sont conservées.

### statistiques_transporteur
```sql
SELECT carrier_name,COUNT(*) passages,AVG(wait_minutes),AVG(immobilized_minutes) FROM v_visit WHERE arrived_at>=? AND arrived_at<? GROUP BY carrier_id,carrier_name;
```
Paramètres ordonnés : `["2025-05-01", "2025-06-01"]`.
Index/plans : se reporter à l’entrée correspondante du JSON brut ; les métadonnées complètes y sont conservées.

### remplissage_zone
```sql
SELECT l.zone_name,SUM(u.used_kg),SUM(l.max_kg),SUM(u.used_pallets),SUM(l.max_pallets) FROM v_location l JOIN v_location_usage u ON u.id=l.id GROUP BY l.zone_id,l.zone_name;
```
Paramètres ordonnés : `[]`.
Index/plans : se reporter à l’entrée correspondante du JSON brut ; les métadonnées complètes y sont conservées.