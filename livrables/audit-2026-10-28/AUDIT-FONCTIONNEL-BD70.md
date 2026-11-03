# Audit fonctionnel du projet BD70

Date : **28 octobre 2026, heure de Paris**, conformément à la précision de l’utilisateur. Révision examinée : `b7eab735a69b9e2dadb5bf9258c4d40ad538acab`, avec les fichiers locaux présents. Audit uniquement : aucune correction du produit n’a été appliquée.

## 1. Conclusion et décision proposée

**Les huit domaines fonctionnels du sujet sont déjà représentés dans la base, les traitements et l’interface. Le projet n’est cependant pas terminé au niveau de couverture et de qualité demandé.** Les déclarations « réalisé et testé » de l’ancienne matrice sont trop générales : elles ne distinguent pas un parcours nominal réussi d’une fonctionnalité réellement utilisable dans ses variantes.

Il faut conserver le socle existant et compléter ses traitements. Les priorités sont :

1. Corriger les indicateurs sur période vide et unifier l’heure de Paris entre PHP et SQL.
2. Compléter les réserves de réception, notamment lorsque toute une ligne manque.
3. Permettre les modifications légitimes des référentiels et rendre cohérent le cycle de correction des commandes.
4. Approfondir le conditionnement en colis/palettes et contrôler la compatibilité de l’ensemble tracteur/remorque.
5. Fournir un jeu de démonstration nettement plus riche, cohérent et consultable dans l’application.
6. Fiabiliser les tests dans le temps, puis actualiser la documentation et les preuves.

**Aucun pourcentage de conformité ni aucune note scolaire n’est attribué.** La grille ne fournit pas de pondération, et la présence d’une table ou d’un écran ne suffit pas à valider une exigence.

## 2. Sources et méthode

Sources de référence relues directement :

- [Sujet A26, PDF, trois pages](../../document%20projet/A26_Site_Logistique.pdf) : fonctionnalités p. 1–2, exigences générales p. 2, livrables et contraintes p. 3. Les trois pages ont également été rendues et inspectées visuellement.
- [Grille d’évaluation, DOCX](../../document%20projet/Éléments%20dévaluation%20projet%20BD70.docx) : texte et structure des paragraphes/tableaux extraits de l’original OOXML.
- Code : `src/`, `templates/`, `public/`, `sql/`, générateurs et tests.
- Documentation existante : cahier des charges, cas d’utilisation, hypothèses, limites, matrices, normalisation, performances, rapport et preuves.
- Base réellement configurée : `bd70_demo_final`, consultée en lecture seule pour les volumes.

Le PDF exige le modèle complet mais seulement cinq domaines web au minimum. **Pour la suite, la cible retenue est celle demandée par l’utilisateur : tous les domaines décrits doivent être utilisables dans l’application**, même ceux dépassant ce minimum web. La demande orale du professeur, rapportée par l’utilisateur, renforce l’attente de richesse fonctionnelle et de données. Aucun quota officiel de lignes n’est inventé.

Le compte transporteur est explicitement facultatif dans le PDF. FEFO est une alternative admise à FIFO : l’absence de FIFO ne constitue donc pas un manque obligatoire. Les expéditions partielles, le GPS, la facturation, l’EDI ou une conformité réglementaire de lettre de voiture ne sont pas exigés par les documents fournis.

### Vérifications exécutées pendant cet audit

| Vérification | Résultat actuel | Portée |
|---|---|---|
| Suite métier `tests/integration.php` | **64 réussis, 0 échec** | Base neuve dédiée ; règles, contraintes, stock, FEFO et quatre scénarios concurrents |
| Suite navigateur `tests/browser.cjs` | **70 réussis, 1 échec** | Échec de la page des indicateurs sur période sans camion ; 39 rubriques chargées, CRUD transporteur, droits, CSV et documents testés |
| Parcours métier `tests/parcours.cjs` | **Échec avant sa fin** | Sur une autre base neuve : le test cherche une sortie sur un lot déjà périmé ; diagnostic détaillé ci-dessous |
| Sondes ciblées complémentaires | Plusieurs limites reproduites | Réserves, modifications, commandes, colis, compatibilité et horloges ; résultats JSON conservés |
| Volumes de la démonstration | Comptés dans la base active | Aucun chargement ni écrasement de cette base |

Les visites des 39 rubriques ne prouvent pas tous les CRUD de chaque table. Les tests ne constituent pas une certification exhaustive de l’application. Les performances, la restauration et l’installation sur un autre poste n’ont pas été intégralement rejouées pendant cet audit ; leurs résultats antérieurs restent identifiés comme historiques.

