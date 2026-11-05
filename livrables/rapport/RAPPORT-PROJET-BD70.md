# Transit

Rapport de projet BD70 · A26

Eliott LE · Semih TASKIN · Thomas VUILLIN

## Introduction

Lorsqu’un client signale un problème sur un lot de café, l’entrepôt doit pouvoir répondre à trois questions. Qui a livré ce lot ? Où la marchandise a-t-elle été rangée ? Dans quel camion est-elle repartie ? Le stock disponible à l’instant présent ne suffit pas à répondre. Il faut conserver les événements qui expliquent comment les quantités ont évolué.

Nous avons développé Transit pour suivre cette chaîne dans un entrepôt unique. Le sujet A26 demande une base relationnelle couvrant huit domaines et une interface web pour au moins cinq d’entre eux. Transit propose une interface pour les huit, depuis la gestion des accès jusqu’aux indicateurs d’activité. Les opérations sont réalisées dans le navigateur avec PHP et PDO côté serveur et MariaDB pour la persistance.

## Acteurs et responsabilités

Le diagramme de cas d’utilisation distingue la décision, l’exécution et le contrôle. La préparation d’une commande illustre cette séparation. Le responsable désigne un magasinier. Ce dernier réserve et prélève les unités de sa commande. L’affectation et la réservation correspondent donc à deux actions distinctes.

| Acteur | Responsabilité dans Transit |
|---|---|
| Administrateur technique | Active les comptes, gère les profils et consulte le journal. |
| Responsable d’exploitation | Tient les référentiels, planifie les quais, gère les commandes, affecte les préparateurs et consulte les indicateurs. |
| Agent d’accueil | Enregistre l’arrivée, le contrôle documentaire, l’attente, l’appel à quai et le départ. |
| Magasinier ou préparateur | Horodate les opérations à quai, réceptionne, range et prépare les commandes qui lui sont affectées. |
| Transporteur | Gère les rendez-vous et les ressources de sa propre société dans un espace dédié. |

## Du modèle conceptuel au schéma relationnel

Le MCD en notation de Chen décrit les faits métier. Le schéma relationnel les traduit en 41 tables, dont deux tables techniques consacrées au journal et au verrou du site. Les deux modèles et le use case corrigé figurent dans le recueil de diagrammes joint au rapport.

**Distinguer la prévision du fait constaté.** Le rendez-vous décrit le quai et les ressources prévus. Le passage décrit le camion effectivement arrivé et la chronologie de ses opérations. Une réservation peut rester sans passage et un camion peut arriver spontanément. De même, un avis fournisseur décrit les quantités attendues, alors que la réception conserve le comptage réel et les réserves.

**Conserver la provenance.** Un même lot peut arriver en plusieurs livraisons. Chaque fraction reçue conserve son lien avec la ligne de réception, le lot et l’emplacement initial. Les transferts expliquent ses déplacements ultérieurs. Le prélèvement relie cette fraction à une ligne de commande et à l’emplacement où elle a été prise.

**Choisir où placer un attribut.** Une société emploie plusieurs chauffeurs. Une clé étrangère sur le chauffeur suffit à exprimer cette relation 1:N. Pour les colis, il faut représenter une relation N:N. Si un prélèvement de douze unités est réparti entre deux colis, les quantités sept et cinq décrivent chacune une affectation précise. La table package_pick porte donc les deux clés étrangères, l’unicité du couple et la quantité affectée.

**Normaliser les sorties.** Lors d’une expédition, le prélèvement détermine déjà la fraction, l’emplacement et la quantité. Le mouvement de sortie référence ce prélèvement. La vue v_stock_movement reconstitue les valeurs nécessaires au calcul du stock. Pour les autres mouvements, ces valeurs sont portées directement par le mouvement. Un CHECK impose l’exclusivité des deux structures. Cette décision évite que deux enregistrements donnent des quantités différentes pour la même sortie.

## Intégrité, transactions et historisation

