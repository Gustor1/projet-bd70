# Consolidation technique du 3 novembre 2026

Les quatre lots du plan ont été traités localement sur `codex/completion-bd70`. Les modifications antérieures ont été conservées. Aucun commit, push, merge, déploiement, support de présentation ou réédition générale du rapport n’a été effectué. Aucune migration ni écriture métier n’a visé la démonstration.

## Constats vérifiés

Confirmés : références ambiguës entre anciens MCD et MCD final ; CRUD générique inexact pour les passages, événements et faits protégés ; actions impossibles proposées dans le catalogue ; argumentation de normalisation répétitive. Défaut supplémentaire confirmé et corrigé : avis clôturé sans réception encore éditable/supprimable par le catalogue.

Invalidés : il ne manque pas de grand module métier ; les brouillons disposent déjà de chemins de correction, et les réceptions partielles, reprises et répartitions multicolis sont réalisées. Le MCD final n’exige pas une refonte : ses 60 FK et 213 colonnes métier correspondent au SQL installé. Le modèle corrigé pour le professeur n’est pas le diagramme exact des droits livrés : c’est une cible distincte à conserver comme telle. L’ajout d’un compte transporteur ou de FIFO ne découle pas de cette consolidation.

## Lot 1 — Références et génération

L’[index des modèles](modeles-reference.md) identifie les versions et leur portée. Références : [UML livré V2](../livrables/use-case-v2/BD70-USE-CASE-V2.pdf), source Draw.io dans le même dossier ; [MCD final](../livrables/mcd-final/BD70-MCD-FINAL.pdf), source Draw.io et DOT conservés ; [MLD complet](diagrammes/mld-complet.svg), source DOT et vues par domaine. Les MCD historiques et le recueil DIAGRAMMES-BD70.pdf sont conservés et explicitement déclassés. README, architecture, conformité, cas d’utilisation et source du rapport renvoient à cet index.

`scripts/diagrams.py` ne régénère plus les anciens MCD, la matrice ou la normalisation par défaut. Le rendu SVG accepte `--mld-only`. La chaîne faisant autorité est documentée dans l’index. Les sept DOT MLD reconstruits sont identiques ; les textes des sept SVG concordent avec leur reconstruction. Les 11 pages du MCD final et les 2 pages UML ont été rendues et inspectées ; le global MCD exige le zoom, les vues détaillées permettent la lecture. Aucun PDF technique de modèle n’avait besoin d’être modifié ; aucun ancien recueil n’a été réannoncé comme final.

Preuves : [modèles](../livrables/preuves/finalisation-2026-11-03/modeles.json), [génération préservant les textes manuels](../livrables/preuves/finalisation-2026-11-03/generation.json), [exports MLD](../livrables/preuves/finalisation-2026-11-03/svg-mld.json), [inspection des modèles](../livrables/preuves/finalisation-2026-11-03/inspection-modeles.json).

## Lot 2 — Opérations, interface et protections

La [matrice des 41 relations](matrice-crud-droits.md) décrit les opérations réelles et leurs profils, états et alternatives. Dans `src/Catalog.php`, les restrictions de structure ont une source commune pour le formulaire et le serveur ; le catalogue masque les éditions/suppressions impossibles, refuse l’édition directe d’un fait figé et désactive les seuls champs structurels protégés. Les champs descriptifs autorisés restent disponibles. Les avis clôturés et leurs lignes sont protégés même sans réception. Les suppressions tiennent compte des références SQL et de l’utilisation des associations, y compris comme remorque. Les contrôles transactionnels et SQL restent en place.

Les modifications de poids/identité historiques restent refusées, un libellé d’article utilisé peut être corrigé, un brouillon peut être modifié puis supprimé, et une réception validée n’est pas altérée. La nouvelle suite `tests/finalisation.php` couvre ces comportements. `tests/finalisation-browser.cjs` vérifie l’explication, les actions et champs désactivés, un POST direct, un rapport vide et le catalogue mobile simulé. Deux lectures prématurées de `tests/browser.cjs` ont échoué au premier passage (69/71) ; les attentes explicites de navigation et de contenu les corrigent, avec 71/71 au rejeu. Les échecs initiaux sont conservés dans le dossier r1.

## Lot 3 — Normalisation

