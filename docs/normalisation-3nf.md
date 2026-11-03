# Normalisation et dépendances fonctionnelles

Analyse du 3 novembre 2026 à partir de `sql/01_schema.sql`, des vues et des services `Catalog` et `Warehouse`. Les dépendances ci-dessous sont les hypothèses métier effectivement représentées ; il ne s’agit pas d’une preuve exhaustive de toutes les dépendances possibles. Une clé artificielle ne suffit pas à prouver la 3NF.

## Clés et granularité

Pour chaque relation, chaque clé candidate totale ci-dessous détermine les autres attributs de la ligne. Les clés naturelles sont contraintes par UNIQUE et NOT NULL. Les clés contenant une colonne nullable sont signalées séparément : MariaDB autorise plusieurs NULL et elles ne sont donc pas des clés candidates totales.

| Relation | Clés candidates totales | Unicités conditionnelles |
|---|---|---|
| `user_account` | (id) ; (email) | — |
| `carrier` | (id) ; (code) | — |
| `carrier_contact` | (id) | — |
| `carrier_contract` | (id) ; (reference) | — |
| `qualification` | (id) ; (code) | — |
| `driver` | (id) ; (license_number) | — |
| `driver_qualification` | (id) ; (driver_id, qualification_id) | — |
| `equipment` | (id) ; (code) | — |
| `vehicle` | (id) ; (plate) | — |
| `vehicle_equipment` | (id) ; (vehicle_id, equipment_id) | — |
| `dock` | (id) ; (code) | — |
| `dock_equipment` | (id) ; (dock_id, equipment_id) | — |
| `dock_vehicle_type` | (id) ; (dock_id, vehicle_type) | — |
| `dock_downtime` | (id) | — |
| `appointment` | (id) ; (reference) | — |
| `truck_visit` | (id) ; (reference) | (appointment_id) |
| `visit_event` | (id) ; (visit_id, state) | — |
| `owner` | (id) ; (code) | — |
| `supplier` | (id) ; (code) | — |
| `article` | (id) ; (owner_id, sku) | — |
| `zone` | (id) ; (code) | — |
| `aisle` | (id) ; (code) | — |
| `rack` | (id) ; (code) | — |
| `rack_level` | (id) ; (code) | — |
| `location` | (id) ; (code) | — |
| `lot` | (id) ; (article_id, code) | — |
| `supplier_notice` | (id) ; (reference) | — |
| `notice_line` | (id) ; (notice_id, article_id) | — |
| `receipt` | (id) ; (reference) | — |
| `receipt_line` | (id) ; (receipt_id, notice_line_id) | — |
| `receipt_item` | (id) ; (pallet_code) | — |
| `customer_order` | (id) ; (reference) | — |
| `order_line` | (id) ; (order_id, article_id) | — |
| `pick` | (id) | — |
| `package` | (id) ; (code) | — |
| `package_pick` | (id) ; (package_id, pick_id) | — |
| `shipment` | (id) ; (order_id) ; (reference) | — |
| `stock_movement` | (id) | (pick_id) |
| `audit_log` | (id) | — |
| `receipt_reserve` | (id) | — |
| `site_lock` | (id) | — |

## Référentiels et structure physique

`carrier`, `carrier_contact`, `carrier_contract`, `driver`, `vehicle`, `qualification` et `equipment` séparent société, personnes, contrat et ressources. `carrier_id` ne détermine ni le nom d’un contact ni le permis d’un chauffeur : une société en possède plusieurs. La référence du contrat détermine ses propres dates et conditions ; elle n’est pas une copie de coordonnées de la société. L’immatriculation détermine type et capacités du véhicule. Aucun lien métier n’impose qu’un type détermine une capacité unique.

`owner` et `supplier` représentent deux fonctions différentes. Dans `article`, (owner_id, sku) détermine désignation, conditions, conditionnement, dimensions, poids et unités par palette. Un SKU seul n’est pas unique entre propriétaires. Ces caractéristiques concernent l’article complet, pas seulement le propriétaire. Dans `lot`, (article_id, code) détermine DLC et blocage ; le code fabricant seul ne détermine pas l’article.

`zone` détermine sa condition de stockage ; allée, rack, niveau et emplacement portent seulement leur parent direct. `location.level_id` ne détermine pas ses dimensions ni capacités : plusieurs emplacements distincts partagent un niveau. La zone d’un emplacement est obtenue par jointures, et ses volumes et taux de remplissage sont calculés. Les noms des parents ne sont pas recopiés dans leurs enfants.

`user_account.email` est une clé métier de connexion. Nom, empreinte, rôle et activation décrivent ce compte ; aucun nom de rôle n’est recopié dans les événements. `site_lock` est une relation technique singleton de sérialisation, sans justification fonctionnelle métier à lui prêter.

## Associations et dépendance à la clé entière

`driver_qualification` : (driver_id, qualification_id) → expires_on. La validité dépend du couple chauffeur/habilitation, aucun de ses participants ne suffit. Ce modèle garde une validité courante, pas toutes les périodes successives ; les renouvellements sont journalisés. `vehicle_equipment` et `dock_equipment` sont des ensembles de couples sans propriété descriptive redondante. `dock_vehicle_type` associe un quai à un domaine ENUM commun aux véhicules, sans table de type supplémentaire.