Une clé étrangère garantit qu’un emplacement existe. Elle ne garantit pas qu’il dispose encore de la capacité requise. Transit complète les contraintes SQL par des contrôles sur les quantités, les poids, les volumes, les équivalents palettes et la compatibilité entre le produit et la zone de stockage.

Lorsqu’une opération touche plusieurs lignes, le backend ouvre une transaction. Par exemple, deux responsables peuvent voir le même créneau libre au même moment. La procédure lock_site verrouille une ligne avec SELECT FOR UPDATE. La première transaction vérifie la disponibilité et enregistre son rendez-vous. La seconde attend, puis relit le planning et détecte le chevauchement. Si un contrôle échoue, les écritures de la transaction sont annulées. Le verrou de site simplifie cette garantie, au prix d’une attente possible entre des écritures indépendantes.

MariaDB définit 120 déclencheurs, deux procédures stockées et neuf vues. Par exemple, le trigger audit_carrier_update enregistre automatiquement l’ancienne et la nouvelle valeur quand un transporteur est modifié. D’autres déclencheurs protègent l’historique contre des modifications ou suppressions. La procédure trace_lot est appelée par l’écran de traçabilité pour retrouver les mouvements et, le cas échéant, l’expédition et le camion associés.

L’application vérifie le rôle et les objets concernés côté serveur. Le transporteur doit appartenir à la société du rendez-vous qu’il modifie. Les requêtes paramétrées, les mots de passe hachés et la vérification des jetons CSRF complètent ces contrôles. Le compte SQL de l’application dispose de privilèges limités.

## Fonctionnalités du site et des quais

**1. Connexion et profils.** Objectif : identifier les utilisateurs et limiter leurs droits. Réalisation : une inscription crée un compte en attente, qu’un administrateur doit activer. Les autorisations sont contrôlées lors de l’accès aux pages et lors des actions. Conclusion : un compte désactivé est refusé et un transporteur autorisé reste limité à sa société.

**2. Transporteurs et ressources.** Objectif : savoir qui transporte la marchandise et avec quel matériel. Réalisation : les fiches regroupent sociétés, contacts, contrats, chauffeurs, habilitations, véhicules, capacités et équipements. Conclusion : le responsable peut actualiser un numéro de téléphone ou supprimer une fiche inutilisée. Une ressource déjà référencée reste identifiable dans son historique.

**3. Quais et rendez-vous.** Objectif : attribuer un créneau réalisable. Réalisation : le responsable choisit un quai, un horaire et des ressources compatibles. L’application contrôle les indisponibilités et les conflits de réservation. Conclusion : le planning présente les quais libres, réservés, occupés ou hors service. Il s’actualise toutes les trente secondes en dehors d’une saisie.

**4. Passage du camion.** Objectif : mesurer où le camion passe du temps. Réalisation : l’accueil et le magasinier enregistrent les étapes successives, depuis l’arrivée jusqu’au départ. Le parking est facultatif. Conclusion : la chronologie permet de distinguer l’attente et l’immobilisation totale, et de comparer l’arrivée effective au rendez-vous prévu.

## Fonctionnalités de réception et d’expédition

**5. Réception.** Objectif : comparer la livraison à l’annonce du fournisseur. Réalisation : le magasinier enregistre les fractions reçues, les lots, les dates limites, les avaries et les réserves. Conclusion : seules les quantités acceptées entrent en stock. Un manque total peut faire l’objet d’une réserve sans créer de palette fictive.

**6. Emplacements et stock.** Objectif : connaître la quantité d’un lot et sa position. Réalisation : le rangement est organisé par zone, allée, rack, niveau et emplacement. Les propositions tiennent compte des capacités disponibles et des conditions de stockage. Les entrées, transferts, sorties et ajustements alimentent le journal des mouvements. Conclusion : le solde se calcule depuis ce journal et chaque déplacement reste explicable.

**7. Préparation et expédition.** Objectif : servir la commande avec les lots utilisables et charger les quantités prévues. Réalisation : le préparateur affecté lance la sélection FEFO, qui privilégie les échéances les plus proches. Il confirme les prélèvements, constitue les colis et les rattache au camion sortant. Conclusion : la validation contrôle les quantités et les capacités avant l’émission du bon de livraison et de la lettre de voiture.

