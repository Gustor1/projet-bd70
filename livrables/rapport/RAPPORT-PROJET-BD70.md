# Transit - Gestion d’un entrepôt logistique

Projet BD70 - 22 octobre 2026

Auteurs réels : à renseigner par le groupe. Noms de démonstration fictifs.

## Table des matières
1. Contexte et cahier des charges
2. Acteurs et cas d’utilisation
3. Règles et hypothèses
4. MCD et chemin de traçabilité
5. MLD, dictionnaire et normalisation
6. Architecture et sécurité
7. F01 et F02 - Personnel et transport
8. F03 et F04 - Quais et flux camions
9. F05 et F06 - Réception, rangement et stocks
10. F07 et F08 - Sorties, trace et pilotage
11. SQL, automatismes et transactions
12. Données et résultats attendus
13. Recette et restauration
14. Performances mesurées
15. Indicateurs et états imprimables
16. Conclusion et limites

## 1. Contexte et cahier des charges

Le projet répond au sujet A26 « Système de Gestion d’un Entrepôt Logistique ». Il organise les rendez-vous, les passages de camions, la réception, le stockage, la préparation et l’expédition. L’objectif est de pouvoir expliquer la provenance d’une quantité et de piloter l’activité depuis des faits fiables.


Le sujet de trois pages définit les exigences et autorise MySQL/MariaDB ou PostgreSQL. La grille d’évaluation demande notamment UML, MCD, MLD, normalisation, formulaires CRUD, recherche multicritère, tableaux, graphiques et états. Elle ne donne pas de pondération. Les supports de cours A25 expliquent la méthode et PHP/PDO ; leurs exemples d’agence de voyage ne sont pas le domaine à réaliser.


Le modèle couvre F01 à F08. L’interface couvre les cinq domaines minimaux de S et ajoute les référentiels, les commandes, les expéditions, les documents et les indicateurs pour répondre à la grille. Un compte transporteur externe est optionnel dans S et n’est pas retenu.


Les originaux sont préservés ; les extractions textuelles des quatre supports, y compris les SmartArt, sont livrées dans docs/sources/. Les auteurs réels et la date de remise n’étaient pas fournis. La soutenance de 10 minutes est préparée à titre indicatif, sous réserve des modalités A26.


|Exigence|Résultat cible|
|---|---|
|F01 / F02|Personnel authentifié et référentiels transport|
|F03 / F04|Planning sans conflit et chronologie des camions|
|F05 / F06|Réception multilots, rangement et mouvements|
|F07 / F08|Préparation FEFO, expédition, traçabilité et pilotage|

## 2. Acteurs et cas d’utilisation

L’administrateur active les comptes et possède tous les droits. Le responsable gère les référentiels, le planning et les opérations. L’accueil gère les rendez-vous et les passages. Le magasinier réceptionne, déplace, prépare et expédie. L’inscription seule ne donne aucun droit métier.


Le diagramme UML livré utilise des acteurs, des ellipses et une frontière système. Les généralisations indiquent que le responsable reprend les opérations de l’accueil et du magasinier, et que l’administrateur reprend celles du responsable. La vérification de disponibilité est incluse dans la réservation et le déplacement. L’arrivée sans rendez-vous étend le suivi des camions.


Les dix cas textuels détaillent acteur, objectif, préconditions, scénario, variantes et postconditions dans docs/02-cas-utilisation.md. La session authentifiée est une précondition : il ne s’agit pas de se reconnecter pour chaque clic.


Exemple UC05 : un camion entrant est en opération ; l’agent saisit les lignes et les fractions par lot, les avaries et réserves, puis valide. La capacité et la provenance sont vérifiées sous transaction. Si une deuxième fraction ne peut pas être rangée, la première entrée est annulée par rollback. Un rejeu de validation est refusé.


|Cas|Acteurs|Données principales|
|---|---|---|
|UC01 / UC02|Personnel / A, R|Comptes, référentiels|
|UC03 / UC04|A, R, accueil|Rendez-vous, passages, événements|
|UC05 / UC06|A, R, magasinier|Réceptions, lots, mouvements|
|UC07 / UC08|A, R, magasinier|Commandes, prélèvements, expéditions|
|UC09 / UC10|Personnel / A, R|Trace / indicateurs et états|

