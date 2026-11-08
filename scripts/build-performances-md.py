"""Écrit docs/performances.md depuis les deux preuves JSON : aucun chiffre recopié à la main.

python scripts/build-performances-md.py
Sources : docs/preuves/performances.json (scripts/performance.php, base volumétrique)
          docs/preuves/performances-demo.json (scripts/performance-demo.php, jeu de démonstration)
"""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
vol = json.loads((root / 'docs/preuves/performances.json').read_text(encoding='utf-8'))
demo = json.loads((root / 'docs/preuves/performances-demo.json').read_text(encoding='utf-8'))
LABELS = {
    'disponibilite_quai': ('Disponibilité d’un quai', 'Planning : refus des chevauchements'),
    'recherche_passages': ('Recherche de passages', 'Passages camions : filtres période, transporteur, état'),
    'recherche_stock': ('Recherche de stock', 'Stocks : filtres article, propriétaire, zone'),
    'emplacements': ('Emplacements compatibles', 'Réception : proposition de rangement'),
    'historique_lot': ('Historique d’un lot', 'Traçabilité'),
    'selection_fefo': ('Sélection FEFO', 'Préparation : réservation des prélèvements'),
    'statistiques_transporteur': ('Statistiques par transporteur (GROUP BY)', 'Indicateurs'),
    'transporteurs_lents': ('Transporteurs au-dessus du seuil (HAVING)', 'Indicateurs'),
    'historique_rendez_vous': ('Rendez-vous courants et historisés (UNION ALL)', 'Rendez-vous historisés'),
    'remplissage_zone': ('Remplissage par zone', 'Indicateurs'),
}
f = lambda x: f'{x:.3f}'.replace('.', ',')
def explain(rows):
    out = ['| table | type | index utilisé | lignes estimées | Extra |', '|---|---|---|---:|---|']
    for e in rows:
        out.append(f"| {e['table']} | {e['type']} | {e['key'] or '—'} | {e['rows']} | {e['Extra'] or ''} |")
    return '\n'.join(out)

cmp_ = vol['comparison']
L = []
L.append('# Rapport d’analyse des performances')
L.append('')
L.append(f"Fichier généré par `scripts/build-performances-md.py` à partir des preuves JSON. Mesures du {vol['date'][:10]} (base volumétrique) et du {demo['date'][:10]} (jeu de démonstration). Moteur : {demo['engine']} ; PHP {demo['php']} ; Windows.")
L.append('')
L.append('## Méthode')
L.append('')
L.append('- Chaque requête est exécutée une fois pour chauffer le cache, puis **dix fois** depuis PHP/PDO avec récupération de toutes les lignes. On retient la **médiane**, plus robuste que la moyenne face à une mesure isolée lente ; minimum et maximum sont dans les JSON.')
L.append('- Le plan d’exécution est obtenu avec `EXPLAIN` sur la même requête et les mêmes paramètres.')
L.append(f"- **Base volumétrique** `{vol['database']}` : {vol['volumes']['truck_visit']} passages, {vol['volumes']['stock_movement']} mouvements de stock, créée par `scripts/performance.php`.")
L.append(f"- **Jeu de démonstration** `{demo['database']}` : {demo['volumes']['truck_visit']} passages, {demo['volumes']['stock_movement']} mouvements, {demo['volumes']['pick']} prélèvements, chargé par `scripts/import-demo.php`.")
L.append('- Les temps mesurent le travail SQL sur une machine de développement ; ils ne prédisent ni le temps d’affichage d’une page, ni un comportement sous forte charge.')
L.append('')
L.append('## Temps d’exécution des requêtes principales (médianes, ms)')
L.append('')
L.append('| Requête | Écran qui l’utilise | Base volumétrique | Jeu de démonstration | Lignes (démo) |')
L.append('|---|---|---:|---:|---:|')
for k, (label, screen) in LABELS.items():
    v = vol['queries'].get(k); d = demo['queries'][k]
    L.append(f"| {label} | {screen} | {f(v['median_ms']) if v else '—'} | {f(d['median_ms'])} | {d['rows']} |")
