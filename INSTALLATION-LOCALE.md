# Installer Transit sur son PC

Guide de première installation pour les camarades du groupe, sous **Windows**. Chaque PC aura sa propre application et sa propre base locale. Le dépôt GitHub ne synchronise pas les saisies entre les PC.

## 1. Préparer les outils

Disposer de XAMPP avec PHP, PDO MySQL/mbstring et MariaDB. L’environnement de référence testé est Windows 11, PHP 8.2.12 et MariaDB 10.4.32 ; d’autres versions ne sont pas certifiées par les essais du projet.

Repérer son dossier XAMPP. Exemples de fichiers attendus :

- `C:/xampp/php/php.exe`
- `C:/xampp/mysql/bin/mysqld.exe`
- `C:/xampp/mysql/bin/mysql_install_db.exe`

Si XAMPP est installé dans `C:/xampp2` ou sur un autre disque, adapter les chemins des commandes ci-dessous. **Il n’est pas nécessaire de lancer Apache ou MySQL depuis le panneau XAMPP** : le projet démarre ses propres serveurs locaux. Node, Python, Composer et Playwright ne sont pas nécessaires pour utiliser l’application ; ils servent aux tests et aux outils de fabrication.

## 2. Récupérer le projet

Depuis [le dépôt GitHub](https://github.com/Gustor1/projet-bd70), choisir **Code → Download ZIP**, extraire l’archive puis ouvrir le dossier contenant `README.md`, `public/`, `scripts/` et `sql/`. Ne pas lancer le projet depuis le ZIP.

Si Git est installé, l’autre possibilité est :

```powershell
git clone https://github.com/Gustor1/projet-bd70.git
cd projet-bd70
```

La branche à utiliser est **main**. Il n’est pas nécessaire de placer le projet dans `htdocs`.

## 3. Ouvrir PowerShell dans le bon dossier

Dans l’Explorateur Windows, ouvrir le dossier du projet, cliquer dans sa barre d’adresse, saisir `powershell` et valider. Vérifier que l’on voit les fichiers du projet :

```powershell
Get-ChildItem README.md,scripts/start.ps1
```

Ne pas recopier le chemin personnel `C:/Users/eliot/...` du poste de développement : utiliser son propre dossier téléchargé/cloné.

## 4. Lancer l’installation automatique

Pour XAMPP dans **C:/xampp** :

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start.ps1 -PhpPath 'C:/xampp/php/php.exe' -MariaPath 'C:/xampp/mysql/bin'
```

Pour XAMPP dans **C:/xampp2** :

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
```

Attendre la fin de l’import et le message `Application : http://127.0.0.1:8070`. La première exécution prend plus de temps que les suivantes, car le jeu contient de nombreuses opérations fictives.

Le script prépare automatiquement :

- une instance MariaDB propre au projet, sur **127.0.0.1:3307**, avec ses fichiers dans `.local/mariadb/` ;
- la base **bd70_demo**, ses tables, vues, procédures, triggers et index ;
- un compte SQL à droits limités et la configuration privée `config/local.php` ;
- le jeu riche de données et les **13 comptes de démonstration** ;
- le serveur PHP sur **127.0.0.1:8070**.

Il ne faut pas créer manuellement les tables dans phpMyAdmin, importer un dump personnel ni copier le fichier `config/local.php` d’un camarade.

## 5. Ouvrir l’application et se connecter

Ouvrir [http://127.0.0.1:8070](http://127.0.0.1:8070) dans Edge ou un navigateur Chromium.

**Mot de passe commun : `Entrepot2026!`**

| Pour tester… | Compte |
|---|---|
| Comptes, activation et journal | admin@bd70.test |
| Pilotage, référentiels, planning, commandes et indicateurs | manager@bd70.test |
| Arrivée, contrôle documentaire, appel à quai et départ | gate@bd70.test |
| Réception, stocks, opérations à quai et commandes affectées | warehouse@bd70.test |
| Rendez-vous de sa société | carrier1@bd70.test |

L’administrateur est **technique** : il n’affiche pas les traitements métier. Utiliser le responsable pour découvrir le pilotage.

Tous les comptes et les refus attendus sont dans [COMPTES-TEST.md](COMPTES-TEST.md). Le parcours complet est dans [COMMENT-TESTER.md](COMMENT-TESTER.md).

Le jeu riche est historique : pour ses graphiques, choisir par exemple du 29 septembre au 28 octobre 2026. Les DLC et le stock disponible sont calculés à la date actuelle ; les lots anciens peuvent donc être périmés.

## 6. Relancer et arrêter

Après un redémarrage du PC, relancer **la même commande start.ps1 avec ses chemins XAMPP**. Les données déjà installées sont conservées.

Pour arrêter le serveur PHP du projet :

```powershell
powershell -ExecutionPolicy Bypass -File scripts/stop.ps1
```

La base MariaDB peut rester active ; le README décrit son arrêt propre si nécessaire. Ne pas supprimer `.local/` pour arrêter l’application : ce dossier contient les données locales.

## 7. En cas de problème

| Symptôme | Vérification/action |
|---|---|
| `PHP introuvable` ou `MariaDB introuvable` | Corriger les paramètres `-PhpPath` et `-MariaPath` selon l’installation XAMPP réelle. |
| Le script n’est pas trouvé | Revenir au dossier contenant `scripts/` et `README.md`, pas au dossier parent. |
| Port 8070 déjà occupé | Ajouter `-WebPort 8074` à la commande et ouvrir `http://127.0.0.1:8074`. |
| Port 3307 déjà occupé par un autre service | Ne pas réutiliser sa base. Lors d’une première installation, ajouter `-DbPort 3308` ; garder ce même port aux relances. Une configuration déjà créée doit viser ce port également. |
| Page inaccessible | Attendre la fin du démarrage, vérifier l’URL/port et lire `.local/php-error.log` ainsi que `.local/mariadb-error.log`. |
| Un compte supplémentaire manque sur une ancienne installation déjà migrée | Exécuter `& 'C:/xampp/php/php.exe' scripts/comptes-demo.php` avec le bon chemin PHP. |
| Erreur de schéma après mise à jour d’un ancien projet | Suivre la migration du README. Télécharger le nouveau code ne migre pas automatiquement une base existante. |
| Connexion refusée avec pending/inactive | C’est attendu : utiliser un compte actif. Les deux servent aux tests de refus. |

Si une installation échoue partiellement, conserver les fichiers et le message d’erreur ; ne pas relancer des imports manuels dans une base non vide ni supprimer les données pour contourner le problème.

## 8. Récupérer les mises à jour

Avec Git, depuis le dossier du projet :

```powershell
git pull origin main
```

Arrêter puis relancer l’application après la mise à jour. Lire les instructions de migration si le schéma a changé. Chaque membre garde sa base et ses saisies ; ni la configuration privée, ni les sessions, ni les sauvegardes ne sont partagées par Git.

Sur macOS/Linux, l’application PHP/MariaDB peut nécessiter une installation manuelle ; le script PowerShell de démarrage et cette procédure ont été testés sous Windows uniquement. Voir le [README](README.md) pour les indications techniques.