## 3. Règles et hypothèses

Le site est unique et utilise l’heure civile Europe/Paris. Les quantités sont des unités entières de conditionnement ; poids en kg, dimensions en mètres, volume calculé en m³. Une capacité palette est un équivalent rationnel quantité/unités_par_palette, sans addition avec les kg ou les m³.


Un article appartient à un client propriétaire et possède une référence unique chez celui-ci. Le fournisseur livre ; le transporteur achemine. Ces trois acteurs restent séparés. Un lot est identifié par article et code fabricant, avec DLC facultative et blocage motivé.


Réceptions partielles autorisées : l’attendu d’une livraison est une allocation du reste de l’avis. Les excédents et avaries sont visibles ; les avaries ne sont pas mises au stock disponible. Une fraction reçue possède un code palette interne unique et peut être déplacée entre plusieurs emplacements.


Le FEFO réserve toute la commande : DLC croissante, sans DLC en dernier, puis date de réception, fraction et emplacement. Les lots bloqués ou périmés sont exclus. Aucune expédition partielle n’est proposée ; l’annulation avant expédition libère les réservations.


Les historiques sont immuables. Les brouillons et fiches inutilisées peuvent être supprimés ; les FK protègent les fiches référencées. Une correction d’inventaire crée un mouvement motivé. Certaines caractéristiques structurelles utilisées sont figées pour préserver les faits. Le détail est dans docs/hypotheses-decisions.md et docs/matrice-crud-droits.md.


## 4. MCD et chemin de traçabilité

Les concepts se répartissent en cinq domaines : transport/personnel, quais/passages, articles/structure de stockage, réceptions/mouvements, commandes/expéditions. Les MCD sont distincts des MLD : concepts, attributs métier et associations à cardinalités ; pas de types SQL ni de FK.


Une ligne de réception se décompose en plusieurs fractions portant des lots. Un lot peut être reçu plusieurs fois. Chaque mouvement et chaque prélèvement référence la fraction de réception, ce qui conserve une provenance exacte quand un même lot est mélangé dans plusieurs réceptions.


Une ligne de commande peut être servie par plusieurs fractions et donc plusieurs lots ; une fraction peut servir plusieurs commandes. Le prélèvement quantifié est l’association qui porte cette relation N:N. Les équipements et habilitations sont aussi des relations structurées, jamais des listes de valeurs dans une cellule.


Chemin complet : fournisseur → avis → ligne attendue → ligne de réception → fraction → lot/article/propriétaire. La fraction rejoint les mouvements et les emplacements successifs, puis les prélèvements, lignes de commande, expédition et passage du camion sortant.


Les exports vectoriels détaillés et complets sont dans docs/diagrammes/. Le recueil DIAGRAMMES-BD70.pdf les conserve à leur taille native : lecture par zoom à 100 %, sans réduction illisible sur une feuille A4.


|Relation|Cardinalité et justification|
|---|---|
|Avis → réceptions|1:N, livraisons partielles|
|Ligne reçue → fractions|1:N, plusieurs lots/palettes|
|Lot → fractions|1:N, plusieurs réceptions du même lot|
|Commande → lignes → prélèvements|1:N puis 1:N, plusieurs fractions par ligne|
|Fraction → prélèvements|1:N, un lot alimente plusieurs commandes|
|Commande → expédition|0..1, expédition intégrale unique|

## 5. MLD, dictionnaire et normalisation

Le MLD installé comporte 40 tables, dont le verrou de site et le journal technique. Les types sont explicites : entiers pour les clés et quantités, DECIMAL pour mesures et capacités, DATETIME/DATE pour les faits temporels, VARCHAR bornés pour références et libellés. Les quantités, intervalles et capacités élémentaires sont contrôlés.


1NF : les contacts, équipements, habilitations et lignes sont des occurrences distinctes. 2NF : dans une association chauffeur/habilitation, la validité dépend du couple entier ; les coordonnées du chauffeur restent dans driver. 3NF : les noms de transporteur, d’article et de propriétaire ne sont pas recopiés dans les lignes ; les jointures les retrouvent.


