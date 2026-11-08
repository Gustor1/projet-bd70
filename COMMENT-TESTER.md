# Comment tester toute l’application Transit — BD70

Ce guide couvre les fonctionnalités du sujet A26 et les critères de la grille. Chaque scénario donne le compte, les actions et le résultat attendu. Cocher seulement après exécution réelle : ce document ne prouve pas à lui seul la réussite sur un autre poste. Les originaux du sujet et de la grille sont dans `document projet/`.

## 1. Démarrer et préparer les tests

Pour une première installation sur un autre PC, suivre d’abord [INSTALLATION-LOCALE.md](INSTALLATION-LOCALE.md).

Prérequis testés : Windows, PHP 8.2 avec PDO MySQL/mbstring, MariaDB 10.4, Edge/Chromium. Adapter les chemins XAMPP selon le [README](README.md).

Depuis la racine du dépôt :

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start.ps1
```

Ouvrir [Transit](http://127.0.0.1:8070). Le premier lancement installe le jeu riche ; les suivants conservent les données. Sur une ancienne installation, suivre la migration du README : un `git pull` ne migre pas une base existante.

```powershell
# Sur une installation existante déjà migrée
& C:/xampp2/php/php.exe scripts/comptes-demo.php
```

Les 13 comptes sont décrits dans [COMPTES-TEST.md](COMPTES-TEST.md). **Mot de passe commun : `Entrepot2026!`.** Utiliser plusieurs profils de navigateur pour des sessions indépendantes.

### Faire les essais dans une base distincte

Les créations, validations et expéditions changent les données. Pour conserver la démonstration principale, importer un jeu indépendant :

```powershell
& C:/xampp2/php/php.exe scripts/install.php bd70_demo_essais_groupe_01
$env:BD70_DATABASE='bd70_demo_essais_groupe_01'
& C:/xampp2/php/php.exe scripts/import-demo.php
& C:/xampp2/php/php.exe -S 127.0.0.1:8073 -t public
```

Tester alors [le serveur d’essais](http://127.0.0.1:8073). Garder ce terminal ouvert ; Ctrl+C arrête le serveur. Retirer ensuite la variable avec `Remove-Item Env:/BD70_DATABASE`. Ne pas poursuivre après une commande en échec. Pour recommencer, prendre un nouveau nom de base ; ne pas réimporter dans une base déjà remplie. Ces commandes ne changent pas la configuration du serveur principal au port 8070.

Choisir un préfixe unique, par exemple **TEST-01**, pour toutes ses fiches. Les horaires saisis sont ceux du site **Europe/Paris**.

Le jeu riche est historique, avec une référence au **28 octobre 2026**. Pour ses graphiques, choisir par exemple du 29 septembre au 28 octobre 2026. Stock disponible et DLC sont calculés à la date actuelle : des lots historiques peuvent être périmés. Le parcours ci-dessous crée des lots futurs pour ne pas dépendre de leurs dates.

## 2. Connexion, inscription et profils

- [ ] Se connecter avec les 11 comptes actifs, vérifier le nom/profil, le menu puis la déconnexion.
- [ ] Mauvais mot de passe, compte `pending` ou `inactive` : connexion refusée.
- [ ] Inscrire une adresse unique depuis l’écran public : le compte reste en attente. Avec **admin**, choisir un profil interne, laisser la société vide et l’activer ; sa connexion fonctionne. Le désactiver et vérifier le refus à la reconnexion.
- [ ] Avec **admin**, consulter comptes/journal ; tenter directement `/?page=orders` et `/?page=stock` : refus d’accès métier.
- [ ] Avec **manager**, consulter Indicateurs ; tenter `/?page=catalog&t=user_account` : refus.
- [ ] Avec **warehouse2**, tenter l’URL d’une commande affectée à **warehouse** : refus. Tester l’URL, pas seulement l’absence du bouton.
- [ ] Avec **carrier1**, tenter `/?page=stock`, `/?page=reports` et `/?page=catalog` : refus.
- [ ] Avec les outils réseau, envoyer un formulaire sans jeton CSRF valide : refus. La recette HTTP automatise aussi ce contrôle.

**Attendu :** droits vérifiés côté serveur ; l’administrateur technique ne remplace pas le responsable et un magasinier ne s’affecte pas lui-même une commande.

## 3. Référentiels : ajouter, modifier, supprimer et contrôler les saisies

**Compte : manager**, dans **Référentiels**. Créer les fiches suivantes, nécessaires au parcours complet :

| Fiche | Valeurs de test |
|---|---|
| Société du parcours | Utiliser la société affichée pour **carrier1** par le script des comptes. Créer en plus `TEST-01-TR` pour essayer le CRUD transporteur, avec coordonnées complètes. |
| Chauffeur | `TEST-01-Chauffeur`, société de carrier1, téléphone fictif, permis unique `TEST-01-PERMIS`. |
| Véhicule | Plaque `TEST-01-CAM`, même société, type **porteur**, **20 000 kg / 30 palettes**. |
| Quai | `TEST-01-Q`, type **mixte** ; ajouter sa compatibilité avec **porteur**. Aucun équipement spécial pour l’article ambiant. |
| Propriétaire et fournisseur | `TEST-01-CLI` et `TEST-01-FOU`, coordonnées fictives complètes. |
| Article | `TEST-01-ART`, propriétaire ci-dessus, **ambiant**, carton, **0,1 × 0,1 × 0,1 m**, **1 kg/unité**, **20 unités/palette**. |
| Structure physique | Zone `TEST-01-Z` ambiante → allée `TEST-01-A` → rack `TEST-01-R` → niveau `TEST-01-N`. |
| Emplacements | `TEST-01-E1` et `TEST-01-E2`, dans ce niveau ; chacun **2 × 2 × 2 m**, **1 000 kg**, **10 équivalents palettes**. |

- [ ] Créer une fiche supplémentaire inutilisée, la rechercher, modifier son nom puis la supprimer sans outil SQL.
- [ ] Référence/plaque/permis en double, email invalide, dimension négative, capacité nulle, quantité non entière : refus.
- [ ] Créer/modifier un contrat et un contact de transporteur, une habilitation datée et son association à un chauffeur. Tester le renouvellement de validité.
- [ ] Créer un équipement et ses associations à un quai/véhicule inutilisés ; modifier puis supprimer ces associations.
- [ ] Après utilisation dans le parcours, supprimer le chauffeur/véhicule référencé : refus. Les libellés/coordonnées permis restent corrigeables, les propriétés historiques protégées restent figées.

## 4. Quais, rendez-vous et portail transporteur

**Comptes : manager, puis carrier1/carrier2.**

- [ ] Créer `TEST-01-RDV`, entrant, pour le nouveau chauffeur/véhicule/quai, proche de l’heure du test (maintenant → +30 minutes en heure de Paris).
- [ ] Déplacer le rendez-vous avant l’arrivée, le remettre sur le créneau retenu et filtrer par jour/quai.
- [ ] Créer un chevauchement sur le même quai : refus. Tester aussi le même véhicule/chauffeur réservé sur un autre quai et un type de véhicule incompatible.
- [ ] Ajouter une indisponibilité sur un autre créneau libre ; le quai est hors service à cette heure et une réservation conflictuelle est refusée.
- [ ] Annuler un rendez-vous distinct inutilisé : historique conservé. Un créneau adjacent libre reste autorisé.
- [ ] Avec **carrier1**, retrouver `TEST-01-RDV`, appartenant à sa société ; créer/modifier/annuler un **autre** rendez-vous futur avec ses ressources.
- [ ] Avec **carrier2**, les rendez-vous de carrier1 sont absents. Copier son lien de modification : aucune action possible. Les sélecteurs ne proposent pas les ressources de l’autre société.

**Attendu :** états libre/réservé/occupé/hors service cohérents. Actualisation toutes les 30 secondes hors saisie ; ce n’est pas une synchronisation instantanée.

## 5. Passage entrant et responsabilités à quai

1. **gate** → Passages camions → Enregistrer une arrivée : `TEST-01-ENTREE`, lié à `TEST-01-RDV`.
2. Contrôler les documents, renseigner le résultat, passer éventuellement au parking puis appeler au quai du parcours.
3. Avec **gate**, début/fin d’opération interdits. Avec **warehouse**, enregistrer le **début de l’opération** et garder le camion en opération pour recevoir la marchandise.

- [ ] Chronologie horodatée sans retour arrière ni double étape ; ressources du rendez-vous reprises ; quai occupé.
- [ ] Deuxième occupation du même quai ou deuxième arrivée d’un véhicule déjà sur site : refus.
- [ ] Sur un passage distinct, refuser les documents et vérifier le statut refusé.

## 6. Réception, lots, avaries et réserves

**Compte : warehouse**, Réceptions → Avis, restes et réceptions guidées. Créer `TEST-01-AVIS`, fournisseur du parcours, date du jour, ligne de **20 unités** du nouvel article. Ouvrir `TEST-01-REC`, liée au passage entrant en opération, et allouer les 20 unités attendues.

Créer deux lots et deux fractions dans E1 :

| Fraction | Lot | DLC | Acceptées | Avariées | État/réserve |
|---|---|---|---:|---:|---|
| `TEST-01-P1` | `TEST-01-LOT-TOT` | aujourd’hui +60 jours | 12 | 2 | abîmé ; « Deux unités endommagées » |
| `TEST-01-P2` | `TEST-01-LOT-TARD` | aujourd’hui +90 jours | 6 | 0 | bon |

- [ ] Corriger une quantité du brouillon, puis remettre ces valeurs. Référence palette en double ou lot d’un autre article : refus.
- [ ] Valider : **20 reçues, dont 18 acceptées et 2 avariées**, réserve et écart consultables. Les avaries ne deviennent pas disponibles.
- [ ] Nouvelle validation : aucun mouvement supplémentaire. Réception validée non éditable/supprimable librement.

Avec **warehouse**, finir l’opération ; avec **gate**, enregistrer le départ. Le quai redevient disponible si aucune autre contrainte ne s’y applique.

### Variantes sur des dossiers distincts

- [ ] Avis attendu 10 : sur une première livraison, allouer 6 et recevoir 4 → manquant 2 et reste à allouer 4. Recevoir les 4 restantes sur un nouveau passage/réception → total reçu 8, écarts 2, sans double allocation. Clôturer avec motif.
- [ ] Réception de 5 unités attendues : réserver un manquant total sans créer de palette puis valider. Aucun stock fictif.
- [ ] Tester un excédent accepté, une réserve générale et une réserve de ligne ; retrouver les écarts dans l’historique.
- [ ] Avis clôturé et lignes protégés même sans réception.

## 7. Stocks, rangement, transferts et ajustements

**Compte : warehouse**, Stocks & rangement.

- [ ] Filtrer article + propriétaire + lot + zone + emplacement. Physique du nouvel article : **18 unités**.
- [ ] Demander des propositions d’emplacements : compatibilité et capacité suffisantes.
- [ ] Transférer **3 unités de P1 de E1 vers E2**, avec motif. Lot précoce : **9 en E1, 3 en E2**. Total article inchangé à 18.
- [ ] Transfert trop grand, destination incompatible ou trop petite : refus sans débit partiel. Capacités kg, m³ et palettes vérifiées séparément.
- [ ] Sur un autre article/fraction, ajuster +1 puis −1 avec motifs : total initial retrouvé, deux mouvements conservés. Motif vide ou stock négatif : refus.
- [ ] Sur un scénario distinct, bloquer un lot avec motif ; disponible nul. Un lot périmé reste physique mais est exclu du disponible et de FEFO.

## 8. Commande, affectation et FEFO

1. **manager** : créer `TEST-01-CMD`, propriétaire et article du parcours, adresse fictive, date souhaitée ; ligne de **10 unités**.
2. Affecter **warehouse@bd70.test**. L’affectation seule ne réserve rien.
3. **warehouse2** : commande absente de ses commandes ; URL directe interdite.
4. **warehouse** : lancer FEFO sur la commande affectée. Les 10 unités proviennent du lot à DLC +60 jours, avant celui à +90 jours. Dans notre répartition, les prélèvements sont **9 +1** ; vérifier les lignes effectivement affichées.
5. Confirmer les prélèvements par ligne ou tous ensemble : commande prête.

- [ ] Avant expédition : physique 18, réservé 10, disponible 8.
- [ ] Un magasinier ne peut pas affecter/réaffecter une commande ; le responsable ne peut pas confirmer les prélèvements/expédier à sa place.
- [ ] Quantité supérieure au disponible : refus sans réservation partielle. Article d’un autre propriétaire : refus.
- [ ] Sur une **autre commande**, réserver puis reprendre en brouillon avec motif par le responsable : réservations libérées, anciens prélèvements annulés conservés. Corriger et réaffecter à warehouse2 ; l’ancien préparateur perd l’accès et le nouveau peut préparer. Une commande expédiée ne peut plus être reprise.

## 9. Colis, chargement, expédition et documents

**Compte : warehouse**, fiche de la commande prête.

1. Créer `TEST-01-C1` et `TEST-01-C2`. Répartir **exactement** chaque prélèvement : pour 9 +1, C1 reçoit 5 du premier ; C2 reçoit 4 du premier et 1 du second. Chaque colis contient 5.
2. Essayer une surallocation : refus. Corriger/retirer une allocation puis rétablir la répartition exacte. Créer et supprimer un conditionnement vide supplémentaire.
3. **gate** : arrivée `TEST-01-SORTIE`, **sans rendez-vous**, opération expédition. Réutiliser le chauffeur/véhicule seulement après leur départ entrant. Contrôler les documents, appeler au quai mixte libre.
4. **warehouse** : débuter le chargement à quai. Dans la commande, sélectionner le passage sortant en opération et confirmer chargement/expédition.
5. **warehouse** termine à quai ; **gate** enregistre le départ.

- [ ] Camion non en opération, opération entrante, capacité insuffisante ou colis incomplets : expédition refusée.
- [ ] Débit de **10 une seule fois** : physique 8, réservé 0, disponible 8, si aucun autre mouvement n’a été ajouté.
- [ ] Il reste 2 unités du lot précoce et 6 du lot tardif ; les avaries sont exclues.
- [ ] Imprimer liste de prélèvement, bon de livraison et lettre de voiture : vérifier références, destination, lots, quantités, transporteur, véhicule et totaux, sans débordement.
- [ ] Deuxième expédition de la même commande : refus sans nouveau débit.

## 10. Traçabilité complète d’un lot

**Compte : manager**, Traçabilité des lots.

- [ ] Chercher `TEST-01-LOT-TOT` : retrouver fournisseur, avis, réception, avarie/réserve, fraction, emplacement initial, transfert E1 → E2, prélèvements, commande et camion sortant.
- [ ] Quantités et ordre des événements cohérents. La sortie projetée depuis le prélèvement ne compte pas deux fois.
- [ ] Sur le jeu riche, consulter un lot reçu plusieurs fois, réparti sur plusieurs emplacements et expédié dans plusieurs commandes : provenances distinctes.
- [ ] Recherche absente et pagination : état vide lisible, sans erreur.

## 11. Indicateurs, filtres, graphiques, exports et impressions

**Compte : manager**, Indicateurs & états.

- [ ] Période historique du jeu riche : tableaux/graphiques d’occupation des quais, attentes/immobilisations par transporteur, remplissage par zone, écarts en réception, productivité et lots proches de DLC.
- [ ] Journée du parcours : retrouver les nouvelles opérations, les 2 unités avariées et le travail du préparateur. Un test rapide peut donner de petites durées d’attente.
- [ ] Changer période et horizon DLC ; une période sans activité donne zéro ou un résultat vide, sans division par zéro.
- [ ] Distinguer **activité sur la période** et **stock/DLC à la date actuelle**. Le stock affiché n’est pas une photographie historique.
- [ ] Combiner filtres, recherche, tri et pagination du stock, des passages et réceptions ; réinitialiser. Une combinaison contradictoire donne zéro résultat.
- [ ] Avec le responsable, tester `/?page=export&kind=stock`, `kind=visits` et `kind=receipts`. Ajouter les mêmes paramètres que les filtres des écrans (ex. `&article_id=...`, ou `&from=AAAA-MM-JJ&to=AAAA-MM-JJ`). Vérifier colonnes, accents, séparateur et correspondance au filtre. Ces exports sont autorisés au responsable, même quand l’écran de saisie correspondant est réservé au magasinier/à l’accueil.
- [ ] Imprimer le tableau de bord et les états : tableaux/unités lisibles et navigation masquée à l’impression.

## 12. Historisation, concurrence et finition

- [ ] **admin** → journal : retrouver les créations/modifications/suppressions du parcours, auteurs et valeurs avant/après. Aucun hachage de mot de passe dans les instantanés.
- [ ] Mouvements, événements et expéditions validés sans édition/suppression libre ; correction du stock par nouveau mouvement motivé.
- [ ] Deux sessions **manager/pilotage**, même créneau : une seule réservation conflictuelle acceptée.
- [ ] Deux accueils ne peuvent pas occuper le même quai ; deux préparations ne réservent pas plus que le stock ; deux rangements ne dépassent pas ensemble une capacité. Les quatre courses sont aussi exécutées par `tests/integration.php` sur base dédiée.
- [ ] Parcourir au clavier Tab/Entrée ; vérifier menu, libellés, listes vides et messages. Un rafraîchissement ne rejoue pas une validation.
- [ ] Largeurs de 390 et 768 px : formulaires/boutons accessibles, tableaux défilables. Un simulateur navigateur n’est pas un essai sur téléphone physique.
- [ ] Sélecteurs avec références/noms lisibles, pas seulement des identifiants bruts. Au-delà de 2 000 propositions, utiliser « Affiner les listes de sélection ».

## 13. Tests techniques reproductibles

### Comptes

Exécuter `scripts/comptes-demo.php` deux fois : le second passage doit annoncer les comptes déjà conformes sans les réécrire. `--reinitialiser` sert à les rétablir volontairement après des tests de rôles/mots de passe ; voir [le fichier des comptes](COMPTES-TEST.md).

Pour vérifier automatiquement les comptes sur une base neuve de test **chargée par import-demo.php** : définir `BD70_DATABASE`, puis exécuter `php tests/comptes-demo.php`. Cette suite vérifie profils, mots de passe, sociétés, absence de réécriture au second passage, conservation d’un compte personnalisé et rétablissement explicite. Elle modifie uniquement cette base de test. `node tests/comptes-browser.cjs` vérifie les 11 connexions et les 2 refus sur le serveur indiqué par `BD70_URL` (8070 par défaut).

### Tests métier automatiques

Utiliser une base **neuve et distincte par suite**, car les tests mutent les données :

```powershell
& C:/xampp2/php/php.exe scripts/install.php bd70_test_manuel_integration_01
$env:BD70_DATABASE='bd70_test_manuel_integration_01'
$env:BD70_TEST_DATABASE=$env:BD70_DATABASE
& C:/xampp2/php/php.exe scripts/seed.php
& C:/xampp2/php/php.exe tests/integration.php
Remove-Item Env:/BD70_DATABASE,Env:/BD70_TEST_DATABASE
```

Répéter avec un autre nom neuf pour `tests/completion.php`, `tests/finalisation.php`, `tests/corrections.php` et `tests/optimisation.php` (soldes tenus par triggers égaux au recalcul, fonction `stock_disponible`, prélèvement expédié figé). Charger `seed.php` une seule fois par base. `tests/time.php` contrôle Paris et les transitions saisonnières.

Pour l’ensemble de la recette isolée :

```powershell
$env:BD70_RUN_ID='recette-groupe-01'
# Si nécessaire : BD70_PLAYWRIGHT vers Playwright ; BD70_NODE et BD70_PYTHON vers les runtimes adaptés.
python scripts/verify-finalisation.py
Remove-Item Env:/BD70_RUN_ID
```

Cet outillage exige Python, Node, Playwright/Edge et les dépendances des scripts. L’application PHP fonctionne sans ces outils. Les ports de recette 8071/8072 doivent être libres. Le script crée ses bases et serveurs dédiés ; lire tous les codes de sortie et le manifeste dans `docs/preuves/<identifiant>/`.

Les suites navigateur actuelles sont `tests/corrections-browser.cjs` et `tests/parcours.cjs`. Le premier utilise les comptes créés par `tests/corrections.php` sur le jeu réduit.

### Intégrité, performances, sauvegarde et migration

- **Intégrité :** définir `BD70_DATABASE` vers la base voulue puis exécuter `scripts/validate-data.php`. Vérifie FK, stocks, capacités, allocations, colis, sorties, propriétaires, chronologie et audit en lecture.
- **Performances :** installer une base neuve `bd70_perf*`, ne pas la seeder, définir `BD70_DATABASE` puis lancer `scripts/performance.php 10000`. Huit requêtes, chauffe puis dix exécutions et EXPLAIN ; comparer médianes/unités, en tenant compte de la machine et du cache.
- **Optimisation avant/après :** sur une base de test neuve chargée par `import-demo.php`, lancer `scripts/performance-optimisation.php` (variable `BD70_DATABASE`). Le script mesure avec les anciennes vues GROUP BY, rétablit la table de soldes, mesure à nouveau et écrit gain absolu et relatif dans `docs/preuves/performances-optimisation.json` ; `python scripts/build-performances-md.py` régénère `docs/performances.md`. `scripts/validate-data.php` doit afficher 0 pour `soldes_egaux_historique`.
- **Sauvegarde/restauration :** définir `BD70_BACKUP_SOURCE` vers la démonstration et `BD70_RESTORE_TARGET` vers une nouvelle base `bd70_restore*`, puis `python scripts/backup-restore.py`. Compare 41 tables et routines/triggers, puis vérifie l’audit dans la copie. Le dump reste dans `.local/`.
- **Migration :** `php scripts/migrate-corrections.php source cible_neuve`, selon le README. Compare les faits et conserve la source ; la bascule du dbname est une étape distincte.

Employer de nouveaux noms pour rejouer les essais, sans supprimer de bases existantes. Dumps, secrets SQL et sessions ne sont pas des livrables GitHub.

## 14. Vérifier la conception et le rapport

- [ ] [Cahier des charges](docs/01-cahier-des-charges.md) et [scénarios](docs/02-cas-utilisation.md) cohérents avec les actions testées.
- [ ] [Diagramme de cas d’utilisation V2](livrables/use-case/UML-CAS-UTILISATION-BD70-CORRIGE.pdf) et Draw.io : une page, chaque acteur dessiné une fois, aucun héritage, planification par le responsable, affectation et exécution séparées, transporteur limité à sa société, cas éclatés avec include/extend.
- [ ] [MCD Chen V2](livrables/entite-association/BD70-MCD-CHEN.pdf) et Draw.io : attributs en ovales, identifiants soulignés (visibles dans le PDF), cardinalités placées comme dans le cours (« Client 1 — Possède — 0,N Facture »). Le lien compte/société et les mouvements conditionnels correspondent au schéma courant. Voir [l’index des modèles](docs/modeles-reference.md).
- [ ] [MLD](docs/diagrammes/mld-complet.svg), [dictionnaire](docs/dictionnaire-donnees.md), SQL et [normalisation](docs/normalisation-3nf.md) : PK, FK, types, nullabilités, 1:N/N:N, dépendances et contraintes. Les sorties projettent quantité/emplacement/fraction depuis le prélèvement ; les JSON d’audit sont des instantanés techniques intentionnels.
- [ ] [Rapport](livrables/rapport/RAPPORT-PROJET-BD70.pdf) : introduction, sommaire, auteurs, objectif/travail réalisé/conclusion par domaine, captures et bilan. [Recueil](livrables/rapport/DIAGRAMMES-BD70.pdf) : cas d’utilisation V2, MCD V2, MLD et six extraits par domaine.
- [ ] [Performances](docs/performances.md) et JSON : requêtes, paramètres, volumes, mesures et plans. Le nombre de tables seul ne prouve pas la qualité du modèle. La [matrice CRUD](docs/matrice-crud-droits.md) détaille les opérations permises pour chaque relation.

## 15. Correspondance avec le sujet et la grille

| Attendu | Sections à exécuter |
|---|---|
| Connexion, inscription, multi-utilisateurs, droits | 2 ; 4 pour les transporteurs ; 8 pour l’affectation |
| Transporteurs, chauffeurs, contrats, habilitations, véhicules | 3 |
| Quais, équipements, compatibilité, rendez-vous | 3–4 ; concurrence en 12 |
| Flux de camions avec/sans rendez-vous, heures, attentes/retards | 5 ; 9 ; 11 |
| Avis, réception, lots, DLC, palettes, écarts et réserves | 6 |
| Emplacements, catalogue, propriétaires, stockage et mouvements | 3 ; 7 |
| Commandes, préparateurs, FEFO, colis, chargement et documents | 8–9 |
| Traçabilité complète | 10 |
| Recherches multicritères, tableaux, graphiques et états | 7 ; 11 |
| Ajout/édition/suppression et saisies contrôlées | 2–3 ; brouillons en 6 ; colis en 9 |
| Sécurité, confidentialité et automatisation interne | 2 ; 12–13 |
| Base riche, clés/types, relations, normalisation, performances | 3 ; 13–14 |
| Cahier des charges, UML, MCD, MLD et rapport | 14 |
| Ergonomie et finition générale | 11–12 ; rapport en 14 |

Le minimum web du sujet porte sur cinq domaines ; ce guide couvre aussi les commandes/expéditions et le portail transporteur réalisés en complément. La validation du MCD, les modalités de remise/soutenance et la note restent du ressort de l’enseignant.


## Contrôles ajoutés (historisation, HAVING, droits de l’accueil)

- [ ] **manager** → Quais & rendez-vous → « Nouveau rendez-vous » : créer un rendez-vous sur un créneau libre, puis tenter le même quai et le même horaire : refus « Ce créneau chevauche un rendez-vous actif ». Avec **gate**, le bouton n’apparaît pas (planification réservée au responsable).
- [ ] **manager** → Indicateurs : champ « Seuil d’attente (min) » ; le tableau « Transporteurs au-dessus du seuil d’attente » utilise GROUP BY … HAVING. Avec le jeu riche, un seuil de 8 affiche les transporteurs ; un seuil de 20 n’en affiche aucun.
- [ ] **manager** → Référentiels → rubrique « Rendez-vous historisés » : consultation en lecture seule (aucun bouton de modification).
- [ ] En SQL, sur une base de test uniquement : `CALL archive_appointments(30);` puis `SELECT origine, COUNT(*) FROM v_appointment_all GROUP BY origine;` ; `SHOW EVENTS;` affiche ev_archive_appointments.
- [ ] En SQL, sur une base de test : insérer un rendez-vous actif chevauchant un autre sur le même quai → erreur 45000 levée par le trigger.

## 16. Consigner sa recette

Pour une anomalie, noter : version Git (`git rev-parse --short HEAD`), date, base/URL, compte, référence de l’objet, étapes exactes, résultat attendu/observé et capture éventuelle. Ne pas joindre les secrets SQL ni les cookies.

| Test | Compte | Référence créée | Réussi ? | Observation |
|---|---|---|---|---|
| Connexion et refus | | | | |
| CRUD et saisies | | | | |
| Planning et conflits | | | | |
| Passage et réception | | | | |
| Partiels/manquants/réserves | | | | |
| Stocks et mouvements | | | | |
| Affectation et FEFO | | | | |
| Colis et expédition | | | | |
| Traçabilité | | | | |
| Indicateurs et impressions | | | | |
| Isolement préparateurs/sociétés | | | | |
| Conception et performances | | | | |
