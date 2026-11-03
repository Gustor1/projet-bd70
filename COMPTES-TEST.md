# Comptes de test du groupe

Ces comptes sont publics et fictifs, destinés au projet BD70 exécuté en local par le groupe. Chaque membre possède sa propre base ; GitHub partage le code et le jeu de données, pas les modifications de sa base locale.

| Profil | Email | Mot de passe |
|---|---|---|
| **Administrateur** | **admin@bd70.test** | **Entrepot2026!** |
| Responsable | manager@bd70.test | Entrepot2026! |
| Accueil | gate@bd70.test | Entrepot2026! |
| Magasinier | warehouse@bd70.test | Entrepot2026! |

## Première utilisation

Depuis la racine du dépôt, avec XAMPP installé :

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
```

Ouvrir [Transit en local](http://127.0.0.1:8070), puis se connecter avec le compte administrateur ci-dessus. L’installation et l’import initiaux créent automatiquement ces comptes. Si XAMPP est ailleurs, passer `-PhpPath` et `-MariaPath` comme expliqué dans le [README](README.md).

## Créer ou récupérer l’accès administrateur

Après installation de la structure et démarrage de MariaDB, cette commande crée le compte s’il manque, ou rétablit son mot de passe, son activation et son rôle :

```powershell
& C:/xampp2/php/php.exe scripts/admin-local.php
```

La commande conserve l’identifiant et les liens historiques du compte existant. Si l’accès est déjà correct, elle ne modifie rien. Elle ne réinitialise pas les données métier, ne recharge pas le jeu de démonstration et n’est pas accessible depuis le navigateur. Elle cible la base de `config/local.php`, ou celle indiquée explicitement par `BD70_DATABASE`, et refuse les serveurs distants et les bases autres que `bd70_demo*`/`bd70_test*`.

Les identifiants ci-dessus peuvent être partagés sur GitHub pour ce projet local. Le mot de passe SQL de `config/local.php`, les sessions et les sauvegardes restent privés et exclus de Git. Ne pas utiliser ces comptes publics pour une application exposée sur Internet.
