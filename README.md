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

Ouvrir http://127.0.0.1:8070. Le script lance une instance MariaDB locale sur le port 3307 et le serveur PHP sur le port 8070. Une première installation crée la base bd70_demo, un compte SQL à droits limités et le jeu de démonstration. Les lancements suivants préservent les données.

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
| Recueil des trois modèles | [DIAGRAMMES-BD70.pdf](livrables/rapport/DIAGRAMMES-BD70.pdf) |
| Use case corrigé après retour enseignant | [PDF](livrables/use-case/UML-CAS-UTILISATION-BD70-CORRIGE.pdf) et Draw.io dans le même dossier |
| MCD en notation Chen corrigé | [PDF](livrables/entite-association/BD70-MCD-CHEN.pdf) · [Draw.io](livrables/entite-association/BD70-MCD-CHEN.drawio) |
| Schéma relationnel complet | [PDF](livrables/schema-relationnel/mld-complet.pdf) · [Draw.io](livrables/schema-relationnel/mld-complet.drawio) |
| Base de données et données fictives | sql/01_schema.sql à sql/07_donnees_demo_riches.sql |
| Conception et fonctionnalités | [Cahier des charges](docs/01-cahier-des-charges.md), [cas d’utilisation](docs/02-cas-utilisation.md), [conformité](docs/matrice-conformite.md) |
| Normalisation et données | [Dictionnaire](docs/dictionnaire-donnees.md), [normalisation](docs/normalisation-3nf.md), [droits](docs/matrice-crud-droits.md) |
| Analyse des performances | [Mesures et méthode](docs/performances.md) |
| Vérifications | [Recette et preuves](docs/recette.md) |

L’[index des modèles](docs/modeles-reference.md) précise la lecture, les règles complémentaires et la reconstruction des documents. Le recueil contient les cinq vues du use case corrigé, le MCD Chen global et le schéma relationnel complet.

## Supports de soutenance

Le passage dure 20 minutes. Les cinq premières minutes sont consacrées à la BDD et au backend avec le diaporama. Les cinq suivantes présentent l’application dans le navigateur. Le professeur dispose ensuite de dix minutes pour ses questions.

| Support actuel | Usage |
|---|---|
| [Transit-diapo.html](livrables/soutenance/Transit-diapo.html) | Six diapositives animées sur l’architecture, le SQL et les choix du projet |
| [Transit.pdf](docs/soutenance/Transit.pdf) | Copie statique des mêmes six diapositives |
| [Guide-oral.md](livrables/soutenance/Guide-oral.md) | Discours aligné sur les six diapositives et minutage de la démonstration |
| [Parcours-application.pdf](livrables/soutenance/Parcours-application.pdf) | Démarrage, connexions, saisies et captures ordonnées. Page 3 pour le parcours de cinq minutes |
| [Questions-prof.md](livrables/soutenance/Questions-prof.md) | Compréhension du projet, SQL, choix et limites |

## Organisation

- public/, src/, templates/ et config/example.php composent l’application.
- sql/ contient le schéma, les vues, procédures, déclencheurs, index, exemples de privilèges et données fictives.
- scripts/ contient l’installation, les sauvegardes, l’import, les contrôles et les générateurs actuels.
- tests/ contient les recettes du modèle et des droits actuels.
- docs/ et livrables/ contiennent la documentation et les documents du rendu.

PHP 8.2.12 avec PDO MySQL et mbstring, MariaDB 10.4.32, Windows et Edge/Chromium constituent l’environnement testé. L’application fonctionne sans Composer, Node ou Python. Ces deux derniers servent aux tests navigateur et à la reconstruction documentaire.

## Recette et maintenance

Suivre COMMENT-TESTER.md pour les parcours et les bases de test séparées. scripts/verify-finalisation.py exécute une recette isolée. Les résultats livrés sont datés dans docs/recette.md.

scripts/backup-restore.py sauvegarde puis restaure dans une nouvelle base et compare les tables et les automatismes. Définir BD70_BACKUP_SOURCE vers la base à sauvegarder et BD70_RESTORE_TARGET vers un nouveau nom bd70_restore*. Les dumps restent dans .local/.

Pour reprendre une ancienne base, scripts/migrate-corrections.php source cible_neuve crée une copie corrigée et compare les faits métier. La configuration doit ensuite désigner la cible vérifiée. scripts/admin-local.php permet de rétablir le compte administrateur pédagogique.

## État local

.local/ contient les bases locales, sessions, sauvegardes et outils de travail. config/local.php contient le compte SQL propre au poste. Ces éléments sont exclus de Git et du dossier à transmettre. Le nettoyage du rendu conserve cet environnement local pour permettre de continuer à lancer l’application.