Exemples de DF : (owner_id, sku) → caractéristiques de l’article ; (article_id, code) → DLC et blocage du lot ; (driver_id, qualification_id) → expires_on ; référence de commande → propriétaire, destination et date souhaitée. Le dictionnaire et la justification table par table sont fournis en annexes Markdown.


Les unicités nullable ne sont pas présentées comme des clés candidates totales. Le rendez-vous est distinct du passage réel. Le statut courant est une projection de pilotage ; les événements conservent les faits horodatés. Les soldes, durées et totaux sont calculés par vues. L’attendu local d’une réception partielle n’est pas une redondance de l’attendu total de l’avis.


|Relation|Clés métier et associations|
|---|---|
|article|UNIQUE(owner_id, sku), FK propriétaire|
|lot|UNIQUE(article_id, code), FK article|
|receipt_item|UNIQUE(pallet_code), FK ligne, lot et emplacement|
|pick|FK ligne de commande, fraction et emplacement|
|shipment|UNIQUE(order_id), FK passage sortant|
|stock_movement|FK fraction, emplacement, auteur, prélèvement optionnel|

## 6. Architecture et sécurité

L’application suit l’architecture trois tiers enseignée : navigateur HTML/CSS, contrôleur PHP et services métier, accès PDO explicite vers MariaDB/InnoDB. Versions vérifiées : PHP 8.2.12, MariaDB 10.4.32-MariaDB, Windows 11. Aucune bibliothèque distante ou API n’est nécessaire à l’usage du site.


Le seul répertoire exposé est public/. Database.php centralise PDO et les transactions ; Catalog.php décrit les fiches et protège les données validées ; Warehouse.php applique les transitions, capacités, FEFO et opérations atomiques ; Reports.php contient les recherches et indicateurs. Les vues sont dans templates/.


Les mots de passe sont hachés et vérifiés par les fonctions PHP adaptées. Les sessions sont renouvelées à la connexion, cookies HttpOnly/SameSite, écritures protégées par CSRF, HTML échappé et SQL préparé. Les droits sont contrôlés à chaque route et action, indépendamment des menus. Un compte en attente ne peut pas s’octroyer un rôle.


Le compte applicatif SQL possède SELECT/EXECUTE et les écritures par table nécessaires, sans droit DDL. Les journaux ne sont pas modifiables ; les mouvements, événements et expéditions n’acceptent pas UPDATE/DELETE. Le secret SQL est généré dans config/local.php hors dépôt. Les comptes du jeu sont fictifs.


Le serveur de démonstration PHP et l’instance MariaDB isolée écoutent seulement sur 127.0.0.1. Aucun déploiement public ou validation de serveur de production n’est revendiqué.


## 7. F01 et F02 - Personnel et transport

Objectif. Identifier le personnel et gérer les transporteurs, contacts, contrats, chauffeurs, habilitations et véhicules avec des droits distincts.


Travail réalisé. Inscription en attente, activation et profils par administrateur, connexion/déconnexion. Les référentiels disposent de formulaires d’ajout/modification/suppression d’éléments inutilisés. Les véhicules portent type, immatriculation et capacités ; les équipements et habilitations sont gérés par associations. Un tracteur demande une remorque du même transporteur.


Contrôles. Emails et références uniques, FK valides, dates de contrat cohérentes, compte actif, données structurantes protégées. Les entrées avec apostrophe et balises HTML ont été créées, recherchées, modifiées et supprimées dans un navigateur réel sans exécution de HTML.


Conclusion. Quatre profils réellement utilisables. Les requêtes directes aux comptes et les tentatives d’écriture privilégiée sont refusées pour responsable, accueil et magasinier. Les formulaires masquent les clés techniques ; l’utilisateur sélectionne noms, références et plaques.


Capture authentique : ../preuves/connexion.png

## 8. F03 et F04 - Quais et flux camions

Objectif. Planifier sans chevauchement et suivre chaque étape du camion, y compris sans rendez-vous.


Travail réalisé. Planning journée/quai, création, déplacement et annulation de rendez-vous ; types compatibles, équipements et indisponibilités. L’état actuel suit la priorité hors service, occupé, réservé, libre ; rafraîchissement à 30 secondes hors saisie et bouton manuel.


