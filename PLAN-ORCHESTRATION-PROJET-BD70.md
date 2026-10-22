# Plan d’orchestration du projet BD70 — Entrepôt logistique

Ce document est une consigne de travail à transmettre à une IA avec les quatre fichiers sources. Il organise la réalisation du projet, depuis l’analyse jusqu’à la livraison vérifiée. Il ne constitue ni un modèle de données déjà validé, ni la preuve d’une application réalisée.

Analyse des documents effectuée le 22 octobre 2026. Les choix d’architecture, les volumes de données et les tests proposés ci-dessous sont des recommandations de réalisation, sauf lorsqu’ils sont explicitement rattachés à une exigence des sources.

## 1. Mission à donner à l’IA

Tu dois réaliser le projet BD70 « Système de Gestion d’un Entrepôt Logistique » en appliquant ce plan et les documents sources. Le résultat doit être compréhensible et présentable par des étudiants : modèle relationnel justifié, SQL explicite, application fonctionnelle, preuves de tests et rapport fidèle au travail réalisé.

Lis les sources avant de coder. Réalise les lots dans l’ordre de leurs dépendances. Pour chaque lot, produis ses livrables, vérifie ses critères de sortie et mets à jour le suivi. Corrige les défauts avant de poursuivre. Ne demande pas une confirmation après chaque étape : avance sur les décisions techniques réversibles, en consignant les hypothèses. Demande une précision seulement lorsqu’une information manquante bloque réellement la conformité ou impose un choix irréversible.

Si tu as accès au dossier du projet, travaille directement dedans en préservant les fichiers existants. Si tu ne peux pas exécuter le code, fournis les fichiers et les commandes nécessaires, mais indique clairement les vérifications non exécutées. N’invente jamais une capture d’écran, une mesure de performance ou un résultat de test.

### Sources à lire et priorité

| Référence | Fichier relatif à la racine | Rôle |
|---|---|---|
| S | `document projet/A26_Site_Logistique.pdf` — 3 pages | Sujet spécifique, périmètre, livrables et contraintes techniques |
| E | `document projet/Éléments dévaluation projet BD70.docx` | Critères qualitatifs d’évaluation |
| C | `document cours/BD70_A25 (4).pptx` — 261 diapositives | Concepts et méthode de conception, SQL, administration |
| W | `document cours/BD70_Introduction Web_A25.pptx` — 31 diapositives | Architecture web, HTML, PHP et PDO |

Le sujet S définit le domaine logistique ; les exemples « agence de voyage » et « recettes » du cours C ne sont pas le projet à réaliser. S autorise MySQL/MariaDB ou PostgreSQL. La mention MySQL du cours oriente le choix pédagogique sans annuler les alternatives du sujet. La grille E mentionne VBA **ou un langage approprié** : elle n’impose ni VBA ni Access.

La grille E ne donne pas de points par critère : ne pas inventer de barème ou promettre une note. Le cours C indique un projet en groupe de 2 ou 3 et une soutenance de 10 minutes (diapositive 8) ; ces modalités A25 sont à confirmer pour A26. Aucune date de remise n’est indiquée dans le sujet fourni. Prévoir la soutenance sans transformer ces modalités anciennes en certitudes.

## 2. Périmètre et stratégie de conformité

### Trois niveaux à distinguer

1. **Base complète obligatoire** : le modèle doit permettre toutes les fonctionnalités de S, y compris préparation, expédition, documents de transport et traçabilité.
2. **Interface minimale obligatoire** : authentification, quais/rendez-vous, flux de camions, réception, emplacements/stocks (S, p. 2). Les recherches, filtres, statistiques et rapports restent requis par les exigences générales.
3. **Compléments retenus pour couvrir la grille** : écrans de gestion des référentiels et des commandes/expéditions, tableaux et graphiques, états imprimables. Ils répondent notamment au critère E « ajout, édition, suppression pour l’ensemble des données sans intervention sur les tables ».

La cible de ce plan inclut le troisième niveau, avec des écrans simples. Le minimum web ne doit pas être présenté comme couvrant automatiquement toute la grille. Si une contrainte de délai force à réduire ce niveau, conserver le modèle complet et les données de simulation, puis signaler exactement la couverture restante dans le rapport. Ne pas déclarer le projet pleinement terminé dans ce cas.

Les journaux, mouvements validés et historiques ne doivent pas devenir librement modifiables pour satisfaire littéralement le CRUD : fournir une annulation ou une correction métier traçable. Autoriser la suppression physique de brouillons et de référentiels inutilisés ; protéger les éléments déjà référencés, avec explication à l’utilisateur. Documenter cette politique dans la matrice CRUD.

### Couverture fonctionnelle attendue