Les exécutions finales ont été séparées : `bd70_test_audit_20261029` pour l’intégration, `bd70_test_audit_flows_20261029` pour les contrôles navigateur, `bd70_test_audit_probes_20261029` pour les sondes, et `bd70_test_audit_ui_20261029` pour le parcours final indépendant. Le suffixe technique a été choisi avant la précision « heure de Paris » et ne définit pas la date de ce rapport. Une première exploration partageait la base navigateur ; les sondes et le parcours ont ensuite été rejoués chacun sur une base neuve distincte. Seuls ces derniers résultats sont retenus pour leur diagnostic.

## 3. Couverture de chaque exigence fonctionnelle du sujet

**Présent** signifie que modèle, traitement et accès utilisateur existent. **Partiel** signale une capacité réellement incomplète. **À corriger** signale un défaut établi. **À approfondir** vise la qualité d’usage au-delà du scénario nominal. Les renvois D01–D14 correspondent aux constats détaillés plus bas.

### F01 — Connexion et authentification

| Demande du sujet | Ce qui existe | Évaluation et suite |
|---|---|---|
| Inscription et connexion du personnel | `Auth::register/login`, formulaires, compte en attente, activation administrateur, déconnexion | **Présent.** Inscription sans élévation de rôle et contrôles HTTP testés. Ajouter ensuite un changement de mot de passe personnel et une récupération encadrée si souhaité ; ce ne sont pas des exigences explicites. |
| Profils distincts : administrateur, responsable, accueil, magasinier/préparateur | `Auth::RIGHTS`, contrôles de droits sur actions et routes | **Présent.** Vérifier les habilitations métier par action lors de la recette finale. Le profil transporteur externe n’existe pas ; il reste **facultatif** dans le sujet. |

### F02 — Transporteurs, chauffeurs et véhicules

| Demande du sujet | Ce qui existe | Évaluation et suite |
|---|---|---|
| Sociétés, coordonnées, contrats, contacts | `carrier`, `carrier_contact`, `carrier_contract`, formulaires du catalogue | **Présent.** Regrouper les relations dans une fiche transporteur pour éviter plusieurs écrans indépendants. |
| Chauffeurs rattachés, identité, téléphone, permis, habilitations | `driver`, `qualification`, `driver_qualification`, contrôle ADR lors des opérations de marchandises dangereuses | **À corriger : D04.** Le téléphone et le renouvellement d’une habilitation deviennent non modifiables dès que le chauffeur a été utilisé. |
| Quatre types de véhicules, plaques, capacités et équipements | `vehicle`, `vehicle_equipment`, capacités kg/palettes, association tracteur/remorque | **Présent, à corriger/approfondir : D04, D05.** Geler toutes les propriétés est trop restrictif ; les contrôles de quai n’examinent pas le type de la remorque. |

### F03 — Quais et rendez-vous

| Demande du sujet | Ce qui existe | Évaluation et suite |
|---|---|---|
| Type du quai, équipements, types de véhicules compatibles | `dock`, `dock_equipment`, `dock_vehicle_type`, indisponibilités | **Présent.** Les données peuvent représenter des compatibilités plus fines que celles réellement contrôlées. |
| Créneaux sans chevauchement et compatibilité véhicule/quai | `Warehouse::appointment/compatible`, verrou transactionnel, contrôle d’indisponibilité | **Présent, à corriger : D05.** Les conflits sur le même quai et la concurrence sont testés. Ajouter aussi la disponibilité du chauffeur, véhicule et remorque entre quais : D10, amélioration métier. |
| État actuel libre, réservé, occupé, hors service | `Reports::docks`, planning et actualisation à 30 secondes | **À corriger : D02.** L’heure SQL diffère de l’heure Paris. L’actualisation est une recharge conditionnelle, pas un flux instantané ; ce choix peut convenir après fiabilisation. |

### F04 — Flux de camions

| Demande du sujet | Ce qui existe | Évaluation et suite |
|---|---|---|
| Arrivée, contrôle documentaire, parking, appel, début/fin d’opération, départ | `truck_visit`, événements horodatés et transitions contrôlées | **Présent.** Parking facultatif, refus au contrôle, documents décrits par un texte. Pas de pièce jointe documentaire, non exigée explicitement. |
| Horodates, attente, immobilisation, retards par rapport au RDV | `visit_event`, `v_visit`, calcul du retard dans l’écran Camions | **Présent, à fiabiliser : D02.** Ajouter une vue des retards/no-shows et une correction exceptionnelle tracée est utile, mais aucun tableau d’alertes spécifique n’est imposé. |
| Arrivée sans RDV et affectation à un quai disponible | `Warehouse::arrive/transition`, sélection du quai, vérification à l’appel | **Présent.** Une liste limitée aux quais réellement utilisables améliorerait le parcours ; le contrôle serveur existe déjà. |

### F05 — Réception des marchandises

