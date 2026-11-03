# Modèles de référence de la version livrée

Vérification du 3 novembre 2026. Le choix repose sur les attributs, associations et droits représentés, comparés au SQL et aux contrôles PHP, et non sur les noms des fichiers.

| Modèle | Référence livrée | Source modifiable | Justification |
|---|---|---|---|
| UML des fonctionnalités livrées | [PDF V2](../livrables/use-case-v2/BD70-USE-CASE-V2.pdf), deux vues | [Draw.io V2](../livrables/use-case-v2/BD70-USE-CASE-V2.drawio), générateur `scripts/build-usecase-v2.py` | Quatre profils internes ; droits cumulés A/R ; opérations de réception, reprise et colis ; transporteur externe absent, comme dans Auth et les routes. Les restrictions d’objet restent précisées dans la matrice CRUD. |
| MCD métier | [PDF final](../livrables/mcd-final/BD70-MCD-FINAL.pdf), global et dix détails | [Draw.io final](../livrables/mcd-final/BD70-MCD-FINAL.drawio), DOT dans `livrables/mcd-final/sources/`, générateur `scripts/build-mcd-final.py` | Attributs propres complets, identifiants, deux rôles véhicule/remorque, auteurs, associations N:N avec quantité/validité ; correspondance aux 60 FK métier et 213 colonnes métier. |
| MLD physique | [SVG complet](diagrammes/mld-complet.svg) et `mld-*` par domaine | [DOT complet](diagrammes/mld-complet.dot), `schema.json`, `scripts/diagrams.py` | 41 tables, colonnes/types/nullabilités, PK, FK et UNIQUE du schéma installé. Les deux tables techniques sont conservées. Les CHECK restent dans le SQL. |

Le [schéma SQL](../sql/01_schema.sql) est l’autorité physique ; les [vues](../sql/02_vues.sql), procédures et triggers complètent ses garanties. Les cardinalités ne garantissent pas à elles seules l’égalité d’articles/propriétaires entre chemins, les capacités cumulées, les transitions ou les quantités d’allocations. Voir [normalisation](normalisation-3nf.md), [hypothèses](hypotheses-decisions.md) et [correspondance MCD/SQL](../livrables/mcd-final/CORRESPONDANCE-SQL.md).

Les cinq N:N sont chauffeur/habilitation (validité), véhicule/équipement, quai/équipement, quai/type de véhicule et colis/prélèvement (quantité). TYPE DE VÉHICULE est un domaine conceptuel réalisé par deux ENUM cohérents, pas une table manquante. Une réserve appartient à une réception OU à une ligne ; les deux participations optionnelles sont complétées par le CHECK XOR. `shipment.order_id` est obligatoire unique ; les unicités nullable de passage/rendez-vous et mouvement/prélèvement ne sont pas des clés totales. Le lien facultatif sortie/prélèvement est complété par CHECK et contrôles transactionnels.

## Versions conservées et portée

- `docs/diagrammes/cas-utilisation.*` : synthèse historique, cohérente avec les droits cumulés du logiciel mais moins détaillée que V2.
- `livrables/uml-use-case/`, `livrables/rendu-intermediaire/` : rendus antérieurs ; aucune suppression.
- `livrables/use-case-v2/` : UML retenu pour décrire l’application effectivement livrée.
- `livrables/correction-prof-use-case/` : modèle métier corrigé pour le professeur, conservé comme **cible distincte**. Son administrateur technique, son transporteur externe et sa séparation de l’affectation diffèrent du code. Ce document ne prouve pas l’implémentation de ces choix. Le portail externe reste facultatif et hors de cette intervention.
- `docs/diagrammes/mcd-*` : six vues historiques avec attributs limités, remplacées comme références par le MCD final, sans modifier leurs chemins.
- `livrables/rapport/DIAGRAMMES-BD70.pdf` : recueil historique UML/MCD/MLD, **ne contient pas le MCD final**. Son maintien ne signifie pas qu’il fait référence.
- `livrables/rapport/RAPPORT-PROJET-BD70.pdf` : rapport antérieur à cette consolidation. Les références techniques actualisées sont dans cet index et la source Markdown du rapport ; pas de réédition générale du rapport dans cette mission.

## Génération faisant autorité

Exécuter depuis la racine, après installation d’une base neuve de test et chargement du schéma courant. Exporter ses métadonnées, jamais celles d’une ancienne base de démonstration :

```powershell
$env:BD70_DATABASE='bd70_test_modele_nouveau'
& C:/xampp2/php/php.exe scripts/model.php
python scripts/diagrams.py
node scripts/render-diagrams.cjs --mld-only
python scripts/build-mcd-final.py
python scripts/build-usecase-v2.py
Remove-Item Env:/BD70_DATABASE
```

Outils : Python avec ReportLab/svglib/pypdf, Node avec `@viz-js/viz` ; variables `BD70_VIZ` et `BD70_PLAYWRIGHT` selon l’environnement. Les générateurs de PDF utilisent les polices Windows livrées sur ce poste. Conserver une copie des sources Draw.io avant reconstruction si elles ont été modifiées manuellement.

`diagrams.py` génère désormais les seuls MLD par défaut : la normalisation et la matrice des droits sont des analyses maintenues à la main. Son ancien chemin `--legacy`, `finalize-docs.py`, `finalize-completion.py` et `build_report.py` sont des outils historiques et ne font pas partie de cette chaîne. Ils peuvent réécrire des textes ou assembler les anciens MCD. Ne pas les utiliser pour fabriquer un recueil prétendument final.

Après génération : contrôler les métadonnées contre le schéma installé, la couverture des attributs/FK dans `sources/modele.json`, les cardinalités et règles complémentaires, puis rendre et inspecter visuellement les PDF. Les preuves du 3 novembre sont référencées dans la recette ; elles ne valent que pour les fichiers identifiés par leurs empreintes.