| ID | Domaine et exigences à couvrir | Interface cible et preuve |
|---|---|---|
| F01 | Inscription, connexion, déconnexion ; administrateur, responsable d’exploitation, agent d’accueil, magasinier/préparateur ; droits distincts | Formulaires, comptes de démonstration et tests d’accès par rôle. Le rôle transporteur est explicitement optionnel dans S. |
| F02 | Transporteurs : coordonnées, contrats, contacts ; chauffeurs : identité, téléphone, permis, habilitations ; véhicules : tracteur, remorque, porteur, fourgon, immatriculation, capacités et caractéristiques | Écrans de référentiels et associations ; sélections lisibles dans les formulaires opérationnels |
| F03 | Quais : réception/expédition/mixte, équipements, compatibilités ; rendez-vous sans chevauchement ; libre/réservé/occupé/hors service | Planning filtrable, création/modification/annulation, contrôle concurrent et actualisation de l’état |
| F04 | Arrivée, contrôle documentaire, attente parking, appel à quai, début/fin d’opération, départ ; horodatages ; retards ; arrivées sans rendez-vous | Parcours de poste de garde et boutons de transition ; chronologie d’un passage |
| F05 | Avis fournisseurs et lignes attendues ; réception effective, quantités, lots, DLC éventuelles, état des palettes ; manquants, excédents, avaries, réserves ; rangement | Formulaires de réception et propositions d’emplacements compatibles ; comparaison attendu/reçu |
| F06 | Zones ambiant/froid/dangereux, allées, racks, niveaux, emplacements et capacités ; articles, dimensions, poids, conditionnements, conditions de stockage, propriétaires ; stocks et mouvements | Recherche multicritère, entrée/transfert/sortie/ajustement, historique et refus des incohérences |
| F07 | Commandes et lignes, date souhaitée ; liste de prélèvement FIFO ou FEFO et affectation ; colis/palettes ; chargement sortant ; bon de livraison et lettre de voiture | Modèle et traitements démontrables ; écrans simples et documents imprimables prévus pour la couverture de E |
| F08 | Traçabilité complète des lots ; occupation quais ; attente et immobilisation par transporteur ; remplissage par zone ; écarts ; productivité ; proximité des DLC | Vue de traçabilité, tableaux, graphiques, filtres de période et états exportables |

## 3. Architecture proposée et lien avec le cours

Choix par défaut : **PHP avec PDO, HTML/CSS, MySQL avec tables transactionnelles InnoDB**, JavaScript limité aux améliorations d’ergonomie et aux graphiques. Ce choix suit directement W, notamment les diapositives 20 et 30. MariaDB est une alternative si c’est le moteur disponible, mais choisir et tester **un moteur précis**, sans revendiquer une compatibilité non vérifiée.

Avant installation, relever les versions et outils déjà présents. Fixer ensuite les versions utilisées dans le README. Éviter les dépendances externes indispensables à la démonstration : garder les ressources nécessaires en local. Un framework lourd, un ORM ou une application monopage ne sont pas nécessaires pour atteindre les objectifs pédagogiques.

Séparer les responsabilités, même avec une petite application :

- navigateur : formulaires, navigation, tableaux, graphiques ;
- contrôleurs PHP : réception des requêtes, authentification, autorisations, validation ;
- services métier : transitions et orchestration des opérations ;
- accès PDO : SQL paramétré et récupération des résultats ;
- base : contraintes, relations, traitements internes et historisation automatique.

Les compléments techniques nécessaires à une application fiable — sessions, protection CSRF, gestion des mots de passe, verrouillage concurrent — doivent être expliqués comme des applications des exigences de sécurité/intégrité, sans prétendre que leur détail figure dans les supports.

| Notion enseignée | Repères du cours | Application au projet |
|---|---|---|
| Clés, types, relations 1:N et N:N | C 29–49 | Transporteur/chauffeurs, commandes/lignes, compatibilités et habilitations |
| Analyse, cas d’utilisation UML, pré/postconditions | C 197–210 | Cahier des charges et scénarios par rôle avant les tables |
| Entités, associations, cardinalités, traduction relationnelle | C 211–224 | MCD distinct du MLD ; justification des tables de jointure |
| Dépendances fonctionnelles et 1NF/2NF/3NF | C 166–196 | Dictionnaire, clés candidates, suppression des redondances |
| SELECT, filtres, agrégats, GROUP BY/HAVING, jointures | C 68–103 | Recherches, statistiques et traçabilité |
| INSERT, UPDATE, DELETE, DDL, vues, contraintes | C 83–88 et 104–122 | CRUD, schéma, contraintes et vues de consultation |
| Index et coûts | C 123–130 | Optimisation guidée par les requêtes réelles |
| Procédures, fonctions, déclencheurs, événements | C 135–154 | Opérations métier en base et historique automatique |
| Droits SQL et transactions ACID | C 155–165 et 233–240 | Compte applicatif limité, opérations atomiques, accès concurrents |
| Sauvegarde, performances, journalisation | C 241–250 | Restauration testée, mesures, suivi des erreurs |
| Architecture trois tiers, HTML, formulaires, PHP/PDO | W 4–7, 9–18, 20–31 | Application web avec formulaires et requêtes préparées |

Les exemples de cours servent à comprendre les notions. Vérifier la syntaxe SQL et le comportement sur le moteur retenu ; certains exemples mélangent des dialectes ou simplifient des comportements. Ne pas recopier aveuglément des identifiants administrateur, des suppressions en cascade ou des opérations DDL dans une démonstration de rollback.

