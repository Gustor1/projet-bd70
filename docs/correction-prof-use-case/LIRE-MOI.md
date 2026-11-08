# Diagramme de cas d’utilisation : V1, remarques et V2

## Historique

| Version | Fichier | État |
|---|---|---|
| V1 | [V1-rendue-au-professeur.pdf](V1-rendue-au-professeur.pdf) | Rendue au professeur, commentée (remarques ci-dessous). |
| Correction intermédiaire (4 novembre 2026) | [version-precedente-2026-11-04/](version-precedente-2026-11-04/) | Répondait aux remarques mais dupliquait chaque acteur à côté de chacun de ses cas. Conservée pour comparaison. |
| **V2 (8 novembre 2026)** | [livrables/use-case/](../../livrables/use-case/) : une page, PDF et SVG vectoriels, Draw.io modifiable | Version du rendu. **Pas encore relue par le professeur.** |

## Remarques du professeur sur la V1

1. Revoir les relations d’héritage entre acteurs (le responsable d’exploitation n’est pas un préparateur, l’administrateur a trop de rôles).
2. Le transporteur n’est pas mentionné (même si son rôle est minime).
3. Le préparateur a pour use-case d’affecter un préparateur : la répartition des rôles est à affiner.
4. Certains use-cases doivent être éclatés en plusieurs sous-cas avec relations entre eux (par exemple : « suivre le passage d’un camion », « gérer et préparer les commandes », « expédier les commandes », « tracer un lot »).

## Réponses apportées dans la V2

1. **Aucun héritage.** Chaque acteur est dessiné une seule fois et relié uniquement aux cas qu’il réalise. L’administrateur ne gère que les comptes, les profils et le journal.
2. **Transporteur ajouté** : il planifie uniquement les rendez-vous de sa société (portail transporteur de l’application).
3. **Commandes réparties** : le responsable gère les commandes clients et affecte un préparateur ; le magasinier / préparateur prépare, expédie et édite les documents des seules commandes qui lui sont affectées.
4. **Cas éclatés** : sur la même page, « Suivre le passage d’un camion », « Gérer et préparer les commandes », « Expédier une commande » et « Tracer un lot » sont remplacés par leurs sous-cas, reliés par « include » et « extend » (15 include, 2 extend).

Correction supplémentaire, non demandée mais imposée par le sujet : la planification des quais et des rendez-vous, rattachée à l’agent d’accueil dans la V1, revient au **responsable d’exploitation** (« responsable d’exploitation (planification des quais), agent d’accueil (poste de garde) »). L’application applique la même règle.

## Reconstruction

```
python scripts/build-usecase.py
```

À lancer avec le Python des dépendances PDF (voir le README). Le script régénère le PDF (une page A3 paysage), le SVG et le Draw.io, puis vérifie : une seule page, aucun héritage, six acteurs dessinés chacun une seule fois, aucun chevauchement de cas, textes contenus dans leurs ellipses, connecteurs Draw.io valides. Conserver une copie du Draw.io avant toute retouche manuelle : une reconstruction l’écrase.
