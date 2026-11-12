# Transit — Projet BD70

Application PHP/MariaDB de gestion d’un entrepôt logistique, réalisée pour le sujet A26. Les consignes originales et la grille d’évaluation sont dans document projet/.

## Démarrer et tester

- [Installer sur son PC](INSTALLATION-LOCALE.md)
- [Comptes de démonstration](COMPTES-TEST.md)
- [Guide complet de test](COMMENT-TESTER.md)

Sur ce poste avec XAMPP installé dans C:/xampp2, lancer depuis la racine du projet.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
```

Ouvrir http://127.0.0.1:8070. Le script lance une instance MariaDB locale sur le port 3307 et le serveur PHP sur le port 8070. Une première installation crée la base bd70_demo, un compte SQL à droits limités et le jeu de démonstration. Les lancements suivants préservent les données ; ils ajoutent si besoin, sans modifier les données, les objets d’historisation (scripts/migrate-historisation.php sur la base de config/local.php).

La démonstration de ce poste utilise bd70_demo_corrige_20261103b. Sa configuration se trouve dans config/local.php, hors Git. L’heure du site est Europe/Paris.

| Profil | Compte pédagogique |
|---|---|
| Administrateur technique | admin@bd70.test |
| Responsable | manager@bd70.test |
| Accueil | gate@bd70.test |
| Magasinier | warehouse@bd70.test |

Le mot de passe pédagogique est Entrepot2026!. Les treize comptes et leurs usages sont détaillés dans COMPTES-TEST.md. L’administrateur gère les comptes. Le responsable affecte les commandes, puis le magasinier affecté lance la préparation FEFO.

## Dossier de remise

| Élément | Fichier |
|---|---|
| Rapport final | [RAPPORT-PROJET-BD70.pdf](livrables/rapport/RAPPORT-PROJET-BD70.pdf) |
| Recueil des modèles et extraits par domaine | [DIAGRAMMES-BD70.pdf](livrables/rapport/DIAGRAMMES-BD70.pdf) |
| Diagramme de cas d’utilisation V2 (après remarques sur la V1) | [PDF](livrables/use-case/UML-CAS-UTILISATION-BD70-CORRIGE.pdf) · [SVG](livrables/use-case/UML-CAS-UTILISATION-BD70-CORRIGE.svg) · [Draw.io](livrables/use-case/UML-CAS-UTILISATION-BD70-CORRIGE.drawio) |
| MCD en notation de Chen | [PDF](livrables/entite-association/BD70-MCD-CHEN.pdf) · [SVG](livrables/entite-association/BD70-MCD-CHEN.svg) · [Draw.io](livrables/entite-association/BD70-MCD-CHEN.drawio) |
| Schéma relationnel complet | [PDF](livrables/schema-relationnel/mld-complet.pdf) · [SVG](livrables/schema-relationnel/mld-complet.svg) · [Draw.io](livrables/schema-relationnel/mld-complet.drawio) |
| Base de données et données fictives | sql/01_schema.sql à sql/08_historisation.sql (historisation, évènement, trigger anti-chevauchement) |
| Conception et fonctionnalités | [Cahier des charges](docs/01-cahier-des-charges.md), [cas d’utilisation](docs/02-cas-utilisation.md), [conformité](docs/matrice-conformite.md) |
| Normalisation et données | [Dictionnaire](docs/dictionnaire-donnees.md), [normalisation](docs/normalisation-3nf.md), [droits](docs/matrice-crud-droits.md) |
| Analyse des performances | [Mesures et méthode](docs/performances.md) |
| Vérifications | [Recette et preuves](docs/recette.md) |

L’[index des modèles](docs/modeles-reference.md) précise la lecture, les règles complémentaires et la reconstruction des documents. Le recueil contient le diagramme de cas d’utilisation V2 (une page), le MCD Chen global, le schéma relationnel complet et six extraits lisibles par domaine. Tous les diagrammes sont vectoriels (texte et formes, aucune image) ; les sources modifiables sont les fichiers Draw.io.

Reconstruction : `python scripts/export-diagrammes.py` (SVG), `python scripts/build-mcd-extraits.py` et `python scripts/build-mld-extraits.py` (extraits), `python scripts/build-performances-md.py` (rapport de performances), puis `scripts/build-report-final.py` avec le Python des dépendances PDF (rapport et recueil).

## Supports de soutenance

Le passage dure 20 minutes. Les cinq premières minutes sont consacrées à la BDD et au backend avec le diaporama. Les cinq suivantes présentent l’application dans le navigateur. Le professeur dispose ensuite de dix minutes pour ses questions.

| Support actuel | Usage |
|---|---|
| [Transit-diapo.html](livrables/soutenance/Transit-diapo.html) | Onze diapositives animées : architecture (front, back, base), démarche et modèle, choix, normalisation 1NF à 3NF, automatisation, triggers, procédures et fonction, évènement, vues et calculs, fonctions PHP, optimisation ; captures phpMyAdmin dans [captures-phpmyadmin](livrables/soutenance/captures-phpmyadmin) |
| [Transit.pdf](docs/soutenance/Transit.pdf) | Copie PDF vectorielle des onze diapositives (scripts/export-diapo-pdf.cjs) |
| [Guide-oral.md](livrables/soutenance/Guide-oral.md) | Discours aligné sur les onze diapositives et minutage de la démonstration |
| [GUIDE-TEST-ET-DEMO.pdf](livrables/soutenance/GUIDE-TEST-ET-DEMO.pdf) | Guide de A à Z avec captures : démarrage, vérifications SQL, nouveautés, scénario ORAL-CAFE complet avec phrases pour le professeur, tests automatisés, livrables, déroulé du jour J (généré par scripts/build-guide-test.cjs) |
| [Parcours-application.pdf](livrables/soutenance/Parcours-application.pdf) | Démarrage, connexions, saisies et captures ordonnées. Page 3 pour le parcours de cinq minutes |
| [Questions-prof.md](livrables/soutenance/Questions-prof.md) | Compréhension du projet, SQL, choix et limites |

## Organisation

- public/, src/, templates/ et config/example.php composent l’application.
- sql/ contient le schéma, les vues, procédures, déclencheurs, index, exemples de privilèges (GRANT/REVOKE), données fictives et l’historisation (table d’archive, procédure, évènement).
- scripts/ contient l’installation, les sauvegardes, l’import, les contrôles et les générateurs actuels.
- tests/ contient les recettes du modèle et des droits actuels.
- docs/ et livrables/ contiennent la documentation et les documents du rendu.

PHP 8.2.12 avec PDO MySQL et mbstring, MariaDB 10.4.32, Windows et Edge/Chromium constituent l’environnement testé. L’application fonctionne sans Composer, Node ou Python. Ces deux derniers servent aux tests navigateur et à la reconstruction documentaire.

## Recette et maintenance

L’évènement d’archivage ne s’exécute que si le planificateur MariaDB est actif : `scripts/start.ps1` lance MariaDB avec `--event-scheduler=ON` ; sur un autre serveur, `SET GLOBAL event_scheduler=ON;` avec le compte administrateur (ou `event_scheduler=ON` dans my.ini). La procédure peut aussi être lancée à la main : `CALL archive_appointments(365);`.


Suivre COMMENT-TESTER.md pour les parcours et les bases de test séparées. scripts/verify-finalisation.py exécute une recette isolée. Les résultats livrés sont datés dans docs/recette.md.

scripts/backup-restore.py sauvegarde puis restaure dans une nouvelle base et compare les tables et les automatismes. Définir BD70_BACKUP_SOURCE vers la base à sauvegarder et BD70_RESTORE_TARGET vers un nouveau nom bd70_restore*. Les dumps restent dans .local/.

Pour reprendre une ancienne base, scripts/migrate-corrections.php source cible_neuve crée une copie corrigée et compare les faits métier. La configuration doit ensuite désigner la cible vérifiée. scripts/admin-local.php permet de rétablir le compte administrateur pédagogique.

## État local

.local/ contient les bases locales, sessions, sauvegardes et outils de travail. config/local.php contient le compte SQL propre au poste. Ces éléments sont exclus de Git et du dossier à transmettre. Le nettoyage du rendu conserve cet environnement local pour permettre de continuer à lancer l’application.
