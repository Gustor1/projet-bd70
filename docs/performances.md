# Analyse des performances

Mesures de la version corrigée du **3 novembre 2026**, incluant la projection normalisée des sorties. Preuve : livrables/preuves/corrections-rendu-2026-11-03/performances.json. Les temps SQL, réponses HTTP et navigations avec ressources sont mesurés séparément.

Environnement : 10.4.32-MariaDB, PHP 8.2.12, Windows ; base isolée bd70_perf_corrections_20261103. Chauffe puis dix exécutions PDO avec récupération des résultats. Paramètres, EXPLAIN, index et observations dans performances.json.

| Requête | Médiane ms | Min ms | Max ms |
|---|---:|---:|---:|
| disponibilite_quai | 1.263 | 0.845 | 1.744 |
| recherche_passages | 48.410 | 41.429 | 75.394 |
| recherche_stock | 60.175 | 44.939 | 75.853 |
| emplacements | 41.890 | 39.288 | 53.623 |
| historique_lot | 38.453 | 31.770 | 49.741 |
| selection_fefo | 65.776 | 57.190 | 116.835 |
| statistiques_transporteur | 59.515 | 51.458 | 90.713 |
| remplissage_zone | 48.001 | 46.746 | 59.589 |

Comparaison historique de l’index (avant cette correction) : idx_appointment_slot uniquement ; index FK simple maintenu. Lecture avant 10.481 ms, après 1.361 ms. Les dix observations et le coût INSERT + ROLLBACK sont publiés dans le JSON.

v_visit joint les événements uniques (passage, état) au lieu d’agréger tout l’historique. v_location_usage calcule les capacités physiques sans toutes les jointures de v_stock. La seconde correction répond à une expiration de 30 secondes observée avec les données riches.

Les navigations riches ont été rejouées après correction : navigateur-riche.json contient des observations uniques, avec rendu et ressources, distinctes des dix mesures PDO. La page Indicateurs a alors chargé en environ 2,2 s dans ce relevé. Le jeu volumétrique de 10 000 passages et le catalogue riche de 180 articles sont complémentaires.

Ces mesures locales ne sont pas une certification de charge industrielle. Les comparaisons historiques de réécriture ne contrôlent pas cache et charge à l’identique. Le verrou global limite le parallélisme.

## disponibilite_quai

```sql
SELECT reference FROM appointment WHERE dock_id=? AND status='active' AND starts_at<? AND ends_at>?;
```

Paramètres : [1, "2025-05-02 09:00:00", "2025-05-02 08:00:00"]

## recherche_passages

```sql
SELECT reference,carrier_name,status,arrived_at FROM v_visit WHERE arrived_at>=? AND arrived_at<? AND carrier_id=? AND status=? ORDER BY arrived_at DESC LIMIT 20;
```

Paramètres : ["2025-05-01", "2025-06-01", 1, "departed"]

## recherche_stock

```sql
SELECT sku,lot_code,location_code,qty,available_qty FROM v_stock WHERE article_id=? AND owner_id=? AND zone_id=? ORDER BY lot_code,location_code LIMIT 20;
```

Paramètres : [1, 1, 1]

## emplacements

```sql
SELECT l.code,u.used_kg,u.used_pallets FROM v_location l JOIN v_location_usage u ON u.id=l.id JOIN article a ON a.id=? WHERE l.storage=a.storage AND l.width_m>=a.width_m AND l.height_m>=a.height_m AND l.depth_m>=a.depth_m AND u.used_kg+?*a.unit_kg<=l.max_kg AND u.used_m3+?*a.width_m*a.height_m*a.depth_m<=l.capacity_m3 AND u.used_pallets+?/a.units_per_pallet<=l.max_pallets;
```

Paramètres : [1, 5, 5, 5]

## historique_lot

```sql
SELECT m.operation_ref,m.created_at,m.delta,l.code FROM stock_movement m JOIN receipt_item i ON i.id=m.receipt_item_id JOIN location l ON l.id=m.location_id WHERE i.lot_id=? ORDER BY m.created_at,m.id LIMIT 20;
```

Paramètres : [7]

## selection_fefo

```sql
SELECT receipt_item_id,location_id,available_qty,expires_on FROM v_stock WHERE article_id=? AND available_qty>0 AND blocked=0 AND (expires_on IS NULL OR expires_on>=?) ORDER BY expires_on IS NULL,expires_on,received_at,receipt_item_id,location_id LIMIT 20;
```

Paramètres : [1, "2026-10-22"]

## statistiques_transporteur

```sql
SELECT carrier_name,COUNT(*) passages,AVG(wait_minutes),AVG(immobilized_minutes) FROM v_visit WHERE arrived_at>=? AND arrived_at<? GROUP BY carrier_id,carrier_name;
```

Paramètres : ["2025-05-01", "2025-06-01"]

## remplissage_zone

```sql
SELECT l.zone_name,SUM(u.used_kg),SUM(l.max_kg),SUM(u.used_pallets),SUM(l.max_pallets) FROM v_location l JOIN v_location_usage u ON u.id=l.id GROUP BY l.zone_id,l.zone_name;
```

Paramètres : []