## 4. Organisation de l’exécution

Un même agent peut assurer tous les rôles successivement. Si l’outil permet une équipe d’agents et que cette organisation est retenue, partager le travail selon ces responsabilités, avec un seul intégrateur responsable des fichiers communs :

| Rôle | Responsabilité | Dépendance |
|---|---|---|
| Orchestrateur | Exigences, arbitrages, suivi, intégration, contrôle final | Toutes les phases |
| Analyste/concepteur | Cas d’utilisation, règles métier, MCD, MLD, 3NF | Avant le développement |
| Développeur BDD | Schéma, contraintes, automatismes, données, requêtes, mesures | Modèle stabilisé |
| Développeur web | Parcours, formulaires, sécurité, recherche, restitution | Contrat BDD défini |
| Vérificateur/documentaliste | Recette, audit de conformité, rapport, captures | Prépare les tests dès l’analyse, vérifie les réalisations ensuite |

Ne pas développer indépendamment plusieurs schémas concurrents. Toute modification du modèle doit se répercuter sur MCD, MLD, dictionnaire, SQL, formulaires et tests. Les tâches parallèles possibles après stabilisation du modèle sont la préparation des données, les écrans indépendants et la rédaction des scénarios de recette.

### Suivi à maintenir

Créer `docs/SUIVI-PROJET.md` avec, pour chaque lot : état (`à faire`, `en cours`, `validé`, `bloqué`), livrables, tests exécutés et résultats, décisions, limites, prochaine action. Maintenir aussi une matrice `exigence → cas d’utilisation → tables → traitement/écran → test → section du rapport`.

À chaque reprise, lire ce suivi et vérifier les fichiers réels avant de continuer. Un fichier existant n’est pas une preuve de fonctionnement. En cas d’interruption, laisser les commandes de reprise et les points encore non testés.

## 5. Lots de réalisation et critères de sortie

### Lot 0 — Inventaire et cadrage technique

**Entrées :** les quatre sources, ce plan et le dossier existant.

1. Examiner `git status`, les éventuelles instructions locales et l’arborescence. Préserver les supports de cours et du projet. Ne pas effacer du travail antérieur.
2. Lire les sources intégralement, y compris tableaux et diagrammes utiles des présentations ; vérifier les contenus SmartArt si l’extraction textuelle paraît vide.
3. Confirmer le moteur, l’environnement PHP/PDO et les possibilités d’exécution locale ; documenter ce qui manque.
4. Initialiser le suivi, les exigences F01–F08, la matrice de conformité et le registre des hypothèses.
5. Préparer une configuration d’exemple sans secret, les exclusions Git et une procédure locale d’installation.

**Sortie :** inventaire complet, choix technique explicite, périmètre compris, aucune confusion entre minimum de S et couverture de E. Les noms des auteurs et la date de remise restent à renseigner par les étudiants s’ils ne sont pas connus.

### Lot 1 — Cahier des charges et cas d’utilisation

**Dépendance :** lot 0.

Produire `docs/01-cahier-des-charges.md`, `docs/02-cas-utilisation.md` et un véritable diagramme UML de cas d’utilisation avec sa source éditable et son export lisible. Un simple organigramme de pages ne suffit pas.

Définir les acteurs, limites du système et droits par opération. Pour chaque cas important, préciser objectif, acteur, préconditions, déroulement nominal, variantes/erreurs, postconditions et données affectées. Couvrir notamment la réception avec écart, le camion sans rendez-vous, la réservation concurrente, le transfert de stock et l’expédition partielle si elle est retenue.

Consigner les hypothèses nécessaires : un seul entrepôt ou plusieurs, fuseau horaire du site, unité des quantités et capacités, identification des lots, rattachement au propriétaire, réception partielle, stratégie FIFO/FEFO, annulation, droits d’inscription. Par défaut, privilégier un seul site et une politique métier simple, mais préserver toutes les fonctions demandées.

**Sortie :** chaque ligne F01–F08 possède des cas d’utilisation et un niveau d’interface ; tous les rôles ont des permissions explicites ; aucune règle structurante n’est laissée implicitement au développeur.

### Lot 2 — Modélisation conceptuelle, logique et normalisation

**Dépendance :** lot 1. Réaliser cette étape avant de créer les tables définitives.

Produire un MCD, un MLD, un dictionnaire et une justification de la 3NF. Le MCD présente les concepts et cardinalités ; le MLD précise tables, PK, FK, unicités et nullabilité. Fournir des exports lisibles et les sources des diagrammes.

#### Domaines à étudier dans le modèle

Les éléments suivants sont des **concepts candidats**, pas une liste de tables imposée. Justifier tout regroupement ou séparation :