La [justification réécrite](normalisation-3nf.md) inventorie les clés totales et unicités nullable, puis explique les DF par granularité : référentiels, N:N, allocations de réception, fraction de provenance, colis/prélèvement, états et événements, journal JSON. Les garanties SQL et transactionnelles sont distinguées.

Exception explicitée : les sorties de `stock_movement` répètent fraction, emplacement et quantité du prélèvement dans un journal uniforme. Cette redondance conditionnelle est contrôlée par le service d’expédition et les contrôles d’intégrité ; une 3NF stricte de cette projection n’est pas revendiquée. Les JSON d’audit sont également des instantanés techniques dénormalisés intentionnels. Aucun changement de schéma, migration supplémentaire ni altération de données n’a été introduit sur la base d’un soupçon.

## Lot 4 — Recette effectivement exécutée

La série **r2** teste le code final. Les [commandes et codes de sortie](../livrables/preuves/finalisation-2026-11-03-r2/execution.json) et [empreintes des sources](../livrables/preuves/finalisation-2026-11-03-r2/manifest.json) identifient la version. L’horodatage réel d’exécution est dans le manifeste ; les dates du 22 octobre dans certains JSON sont l’horloge fonctionnelle fixe du jeu réduit, pas la date du rejeu. Les bases sont neuves, suffixées `20261103_191012`, distinctes par suite. Les serveurs PHP de test sont arrêtés par le script.

| Vérification | Résultat | Preuve r2 |
|---|---|---|
| Syntaxe PHP | 38/38 fichiers | [syntaxe.json](../livrables/preuves/finalisation-2026-11-03-r2/syntaxe.json) |
| Intégration métier, SQL, droits et concurrence | 64 réussis, 0 échec | [integration.json](../livrables/preuves/finalisation-2026-11-03-r2/integration.json) |
| Compléments métier | 23 réussis, 0 échec | [completion.json](../livrables/preuves/finalisation-2026-11-03-r2/completion.json) |
| Régressions ciblées | 14 réussis, 0 échec | [finalisation.json](../livrables/preuves/finalisation-2026-11-03-r2/finalisation.json) |
| Navigateur général et droits HTTP | 71 réussis, 0 échec | [navigateur.json](../livrables/preuves/finalisation-2026-11-03-r2/navigateur.json) |
| Parcours réel complet | 31 réussis, 0 échec | [parcours.json](../livrables/preuves/finalisation-2026-11-03-r2/parcours.json) |
| Parcours guidé, réserves et colis | 34 réussis, 0 échec | [completion-navigateur.json](../livrables/preuves/finalisation-2026-11-03-r2/completion-navigateur.json) |
| Actions/champs protégés, POST direct, vide et mobile | 9 réussis, 0 échec | [finalisation-navigateur.json](../livrables/preuves/finalisation-2026-11-03-r2/finalisation-navigateur.json) |
| Horloge du site | 8/8 | [heure-paris.json](../livrables/preuves/finalisation-2026-11-03-r2/heure-paris.json) |
| Import fictif riche et intégrité | import réussi ; 82 contrôles sans anomalie | [intégrité](../livrables/preuves/finalisation-2026-11-03-r2/integrite-donnees.json) |
| Installation sans configuration | compte SQL neuf, booléens, CRUD et 8 routes authentifiées réussis | [installation](../livrables/preuves/finalisation-2026-11-03-r2/installation-propre.json) |
| Sauvegarde/restauration de la copie riche | 41 tables, comptes/checksums identiques ; 119 triggers, 2 procédures, historisation après restauration | [restauration](../livrables/preuves/finalisation-2026-11-03-r2/restauration.json) |
| Migration de la sauvegarde initiale conservée | 42 contrôles réussis sur cible neuve ; colonnes antérieures conservées | [migration](../livrables/preuves/finalisation-2026-11-03-r2/migration.json) |
| Démonstration préservée | comptes et checksums des 41 tables identiques avant/après r2 | [comparaison](../livrables/preuves/finalisation-2026-11-03-r2/demonstration-preservee.json) |