**8. Traçabilité et pilotage.** Objectif : retrouver un lot et mesurer l’activité du site. Réalisation : une recherche par lot relie réceptions, mouvements, commandes et camions. Le tableau de bord propose l’occupation des quais, les temps par transporteur, le remplissage par zone, les écarts en réception, la productivité et les alertes de date limite. Conclusion : les filtres, tableaux, graphiques, impressions et exports permettent d’exploiter les résultats. Les indicateurs d’activité portent sur la période choisie, tandis que les stocks et les alertes de péremption reflètent la situation courante.

## Vérification sur un parcours complet

Le scénario de soutenance utilise une base de test distincte et le lot ORAL-CAFE-LOT. Le fournisseur annonce 20 unités. À la réception, le magasinier en accepte 18 et déclare 2 unités endommagées. Il transfère ensuite 3 unités entre deux emplacements. Ce transfert change leur répartition tout en préservant le total de 18 unités.

Le responsable crée une commande de 10 unités et l’affecte à un magasinier. Après réservation, prélèvement et mise en colis, celui-ci confirme le chargement dans le passage ORAL-CAFE-SORTIE. La recherche de traçabilité retrouve ce camion à partir du lot. Les 32 étapes vérifiées sur ce parcours ont réussi. Le guide illustré du dossier soutenance présente les écrans et les saisies correspondantes.

D’autres recettes ciblent les refus que ce parcours nominal ne montre pas : conflit de créneaux, dépassement de capacité, accès aux données d’une autre société et double validation. La recette métier de référence comprend 64 contrôles d’intégration. Sur le jeu riche, 83 contrôles d’intégrité ont été exécutés sans anomalie détectée. Ces résultats correspondent aux versions et aux jeux de données indiqués dans docs/recette.md.

## Données de démonstration et performances

Le jeu riche est fictif. Il couvre 90 jours simulés, avec 180 articles, 1 806 passages de camions, 903 réceptions et 900 expéditions. Il alimente les formulaires de recherche et les tableaux de bord. Une base distincte contenant 10 000 passages sert aux mesures de performances.

Pour chaque requête, une exécution de chauffe précède dix exécutions mesurées côté PDO, récupération des résultats comprise. Le tableau donne les médianes en millisecondes. Le détail des paramètres, des plans EXPLAIN et des valeurs extrêmes figure dans docs/performances.md.

| Requête | Médiane (ms) |
|---|---:|
| Disponibilité d’un quai | 1,263 |
| Recherche de passages | 48,410 |
| Recherche de stock | 60,175 |
| Emplacements | 41,890 |
| Historique d’un lot | 38,453 |
| Sélection FEFO | 65,776 |
| Statistiques par transporteur | 59,515 |
| Remplissage par zone | 48,001 |

L’index de réservation facilite la recherche des créneaux qui se chevauchent sur un quai. La vue d’utilisation des emplacements a aussi été revue pour éviter des jointures inutiles lors du calcul des capacités. Les temps mesurés dépendent du volume, du cache et de la machine. L’affichage d’une page ajoute le traitement PHP et le rendu du navigateur.

## Conclusion

À partir d’un numéro de lot, Transit permet de retrouver la livraison d’origine, les emplacements successifs et le camion d’expédition. Cette réponse repose sur trois décisions de conception : séparer l’attendu du réalisé, conserver la provenance des fractions et rattacher chaque sortie à un prélèvement identifié.

L’application couvre les huit domaines du sujet sur un site unique. Les commandes sont expédiées intégralement. La restauration d’une sauvegarde a été vérifiée dans une base séparée par comparaison des 41 tables et contrôle de l’historisation. Pour étendre le système à plusieurs entrepôts ou à des expéditions partielles, il faudrait revoir les règles d’affectation des ressources, la clôture des commandes et la granularité des verrous.

Le dossier livrables contient le use case corrigé, le modèle Chen, le schéma relationnel et leurs sources Draw.io. Le README indique comment installer Transit et charger le jeu fictif pour reproduire le parcours.