- utilisateurs, rôles et affectations ;
- transporteurs, contacts, contrats, chauffeurs, permis/habilitations, véhicules et caractéristiques ; représentation de l’ensemble tracteur/remorque lorsqu’il intervient dans un passage ;
- quais, équipements, compatibilités, indisponibilités, rendez-vous ;
- passages camion, contrôles documentaires, événements horodatés, occupations effectives ;
- fournisseurs, avis d’expédition et lignes, réceptions et lignes, lots, palettes reçues, écarts et réserves ;
- clients propriétaires, articles, conditions de stockage et conditionnements ;
- zones, allées, racks, niveaux, emplacements, capacités ;
- mouvements et affectations de stock par lot, emplacement et propriétaire selon l’identification retenue ;
- commandes et lignes, tâches/lignes de prélèvement, préparateurs, colis/palettes de sortie, chargements, expéditions et documents de transport ;
- historiques métier nécessaires à la traçabilité.

#### Questions que le modèle doit résoudre

1. Une ligne de réception peut-elle contenir plusieurs lots ? Un lot peut-il être reçu plusieurs fois et réparti sur plusieurs emplacements ? Préserver ces possibilités par les associations adaptées.
2. Une ligne de commande peut-elle être servie par plusieurs lots ? Un lot peut-il alimenter plusieurs commandes ? Représenter les quantités dans les associations de prélèvement/expédition.
3. Comment distinguer le rendez-vous prévu du passage réel, y compris sans rendez-vous ?
4. Comment remonter d’une quantité expédiée à sa réception, ses emplacements successifs et son camion sortant ?
5. Comment conserver le propriétaire des marchandises sans confondre fournisseur, transporteur et client ?
6. Quelles capacités sont comparées, dans quelles unités, et comment convertir unités d’articles, poids, dimensions et palettes ?
7. Quelles données sont des faits historiques et quelles valeurs sont calculables (durées, totaux, disponibilités, taux) ?

#### Contrôle de normalisation

Pour chaque relation, indiquer les clés candidates et les dépendances fonctionnelles pertinentes. Vérifier les valeurs atomiques, les dépendances à toute clé candidate et l’absence de dépendance transitive problématique. Une clé artificielle ne suffit pas à prouver la normalisation.

Les équipements, habilitations et lignes de commande doivent être structurés par relations, pas stockés en listes séparées par des virgules. Éviter de recopier noms de transporteur et libellés d’article dans les tables opérationnelles. Calculer durées, totaux et indicateurs à partir de leurs faits sources. Distinguer les snapshots historiques justifiés des redondances accidentelles.

**Sortie :** couverture de F01–F08 ; plusieurs relations 1:N et N:N pertinentes ; toutes les cardinalités et contraintes expliquées ; chemin de traçabilité complet ; justification de 3NF table par table. Ne pas multiplier les tables artificiellement pour satisfaire un supposé quota d’entités.

### Lot 3 — Base, intégrité et automatisation

**Dépendance :** lot 2.

Créer des scripts SQL ordonnés : schéma, contraintes, index de base, vues, procédures et déclencheurs. Ajouter les scripts de privilèges séparément pour ne pas exiger un compte administrateur pendant l’usage normal de l’application.

Mettre les contraintes élémentaires dans la base : PK, FK, UNIQUE, NOT NULL, contrôles de domaines et de quantités lorsque le moteur choisi les prend en charge. Tester effectivement leur application. Définir les règles de suppression par relation pour conserver la traçabilité.

Pour les opérations multitable, fixer un seul responsable de la transaction : PHP ou procédure stockée, sans commits implicites contradictoires. Prévoir rollback, remontée d’erreur et gestion des conflits. Les écritures critiques doivent emprunter le même chemin contrôlé, y compris les modifications et annulations.

#### Invariants obligatoires à tester

| ID | Invariant | Mise en œuvre attendue |
|---|---|---|
| R01 | Deux réservations actives du même quai ne se chevauchent pas | Intervalles `[début, fin[` ; début strictement avant fin ; contrôle transactionnel sérialisé par quai, y compris création, déplacement et modification |
| R02 | Quai, véhicule, opération et équipements sont compatibles ; quai hors service indisponible | Vérification métier et état réel ; règle explicite pour les réservations existantes lorsqu’une indisponibilité est créée |
| R03 | Une seule occupation effective simultanée par quai | Contrôle à l’affectation et au début de service, indépendant du planning prévisionnel |
| R04 | Chronologie d’un passage cohérente | Transitions autorisées et horodatages ordonnés ; traitement explicite des étapes facultatives |
| R05 | Réception validée une seule fois | Entrée de stock atomique avec réception et historique ; double clic/rejeu sans double comptage |
| R06 | Stock disponible non négatif | Contrôle atomique des quantités disponibles, réservées et prélevées selon le modèle ; concurrence testée |
| R07 | Transfert conserve la quantité | Débit source et crédit destination dans une seule transaction, avec historique reliant les deux |
| R08 | Stockage compatible et capacité respectée | Contrôle produit/zone et capacité restante, y compris deux rangements simultanés |
| R09 | Marchandise endommagée ou bloquée non proposée comme disponible | État explicite et règle de disponibilité ; les réserves restent consultables |
| R10 | Chaque sortie correspond aux lots réellement prélevés et au chargement | Chaîne de références, quantités cohérentes et absence de double sortie |
| R11 | Historique créé automatiquement et rattaché à l’opération | Déclencheurs ciblés en base ; auteur et date pour les actions applicatives ; aucune donnée de mot de passe dans les journaux |
| R12 | Échec d’une opération ne laisse pas d’état partiel | Scénarios de rollback sur réception, transfert, prélèvement et réservation |

