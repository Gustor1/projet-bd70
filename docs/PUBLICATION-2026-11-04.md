# Comptes, guide de test et publication — 4 novembre 2026

Cette livraison regroupe les corrections du 3 novembre, leurs PDF et preuves, et les compléments demandés pour le groupe.

## Comptes utilisables

COMPTES-TEST.md décrit 13 comptes nommés : deux administrateurs techniques, deux responsables/pilotage, deux accueils, trois magasiniers, deux transporteurs de sociétés différentes, un compte en attente et un désactivé. Les deux derniers doivent être refusés à la connexion. Le mot de passe public est Entrepot2026!.

scripts/comptes-demo.php crée les comptes manquants dans une base pédagogique locale déjà alimentée. L’import riche le lance automatiquement pour les nouvelles installations. Sans option, aucun compte existant différent n’est écrasé ; --reinitialiser rétablit explicitement les seuls comptes listés, en conservant identifiants et liens historiques. Les comptes supplémentaires ont également été préparés sur la démonstration locale.

## Guide de recette

COMMENT-TESTER.md, accessible depuis le README, décrit les préparatifs, une base d’essais distincte, un parcours chiffré avec résultats attendus, les variantes/refus, les impressions/exports, les tests techniques et la vérification des livrables. Une matrice relie ses scénarios aux exigences du sujet et de la grille. Les cases à cocher sont destinées au testeur ; elles n’affirment pas une exécution manuelle de chaque scénario.

Le dernier MCD reste conservé en attente du retour enseignant. Ses différences avec le schéma physique corrigé sont explicitement documentées dans docs/modeles-reference.md.

## Défaut trouvé en vérifiant les comptes

Après un refus de connexion, l’exception pouvait laisser la page demandée sur un écran métier, sans créer de session authentifiée. Le contrôleur impose désormais le formulaire de connexion pour tout utilisateur anonyme tant que la base est disponible. Les comptes en attente/désactivés, un mauvais mot de passe et un jeton CSRF invalide sont vérifiés au navigateur, y compris avec une page métier demandée.

## Vérifications exécutées

Preuves et empreintes : livrables/preuves/comptes-2026-11-04/.

- Import riche dans une base neuve, avec création automatique des comptes : réussi.
- 31 contrôles de comptes : profils/mots de passe/sociétés, idempotence sur les 41 tables, préservation d’un compte personnalisé, rétablissement explicite et données métier inchangées.
- 15 cas navigateur sur les comptes et les refus : réussis.
- Suite de droits/isolation précédente rejouée : 32/32 ; préparation de ses données métier ciblées : 18/18.
- Contrôles d’intégrité après import et essais des comptes : aucune anomalie.
- Syntaxe PHP : 45 fichiers sans erreur. Liens des deux guides vérifiés ; git diff --check réussi.

Les suites métier/parcours complètes du 3 novembre restent des preuves de cette version antérieure, pas un nouveau rejeu global. Les nouveaux contrôles ciblent les modifications de cette livraison. Aucune donnée métier de la démonstration principale n’a été réinitialisée ; seuls les comptes pédagogiques supplémentaires y ont été ajoutés.