| Demande du sujet | Ce qui existe | Évaluation et suite |
|---|---|---|
| Avis fournisseurs avec articles et quantités attendues | `supplier_notice`, `notice_line`, formulaires | **Présent, à approfondir : D09.** Pas de synthèse métier « attendu/reçu/reste/clos » d’un avis ; les réceptions partielles existent. |
| Réception effective, quantités, lots, DLC, état des palettes | `receipt`, `receipt_line`, `receipt_item`, `lot`, validation transactionnelle | **Présent.** Multilots, plusieurs réceptions d’un lot, avaries et provenance sont modélisés. Le parcours utilisateur reste éclaté entre de nombreux formulaires. |
| Manquants, excédents, dommages et réserves transporteur | Vue des écarts, quantités endommagées, champ réserve sur une fraction reçue | **Partiel : D03.** Un manquant total est calculable, mais sa réserve métier n’a aucun support adapté lorsqu’aucune palette n’est reçue. |
| Affectation à un emplacement de stockage | Emplacement par fraction, validation des capacités et compatibilités | **Présent.** Relier directement les propositions au formulaire de réception plutôt que faire rechercher l’emplacement dans un autre écran. |

### F06 — Emplacements et stocks

| Demande du sujet | Ce qui existe | Évaluation et suite |
|---|---|---|
| Zones, allées, racks, niveaux, emplacements et capacités | Hiérarchie de tables ; dimensions, kg, équivalents palettes à l’emplacement ; agrégations par zone | **Présent.** La capacité est détaillée au niveau emplacement, calculée au niveau supérieur. Prévoir un navigateur de structure pour rendre les 300+ futurs emplacements utilisables. |
| Articles, dimensions, poids, conditionnement, stockage et propriétaires | `article`, `owner`, formulaires et filtres | **Présent, édition trop figée : D04.** La démonstration ne contient que trois articles, tous du même propriétaire. |
| Quantités par article/lot/emplacement ; entrées, transferts, sorties et ajustements historisés | Journal immuable `stock_movement`, vues de stock/réservations, transactions et motifs | **Présent et bien structuré.** Les tests de conservation, rollback et concurrence passent. Conserver ce principe. |
| Compatibilité produit/zone et propositions d’emplacements libres adaptés | `Warehouse::capacity/suggestions`, dimensions, poids, volume et équivalents palettes | **Présent.** Les propositions peuvent inclure un emplacement partiellement occupé mais avec capacité restante : c’est cohérent avec ce modèle. Un filtre « totalement vide » serait une amélioration. |

### F07 — Préparation et expédition

| Demande du sujet | Ce qui existe | Évaluation et suite |
|---|---|---|
| Commandes, lignes, quantités, date d’expédition souhaitée | `customer_order`, `order_line`, formulaires et statuts | **Présent, correction à compléter : D06.** L’annulation est définitive alors que le message demande d’annuler avant modification. |
| Liste de prélèvement FIFO ou FEFO, affectation à un préparateur | Réservation FEFO, préparateur actif, liste imprimable, exclusion des lots bloqués/périmés | **Présent.** FEFO suffit au sujet. La confirmation de tous les prélèvements en un seul clic reste simplifiée ; un suivi par ligne serait plus convaincant. |
| Constitution de colis/palettes puis chargement dans un camion sortant | `package`, `package_pick`, expédition reliée au passage, capacité cumulée du camion | **Partiel au sens de richesse d’usage : D07.** Un prélèvement entier doit tenir dans un seul colis/palette ; impossible de répartir sa quantité. Le sujet ne dicte pas le découpage, mais cette limitation gêne des commandes ordinaires. |
| Bon de livraison et lettre de voiture | Deux documents imprimables distincts dans `templates/document.php`, données de transport et signatures pour la lettre | **Présent.** Documents pédagogiques simples. Ajouter totaux, poids, nombre de colis et mentions métier ; éviter de les présenter comme absents ou certifiés réglementaires. |

### F08 — Traçabilité et tableaux de bord

| Demande du sujet | Ce qui existe | Évaluation et suite |
|---|---|---|
| Historique du lot : réception, emplacements successifs, commande, camion de sortie | Écran Trace, procédure `trace_lot`, provenance des fractions et prélèvements | **Présent.** La trace d’origine est testée. L’échec du parcours daté n’est pas une preuve de trace cassée : D08. Pagination et recherche à renforcer sur gros volume : D11. |
| Taux d’occupation des quais | Durée d’opération / temps disponible, indisponibilités déduites | **Présent, à fiabiliser : D01/D02.** Convention 24 h/24 explicitée. Une occupation par quai, en plus du total, serait utile. |
| Attente et immobilisation moyennes par transporteur | Vue des passages, moyennes et nombres de mesures | **Présent, page à corriger : D01.** Les oracles métier passent, la période vide casse l’affichage. |
| Remplissage par zone | kg, m³, équivalents palettes et barre de remplissage | **Présent.** Photographie actuelle, clairement annoncée ; ne pas la présenter comme une photographie historique de la période filtrée. |
| Taux d’écart en réception | Pourcentage de lignes validées avec écart, totaux manquants/excédents/avaries | **Présent.** Définition explicite et oracle vérifié. À compléter avec le suivi des avis non soldés : D09. |
| Productivité des préparateurs | Quantités et lignes, temps réservation→confirmation, unités/heure | **Présent, mesure simplifiée.** Un seul préparateur actif dans les opérations de démonstration ne permet pas une comparaison intéressante. |
| Articles proches de la date limite | Stock disponible par lot et horizon de DLC | **À corriger : D02/D08.** Mélange de la date courante SQL et de la date choisie pour le rapport ; les résultats anciens changent avec le temps. |