Pour MySQL, une proposition simple pour R01 consiste à verrouiller la ligne du quai dans une transaction, vérifier les chevauchements puis enregistrer. Toute opération affectant son planning doit respecter ce protocole ; un simple SELECT puis INSERT sans protection concurrente n’est pas suffisant. Définir un ordre de verrouillage stable si plusieurs ressources interviennent.

Choisir une seule stratégie de stock : calcul depuis les mouvements, ou solde maintenu atomiquement avec ceux-ci. Si un solde est stocké pour les performances, expliquer cette donnée dérivée, empêcher sa modification indépendante et fournir un contrôle de rapprochement avec les mouvements.

Prévoir au moins une automatisation utile **interne à la base**, notamment l’historisation, et des opérations stockées cohérentes avec le cours. Un journal uniquement écrit par PHP ne démontre pas à lui seul cette exigence. Les événements planifiés sont optionnels : ne les ajouter que pour un besoin réel, avec activation documentée.

**Sortie :** installation SQL réussie sur base vierge ; contraintes et automatismes testés ; scénarios de rollback et de concurrence reproductibles ; documentation du rôle de chaque procédure/vue/trigger.

### Lot 4 — Données factices cohérentes et requêtes métier

**Dépendance :** lot 3.

Créer deux jeux reproductibles, avec graine fixe et date de référence documentée :

- **démonstration** : petit jeu lisible, contenant tous les rôles, types de zones et de véhicules, plusieurs transporteurs, articles, lots, réceptions, commandes, cas normaux et cas limites ;
- **performance** : volume paramétrable, par exemple 10 000 passages, 50 000 lignes de réception et 100 000 mouvements, ajusté à la machine. Ces nombres sont des objectifs proposés, pas un minimum officiel.

Le générateur doit respecter la chronologie, les capacités, les FK et la conservation du stock. Répartir les données sur plusieurs dates, transporteurs et zones pour que les statistiques aient du sens. Créer les données invalides uniquement dans des tests isolés destinés à vérifier leur rejet.

Écrire et commenter les requêtes de recherche, de traçabilité et de statistiques. Fournir des résultats attendus calculables à la main sur le petit jeu. Les jeux de simulation des fonctions non encore accessibles dans l’interface doivent être identifiés comme tels.

**Sortie :** chargement reproductible, comptage des lignes par table, contrôle d’intégrité sans anomalie ; toutes les statistiques possèdent un scénario de vérification.

### Lot 5 — Socle web, utilisateurs et référentiels

**Dépendances :** lots 3 et 4.

Réaliser l’installation, le menu, les vues communes, les messages de réussite/erreur, l’inscription, la connexion, la déconnexion et le contrôle des droits côté serveur. L’inscription attribue un droit faible ou un compte en attente ; seul l’administrateur peut donner des rôles privilégiés.

Utiliser des mots de passe hachés et vérifiés par les fonctions adaptées de PHP, des requêtes PDO préparées, l’échappement HTML, la protection CSRF des écritures et des sessions correctement renouvelées. Les identifiants SQL restent côté serveur, hors des fichiers publics et du dépôt. Distinguer comptes applicatifs et compte de connexion SQL.

Construire les écrans de référentiels nécessaires : transporteurs, chauffeurs, véhicules, clients, fournisseurs, articles, quais, équipements et structure de stockage. Les relations N:N doivent être gérables par des formulaires adaptés. L’utilisateur sélectionne des noms, références ou immatriculations, pas des identifiants techniques internes.

**Sortie :** parcours d’inscription/connexion opérationnel ; accès interdit réellement rejeté même par URL ou requête directe ; CRUD autorisé vérifié ; liens et formulaires utilisables sans intervention manuelle dans les tables.

### Lot 6 — Quais, rendez-vous et flux camion

**Dépendance :** lot 5.

Construire le planning par date/quai, les filtres, la création/modification/annulation et l’affichage des compatibilités. Définir la priorité entre état hors service, occupation réelle et réservation ; expliciter l’intervalle d’actualisation automatique choisi pour l’affichage « temps réel » et permettre le rafraîchissement manuel.

Réaliser le parcours d’un camion avec ou sans rendez-vous, du poste de garde au départ. Les boutons disponibles dépendent de l’état courant et du rôle. Afficher les heures prévues/réelles, les retards et les durées selon les définitions retenues.

**Sortie :** F03 et F04 utilisables ; tests R01–R04 réussis ; deux sessions concurrentes ne peuvent ni réserver abusivement le même créneau ni occuper le même quai. Tester une modification de rendez-vous et une arrivée sans rendez-vous, pas seulement la création nominale.

### Lot 7 — Réceptions, rangement et stocks

**Dépendance :** lot 6.

