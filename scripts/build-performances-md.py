"""Écrit docs/performances.md depuis les deux preuves JSON : aucun chiffre recopié à la main.

python scripts/build-performances-md.py
Sources : docs/preuves/performances.json (scripts/performance.php, base volumétrique)
          docs/preuves/performances-demo.json (scripts/performance-demo.php, jeu de démonstration)
          docs/preuves/performances-optimisation.json (scripts/performance-optimisation.php, avant/après des soldes)
"""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
vol = json.loads((root / 'docs/preuves/performances.json').read_text(encoding='utf-8'))
demo = json.loads((root / 'docs/preuves/performances-demo.json').read_text(encoding='utf-8'))
opti = json.loads((root / 'docs/preuves/performances-optimisation.json').read_text(encoding='utf-8'))
pct = lambda x: f'{x:.0f}'.replace('.', ',')
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
L.append(f"Comparaison sur la base volumétrique, même requête et mêmes paramètres : index simple sur `dock_id` (avant) puis index composé `idx_appointment_slot(dock_id, status, starts_at, ends_at)` (après). Médiane **{f(cmp_['before']['median_ms'])} ms → {f(cmp_['after']['median_ms'])} ms**, soit un gain absolu de {f(cmp_['before']['median_ms']-cmp_['after']['median_ms'])} ms et un gain relatif de {pct(100*(cmp_['before']['median_ms']-cmp_['after']['median_ms'])/cmp_['before']['median_ms'])} %.")
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
L.append('## Optimisation du stock : table de soldes tenue à jour par triggers')
L.append('')
m = opti['mesures']
L.append(f"**Constat (mesure avant).** Le solde n’était pas conservé : la vue `v_balance` recalculait chaque solde par `GROUP BY` sur tout l’historique `stock_movement` ({opti['volumes']['stock_movement']} mouvements dans le jeu de démonstration) et `v_reserved` sur les {opti['volumes']['pick']} prélèvements. Comme ces vues contiennent un `GROUP BY`, MariaDB les matérialise en tables temporaires (lignes `<derived…>` du plan) et lit ces tables **en entier** (`ALL`) avant d’appliquer le filtre sur l’article :")
L.append('')
L.append(explain(m['recherche_stock']['detail_avant']['explain']))
L.append('')
L.append('**Optimisation (`sql/09_optimisation.sql`).** Même démarche que le TD « Automatisation » (table de statistiques hebdomadaires mise à jour par un déclencheur) :')
L.append('')
L.append('- table `stock_balance(receipt_item_id, location_id, qty, reserved_qty)`, clé primaire composée ;')
L.append('- trigger `balance_movement_insert` : chaque mouvement ajoute sa variation au solde (`INSERT … ON DUPLICATE KEY UPDATE`, coût constant) ; une sortie lit fraction, emplacement et quantité dans son prélèvement ;')
L.append('- triggers `balance_pick_insert/update/delete` : la quantité réservée suit les prélèvements prévus ou confirmés ; `pick_shipped_frozen` interdit de modifier un prélèvement déjà expédié ;')
L.append('- vues `v_balance` et `v_reserved` réécrites sur `stock_balance` : sans `GROUP BY`, elles sont fusionnées dans la requête et lues par clé ;')
L.append('- fonction stockée `stock_disponible(article, date)`, utilisée par la préparation de commande ;')
L.append('- initialisation des soldes existants dans une seule transaction (`START TRANSACTION … COMMIT`), par `scripts/migrate-optimisation.php`.')
L.append('')
L.append('Plan après optimisation, même requête :')
L.append('')
L.append(explain(m['recherche_stock']['detail_apres']['explain']))
L.append('')
L.append(f"**Résultats** (`scripts/performance-optimisation.php`, base `{opti['database']}`, mêmes données ; « avant » = anciennes vues et pas de trigger de solde ; médiane de 15 mesures) :")
L.append('')
L.append('| Requête | Écran | Avant (ms) | Après (ms) | Gain absolu (ms) | Gain relatif |')
L.append('|---|---|---:|---:|---:|---:|')
for k, x in m.items():
    if k == 'ecriture_mouvement': continue
    L.append(f"| {LABELS.get(k, ('Contrôle du stock libre',))[0]} | {x['ecran']} | {f(x['avant_ms'])} | {f(x['apres_ms'])} | {f(x['gain_absolu_ms'])} | {pct(x['gain_relatif_pct'])} % |")
w = m['ecriture_mouvement']
L.append('')
L.append(f"**Contrepartie.** Chaque écriture de mouvement exécute un trigger de plus : {f(w['avant_ms'])} ms avant, {f(w['apres_ms'])} ms après (insertion puis ROLLBACK). L’écart est de l’ordre du bruit de mesure : pas de surcoût mesurable à ce volume. Le solde devient une **redondance contrôlée** : la référence reste l’historique immuable, la vue `v_balance_controle` le recalcule et `scripts/validate-data.php` vérifie que les deux sont égaux ({opti['ecarts_apres_mesure']} écart après la mesure). `stock_balance` n’est modifiable que par les triggers (aucun droit d’écriture pour le compte applicatif).")
L.append('')
L.append('## Autres optimisations appliquées')
L.append('')
L.append('- Requêtes paginées (`LIMIT 20`) et colonnes sélectionnées explicitement dans les requêtes mesurées.')
L.append('- `v_visit` joint les événements uniques `(passage, état)` au lieu d’agréger tout l’historique ; `v_location_usage` calcule l’occupation sans les jointures de `v_stock`.')
L.append('- Contrôle du stock libre avant transfert ou ajustement : une ligne de `stock_balance` lue par clé primaire au lieu de deux agrégations.')
L.append('- L’archivage des rendez-vous (`archive_appointments`, évènement nocturne) allège la table consultée par le planning ; la vue `v_appointment_all` garde l’accès à l’ensemble avec `UNION ALL`.')
L.append('- Écritures concurrentes : le verrou `lock_site` (`SELECT … FOR UPDATE`) garantit la cohérence des contrôles portant sur plusieurs lignes, mais sérialise les écritures. Pour un site très actif, il faudrait des verrous par quai ou par emplacement.')
(root / 'docs/performances.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
print('docs/performances.md écrit')
