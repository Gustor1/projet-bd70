# Recette et preuves du rendu

[COMMENT-TESTER.md](../COMMENT-TESTER.md) décrit les comptes, parcours et résultats attendus. Les cases de ce guide sont à compléter par le testeur.

## Vérifications enregistrées

Les preuves métier du 3 novembre 2026 sont conservées dans [corrections-rendu-2026-11-03](preuves/corrections-rendu-2026-11-03). Elles concernent la version avec droits corrigés, portail transporteur et sorties de stock normalisées.

| Vérification | Résultat |
|---|---|
| Intégration métier, SQL et concurrence | 64/64 |
| Compléments métier | 23/23 |
| Protection des faits | 14/14 |
| Droits, isolation et normalisation | 18/18 |
| Navigateur et portail transporteur | 32/32 |
| Parcours complet avec changement de profils | 32/32 |
| Horloge du site | 8/8 |
| Import riche et intégrité | 83 contrôles sans anomalie |

Ce dossier contient aussi les résultats de migration, sauvegarde/restauration, performances, commandes exécutées et captures du rapport.

Les compléments de comptes du 4 novembre sont dans [comptes-2026-11-04](preuves/comptes-2026-11-04). Ils couvrent 31 contrôles des comptes, 15 cas navigateur, ainsi que le rejeu ciblé des 18 contrôles métier et des 32 contrôles de droits.

Les vérifications documentaires du MCD Chen sont dans [mcd-2026-11-04](preuves/mcd-2026-11-04). La cohérence couvre 61 FK métier et 214 colonnes métier. Les empreintes conservées dans les recettes datées décrivent leur version d’exécution.

Ces résultats proviennent de recettes datées. Ils ne signifient pas qu’une recette globale a été rejouée après chaque modification documentaire. Les limites comprennent les appareils physiques, les lecteurs d’écran et une preuve formelle exhaustive de tous les entrelacements concurrents.

## Reproduire

scripts/verify-finalisation.py crée des bases neuves et des serveurs de test dédiés. BD70_RUN_ID permet un identifiant unique. Les ports 8071 et 8072 doivent être libres. BD70_PHP, BD70_PYTHON, BD70_NODE et BD70_PLAYWRIGHT permettent de préciser l’outillage.

Les suites navigateur courantes sont tests/corrections-browser.cjs, tests/parcours.cjs et tests/comptes-browser.cjs. Les tests de comptes nécessitent le jeu riche. Utiliser uniquement des bases de test distinctes pour les recettes qui modifient les données.

scripts/validate-data.php réalise un contrôle d’intégrité en lecture. scripts/clean-install.py vérifie une installation depuis une copie neuve. scripts/backup-restore.py teste la restauration dans une nouvelle base.

L’horloge fixe du 22 octobre 2026 est réservée aux scénarios reproductibles. La démonstration utilise l’heure réelle du site Europe/Paris.