Construire les avis fournisseurs, la réception des lignes/lots/palettes, les écarts, les réserves, le choix d’emplacements adaptés et la validation atomique. Séparer les quantités reçues, acceptées/disponibles et endommagées selon les règles du lot 1.

Réaliser les consultations par article, lot, propriétaire, zone et emplacement ; transferts, sorties autorisées et ajustements motivés ; consultation de l’historique. Les mouvements validés sont corrigés par une opération traçable, pas par une modification silencieuse du solde.

**Sortie :** F05 et F06 utilisables ; tests R05–R09 et R12 réussis ; un parcours réception → rangement → transfert restitue des quantités et un historique exacts.

### Lot 8 — Commandes, préparation, expédition et traçabilité

**Dépendance :** lot 7.

Implémenter les traitements nécessaires à F07. Retenir et expliquer au moins une règle de sortie, FIFO **ou** FEFO, comme le permet S. Si les deux sont proposées, définir leur sélection et le traitement des lots sans DLC. Ajouter une règle de départage stable et exclure les stocks bloqués ou incompatibles.

Pour couvrir E, réaliser des écrans simples : commandes et lignes, lancement/affectation du prélèvement, confirmation des quantités, constitution de colis/palettes, affectation au camion sortant et confirmation d’expédition. Prévoir une liste de prélèvement, un bon de livraison et une lettre de voiture imprimables avec leurs données de démonstration. Ne pas revendiquer une conformité réglementaire non demandée/non vérifiée.

Créer une consultation de lot montrant réceptions, mouvements, emplacements successifs, prélèvements, commandes et camion d’expédition. Inclure un cas de lot réparti entre plusieurs emplacements et plusieurs commandes, afin de vérifier les cardinalités.

**Sortie :** chaîne complète démontrable ; tests de choix FIFO/FEFO, de stock insuffisant, de double expédition et de traçabilité réussis. Si seule une simulation SQL existe, la signaler comme une couverture BDD, pas comme une interface réalisée.

### Lot 9 — Recherches, statistiques et états

**Dépendances :** lots 6 à 8.

Fournir des recherches combinant plusieurs critères via formulaires : période + transporteur + statut ; article + lot + zone + propriétaire ; réception + fournisseur + présence d’écart. Prévoir tri, pagination, remise à zéro des filtres et message explicite si aucun résultat.

Définir les indicateurs avant de les afficher :

| Indicateur | Définition proposée à documenter et tester |
|---|---|
| Occupation des quais | Durée d’occupation réelle intersectant la période / durée disponible des quais sur la période ; préciser le traitement des indisponibilités |
| Attente des camions | Début d’opération moins arrivée au site ; distinguer éventuellement attente parking et attente à quai |
| Immobilisation | Départ moins arrivée, moyenne par transporteur pour les passages terminés ; afficher séparément les passages encore ouverts |
| Remplissage par zone | Capacité utilisée / capacité utilisable dans la même unité ; ne pas additionner directement kg, palettes et unités d’articles |
| Écarts en réception | Par exemple lignes comportant au moins un écart / lignes réceptionnées ; compléter par les quantités manquantes/excédentaires/endommagées |
| Productivité | Lignes ou quantités préparées / durée de préparation observée ; indiquer unité, période et préparateur |
| Articles proches de la DLC | Stock disponible dont la DLC est entre la date de référence et un horizon paramétrable ; traiter séparément périmés et DLC absentes |

Ces définitions sont des choix proposés, pas des formules imposées par le sujet. Afficher les dénominateurs, unités et exclusions utiles. Gérer les divisions par zéro et les périodes sans données.

Présenter les résultats avec tableaux et graphiques lisibles. Prévoir au minimum des états de stock, d’activité des quais/camions et d’écarts en réception, imprimables et/ou exportables en CSV, plus les documents de F07. Les exports doivent respecter les filtres et les droits de l’utilisateur.

**Sortie :** résultats comparés aux valeurs attendues ; les graphiques utilisent les données réelles ; états lisibles et utilisables ; tous les indicateurs demandés sont disponibles ou explicitement identifiés comme incomplets.

### Lot 10 — Performances, sécurité et recette complète

**Dépendances :** lots 3 à 9.

#### Rapport de performances obligatoire

Mesurer au moins les requêtes représentatives suivantes : disponibilité d’un quai, recherche multicritère des passages, recherche de stock, propositions d’emplacements, historique d’un lot, sélection FIFO/FEFO, statistiques par transporteur et remplissage par zone.

Pour chaque mesure, conserver : SQL et paramètres, version du moteur, machine et configuration utile, volume par table, index présents, plan d’exécution, méthode de chronométrage et résultats bruts. Distinguer temps SQL et temps de réponse HTTP.

Protocole proposé : une exécution de chauffe puis au moins dix exécutions mesurées sur le même jeu et les mêmes paramètres ; publier la médiane et une indication de dispersion. Comparer avant/après sur une copie de test, en modifiant un élément à la fois. Utiliser EXPLAIN et les outils disponibles sur la version choisie, sans supposer qu’une syntaxe est universelle.

