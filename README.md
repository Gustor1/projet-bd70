# Transit - Projet BD70

Application PHP/PDO de gestion d'un entrepôt logistique, réalisée à partir du sujet A26, de la grille d'évaluation et des deux supports de cours fournis. Les fichiers d'origine sont conservés dans `document cours/` et `document projet/`.

**Pour le groupe : [Installer sur son PC](INSTALLATION-LOCALE.md) · [13 comptes de démonstration](COMPTES-TEST.md) · [Comment tester toute l’application](COMMENT-TESTER.md).** L’admin local est créé automatiquement à la première installation ; `scripts/admin-local.php` permet de le recréer ou de rétablir son accès sans effacer les données.

**Démarrage Windows** (outils XAMPP déjà présents sur ce poste) :

```powershell
cd C:/Users/eliot/Documents/GitHub/projet-bd70
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
```

Ouvrir [l'application locale](http://127.0.0.1:8070). Le script initialise sa propre instance MariaDB sur **127.0.0.1:3307**, avec les données dans `.local/mariadb/`, sans utiliser les bases XAMPP existantes. Le serveur PHP écoute seulement la boucle locale. La première exécution installe la base de démonstration vide, génère le compte SQL à droits limités et charge les données. Les suivantes préservent les données. Sur ce poste, la démonstration vérifiée est dans `bd70_demo_corrige_20261103b` (configuration locale ; ancienne base `bd70_demo_final` conservée) ; une nouvelle installation utilise `bd70_demo`.

| Profil | Email de démonstration | Mot de passe fictif |
|---|---|---|
| Administrateur | admin@bd70.test | Entrepot2026! |
| Responsable | manager@bd70.test | Entrepot2026! |
| Accueil | gate@bd70.test | Entrepot2026! |
| Magasinier | warehouse@bd70.test | Entrepot2026! |

Ces comptes appartiennent au jeu pédagogique. L'inscription publique crée un compte en attente ; l'administrateur l'active dans Référentiels → Utilisateurs. Le mot de passe SQL est généré dans `config/local.php`, exclu de Git. Ne pas transmettre ce fichier, les sessions ou les dumps contenant les hachages.

## Installation sur un autre poste

Environnement réellement testé : **Windows 11 x64, PHP 8.2.12 avec PDO MySQL/mbstring, MariaDB 10.4.32, InnoDB, utf8mb4**. Navigateurs Edge/Chromium. Les autres versions et MySQL/PostgreSQL ne sont pas revendiqués comme testés. Les versions XAMPP disponibles ici servent à une démonstration locale ; une mise en ligne nécessite un environnement maintenu et un serveur HTTPS configuré.

Avec XAMPP ailleurs : préciser `-PhpPath 'D:/xampp/php/php.exe' -MariaPath 'D:/xampp/mysql/bin'`. Les chemins contenant des espaces sont à transmettre comme chaînes PowerShell. Le script accepte `-DbPort` et `-WebPort` ; la configuration doit désigner le même port. `scripts/install.php` accepte `BD70_PORT` et les variables d'administration `BD70_ADMIN_USER`, `BD70_ADMIN_PASSWORD`. Il refuse une base non vide et limite les noms à `bd70_demo*`, `bd70_test*`, `bd70_perf*`, `bd70_restore*`.

Pour un serveur MariaDB déjà configuré, copier `config/example.php` vers `config/local.php`, adapter le DSN et le compte SQL local ; installer les cinq scripts SQL ordonnés dans une base **vide**, puis les privilèges d'exemple adaptés. Le seul répertoire public doit être `public/`. L'application ne nécessite ni Composer, ni Node, ni Python, ni connexion internet une fois installée. Les outils Node/Python servent uniquement à la recette et à la fabrication des livrables.

```powershell
# Installation manuelle sur l'instance isolée, sans écraser une base existante
& C:/xampp2/php/php.exe scripts/install.php bd70_demo
$env:BD70_DATABASE='bd70_demo'
& C:/xampp2/php/php.exe scripts/import-demo.php
Remove-Item Env:/BD70_DATABASE
& C:/xampp2/php/php.exe -S 127.0.0.1:8070 -t public
```

## Utilisation

- Quais : filtrer par journée et quai ; créer/modifier/annuler un rendez-vous. Les états actuels se rafraîchissent toutes les 30 secondes hors saisie. L'heure affichée est celle du site Europe/Paris.
- Camions : arrivée avec ou sans rendez-vous → contrôle documentaire → parking facultatif → appel à quai → début → fin → départ. Les actions sont proposées selon l'état.
- Réception : avis et lignes attendues → réception brouillon liée au passage entrant en opération → lignes de réception → lots → palettes/fractions avec emplacement → validation. Le suivi des avis permet d’ouvrir une fiche guidée, de saisir une réserve même sans palette, puis de suivre les restes et clôturer. Les propositions d'emplacements sont dans Stocks & rangement.
- Stocks : recherche article + lot + zone + propriétaire ; transfert et ajustement motivé. Les avaries ne deviennent pas disponibles, les lots bloqués/périmés sont exclus du disponible.
- Commandes : créer la commande et ses lignes → affecter un préparateur et réserver FEFO → confirmer → créer colis/palettes et leur contenu → choisir le camion sortant au chargement → expédier. Les documents sont imprimables après validation.
- Rapports : période, graphiques, tableaux et impression ; CSV filtrés pour stock, passages et écarts. Traçabilité par lot jusqu'au camion sortant.

Les fiches inutilisées et les brouillons peuvent être supprimés. Les FK protègent les données référencées ; les historiques validés sont immuables. Utiliser annulation, blocage ou ajustement. Certaines propriétés structurelles d'une fiche déjà exploitée sont protégées pour ne pas invalider les faits.

## Vérifications reproductibles

Les tests modifient uniquement des bases désignées de test. Utiliser un **nouveau nom** à chaque recette ; aucune commande de nettoyage général n'est nécessaire.

```powershell
& C:/xampp2/php/php.exe scripts/install.php bd70_test_recette2
$env:BD70_DATABASE='bd70_test_recette2'
& C:/xampp2/php/php.exe scripts/seed.php
$env:BD70_TEST_DATABASE='bd70_test_recette2'
& C:/xampp2/php/php.exe tests/integration.php
Remove-Item Env:/BD70_DATABASE,Env:/BD70_TEST_DATABASE

# Recette navigateur sur le serveur de test décrit plus bas
$env:BD70_URL='http://127.0.0.1:8071'
node tests/browser.cjs

# Jeu volumétrique indépendant et huit mesures (chauffe + dix exécutions)
& C:/xampp2/php/php.exe scripts/install.php bd70_perf_nouveau
$env:BD70_DATABASE='bd70_perf_nouveau'
& C:/xampp2/php/php.exe scripts/performance.php 10000
Remove-Item Env:/BD70_DATABASE
```

La recette navigateur emploie Playwright et Edge. Installer Playwright dans un environnement d'outillage, puis définir `BD70_PLAYWRIGHT` avec le chemin du module si le runtime Codex n'est pas disponible. `tests/parcours.cjs` effectue 31 étapes métier par les formulaires sur **un serveur distinct au port 8071**, lancé avec `BD70_DATABASE=bd70_test_ui` après installation et chargement d'une base vierge. Définir `BD70_URL` pour un autre port. Les comptes, jeux et éléments créés par les tests sont exclusivement fictifs. Les tests PHP ne dépendent d'aucune bibliothèque supplémentaire.

`python scripts/clean-install.py` vérifie une copie sans configuration locale, avec un compte SQL nouvellement généré, trois refus de booléens invalides, un CRUD de relation inutilisée et huit routes authentifiées. Pour répéter sans écraser la première copie, définir `BD70_CLEAN_DIR=installation-propre-2` et `BD70_CLEAN_DB=bd70_demo_installation_2`.

Modèles de référence et commandes de génération : voir [docs/modeles-reference.md](docs/modeles-reference.md). Les générateurs historiques de finalisation réécrivent des documents et ne doivent pas servir à reconstruire la version consolidée.

## Sauvegarde et restauration

`python scripts/backup-restore.py` réalise un dump cohérent avec routines/triggers puis le restaure dans une base **distincte inexistante**. Il compare les 41 tables par compte et checksum et déclenche réellement une historisation dans la copie. Le dump reste dans `.local/` et est exclu de Git. Pour répéter, changer `BD70_RESTORE_TARGET` vers un nouveau nom `bd70_restore*`. Par défaut, `BD70_BACKUP_SOURCE=bd70_demo_final`. Adapter la source lors d'une première installation `bd70_demo`.

Équivalent manuel (client MariaDB, préserver l'encodage du fichier par les options natives) :

```powershell
& C:/xampp2/mysql/bin/mysqldump.exe --host=127.0.0.1 --port=3307 --user=root --single-transaction --routines --triggers --result-file=.local/bd70_demo.sql bd70_demo
# Créer une nouvelle cible explicitement désignée ; ne pas restaurer par-dessus la démonstration.
& C:/xampp2/mysql/bin/mysql.exe --host=127.0.0.1 --port=3307 --user=root --execute='CREATE DATABASE bd70_restore_manuelle CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'
& C:/xampp2/mysql/bin/mysql.exe --host=127.0.0.1 --port=3307 --user=root bd70_restore_manuelle --execute='source .local/bd70_demo.sql'
```

Pour arrêter : `scripts/stop.ps1` ferme seulement le serveur PHP dont le PID a été enregistré ; arrêter MariaDB proprement avec `C:/xampp2/mysql/bin/mysqladmin.exe --host=127.0.0.1 --port=3307 --user=root shutdown` **après avoir vérifié qu'il s'agit de l'instance isolée de ce projet**. Aucune remise à zéro automatique de la démonstration n'est fournie : installer une nouvelle base préfixée plutôt que supprimer des données.

## Livrables et preuves

- `livrables/rapport/RAPPORT-PROJET-BD70.pdf` : rapport final actualisé avec les droits corrigés et la normalisation des sorties.
- [Index des modèles de référence](docs/modeles-reference.md) : UML corrigé dans `livrables/correction-prof-use-case/`, MCD dans `livrables/mcd-final/`, MLD dans `docs/diagrammes/mld-*`. Les anciens MCD et l’ancien recueil sont historiques ; `DIAGRAMMES-BD70.pdf` est reconstruit à partir des références actuelles.
- `docs/dictionnaire-donnees.md`, `docs/normalisation-3nf.md`, `docs/matrice-crud-droits.md` : conception détaillée des 41 tables.
- `docs/matrice-conformite.md`, `docs/recette.md`, `docs/performances.md`, `docs/SUIVI-PROJET.md` : couverture, résultats et reprise.
- `livrables/preuves/` : résultats JSON, plans EXPLAIN, captures authentiques, états imprimés et exemple CSV. Les captures de démonstration, le parcours sur base de test et le jeu volumétrique sont distingués.

Le jeu riche livré a pour référence le **28 octobre 2026** : 90 jours, 180 articles, 720 lots, 360 emplacements, 903 réceptions, 924 commandes, 900 expéditions et 24 917 mouvements. Les situations historiques sont simulées ; les scénarios actifs utilisent les services métier. Les jeux de recette réduits restent fixés au 22 octobre 2026. La disponibilité réelle évolue avec les DLC.

Auteurs : **ELIOTT LE, SEMIH TASKIN, Thomas VUILLIN**. Les contributions individuelles n’ont pas été fournies. Voir le rapport, la matrice de conformité et la recette actualisés ; aucun déploiement public n’est revendiqué.

## Données riches et migration

`sql/07_donnees_demo_riches.sql` est un export de données fictives (environ 5 Mo), à importer après la structure. Il exclut le journal : les triggers le recréent à l’import. Première installation par `start.ps1` : chargement automatique du SQL riche. Une configuration existante est préservée.

```powershell
& C:/xampp2/php/php.exe scripts/install.php bd70_demo_rich_nouveau
$env:BD70_DATABASE='bd70_demo_rich_nouveau'
& C:/xampp2/php/php.exe scripts/import-demo.php
& C:/xampp2/php/php.exe scripts/validate-data.php
# Alternative sur une autre base vide : régénérer à une date choisie
# & C:/xampp2/php/php.exe scripts/seed-rich.php 2026-10-28 90
Remove-Item Env:/BD70_DATABASE
```

Pour ouvrir cette nouvelle base, changer uniquement le dbname du DSN dans config/local.php, ou passer BD70_DATABASE au serveur PHP. Ne pas recharger dans une base déjà alimentée. Pour adapter les DLC, générer une nouvelle base à la date actuelle.

Migration d’une version antérieure : sauvegarder, restaurer dans une cible distincte, puis `php scripts/migrate.php bd70_restore_copie chemin/backup.sql`. Les DDL MariaDB ne sont pas atomiques ; conserver le dump. `scripts/verify-migration.py` reproduit le contrôle sur le dump initial local avec une nouvelle cible BD70_MIGRATION_TARGET. La migration ajoute les réserves et préserve les allocations historiques. Le journal conserve aussi les opérations de migration.

## Recette complémentaire

Sur une base neuve chargée avec seed.php : `php tests/completion.php` (BD70_DATABASE). `php tests/time.php` vérifie Paris/hiver/été/transitions. Pour la recette navigateur, lancer un serveur dédié :

```powershell
$env:BD70_DATABASE='bd70_test_ui_nouveau'
$env:BD70_NOW='2026-10-22 12:00:00'
& C:/xampp2/php/php.exe -S 127.0.0.1:8071 -t public
```

Dans un second terminal : BD70_URL=http://127.0.0.1:8071, puis `node tests/browser.cjs`, `node tests/parcours.cjs` et `node tests/completion-browser.cjs`. La base doit avoir été installée et seedée avant ce lancement. Les tests modifient des données fictives : ne pas les lancer sur la démonstration riche. `node tests/rich-browser.cjs` vérifie la base riche en lecture au port 8070.

Le compte applicatif est créé automatiquement ; le secret reste local. L’export fictif contient uniquement les hachages des comptes pédagogiques dont le mot de passe est publié ci-dessus.

## Version corrigée après retour enseignant (3 novembre)

L’administrateur est technique : utiliser manager@bd70.test pour le pilotage et l’affectation, gate@bd70.test pour l’accueil et warehouse@bd70.test pour l’exécution. Tous ont le mot de passe fictif du tableau. Le responsable affecte d’abord ; le magasinier affecté lance ensuite FEFO. Les colis se corrigent dans la fiche de commande.

Pour activer un transporteur : créer/activer son compte dans Utilisateurs avec le profil Transporteur et sa société. Un compte interne garde cette société vide. L’inscription publique demeure en attente et ne choisit jamais de rôle privilégié.

Migration d’une installation antérieure : arrêter les saisies, sauvegarder puis exécuter `php scripts/migrate-corrections.php bd70_demo_source bd70_demo_cible_neuve`. Le script refuse une cible existante, copie les 41 tables sous lecture cohérente, normalise les sorties et compare les valeurs originales à leur projection. Il ne change pas la configuration. Après validation de `livrables/preuves/migration-corrections.json`, changer le dbname de config/local.php vers la cible et conserver la source pour retour arrière. Le compte applicatif reçoit les privilèges de la nouvelle base via l’installation.

Recette actuelle : `tests/integration.php`, `tests/completion.php`, `tests/finalisation.php`, `tests/corrections.php`, `tests/time.php`, `tests/corrections-browser.cjs` et `tests/parcours.cjs`. Les anciennes suites navigateur supposant un administrateur métier sont historiques et ne décrivent plus les droits courants. `scripts/verify-finalisation.py` utilise les suites actuelles. Résultats de cette correction : `livrables/preuves/corrections-rendu-2026-11-03/`.