## 4. Constats détaillés et preuves

### D01 — Page des indicateurs cassée lorsqu’une période n’a aucun camion

**Priorité 1 — défaut reproduit, exigence explicite.** Ouvrir les indicateurs sans changer la période par défaut sur la démonstration : le tableau des transporteurs est vide, puis le reste de la page affiche « Impossible de présenter ces données ». Le serveur répond 422.

Cause : [templates/reports.php](../../templates/reports.php), ligne 5, appelle `max(1, ...$valeurs)` ; avec zéro valeur, PHP reçoit `max(1)` et déclenche un `TypeError`. Il faut un état vide normal, et continuer à afficher les autres indicateurs.

Preuves : [contrôles navigateur](preuves/navigateur.json), [capture de l’erreur](preuves/reports.png), sonde `empty_chart_php` dans [audit-probes.json](preuves/audit-probes.json). Critère de sortie : période vide → HTTP 200, aucune alerte technique et tous les blocs rendus correctement.

### D02 — Heure Paris appliquée à PHP mais pas à MariaDB

**Priorité 1 — défaut reproduit.** À la même seconde, PHP donnait le 28/10/2026 à 17:41:48, MariaDB le 29/10/2026 à 00:41:48. Ce décalage provient du fuseau système SQL ; il ne suffit pas de définir `date_default_timezone_set('Europe/Paris')` côté PHP.

Un RDV couvrant l’heure Paris actuelle est vu **Libre** par `Reports::docks`. En réglant uniquement la session SQL de test sur le décalage Paris du jour, le même quai devient **Réservé**. Le réglage a été rétabli après la sonde ; aucune modification globale de l’horloge ou de MariaDB n’a été faite.

Sources : [src/Database.php](../../src/Database.php), lignes 15–21 ; [src/Reports.php](../../src/Reports.php), méthodes `docks/dashboard` ; [sql/02_vues.sql](../../sql/02_vues.sql), `CURRENT_DATE()`. Preuve : `clock` et `live_dock_during_php_appointment` du JSON des sondes.

Correction attendue : une politique temporelle commune, Paris pour l’utilisateur et des calculs PHP/SQL cohérents. Ne pas figer `+01:00` toute l’année : l’heure d’été doit être traitée. Une heure système réellement fausse nécessite aussi une référence d’horloge correcte ; changer de fuseau ne corrige pas une dérive de l’horloge elle-même. Tester minuit, expiration, créneaux actifs et changements d’heure. Le code refuse actuellement toute une journée de changement d’heure (`Warehouse::datetime`) : lever ou justifier cette limitation dans une évolution ciblée.

### D03 — Réserve transporteur impossible à rattacher proprement à un manquant total

**Priorité 1 — couverture partielle d’une exigence explicite.** Une ligne attendue de 10 unités peut être validée avec 0 reçu : le manquant de 10 est correctement calculé. En revanche, la réserve n’existe que sur `receipt_item`, dont la contrainte impose `accepted_qty + damaged_qty > 0`. Ni `receipt` ni `receipt_line` ne possède de réserve.

Créer une fausse palette ou renseigner le contrôle documentaire du camion n’est pas une solution métier satisfaisante : on perdrait soit la réalité de la réception, soit le rattachement précis de la réserve à l’écart.

Sources : [sql/01_schema.sql](../../sql/01_schema.sql), lignes 65–72 ; `Warehouse::validateReceipt`. Preuve : sonde `full_shortage_and_reserve`. Ajouter une réserve au niveau réception/ligne ou une entité dédiée, avec texte, auteur, date et rattachement à l’écart/transporteur. Cas d’acceptation : livraison totalement absente, manque partiel, excédent, avarie, plusieurs réserves si retenu ; consultation dans les états et la trace.

### D04 — Le CRUD bloque aussi les modifications qui devraient rester possibles

**Priorité 1 — défaut d’usage au regard de la gestion des données.** `Catalog::guard` compare tous les champs d’une fiche considérée « structurelle » dès qu’elle est utilisée. Modifier le téléphone d’un chauffeur utilisé est refusé. Renouveler sa validité ADR de 2028 à 2029 est également refusé. L’unicité chauffeur/habilitation empêche simplement de créer une deuxième association identique.

Le même mécanisme fige intégralement articles, véhicules, quais et structures utilisés. Protéger les dimensions historiques est légitime ; interdire tout changement descriptif est trop large.

