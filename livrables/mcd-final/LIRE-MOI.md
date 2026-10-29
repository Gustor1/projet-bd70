# Modèle entité-association final BD70

- **Consulter le résultat :** [PDF vectoriel](BD70-MCD-FINAL.pdf).
- **Modifier les cases et les liens :** [source Draw.io native](BD70-MCD-FINAL.drawio), à ouvrir dans diagrams.net / Draw.io.
- **Comprendre les corrections et retrouver tous les anciens diagrammes :** [analyse et inventaire](ANALYSE-MCD.md).
- **Vérifier la traduction vers la base :** [correspondance SQL et unicités](CORRESPONDANCE-SQL.md).

Le PDF et le Draw.io comportent onze pages : une vue complète (grand format avec zoom), puis dix vues par domaine en A3 ou A2. Ce sont plusieurs vues d’un même modèle, pas des propositions alternatives. Les entités communes gardent le même nom et les mêmes propriétés. Les associations portent un repère R01 à R57.

La cardinalité placée près d’une entité indique son nombre de participations. Un attribut souligné est l’identifiant ; les autres unicités sont détaillées dans la correspondance SQL. Les types SQL et les clés étrangères ne sont pas affichés comme attributs dans le MCD.

La source est nativement éditable : rectangles, losanges, textes et connecteurs. Enregistrer une copie avant toute modification manuelle. Le script `python scripts/build-mcd-final.py`, lancé depuis la racine du dépôt, régénère ce dossier et écrase les exports du nouveau modèle. Il ne modifie pas les anciens MCD, l’application ou la base.
