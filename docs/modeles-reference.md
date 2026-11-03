# Modèles de référence de la version livrée

Vérification du 3 novembre 2026. Le choix repose sur les attributs, associations et droits représentés, comparés au SQL et aux contrôles PHP, et non sur les noms des fichiers.

| Modèle | Référence livrée | Source modifiable | Justification |
|---|---|---|---|
| UML des fonctionnalités livrées | [PDF corrigé](../livrables/correction-prof-use-case/UML-CAS-UTILISATION-BD70-CORRIGE.pdf), cinq vues | Draw.io dans le même dossier | Retour du professeur appliqué : aucun héritage de droits, administrateur technique, affectation par le responsable, opérations par le magasinier et espace transporteur isolé. |
| MCD métier | [PDF final](../livrables/mcd-final/BD70-MCD-FINAL.pdf), global et dix détails | [Draw.io final](../livrables/mcd-final/BD70-MCD-FINAL.drawio), DOT dans `livrables/mcd-final/sources/`, générateur `scripts/build-mcd-final.py` | Attributs propres complets, identifiants, deux rôles véhicule/remorque, auteurs, associations N:N avec quantité/validité ; couverture du socle précédent (60 FK métier et 213 colonnes métier) ; adaptations physiques actuelles détaillées ci-dessous. |
| MLD physique | [SVG complet](diagrammes/mld-complet.svg) et `mld-*` par domaine | [DOT complet](diagrammes/mld-complet.dot), `schema.json`, `scripts/diagrams.py` | 41 tables, colonnes/types/nullabilités, PK, FK et UNIQUE du schéma installé. Les deux tables techniques sont conservées. Les CHECK restent dans le SQL. |

Le [schéma SQL](../sql/01_schema.sql) est l’autorité physique ; les [vues](../sql/02_vues.sql), procédures et triggers complètent ses garanties. Les cardinalités ne garantissent pas à elles seules l’égalité d’articles/propriétaires entre chemins, les capacités cumulées, les transitions ou les quantités d’allocations. Voir [normalisation](normalisation-3nf.md), [hypothèses](hypotheses-decisions.md) et [correspondance MCD/SQL](../livrables/mcd-final/CORRESPONDANCE-SQL.md).

Les cinq N:N sont chauffeur/habilitation (validité), véhicule/équipement, quai/équipement, quai/type de véhicule et colis/prélèvement (quantité). TYPE DE VÉHICULE est un domaine conceptuel réalisé par deux ENUM cohérents, pas une table manquante. Une réserve appartient à une réception OU à une ligne ; les deux participations optionnelles sont complétées par le CHECK XOR. `shipment.order_id` est obligatoire unique ; les unicités nullable de passage/rendez-vous et mouvement/prélèvement ne sont pas des clés totales. Le lien facultatif sortie/prélèvement est complété par CHECK et contrôles transactionnels.

## Références et adaptations physiques

Le dernier MCD réalisé dans `livrables/mcd-final/` est conservé dans l’attente du retour enseignant, conformément à la demande du groupe. Aucune correction conceptuelle supposée du professeur n’est inventée. Il décrit la base métier précédente ; la correspondance exacte physique est désormais dans le MLD et le SQL : ajout de user_account.carrier_id (profil externe rattaché à une société) et projection des données de sortie par prélèvement. Les mouvements de sortie n’enregistrent plus en double quantité, emplacement et fraction ; la vue v_stock_movement reconstitue ces valeurs.

Le recueil `livrables/rapport/DIAGRAMMES-BD70.pdf` rassemble le use case corrigé, ce dernier MCD et les MLD actuels. Les fichiers `docs/diagrammes/mcd-*`, `cas-utilisation.*`, `livrables/use-case-v2/` et `livrables/rendu-intermediaire/` sont des versions historiques. Le rapport PDF et sa source Markdown décrivent la version corrigée.

## Génération faisant autorité

Exécuter depuis la racine, après installation d’une base neuve de test et chargement du schéma courant. Exporter ses métadonnées, jamais celles d’une ancienne base de démonstration :

```powershell
$env:BD70_DATABASE='bd70_test_modele_nouveau'
& C:/xampp2/php/php.exe scripts/model.php
python scripts/diagrams.py
node scripts/render-diagrams.cjs --mld-only
python scripts/build-report-final.py
Remove-Item Env:/BD70_DATABASE
```

Outils : Python avec ReportLab/svglib/pypdf, Node avec `@viz-js/viz` ; variables `BD70_VIZ` et `BD70_PLAYWRIGHT` selon l’environnement. Les générateurs de PDF utilisent les polices Windows livrées sur ce poste. Conserver une copie des sources Draw.io avant reconstruction si elles ont été modifiées manuellement.

`diagrams.py` génère désormais les seuls MLD par défaut : la normalisation et la matrice des droits sont des analyses maintenues à la main. Son ancien chemin `--legacy`, `finalize-docs.py`, `finalize-completion.py` et `build_report.py` sont des outils historiques et ne font pas partie de cette chaîne. Ils peuvent réécrire des textes ou assembler les anciens MCD. Ne pas les utiliser pour fabriquer un recueil prétendument final.

Après génération : contrôler les métadonnées contre le schéma installé, la couverture des attributs/FK dans `sources/modele.json`, les cardinalités et règles complémentaires, puis rendre et inspecter visuellement les PDF. Les preuves du 3 novembre sont référencées dans la recette ; elles ne valent que pour les fichiers identifiés par leurs empreintes.