Source : [src/Catalog.php](../../src/Catalog.php), lignes 128–145. Preuves : `phone_edit_used_driver`, `renew_used_qualification`. Distinguer champs descriptifs modifiables, changements structurels sous contrôle et historique de validité. Ne pas rendre les mouvements de stock éditables pour satisfaire artificiellement le CRUD.

### D05 — Compatibilité du type de remorque non contrôlée

**Priorité 1 — contrôle incomplet.** `Warehouse::compatible` teste `dock_vehicle_type` seulement avec le véhicule moteur. Un quai déclaré compatible uniquement « tracteur » accepte un rendez-vous avec une remorque, même sans compatibilité « remorque » déclarée.

Source : [src/Warehouse.php](../../src/Warehouse.php), lignes 28–38. Preuve : `trailer_not_in_dock_types`. Clarifier si les compatibilités décrivent le véhicule moteur, l’unité chargée ou l’ensemble ; appliquer la même règle au modèle, aux formulaires, au RDV et à l’appel à quai. Ne pas laisser une compatibilité saisissable sans effet sur les contrôles.

### D06 — Annuler une commande ne permet pas la correction annoncée

**Priorité 2 — incohérence reproduite.** Le message conseille d’annuler la préparation avant modification. `cancelOrder` place pourtant la commande en `cancelled`, et `Catalog::guard` n’autorise l’édition qu’en `draft`. Aucune action ne permet de revenir en brouillon ou de dupliquer proprement la commande pour la corriger.

Sources : [src/Warehouse.php](../../src/Warehouse.php), lignes 198–205 ; [src/Catalog.php](../../src/Catalog.php), branche commandes. Preuve : `cancel_then_edit_order`. Distinguer annulation définitive et abandon de préparation, ou proposer une duplication explicite. Traiter réservations et colis associés sans perdre l’historique.

### D07 — Conditionnement trop limité pour des commandes variées

**Priorité 2 — limitation reproduite, à approfondir pour la cible demandée.** La relation `package_pick` contient un `pick_id UNIQUE`, sans quantité. Deux unités prélevées en une seule fois ne peuvent pas être affectées à deux colis distincts. Le prélèvement n’est pas éditable depuis le catalogue.

Source : [sql/01_schema.sql](../../sql/01_schema.sql), ligne 77 ; `Catalog::READONLY` ; `Warehouse::ship`. Preuve : `split_pick_two_packages`. Ajouter une allocation quantifiée, avec somme des quantités conditionnées égale au prélèvement et contrôle avant chargement. Le fonctionnement actuel suffit à un colis par prélèvement ; il ne faut pas le qualifier d’absence totale de préparation/expédition.

### D08 — Tests et indicateur DLC dépendants de dates devenues anciennes

**Priorité 1 pour la preuve de conformité ; priorité 2 pour l’indicateur.** Le parcours navigateur crée un lot expirant le **23/10/2026**, puis attend que ce lot soit expédié. Le 28 octobre, FEFO l’exclut correctement et choisit `LOT-A`. Le test échoue ensuite car il cherche le camion sortant sur le lot périmé.

Preuves : [log du parcours indépendant](preuves/parcours.log), [lots effectivement reçus et prélevés](preuves/parcours-diagnostic.json). Cause dans [tests/parcours.cjs](../../tests/parcours.cjs), lignes 13 et 31. **Ce résultat ne démontre pas une traçabilité défectueuse ; il démontre un test devenu invalide.** Le parcours de 31 étapes n’est donc plus une preuve reproductible à la date actuelle.

Autre cas : `Reports::dashboard` utilise un horizon relatif au début de période, mais sélectionne `available_qty` dans une vue qui élimine déjà les lots périmés à la date SQL actuelle. En avançant uniquement l’horloge de session de test au 1er décembre puis en demandant le rapport du 22 octobre, les 40 unités froides attendues dans cet horizon disparaissent. Preuve : `historic_dlc_current_sql_date`.

Séparer données pédagogiques datées, démonstration opérationnelle relative à Paris et horloge contrôlée des tests. Pour les DLC, choisir clairement un indicateur « aujourd’hui » ou un calcul historique complet ; ne pas mélanger les deux.

### D09 — Avis fournisseurs sans véritable suivi du reste et de clôture

**Priorité 2 — capacité complémentaire nécessaire pour approfondir les réceptions.** Les réceptions partielles disposent d’allocations de quantités attendues et d’une protection contre la surallocation. Mais l’avis n’a pas de statut ouvert/partiel/soldé/clos ni de synthèse utilisateur des lignes restant à recevoir. Une ligne absente d’une réception n’est pas automatiquement matérialisée comme manquante, ce qui est normal pour une livraison partielle mais doit être explicité lors de la clôture.