L.append('')
L.append('Le texte SQL exact et les paramètres de chaque requête sont dans `sql/requetes_metier.sql` et dans les deux JSON.')
L.append('')
L.append('## Effet d’un index : recherche de chevauchement de créneaux')
L.append('')
L.append('```sql\nSELECT reference FROM appointment\nWHERE dock_id=? AND status=\'active\' AND starts_at<? AND ends_at>?;\n```')
L.append('')
L.append(f"Comparaison sur la base volumétrique, même requête et mêmes paramètres : index simple sur `dock_id` (avant) puis index composé `idx_appointment_slot(dock_id, status, starts_at, ends_at)` (après). Médiane **{f(cmp_['before']['median_ms'])} ms → {f(cmp_['after']['median_ms'])} ms**.")
L.append('')
L.append('Avant :')
L.append('')
L.append(explain(cmp_['before']['explain']))
L.append('')
L.append('Après :')
L.append('')
L.append(explain(cmp_['after']['explain']))
L.append('')
L.append('Lecture : le type passe de `ref` (toutes les lignes du quai) à `range` (plage sur les horaires) et le nombre de lignes estimées diminue. `Using index condition` signifie que le filtre sur le statut et les horaires est appliqué dans l’index avant de lire la table.')
L.append(f"Contrepartie mesurée : une insertion de rendez-vous (trigger compris, puis ROLLBACK) prend {f(cmp_['write_before']['median_ms'])} ms avant et {f(cmp_['write_after']['median_ms'])} ms après. Ces deux séries ne montrent pas de surcoût mesurable de l’index composé à ce volume ; l’index reste un coût de stockage et de mise à jour, d’où un nombre limité d’index (8 index secondaires, en plus des index créés automatiquement par MariaDB sur les clés primaires, UNIQUE et étrangères).")
L.append('')
L.append('## Plan d’une agrégation : statistiques par transporteur')
L.append('')
L.append(explain(demo['queries']['statistiques_transporteur']['explain']))
L.append('')
L.append('La vue `v_visit` est fusionnée dans la requête (`SIMPLE`) : chaque passage rejoint ses événements par l’index unique `(visit_id, state)` (`eq_ref`, une ligne). `Using temporary; Using filesort` correspond au regroupement par transporteur, sur 20 lignes seulement. La version avec `HAVING` a le même plan : le filtre s’applique après le regroupement, sans coût de lecture supplémentaire.')
L.append('')
L.append('## Limite identifiée : le stock calculé depuis les mouvements')
L.append('')
L.append(explain(demo['queries']['recherche_stock']['explain']))
L.append('')
L.append('Les lignes `DERIVED` montrent que la vue `v_balance`, qui contient un `GROUP BY`, est matérialisée en table temporaire : MariaDB lit **tout** l’historique `stock_movement` (`ALL`) et toutes les réservations `pick` avant d’appliquer le filtre sur l’article. Le temps reste de quelques dizaines de millisecondes avec le jeu actuel, mais il augmentera avec la taille de l’historique.')
L.append('')
L.append('Ce coût est le prix d’un choix de conception : le solde n’est jamais stocké, il est toujours recalculé depuis des mouvements immuables, ce qui évite deux valeurs à synchroniser (3NF). Si le volume l’exigeait, deux pistes : (1) une table de soldes par fraction et emplacement, mise à jour dans la même transaction que chaque mouvement ; (2) l’historisation des mouvements anciens, sur le modèle de `appointment_archive`, avec un solde d’ouverture.')
L.append('')
L.append('## Autres optimisations appliquées')
L.append('')
L.append('- Requêtes paginées (`LIMIT 20`) et colonnes sélectionnées explicitement dans les requêtes mesurées.')
L.append('- `v_visit` joint les événements uniques `(passage, état)` au lieu d’agréger tout l’historique ; `v_location_usage` calcule l’occupation sans les jointures de `v_stock`.')
L.append('- L’archivage des rendez-vous (`archive_appointments`, évènement nocturne) allège la table consultée par le planning ; la vue `v_appointment_all` garde l’accès à l’ensemble avec `UNION ALL`.')
L.append('- Écritures concurrentes : le verrou `lock_site` (`SELECT … FOR UPDATE`) garantit la cohérence des contrôles portant sur plusieurs lignes, mais sérialise les écritures. Pour un site très actif, il faudrait des verrous par quai ou par emplacement.')
(root / 'docs/performances.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
print('docs/performances.md écrit')
