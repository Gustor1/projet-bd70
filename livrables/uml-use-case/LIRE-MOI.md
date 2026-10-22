# Diagramme UML des cas d’utilisation — Transit / BD70

Le fichier à modifier est **Transit-Use-Case.drawio**. Il contient des objets Draw.io natifs : chaque acteur, ellipse, texte et connecteur est éditable individuellement.

Ouvrir ce fichier dans Draw.io / diagrams.net, par glisser-déposer dans l’éditeur ou via l’ouverture d’un fichier local. Les trois pages sont accessibles par les onglets en bas de l’éditeur. Enregistrer ensuite au format `.drawio` pour conserver les possibilités de modification.

1. **Vue d’ensemble** : cas d’utilisation regroupés par profil, avec de larges espacements.
2. **Acteurs et accès** : généralisation des acteurs et demande d’inscription. Cette page complète les associations de la première : le Responsable hérite des fonctions Accueil et Magasinier, l’Administrateur de celles du Responsable, et tous partagent les fonctions du Personnel.
3. **Include et extend** : détails des traitements obligatoires et de l’arrivée sans rendez-vous, avec direction des flèches et légende.

Les fichiers SVG et PNG sont des aperçus des mêmes positions et libellés. Pour modifier le diagramme, utiliser le `.drawio`, et non importer les PNG comme images.

## Périmètre et sources

Modèle établi à partir du sujet extrait dans `docs/sources/A26_Site_Logistique.txt`, de `docs/01-cahier-des-charges.md`, de `docs/02-cas-utilisation.md`, de la matrice CRUD, et des contrôles de `src/Auth.php`, `src/Warehouse.php` et `public/index.php`.

Le schéma représente le projet réalisé : pas de portail Transporteur, indiqué comme facultatif dans le sujet. UC01 à UC10 conservent la numérotation documentaire ; UC01a détaille l’inscription et UC11 rend visible la gestion des comptes. Un compte en attente n’a pas accès aux fonctions métier. La connexion constitue une précondition de session, pas une inclusion à chaque action.

Le générateur `scripts/build-usecase-drawio.py` permet de reconstruire le fichier initial et les SVG. Attention : le relancer écrase ces fichiers générés ; conserver une copie distincte des modifications manuelles faites dans Draw.io.

Validation : XML analysé, références des connecteurs contrôlées, absence de chevauchement entre ellipses vérifiée, aperçus rendus dans Chromium et inspectés visuellement. Le fichier Draw.io n’a pas été ouvert dans l’éditeur Draw.io durant cette génération.