Sources : schéma `supplier_notice/notice_line`, `Warehouse::validateReceipt`, écran Réceptions. Ajouter un suivi du reste, une clôture volontaire et une distinction entre reste à livrer et manque définitif. Ne pas déclarer automatiquement toute réception partielle comme erronée.

### D10 — Les ressources peuvent avoir deux RDV simultanés sur deux quais

**Priorité 2 — amélioration métier, au-delà de l’interdiction explicite sur un même quai.** Deux RDV au même horaire, avec le même chauffeur et le même véhicule, sont acceptés si leurs quais diffèrent. Le contrôle d’arrivée empêche ensuite une double présence sur site, mais le planning reste incohérent.

Preuve : `same_driver_vehicle_two_docks`. Ajouter les conflits de chauffeur, moteur et remorque, en conservant les créneaux adjacents et les tests concurrents.

### D11 — L’interface n’est pas encore adaptée à un jeu riche

**Priorité 2 — constats de code.** Les brouillons de réception sont limités à 50 sans pagination ni filtre dans le panneau qui permet leur validation (`templates/receipts.php:4`). Une réception plus ancienne peut rester accessible dans le catalogue mais ne plus être proposée à la validation sur l’écran opérationnel.

`Catalog::options` limite les sélecteurs à 2 000 valeurs. Il existe bien un affinement par référence dans le bandeau de certains écrans : ce n’est pas une absence totale de recherche. Toutefois, l’écran Trace, qui sélectionne aussi un lot, ne fait pas partie des pages où ce bandeau apparaît (`templates/layout.php:13`). De plus, l’affichage du bandeau dépend des nombres de passages, fractions et commandes, pas de la taille de chaque référentiel.

Les formulaires listent aussi des choix que le serveur refusera : anciens camions pour charger, tous les utilisateurs pour préparer, lignes d’autres réceptions. Les contrôles serveur protègent les opérations ; des sélections contextuelles et recherchables réduiraient les erreurs. Un formulaire guidé de réception et une fiche de commande regroupant lignes, prélèvements et colis sont recommandés.

### D12 — Historisation technique présente mais peu explicative

**Priorité 3 — amélioration.** Les déclencheurs enregistrent entité, identifiant, opération, auteur et date, mais le détail vaut seulement « Modification métier ». On sait qu’une fiche a changé, pas quels champs métier ont été modifiés. Les mouvements de stock conservent, eux, des quantités et motifs utiles.

Source : [sql/04_triggers.sql](../../sql/04_triggers.sql). Preuve : `audit_values`. Pour les champs métier utiles, conserver les différences ou les valeurs avant/après, en excluant les secrets. Cela renforcerait l’exigence d’historisation sans réécrire le journal de stock.

### D13 — Documentation trop affirmative et rapport encore incomplet

**Priorité 2 après corrections.** `docs/matrice-conformite.md` indique tous les domaines « réalisé et testé » et renvoie à des preuves désormais partiellement périmées. Le rapport mentionne encore les auteurs à renseigner. Plusieurs versions des diagrammes coexistent, dont `livrables/use-case-v2/` non suivi par Git au début de l’audit.

Actualiser la matrice avec exigences fines, variantes testées, date des preuves et limites réelles ; choisir un jeu officiel de diagrammes ; fournir un récit objectif/travail réalisé/conclusion par fonctionnalité ; compléter auteurs et contributions. Ne pas remplacer les preuves historiques par de nouveaux résultats sans conserver leur date et leur contexte.

### D14 — Données de démonstration insuffisamment riches pour la cible actuelle

**Priorité 1 de livraison, après stabilisation des règles.** Le volume de performance existe, mais la démonstration visible est presque vide hors d’une journée. La diversité est particulièrement faible : un fournisseur, trois articles, un seul préparateur représenté dans les commandes expédiées, deux transporteurs réellement actifs dans le scénario.

Le sujet exige déjà des données factices en quantité ; la consigne rapportée du professeur renforce ce point. Il faut livrer des données riches utilisables, pas seulement augmenter les compteurs du benchmark.

## 5. Données SQL : constat et proposition

### Volumes réellement présents

Mesure dans `bd70_demo_final` : [volumes-demo.json](preuves/volumes-demo.json).

| Données | Démonstration active |
|---|---:|
| Utilisateurs | 7, dont comptes supplémentaires ; le générateur de base prévoit 4 profils internes |
| Transporteurs / chauffeurs / véhicules | 3 / 3 / 4 |
| Clients propriétaires / fournisseurs | 2 / 1 |
| Articles / lots | 3 / 6 |
| Zones / emplacements / quais | 3 / 6 / 3 |
| Rendez-vous / passages camions | 1 / 3 |
| Avis / réceptions / fractions reçues | 2 / 3 / 7 |
| Commandes / expéditions / colis | 3 / 2 / 2 |
| Mouvements de stock | 11 |