Les quatre courses entre deux connexions (rendez-vous, occupation, capacité, réservation de stock) sont détaillées dans [concurrence.json](../livrables/preuves/finalisation-2026-11-03-r2/concurrence.json). Le parcours de formulaires couvre avis → arrivée → réception avec réserve → rangement/transfert → commande → FEFO → colis → chargement → expédition → document → traçabilité. Les refus de conflits, incompatibilité, dépassements, lot bloqué/périmé, doubles validations et accès directs sont dans les suites métier/HTTP.

Les trois documents de transport/prélèvement (une page chacun) et l’état d’indicateurs (trois pages) ont été imprimés via Chromium, rendus puis inspectés : [inspection](../livrables/preuves/finalisation-2026-11-03/inspection-etats.json). Les captures mobile simulent 390 × 844 px ; aucun téléphone physique testé. Les anciennes preuves sont intactes. Les dumps et sessions restent exclusivement dans `.local/`, exclus du dépôt.

## Performances mesurées séparément

Base volumétrique neuve : 10 001 rendez-vous et 22 011 mouvements. Chauffe puis dix exécutions ; temps PDO avec récupération, sans coût HTTP. Les requêtes, paramètres, nombres de lignes et plans sont dans [performances.json](../livrables/preuves/finalisation-2026-11-03-r2/performances.json). Le paramètre de référence FEFO est le 22 octobre ; les vues de disponibilité utilisent l’horloge réelle de cette base volumétrique. Ces résultats ne sont pas une comparaison contrôlée avec les anciennes mesures.

| Requête SQL | Médiane ms |
|---|---:|
| disponibilite_quai | 1.68 |
| recherche_passages | 61.09 |
| recherche_stock | 87.69 |
| emplacements | 75.44 |
| historique_lot | 87.27 |
| selection_fefo | 94.72 |
| statistiques_transporteur | 71.35 |
| remplissage_zone | 77.57 |

Les [réponses HTTP](../livrables/preuves/finalisation-2026-11-03-r2/http.json) mesurent PHP et transfert local sans chargement des ressources, dix observations après chauffe : planning 47.9 ms, stock 299.2 ms, reports 286.7 ms.

Les navigations Chromium jusqu’à `load`, ressources incluses, ont trois observations sur le jeu réduit : catalog&t=receipt médiane 138.7 ms, catalog&t=carrier médiane 1299.5 ms, stock médiane 345.9 ms, reports médiane 255.3 ms. Ce faible échantillon documente le coût observé, sans garantir une latence en production.

## Reproduction et limites

`scripts/verify-finalisation.py` copie les sources dans un nouveau `.local/<identifiant>`, crée les bases neuves et collecte leurs sorties dans `livrables/preuves/<identifiant>`. Il refuse les dossiers déjà présents et les ports de recette occupés. Définir `BD70_PLAYWRIGHT` vers le module Playwright, et si nécessaire `BD70_NODE`/`BD70_PYTHON` vers les runtimes avec leurs dépendances. Exécuter depuis la racine :

```powershell
$env:BD70_RUN_ID='finalisation-nouveau-nom'
python scripts/verify-finalisation.py
```

Le rejeu de migration requiert la sauvegarde privée `.local/bd70-demo-final-before-completion.sql` ; en son absence, cette étape n’est pas exécutée. La comparaison des modèles peut ensuite être relancée explicitement :

```powershell
python scripts/verify-models.py livrables/preuves/finalisation-nouveau-nom/schema-installe.json livrables/preuves/finalisation-nouveau-nom/modeles.json
```

Aucun échec fonctionnel restant dans les suites exécutées. Limites maintenues : pas de téléphone physique, pas de déploiement public, pas de preuve formelle exhaustive de normalisation ou de tous les entrelacements concurrents. Les PDF du rapport et du recueil restent des rendus antérieurs, identifiés comme tels ; seule leur documentation de référence a été corrigée. Le modèle cible du professeur n’est pas entièrement celui des autorisations livrées. Ces distinctions ne sont pas masquées par la réussite de la recette.

La [comparaison du travail préexistant](../livrables/preuves/finalisation-2026-11-03/travail-preexistant.json) confirme que les 87 différences suivies hors intervention sont inchangées. Le statut initial et le patch complet préexistant restent dans `.local/finalisation-2026-11-03/`. Les fichiers déjà modifiés concernés par l’intervention ont reçu des ajouts ciblés ; aucun reset, nettoyage, restauration globale ou suppression de base.