`notice_line` : (notice_id, article_id) → expected_qty. `order_line` : (order_id, article_id) → qty. Ces quantités appartiennent à une annonce ou commande précise ; elles ne dépendent pas de l’article seul. Les noms et propriétaires des articles restent obtenus par jointure.

`package_pick` : (package_id, pick_id) → qty. Un prélèvement peut alimenter plusieurs colis et un colis en regrouper plusieurs : ni package_id ni pick_id seul ne détermine la quantité affectée. Les sommes affectées sont calculées. SQL garantit unicité du couple et quantité positive ; les services vérifient la même commande, le prélèvement confirmé, l’absence de surallocation et la couverture exacte avant expédition.

## Planning et faits constatés

`dock_downtime` décrit une période propre à un quai, sans stocker sa durée. `appointment.reference` détermine ressources prévues, période et opération. `truck_visit.reference` détermine ressources effectivement constatées et quai effectif. Le rendez-vous facultatif unique ne constitue pas une clé totale ; un passage sans réservation reste identifiable. Les valeurs initialisées depuis le rendez-vous sont un constat opérationnel distinct, conservé même si une réservation évoluait.

`visit_event` : (visit_id, state) → happened_at, actor_id. Un état n’apparaît qu’une fois dans ce cycle sans retour arrière. `truck_visit.status` est une projection stockée redondante avec la chaîne d’événements : elle facilite le pilotage et doit rester synchronisée transactionnellement. SQL ne démontre pas cette synchronisation à lui seul. Les attentes et immobilisations sont calculées depuis les événements.

## Réception partielle et provenance

`supplier_notice` décrit l’annonce globale et sa clôture motivée ; `receipt` décrit une livraison réelle liée à un passage. `receipt_line` : (receipt_id, notice_line_id) → expected_qty. Cet attendu est l’allocation locale à cette livraison, pas une copie de l’attendu total de notice_line. Une même ligne d’avis peut alimenter plusieurs livraisons ; notice_line_id seul ne détermine donc pas l’attendu local. Les services vérifient le cumul des allocations à la validation. Un manquant validé consomme l’allocation de cette livraison ; le reste et les écarts sont calculés par des vues distinctes.

`receipt_item` identifie une fraction reçue (pallet_code unique), son lot, les quantités acceptées/avariées et son emplacement initial. Ni lot_id ni line_id seul ne détermine ces faits : un lot peut arriver plusieurs fois et une ligne contenir plusieurs lots. Le lien au passage et au fournisseur se retrouve par la réception, sans duplication. L’emplacement initial reste un fait historique après transfert ; la position actuelle vient des mouvements. `receipt_reserve` porte réception OU ligne, imposé par CHECK XOR : stocker les deux créerait line_id → receipt_id redondant. Une réserve complémentaire après validation est un nouvel événement, jamais l’édition de la réserve précédente.

## Préparation et mouvements

`pick` identifie une allocation de quantité à une ligne, une fraction reçue et un emplacement de prélèvement. La fraction ne détermine pas l’emplacement de prélèvement : elle peut avoir été transférée et répartie. Les prélèvements annulés sont conservés après reprise. `package` détermine sa commande, code et type. `shipment.order_id`, obligatoire et unique, exprime l’expédition intégrale unique d’une commande ; référence et id sont aussi des clés. L’état courant de commande et ses dates sont des projections conservées et contrôlées par les transitions métier, pas des faits indépendants arbitraires.

`stock_movement` identifie un événement signé ; operation_ref regroupe notamment les deux jambes d’un transfert et n’est pas unique. Les soldes ne sont pas stockés. Pour une sortie, pick_id non NULL est unique et détermine déjà fraction, emplacement et quantité négative par le prélèvement. La répétition de receipt_item_id, location_id et delta constitue donc une **redondance contrôlée sur les lignes de sortie** : le journal uniforme permet les sommes et la traçabilité sans joindre tous les types d’opérations. Sur la relation entière, pick_id nullable n’est pas une clé candidate totale. On ne revendique pas une 3NF stricte de cette projection conditionnelle. `Warehouse::ship` construit les sorties à partir des prélèvements, sous transaction ; CHECK garantit signe/type et présence de pick_id, FK son existence et UNIQUE une seule sortie. SQL seul ne garantit pas l’égalité des trois valeurs au prélèvement. Une écriture SQL administrative pourrait les désynchroniser ; les contrôles d’intégrité vérifient ces égalités. Aucune refonte du journal n’est introduite sans migration de données justifiée.

## Journal et garanties

`audit_log` conserve des instantanés JSON avant/après dans un texte technique. Ces documents sont intentionnellement dénormalisés et exclus de la revendication de normalisation des relations métier ; l’identité générique (entity, entity_id) n’est pas une FK polymorphe SQL. Les triggers assurent la capture et excluent password_hash ; les droits applicatifs interdisent UPDATE/DELETE du journal. Les libellés courants des référentiels restent modifiables : les documents imprimables relisent ces libellés, sans constituer une archive figée.

Les clés, FK, nullabilités, domaines, signes, XOR et unicités sont garantis par SQL. Les égalités entre chemins de jointure (article/lot/propriétaire), cumul des capacités, FEFO, quantités réservées, absence de chevauchement et transitions reposent sur les services transactionnels et `site_lock`. Des clés étrangères individuelles ne prouvent pas ces invariants croisés. Les tests comportementaux et d’intégrité vérifient ces garanties sur des données fictives ; ils ne constituent pas une preuve formelle de tous les états possibles.