Le jeu de performance historique décrit dans [docs/performances.md](../../docs/performances.md) contient **10 003 passages, 60 019 événements et 22 011 mouvements**. Ces valeurs proviennent des preuves livrées antérieurement ; elles n’ont pas été recomptées dans la base de performance pendant cet audit. Le script `scripts/performance.php` reprend les quelques référentiels initiaux, utilise essentiellement un article supplémentairement alimenté, et ne diversifie pas massivement les commandes. Il démontre un volume technique, pas un entrepôt varié.

### Jeu riche proposé, sans prétendre à un quota du professeur

| Objet | Cible pédagogique initiale proposée |
|---|---:|
| Utilisateurs avec plusieurs préparateurs | 15–25 |
| Transporteurs / chauffeurs / véhicules | 15–25 / 60–100 / 80–120 |
| Clients / fournisseurs | 15–25 / 15–25 |
| Articles / lots | 150–300 / 600–1 200 |
| Zones / quais / emplacements | 6–9 / 8–12 / 300–600 |
| Rendez-vous et passages sur 3–6 mois | 1 500–3 000 de chaque ordre de grandeur |
| Réceptions / commandes | 800–1 500 / 800–1 500 |
| Mouvements | 15 000–30 000, dérivés de vrais scénarios cohérents |

Conserver deux profils séparés : une démonstration riche et lisible, et un jeu de charge à 10 000 passages ou davantage. Les volumes doivent rester compatibles avec les capacités, ressources et durées, pas être obtenus en dupliquant artificiellement une ligne.

Scénarios à couvrir : plusieurs propriétaires avec des SKU comparables, ambiant/froid/dangereux, remorques et porteurs, habilitations valides et expirées, créneaux futurs/annulés, retards et arrivées sans RDV, parking et refus, quais hors service, réceptions partielles et totalement manquantes, excédents et avaries avec réserves, lots reçus plusieurs fois, DLC proche/périmée/absente, lot bloqué, transferts, ajustements positifs/négatifs, commandes dans chaque état, plusieurs préparateurs, préparation multilots et conditionnement multicolis.

Livrer un générateur reproductible avec graine et date de référence **Paris**, un inventaire des volumes et scénarios, et un export SQL pédagogique prêt à importer dans une **nouvelle base**. Si un export est livré, il ne doit contenir que les comptes et informations fictifs prévus pour la démonstration, jamais la configuration locale ou des données personnelles réelles. Le générateur doit refuser une base non vide ; les données de l’utilisateur ne doivent pas être remplacées.

Vérifier après génération : clés étrangères, contraintes, stock jamais négatif, réservations ≤ stock, capacités respectées, transferts conservatifs, aucune double occupation, cohérence des chronologies, totaux des colis et traçabilité jusqu’au camion. Les tableaux de bord doivent montrer des comparaisons et des distributions variées.

## 6. Grille d’évaluation et livrables

| Critère | État observé | Travail restant |
|---|---|---|
| Cas d’utilisation et UML | Cas textuels et plusieurs diagrammes présents | Aligner la version officielle sur les parcours retenus, y compris réserves et corrections |
| MCD et MLD cohérents | Modèles complets et vues par domaine ; schéma de 40 tables, dont 2 techniques | Mettre à jour après les évolutions de réserves, conditionnement et habilitations |
| PK, types, 1:N, N:N, FK | Contraintes et associations présentes ; refus FK/UNIQUE/CHECK testés | Continuer les contrôles intertables dans les services, documenter les responsabilités SQL/PHP |
| Normalisation et redondances | Dictionnaire et document de 3NF présents ; stocks et durées calculés | Vérifier les dépendances métier table par table lors des migrations ; le texte répétitif actuel ne suffit pas, seul, à prouver toute la 3NF. Aucun défaut précis de 3NF n’est affirmé sans démonstration. |
| Qualité et quantité des informations | Référentiels bien séparés, mais petit jeu visible | Jeu riche et varié décrit ci-dessus |
| Ajout, édition, suppression sans SQL manuel | Catalogue générique, actions métier, annulations et protections | Lever le gel excessif des fiches et compléter les corrections. Préserver les historiques immuables. |
| Contrôle des saisies | Validations serveur, requêtes préparées, contraintes, transactions | Cas D03–D07, sélections contextuelles et messages précis |
| Recherche multicritère | Stocks, camions, réceptions et catalogue | Compléter commandes par propriétaire/date/préparateur et sélecteurs à grande échelle |
| Statistiques et présentation | Tous les indicateurs nommés ont un calcul, tableaux et barres | D01/D02/D08 ; données permettant de comparer plusieurs transporteurs/préparateurs |
| États | CSV filtrés, impressions, prélèvement/BL/lettre de voiture | Totaux métier, réserves et qualité d’impression sur documents plus longs |
| Finition, menus, boutons, identifiants | Menu français, références majoritairement lisibles, contrôles de largeur mobile | Moins de formulaires techniques dispersés ; certains libellés génériques « Association n » restent à remplacer |
| Multi-utilisateurs | Inscription, activation, 4 rôles, droits contrôlés et concurrence testée | Recette complète des parcours par rôle ; verrou global conservateur à mesurer avant optimisation |
| Rapport de projet | Rapport Markdown/PDF, sommaire, introduction, conclusion, captures | Auteurs réels, contributions, nouvelles limites, preuves et périmètre final |
| Performances et optimisation | Rapport avec 8 requêtes, répétitions et EXPLAIN ; comparaison d’index | Rejouer sur le nouveau jeu. Anciennes médianes ~540 ms pour recherche des passages et ~586 ms pour statistiques transporteur : pistes d’optimisation, pas mesures actuelles |
| Automatismes internes | Déclencheurs d’audit, immuabilité et procédures | Historisation plus explicative si retenue ; maintenir restauration avec routines/triggers |
| Sécurité et confidentialité | Hachage, sessions, CSRF, échappement, droits HTTP et compte SQL limité | Conserver ces acquis ; audit de sécurité exhaustif et déploiement public hors du périmètre de cette revue |