Justifier les index retenus par les filtres, jointures et tris réellement utilisés ; observer aussi leur coût d’écriture. Éviter les lectures de toutes les colonnes sans besoin, les listes non paginées et les requêtes répétées dans des boucles. Ne pas chercher à ajouter du partitionnement ou de la réplication sans besoin mesuré.

#### Recette à exécuter

- installation sur une base vierge et chargement des deux jeux ;
- création, modification, suppression autorisée et refus de suppression référencée ;
- doublons de clés métier, FK invalides, quantités négatives, dates incohérentes ;
- tous les invariants R01–R12, y compris tests avec deux connexions simultanées ;
- inscription, connexion, déconnexion, permissions de chaque rôle et absence d’élévation de privilèges ;
- entrées contenant apostrophes et balises HTML, refus d’écriture sans protection CSRF ;
- filtres combinés, tri, pagination, aucun résultat, statistiques et exports ;
- déclenchement réel de l’historisation et cohérence auteur/date/opération ;
- navigation, formulaires, messages, absence d’ID internes affichés, lisibilité des graphiques et des états imprimés ;
- sauvegarde puis restauration dans une base de test distincte, avec vérification des données et automatismes.

**Sortie :** rapport de performances avec mesures réelles, recette traçable, anomalies corrigées ou limites précises. Tout test non exécuté reste marqué « non exécuté », jamais « réussi ».

### Lot 11 — Rapport, documentation et remise

**Dépendance :** lot 10.

Rédiger le rapport à partir des réalisations et preuves. Structure attendue :

1. Page de titre : projet, UV, auteurs réels, date réelle.
2. Table des matières.
3. Introduction : contexte logistique, problématique, objectifs.
4. Cahier des charges, périmètre, acteurs et cas d’utilisation UML.
5. Règles métier et hypothèses.
6. MCD, MLD, dictionnaire, cardinalités, clés et justification de 3NF.
7. Architecture, environnement et sécurité.
8. Fonctionnalités : **objectif / travail réalisé / conclusion** pour chacune, avec captures réelles pertinentes et limites éventuelles.
9. SQL, vues, procédures, déclencheurs, historisation et transactions.
10. Données factices et scénarios de démonstration.
11. Tests et rapport d’analyse des performances, intégré ou annexé.
12. Conclusion : bilan, limites et améliorations raisonnables.
13. Annexes utiles : installation, dictionnaire complet, requêtes et preuves.

Fournir le rapport dans un format lisible de remise, avec sa source éditable ; vérifier visuellement les diagrammes, tableaux et captures dans l’export final. Corriger grammaire et orthographe. Ne pas inventer les noms des membres du groupe ou leur contribution.

Le README doit permettre à un tiers d’installer la base, configurer l’application, charger les données, démarrer le site, utiliser les comptes de démonstration et lancer les contrôles. Fournir les commandes de sauvegarde/restauration et de remise à zéro **uniquement pour une base de démonstration explicitement désignée**.

Préparer une démonstration : connexion par rôle → rendez-vous → arrivée → réception avec écart → rangement/transfert → préparation/expédition → traçabilité → statistiques → présentation d’une mesure avant/après. Prévoir une version de 10 minutes à confirmer selon les modalités de soutenance A26.

**Sortie :** remise reproductible depuis un dossier propre, documents cohérents avec le code, matrice de conformité renseignée et liste explicite des limites. Les étudiants doivent pouvoir expliquer les choix essentiels, exécuter les requêtes principales et montrer les contrôles métier.

## 6. Matrice des critères de notation et des preuves

Utiliser cette table comme checklist de livraison. Elle reprend les critères de E, sans pondération inventée.

| Critère de la grille E | Réalisation/preuve attendue | Lots |
|---|---|---|
| Identification des usages et représentation UML | Cas textuels par acteur + diagramme UML exporté | 1 |
| MCD cohérent avec les usages | Matrice usages/entités, cardinalités justifiées | 2 |
| Modèle relationnel cohérent avec le MCD | MLD et règles de transformation, correspondance avec SQL | 2–3 |
| Traitements cohérents avec les usages | Parcours réalisés et tests liés aux cas d’utilisation | 3, 5–10 |
| Rapport des fonctionnalités | Rapport fidèle à l’existant | 11 |
| Clés primaires bien définies | PK et clés candidates expliquées | 2–3 |
| Types corrects | Dictionnaire, unités, précision, nullabilité | 2–3 |
| Plusieurs relations 1:N et N:N | FK et tables d’association pertinentes, testées | 2–3 |
| Erreurs communes évitées | Absence de listes en cellules, formats cohérents, données dérivées maîtrisées | 2, 10 |
| Redondances évitées et base normalisée | Dépendances fonctionnelles et démonstration 1NF→3NF | 2 |
| Qualité et quantité d’informations | Entités utiles couvrant S, attributs décrits, jeu volumineux cohérent | 2, 4 |
| Ajout, édition, suppression de l’ensemble des données | Matrice CRUD par entité/rôle ; formulaires ; correction/annulation des faits historiques | 5–8 |
| Contrôle des saisies | Validation serveur + contraintes BDD + messages compréhensibles | 3, 5–10 |
| Recherche multicritère par formulaires | Combinaisons de filtres testées | 9–10 |
| Statistiques en tableaux et graphiques | Indicateurs définis, justes et présentés lisiblement | 9 |
| Génération d’états | Stocks, activité, écarts et documents de sortie | 8–9 |
| Finition, menus, boutons, IDs internes masqués, automatisations | Parcours sans SQL manuel, références métier lisibles, automatisations en PHP/SQL | 3, 5–10 |
| Plusieurs utilisateurs | Comptes, sessions, droits, tests simultanés | 5, 10 |
| Cahier des charges et cas d’utilisation rendus | Documents inclus dans le rapport ou en annexes | 1, 11 |
| Diagramme entité-association rendu | Export lisible + source | 2, 11 |
| Schéma relationnel rendu | Export lisible + source | 2, 11 |
| Forme du rapport | Introduction, conclusion, sommaire, noms/prénoms | 11 |
| Présentation objectif/travail réalisé/conclusion | Structure appliquée à chaque fonctionnalité, captures authentiques | 11 |
| Grammaire et orthographe | Relecture finale | 11 |
| Qualité générale, utilisabilité, ergonomie, graphisme | Cohérence visuelle, démonstration fluide, recette depuis installation propre | 10–11 |