Contrôles. Intervalles [début, fin[, durée positive ; dates saisonnières ambiguës refusées. Arrivée → contrôle → parking facultatif → appel → début → fin → départ. Les étapes erronées ou rétrogrades sont refusées. Une indisponibilité chevauchant une réservation exige son déplacement préalable.


Conclusion. Les tests à deux connexions admettent une seule réservation conflictuelle et une seule occupation d’un quai. L’attente, l’immobilisation et le retard se déduisent des dates réelles et prévues, sans mélange entre rendez-vous et passage.


Capture authentique : ../preuves/planning.png

## 9. F05 et F06 - Réception, rangement et stocks

Objectif. Accepter les marchandises contrôlées, signaler les écarts et conserver des stocks compatibles avec les capacités.


Travail réalisé. Avis et lignes, réceptions partielles, plusieurs lots/palettes par ligne, DLC et réserve pour les avaries. Validation unique et atomique ; propositions d’emplacements contrôlant condition de stockage, dimensions, poids, volume et équivalents palettes.


Contrôles. Les avaries ne créent pas de disponible. Les lots bloqués/périmés ne sont pas réservables. Un transfert débite et crédite dans la même transaction, avec référence commune. Les quantités réservées ne peuvent pas être consommées par un ajustement ou un transfert. L’inventaire se corrige par mouvement motivé.


Conclusion. R05 à R09 et R12 vérifiés, dont réception partiellement écrite puis intégralement annulée, conservation de quantité et deux rangements concurrents dans un emplacement limité. Recherche article + lot + propriétaire + zone et historique disponibles.


Capture authentique : ../preuves/stock.png

## 10. F07 et F08 - Sorties, trace et pilotage

Objectif. Préparer et expédier les quantités réellement prélevées, puis retrouver les lots et les indicateurs.


Travail réalisé. Commandes et lignes, affectation à un préparateur, réservation FEFO complète, confirmation, colis/palettes et contenu, chargement sortant et expédition unique. Liste de prélèvement, bon de livraison et lettre de voiture imprimables avec données réelles du jeu fictif.


Contrôles. Lot bloqué ou périmé exclu, départage stable, stock insuffisant sans réservation partielle, colis et capacité véhicule exigés. Le mouvement de sortie référence le prélèvement et la fraction reçue ; une deuxième expédition est refusée.


Conclusion. Le lot A est reçu deux fois, déplacé sur deux emplacements et sert deux commandes. Le parcours navigateur supplémentaire confirme 31 étapes par formulaires jusqu’au camion et au bon. Les tableaux de bord et trois états CSV/imprimables utilisent les faits enregistrés, sans données graphiques codées en dur.


Capture authentique : ../preuves/orders.png

## 11. SQL, automatismes et transactions

Les scripts ordonnés installent schéma, vues, procédures, triggers et index. Les privilèges sont séparés. PK, FK, UNIQUE, NOT NULL, ENUM et CHECK rendent explicites les domaines et règles élémentaires. La suppression référencée est restrictive.


PHP est l’unique propriétaire du BEGIN/COMMIT/ROLLBACK. La procédure lock_site() prend le verrou sur la ligne du site ; elle ne valide aucune transaction. Tous les services critiques et le CRUD suivent ce protocole. La sérialisation conservatrice garantit les contrôles d’agrégats contre les écritures concurrentes.


116 déclencheurs installés : journal automatique après mutations et refus de mutation des historiques. Les entrées du journal contiennent entité, opération, référence technique, auteur et date, jamais mot de passe ou secret. La procédure trace_lot(lot, offset) fournit l’historique des mouvements par pages de 20.


Les vues v_balance et v_reserved calculent le physique et les réservations ; v_stock joint provenance, article, propriétaire et emplacement, et masque le disponible bloqué/périmé. v_location_usage calcule trois capacités indépendantes. v_visit reconstitue les dates et durées. v_receipt_discrepancy calcule manquants, excédents et avaries.


Les règles multiligne ne sont pas prétendues être toutes des CHECK SQL : elles appartiennent aux services transactionnels. Les scripts administratifs ne doivent pas insérer des opérations arbitraires en contournant ces services.


## 12. Données et résultats attendus

Les jeux sont fictifs et reproductibles (graine 70, référence 22/10/2026). La démonstration est créée principalement par les services réellement utilisés dans l’interface. Elle comprend les quatre profils, trois transporteurs, quatre types de véhicules, trois zones, lots normaux/bloqués/périmés/sans DLC, écarts et deux expéditions.


Oracle du petit jeu avant les manipulations de recette : 255 unités acceptées, 50 sorties, 205 physiques. Le lot A représente 120 unités reçues et 50 sorties, soit 70 restantes réparties entre réceptions et emplacements. Dix unités sont périmées, dix bloquées, quarante froides proches de DLC et quinze sans DLC.


Les quatre lignes validées comportent deux écarts : 5 unités excédentaires, 5 endommagées et 5 manquantes. Occupation des quais : 80 minutes / 4 320 minutes disponibles (trois quais sur une journée 24 h/24). Nord Transit : attente moyenne 17,5 minutes, immobilisation 55 minutes. Froid Express : 15 et 50 minutes.


Productivité : 50 unités préparées sur 20 minutes observées, soit 150 unités/heure. Remplissage physique actuel : ambiant 150 unités (7,5 équivalents palettes), froid 40 (2 palettes), dangereux 15 (0,75 palette). Les numérateurs/dénominateurs sont dans les écrans et tests.


Le volume de performance est séparé : 10,003 passages, 2,004 lignes de réception, 22,011 mouvements et 60,019 événements. Il s’agit de simulations SQL contrôlées, avec rapprochement du stock, capacités et somme nulle des transferts, pas d’une preuve de saisie manuelle de ce volume.


## 13. Recette et restauration

Résultats exécutés. 64 contrôles d’intégrité/métier réussis ; 71 contrôles navigateur réussis ; 31 étapes de parcours par formulaires réussies. Les fichiers JSON et les captures authentiques sont dans livrables/preuves/. Les courses utilisent deux connexions SQL distinctes, identifiées dans concurrence.json.


R01 : création/déplacement, adjacence et chevauchement ; R02 : type, indisponibilité et refus de fermeture d’un quai réservé ; R03 : occupation concurrente ; R04 : transitions et dates. R05 : validation unique ; R06 : négatif et réservation concurrente ; R07 : transfert conservatif ; R08 : compatibilité/capacité concurrente ; R09 : avaries et blocage ; R10 : sorties liées et unicité ; R11 : trigger et droits ; R12 : rollback multiétapes.


La recette HTTP contrôle l’inscription sans privilège, l’accès direct par rôle, l’absence de CSRF, les apostrophes/balises, les filtres CSV, le CRUD réel et les états. Les pages sont visitées à 1440 px et les principales pages à 390 px, sans débordement global. Les tableaux larges défilent dans leur propre conteneur.


Restauration : 40 tables comparées par nombre et checksum entre la démonstration et bd70_restore_finale. Les 116 triggers et 2 procédures sont présents ; une modification contrôlée dans la copie ajoute automatiquement une entrée d’audit. Aucun écrasement de la démonstration.


Les contrôles ne constituent pas une certification de production, un test sur téléphone physique ou une validation sur d’autres moteurs. La recette reste reproductible depuis une base vierge portant un nouveau nom de test.


## 14. Performances mesurées

Machine : 12th Gen Intel(R) Core(TM) i7-1260P, 16 processeurs logiques, 15.7 Gio de RAM. Buffer pool InnoDB : 128 Mio ; isolation READ COMMITTED. Le type exact de stockage n’a pas été relevé.


Méthode : une chauffe et dix exécutions mesurées à paramètres et jeu identiques, horloge monotone hrtime. Le temps couvre le tour PDO local avec récupération des résultats ; ce n’est pas un temps CPU serveur isolé. Les SQL, paramètres, plans EXPLAIN, index et mesures brutes sont archivés dans performances.json.


Comparaison contrôlée sur la base de performance : seul idx_appointment_slot change, un index FK simple restant en place. La disponibilité passe d’une médiane de 5.909 ms à 1.563 ms (3.78 fois plus rapide sur cet essai). L’index composite filtre quai/état puis borne la plage de dates ; le plan avant/après est conservé.


Observation d’écriture : INSERT de rendez-vous avec trigger suivi de ROLLBACK, avant 5.554 ms et après 6.738 ms en médiane. Le bruit et le rollback empêchent d’en déduire un coût universel de commit. Les agrégats de v_visit dominent les lectures ; une charge industrielle justifierait d’abord une agrégation ciblée par période. Aucun partitionnement ni réplication ajouté sans besoin mesuré.


|Requête|Médiane (ms)|Min–max (ms)|
|---|---|---|
|disponibilite quai|1.553|1.327–1.826|
|recherche passages|539.618|508.200–590.012|
|recherche stock|88.402|85.454–109.745|
|emplacements|89.460|86.974–102.198|
|historique lot|56.541|55.112–60.425|
|selection fefo|158.653|155.135–208.038|
|statistiques transporteur|586.225|522.160–840.049|
|remplissage zone|87.453|84.906–89.983|

## 15. Indicateurs et états imprimables

Les indicateurs définissent période, unité et exclusions : occupation réelle intersectée à la période / capacité disponible des quais ; attente jusqu’au début d’opération ; immobilisation jusqu’au départ ; remplissage par zone dans chaque unité ; lignes avec écarts / lignes reçues ; productivité sur durée de préparation observée ; DLC dans un horizon inclusif.


Le stock et le remplissage sont une photographie actuelle, même si une période passée est sélectionnée pour les flux. Les données sans DLC et périmées sont isolées. Les opérations sans fin restent ouvertes. Les dénominateurs nuls et durées absentes produisent une valeur explicitement absente, sans division invalide.


Les mesures HTTP sont séparées des temps PDO volumétriques : une chauffe puis dix réponses authentifiées sur le petit jeu. Médianes locales : planning 60.3 ms, stock 345.9 ms, reports 364.1 ms. Elles incluent PHP et le transfert du HTML, sans les ressources ni le rendu du navigateur.


Les états stock, activité et écarts sont imprimables et exportables en CSV. Les exports réutilisent les filtres et les droits ; les clés techniques ne sont pas exportées. Les champs susceptibles d’être interprétés comme des formules sont neutralisés. Les documents de transport reprennent la commande, le propriétaire, les lots, les colis et le camion.


Capture authentique : ../preuves/reports.png

## 16. Conclusion et limites

La chaîne logistique est implémentée et démontrée localement, avec modèle relationnel, SQL lisible, formulaires, règles atomiques, historiques, recherche, pilotage et documents. Les quatre sources sont reliées aux livrables dans la matrice de conformité et le suivi par lots.


Les choix pédagogiques sont explicites : monosite, rôle unique par compte, FEFO, expédition intégrale, verrou global, heures civiles du site et documents non réglementaires. Les fiches structurantes utilisées sont protégées, et les faits se corrigent sans effacement silencieux. Le débit d’écriture et les agrégats historiques constituent les principaux axes d’évolution mesurable.


Les listes proposent jusqu’à 2 000 références à la fois, avec affinage par nom/référence sur les grands jeux. Les mouvements de la trace sont paginés ; les réceptions et commandes liées à un lot restent des tableaux complets. La navigation mobile a été testée dans Edge, pas sur un appareil physique.


Pour la remise, le groupe doit renseigner ses vrais noms, sa répartition des contributions et la date demandée. Les modalités A26 restent à confirmer. Aucun score attendu ni conformité réglementaire n’est annoncé.


Reprise : lancer scripts/start.ps1 ; ouvrir http://127.0.0.1:8070 ; choisir la journée 22/10/2026 pour les indicateurs. Le README donne les comptes fictifs, les commandes de recette, les sauvegardes et les emplacements des preuves. Le script de démonstration de dix minutes est dans docs/demonstration.md.


|Annexe livrée|Contenu|
|---|---|
|DIAGRAMMES-BD70.pdf + DOT/SVG|UML, MCD, MLD complets et par domaine|
|docs/dictionnaire-donnees.md|Attributs, types, unicités, FK, nullabilité|
|docs/normalisation-3nf.md|Clés candidates et DF table par table|
|docs/matrice-conformite.md|Exigence → cas → tables → écran → test → rapport|
|livrables/preuves/*.json|Tests, concurrence, mesures et restauration|