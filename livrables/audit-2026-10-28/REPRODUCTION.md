# Reproduction des constats de l’audit

L’audit a été réalisé le 28 octobre 2026, heure de Paris. Aucun correctif applicatif n’a été appliqué. Les résultats courants sont détaillés dans `AUDIT-FONCTIONNEL-BD70.md` ; les JSON d’origine sont conservés dans `preuves/`.

## Sources et isolation

La copie locale examinée se trouve dans `.local/audit-2026-10-29/`. Les sources de l’application y sont identiques à celles du dépôt au moment de l’audit, vérification par SHA-256 enregistrée dans `preuves/source-manifest.json`. Le suffixe 29 provient du fuseau du contexte initial ; la référence de restitution est Paris.

Les scripts de tests existants écrivent dans `livrables/preuves/` relativement à leur copie. Pour préserver les anciennes preuves, exécuter ces scripts uniquement depuis une nouvelle copie de travail dédiée, avec son propre dossier `livrables/preuves/`, son dossier `.local/` et une base de test neuve. Ne pas copier la base MariaDB elle-même. La configuration locale peut être réutilisée localement, sans l’inclure dans un export ou dans Git.

Les scripts `install.php` et `seed.php` refusent respectivement une base non vide et un jeu déjà alimenté. Contrôler leurs messages et codes de sortie avant de poursuivre : ne jamais supprimer une base pour résoudre un conflit de nom.

## Résultats retenus

| Test | Base finale retenue | Preuve |
|---|---|---|
| Intégration | `bd70_test_audit_20261029` | `preuves/integration.json`, `preuves/concurrence.json` |
| Navigateur général | `bd70_test_audit_flows_20261029` | `preuves/navigateur.json`, capture `preuves/reports.png` |
| Sondes ciblées | `bd70_test_audit_probes_20261029` | `preuves/audit-probes.json` |
| Parcours indépendant | `bd70_test_audit_ui_20261029` | `preuves/parcours.log`, `preuves/parcours-diagnostic.json` |

Les quatre bases sont conservées localement. Elles ne doivent pas être réutilisées pour une nouvelle recette qui suppose le jeu initial. Les serveurs HTTP temporaires des copies ont été arrêtés après les vérifications.

## Rejouer les sondes sur une nouvelle base

`reproduire-sondes.php` reproduit volontairement des comportements incomplets ou incorrects et conserve leurs résultats. Il **crée des données de test** ; il ne corrige pas l’application. Il accepte uniquement un nom de base commençant par `bd70_test_audit_probes_` et suppose le jeu standard initial de `scripts/seed.php`, sans autre test simultané sur cette base.

Exemple PowerShell, après démarrage de l’instance MariaDB locale du projet et choix d’un nom encore inutilisé :

```powershell
# Exécuter depuis la copie de travail dédiée, jamais depuis la base de démonstration.
& C:/xampp2/php/php.exe scripts/install.php bd70_test_audit_probes_nouvelle_recette
$env:BD70_DATABASE = 'bd70_test_audit_probes_nouvelle_recette'
& C:/xampp2/php/php.exe scripts/seed.php

# Chemin de la copie contenant src/, config/, sql/, etc.
$env:BD70_AUDIT_ROOT = (Get-Location).Path
& C:/xampp2/php/php.exe C:/Users/eliot/Documents/GitHub/projet-bd70/livrables/audit-2026-10-28/reproduire-sondes.php
Remove-Item Env:/BD70_DATABASE,Env:/BD70_AUDIT_ROOT
```

La sortie est affichée et enregistrée dans `preuves/audit-probes-reexecution.json`, distinct du résultat original. Certaines valeurs et les effets des DLC évolueront avec la date réelle ; pour une recette durable, le lot 1 doit introduire une horloge de test commune. La sonde d’heure ne change que la session SQL de sa connexion et restaure le réglage ; elle ne modifie ni l’heure Windows, ni la configuration SQL globale.

## Rejouer les suites existantes

- Métier : nouvelle base `bd70_test_...` installée et alimentée, puis définir `BD70_TEST_DATABASE` et exécuter `tests/integration.php` depuis la copie.
- Navigateur : serveur PHP de la copie avec `BD70_DATABASE` pointant vers sa base dédiée ; définir `BD70_URL` et exécuter `tests/browser.cjs` avec le runtime Node disposant de Playwright.
- Parcours : **autre base neuve**, autre serveur, même mécanisme `BD70_URL`, puis `tests/parcours.cjs`. La DLC codée en dur au 23 octobre explique son échec actuel ; ne pas le déclarer réussi en supprimant simplement l’assertion de traçabilité.

Les mesures de performances et la restauration n’ont pas été répétées pendant cet audit. Leurs procédures existantes restent disponibles dans le README et leurs preuves historiques ne sont pas des résultats de cette nouvelle exécution.