Exigences de S à vérifier également, même si elles ne possèdent pas une ligne dédiée dans E : couverture complète du modèle, données factices en quantité, 3NF, moteur autorisé, sécurité/confidentialité, rapport des temps d’exécution, optimisation et automatisation interne de la base.

## 7. Arborescence de livraison proposée

Cette organisation est une proposition ; l’adapter à l’existant sans multiplier les fichiers inutiles.

```text
projet-bd70/
├── document cours/                 # Sources fournies, préservées
├── document projet/                # Sources fournies, préservées
├── PLAN-ORCHESTRATION-PROJET-BD70.md
├── README.md
├── .gitignore
├── config/                         # Exemple de configuration sans secret
├── public/                         # Seul répertoire exposé par le serveur web
│   ├── index.php
│   └── assets/
├── src/                            # Contrôleurs, services et accès PDO
├── templates/                      # Vues HTML/PHP
├── sql/
│   ├── 01_schema.sql
│   ├── 02_vues.sql
│   ├── 03_procedures.sql
│   ├── 04_triggers.sql
│   ├── 05_index.sql
│   ├── 06_privileges.example.sql
│   └── requetes_metier.sql
├── scripts/                        # Installation, génération, mesures
├── tests/                          # Intégrité, métier, concurrence, recette
├── docs/
│   ├── SUIVI-PROJET.md
│   ├── matrice-conformite.md
│   ├── hypotheses-decisions.md
│   ├── 01-cahier-des-charges.md
│   ├── 02-cas-utilisation.md
│   ├── dictionnaire-donnees.md
│   ├── normalisation-3nf.md
│   ├── matrice-crud-droits.md
│   ├── diagrammes/                 # Sources + exports
│   ├── recette.md
│   ├── performances.md
│   └── demonstration.md
└── livrables/
    ├── rapport/                    # Source et export final
    └── preuves/                    # Captures réelles et mesures brutes
```

## 8. Règle de fin et message de remise de l’IA

Le travail est terminé seulement lorsque l’installation est reproductible, les fonctions ciblées sont réellement utilisables, le modèle couvre tout S, les preuves existent et les documents correspondent à l’application.

Dans le message final, fournir :

- les liens vers l’application locale si elle tourne, le README, le rapport et les diagrammes ;
- la procédure courte de lancement ;
- les fonctionnalités effectivement réalisées, distinctes des simulations SQL ;
- les tests exécutés et leurs résultats, les performances réellement mesurées ;
- les éventuelles limites et les informations que les étudiants doivent encore compléter.

Une indisponibilité de moteur, d’outil ou de service n’autorise pas à déclarer une validation fictive. Livrer alors un état de reprise précis et continuer les travaux indépendants possibles. Toute fonctionnalité, preuve ou livrable obligatoire manquant doit rester visible dans la matrice de conformité.

## 9. Message court pour lancer le travail

Copier ce message avec ce fichier et les quatre sources, ou donner accès au dossier complet :

> Réalise le projet BD70 de gestion d’entrepôt logistique en suivant `PLAN-ORCHESTRATION-PROJET-BD70.md`. Lis d’abord le sujet, la grille d’évaluation et les deux supports de cours présents dans les dossiers `document projet` et `document cours`. Travaille par lots dépendants, avec validation et mise à jour du suivi après chaque lot. Utilise par défaut PHP/PDO et MySQL pour rester proche du cours, après inspection de l’environnement. Produis le modèle complet, l’application, les données factices, les scripts, les tests, les mesures de performance et le rapport. Préserve les fichiers existants. Explique simplement les choix pour que nous puissions les comprendre et les présenter. Avance sans demander une confirmation systématique ; signale les vrais blocages et distingue toujours ce qui est réalisé, testé, simulé ou encore à faire.
