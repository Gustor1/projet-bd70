# Comptes de démonstration et de test

Ces comptes fictifs sont publics et réservés à une installation locale. Chaque membre du groupe possède sa propre base : GitHub partage le code et les données initiales, pas les saisies locales.

**Mot de passe commun : `Entrepot2026!`**

| Connexion | Profil | Utilisation |
|---|---|---|
| **admin@bd70.test** | Administrateur technique | Comptes, activations, profils, sociétés des transporteurs et journal. Aucun traitement métier. |
| admin2@bd70.test | Administrateur technique | Deuxième session d’administration. |
| **manager@bd70.test** | Responsable / pilotage | Référentiels, quais, planning, commandes, affectation, indicateurs et états. |
| pilotage@bd70.test | Responsable / pilotage | Deuxième responsable ; essais simultanés et conflits de réservation. |
| **gate@bd70.test** | Accueil | Arrivée, documents, parking, appel à quai et départ des camions. |
| gate2@bd70.test | Accueil | Deuxième poste pour les essais simultanés. |
| **warehouse@bd70.test** | Magasinier / préparateur | Réception, stock, début/fin à quai ; exécution des commandes affectées à ce compte. |
| warehouse2@bd70.test | Magasinier / préparateur | Isolement des commandes et réaffectation par le responsable. |
| warehouse3@bd70.test | Magasinier / préparateur | Troisième préparateur ; répartition des commandes et productivité. |
| **carrier1@bd70.test** | Transporteur | Rendez-vous de la première société, par identifiant croissant. |
| **carrier2@bd70.test** | Transporteur | Deuxième société : aucun accès aux rendez-vous de la première. |
| pending@bd70.test | En attente, inactif | **Connexion refusée** : compte non activé. |
| inactive@bd70.test | Magasinier désactivé | **Connexion refusée**, même avec le bon mot de passe. |

Le script affiche les codes et noms exacts des deux sociétés. Ils diffèrent entre le petit jeu de recette et le jeu riche. Chaque transporteur ne peut sélectionner que les ressources de sa société.

## Installer et utiliser les comptes

Depuis la racine du dépôt, démarrer MariaDB et l’application :

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
```

Une **nouvelle installation** les crée automatiquement après l’import riche. Sur une installation existante déjà migrée vers le schéma courant :

```powershell
& C:/xampp2/php/php.exe scripts/comptes-demo.php
```

Adapter le chemin PHP si nécessaire. Le script utilise `config/local.php`, ou `BD70_DATABASE` si cette variable est définie. Il exige une base locale `bd70_demo*` ou `bd70_test*` et au moins deux sociétés déjà importées. Il crée les comptes manquants sans effacer les opérations métier. Un second passage ne réécrit ni les comptes conformes ni leurs hachages.

Ouvrir [Transit](http://127.0.0.1:8070). Pour le pilotage, choisir **manager@bd70.test**. L’administrateur technique affiche les comptes, pas les opérations de l’entrepôt.

## Rétablir des comptes modifiés pendant un essai

Sans option, le script conserve un compte existant différent et le signale. Pour rétablir explicitement les profils, activations, sociétés et mots de passe des **13 comptes listés** :

```powershell
& C:/xampp2/php/php.exe scripts/comptes-demo.php --reinitialiser
```

Les identifiants et les liens historiques sont conservés. Les noms personnalisés et les autres comptes ne changent pas. `pending` et `inactive` redeviennent volontairement inactifs.

Pour récupérer uniquement l’administrateur historique :

```powershell
& C:/xampp2/php/php.exe scripts/admin-local.php
```

## Ajouter ses propres utilisateurs

Avec **admin**, ouvrir **Référentiels → Utilisateurs**, créer une fiche, choisir un profil et l’activer. Un transporteur doit avoir une société ; un compte interne garde ce champ vide. L’inscription publique crée toujours un compte en attente.

Utiliser des navigateurs, profils ou fenêtres privées distincts pour tester plusieurs personnes. Deux onglets d’un même profil partagent la session : une reconnexion change le compte des deux onglets.

Le parcours complet et ses résultats attendus sont dans [COMMENT-TESTER.md](COMMENT-TESTER.md). Les secrets SQL de `config/local.php`, les sessions et les sauvegardes restent hors Git. Ces mots de passe pédagogiques ne conviennent pas à une application exposée sur Internet.
