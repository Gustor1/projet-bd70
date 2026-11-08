# Modèle entité-association : V1, remarque et V2

## Historique

| Version | Fichier | État |
|---|---|---|
| V1 | [V1-rendue-au-professeur.png](V1-rendue-au-professeur.png) | Rendue au professeur en PNG, commentée (remarque ci-dessous). |
| Version Chen du 4 novembre 2026 | [version-precedente-2026-11-04/](version-precedente-2026-11-04/) | Déjà en Chen, mais cardinalités placées à la manière de Merise, identifiants non soulignés dans le PDF, étiquettes superposées. Conservée pour comparaison. |
| **V2 (8 novembre 2026)** | [livrables/entite-association/](../../livrables/entite-association/) : PDF et SVG vectoriels, Draw.io modifiable | Version du rendu. **Pas encore relue par le professeur.** |

## Remarque du professeur sur la V1

> Le diagramme présenté est bien un diagramme Entité-Association mais il ne respecte pas un formalisme précis. Il faut également le soumettre au format vectoriel (SVG ou PDF vectorisé, mais pas PNG).

La V1 mélangeait deux formalismes : attributs listés dans les rectangles (Merise / UML) et associations en losanges numérotés (Chen).

## Réponses apportées dans la V2

1. **Un seul formalisme, celui du cours : Chen.** Entités en rectangles, associations en losanges, attributs en ovales, identifiants soulignés, attributs d’association en ovales reliés au losange (date de validité d’une habilitation, quantité affectée à un colis).
2. **Cardinalités comme dans le cours** (diapositives 214 et 220 à 222, « Client 1 — Possède — 0,N Facture ») : la valeur min,max écrite près d’une entité indique combien de fois l’autre entité peut lui être liée. Écriture sans parenthèses.
3. **Format vectoriel** : PDF et SVG composés de formes et de texte, sans image. Le soulignement des identifiants est un vrai trait, présent dans le PDF (il manquait dans la version du 4 novembre).
4. **Lisibilité** : surface réduite d’environ 25 % (5 887 × 2 790 contre 6 747 × 3 248), une seule paire de cardinalités qui se touche contre vingt auparavant, aucune cardinalité posée sur une forme ; trois extraits par domaine dans le rapport.

Le contenu (35 entités, 58 associations, 150 attributs d’entités, cardinalités) est inchangé : il provient de `docs/mcd-chen/modele.json`, contrôlé contre la base installée par `scripts/verify-models.py` (61 clés étrangères et 214 colonnes métier couvertes).

## Reconstruction

```
python scripts/build-mcd-chen.py        # DOT, SVG vectoriel (docs/mcd-chen et livrables)
python scripts/export-mcd-drawio.py     # Draw.io natif modifiable
python scripts/build-mcd-extraits.py    # extraits du rapport
```

Le PDF du MCD est produit par `scripts/build-report-final.py` (Python des dépendances PDF), avec le rapport et le recueil. Une reconstruction écrase le Draw.io : conserver une copie avant toute retouche manuelle.