## 7. Plan de continuation proposé

Ce plan est une recommandation pour la prochaine phase. **Aucun lot d’implémentation n’est commencé par cet audit.**

| Lot | Périmètre et résultat attendu | Dépendances | Critère de sortie |
|---|---|---|---|
| 1 — Fiabilité immédiate | Indicateurs vides, cohérence Paris PHP/SQL, politique DLC, horloge de tests et données datées ; D01/D02/D08 | Aucun | Suite métier et navigateur vertes, parcours complet reproductible, minuit et période vide testés |
| 2 — Réception complète | Réserves sur manquants totaux/partiels, suivi des avis/restes/clôture, saisie guidée ; D03/D09 | Lot 1 | Réception partielle, complète, excédentaire, avariée et totalement absente démontrables depuis l’UI, stock/trace corrects |
| 3 — Référentiels et planning | Champs descriptifs éditables, renouvellement habilitations, compatibilité ensemble routier, conflits de ressources ; D04/D05/D10 | Lot 1 | Téléphone et ADR renouvelables sans perdre le passé ; conflits de quai/véhicule/chauffeur/remorque refusés sous concurrence |
| 4 — Préparation et expédition approfondies | Correction/annulation distinctes, allocations quantifiées des colis, confirmation détaillée, documents enrichis ; D06/D07 | Lots 1–3 | Une ligne de 20 unités répartie en deux colis de 10, préparation multilots, reprise correcte et chargement unique conservant la trace |
| 5 — Données riches et interface à volume | Générateur/SQL de démonstration, scénarios variés, sélecteurs et pagination, optimisation des requêtes les plus coûteuses ; D11/D14 | Lots 2–4 | Aucun brouillon inaccessible, recherche de références au-delà des limites anciennes, contrôles d’intégrité et tableaux variés |
| 6 — Recette et remise | Matrice exhaustive, tests par exigence/rôle, performances, restauration, UML/MCD/MLD et rapport à jour ; D12 si retenu, D13 | Tous les précédents | Chaque ligne du sujet associée à une preuve datée ; toutes les anomalies prioritaires closes ; livrables cohérents et auteurs complétés |

Priorité de réalisation recommandée : **lot 1, puis lot 2**, car ils corrigent des défauts visibles et une couverture incomplète du sujet. Les lots 3–5 doivent faire partie de la continuation pour atteindre le niveau de richesse demandé. Le lot 6 est indispensable avant remise.

Ce qui mérite d’être conservé : découpage fournisseurs/propriétaires/transporteurs, stock dérivé des mouvements, provenance des fractions, FEFO, transactions et tests de concurrence, protections de droits, formats documentaires et outillage de performances. Une réécriture totale augmenterait le risque sans résoudre automatiquement les lacunes.

## 8. État laissé et preuves disponibles

- Aucun fichier applicatif, schéma SQL existant, ancienne preuve, ancien diagramme ou rapport de remise modifié.
- Seul ce dossier d’audit est ajouté aux livrables. Les fichiers non suivis préexistants `livrables/use-case-v2/` et `scripts/build-usecase-v2.py` sont conservés.
- Copie locale d’exécution : `.local/audit-2026-10-29/`, exclue de Git ; bases de test nommées ci-dessus conservées, aucune base supprimée.
- Le service local de démonstration a été redémarré avec le script du projet. Aucun changement de l’heure du PC, aucun déploiement, commit ou push.
- Les secrets de configuration, cookies et sessions ne figurent pas dans les preuves livrées.

Les preuves détaillées sont dans [preuves/](preuves/) : intégration et concurrence, navigateur, sondes, capture du défaut d’indicateurs, volumes actifs et diagnostic du parcours. Les anciennes preuves du dépôt demeurent historiques. Le présent audit ne les transforme pas en résultats actuels.
