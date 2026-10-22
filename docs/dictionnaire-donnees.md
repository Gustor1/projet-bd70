# Dictionnaire des données

Généré depuis les métadonnées du moteur exécuté. NN = obligatoire ; NULL = facultatif. Quantités : unités entières ; dimensions : m ; poids : kg ; capacité palettes : équivalents. Dates/heures civiles du site Europe/Paris. Les clés et FK ci-dessous sont réellement installées.


## user_account - Utilisateurs

Unicités : (id); (email).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| email | Email | varchar(190) | NO |  |
| name | Nom | varchar(100) | NO |  |
| password_hash | Valeur interne documentée dans SQL | varchar(255) | NO |  |
| role | Profil | enum('pending','admin','manager','gate','warehouse') | NO |  |
| active | Compte actif | tinyint(1) | NO |  |
| created_at | Créé le | datetime | NO |  |

## carrier - Transporteurs

Unicités : (id); (code).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| code | Code | varchar(30) | NO |  |
| name | Nom | varchar(100) | NO |  |
| address | Adresse | varchar(255) | NO |  |
| phone | Téléphone | varchar(30) | NO |  |
| email | Email | varchar(190) | NO |  |

## carrier_contact - Contacts transporteurs

Unicités : (id).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| carrier_id | Transporteur | int(11) | NO | carrier.id |
| name | Nom | varchar(100) | NO |  |
| phone | Téléphone | varchar(30) | NO |  |
| email | Email | varchar(190) | NO |  |

## carrier_contract - Contrats

Unicités : (id); (reference).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| carrier_id | Transporteur | int(11) | NO | carrier.id |
| reference | Référence | varchar(40) | NO |  |
| starts_on | Date de début | date | NO |  |
| ends_on | Date de fin | date | NO |  |
| terms | Conditions du contrat | text | NO |  |

## qualification - Habilitations

Unicités : (id); (code).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| code | Code | varchar(30) | NO |  |
| name | Nom | varchar(100) | NO |  |

## driver - Chauffeurs

Unicités : (id); (license_number).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| carrier_id | Transporteur | int(11) | NO | carrier.id |
| name | Nom | varchar(100) | NO |  |
| phone | Téléphone | varchar(30) | NO |  |
| license_number | Numéro de permis | varchar(60) | NO |  |

## driver_qualification - Habilitations des chauffeurs

Unicités : (id); (driver_id, qualification_id).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| driver_id | Chauffeur | int(11) | NO | driver.id |
| qualification_id | Habilitation | int(11) | NO | qualification.id |
| expires_on | Date limite / validité | date | NO |  |

## equipment - Équipements

Unicités : (id); (code).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| code | Code | varchar(30) | NO |  |
| name | Nom | varchar(100) | NO |  |

## vehicle - Véhicules

Unicités : (id); (plate).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| carrier_id | Transporteur | int(11) | NO | carrier.id |
| plate | Immatriculation | varchar(30) | NO |  |
| type | Type | enum('tracteur','remorque','porteur','fourgon') | NO |  |
| max_kg | Capacité (kg) | decimal(12,3) | NO |  |
| max_pallets | Capacité (équiv. palettes) | decimal(10,3) | NO |  |

## vehicle_equipment - Équipements des véhicules

Unicités : (id); (vehicle_id, equipment_id).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| vehicle_id | Véhicule | int(11) | NO | vehicle.id |
| equipment_id | Équipement | int(11) | NO | equipment.id |

## dock - Quais

Unicités : (id); (code).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| code | Code | varchar(30) | NO |  |
| name | Nom | varchar(100) | NO |  |
| type | Type | enum('reception','expedition','mixte') | NO |  |

## dock_equipment - Équipements des quais

Unicités : (id); (dock_id, equipment_id).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| dock_id | Quai | int(11) | NO | dock.id |
| equipment_id | Équipement | int(11) | NO | equipment.id |

## dock_vehicle_type - Compatibilités des quais

Unicités : (id); (dock_id, vehicle_type).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| dock_id | Quai | int(11) | NO | dock.id |
| vehicle_type | Type de véhicule | enum('tracteur','remorque','porteur','fourgon') | NO |  |

## dock_downtime - Indisponibilités

Unicités : (id).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| dock_id | Quai | int(11) | NO | dock.id |
| starts_at | Début | datetime | NO |  |
| ends_at | Fin | datetime | NO |  |
| reason | Motif | varchar(255) | NO |  |

## appointment - Rendez-vous

Unicités : (id); (reference).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| reference | Référence | varchar(40) | NO |  |
| dock_id | Quai | int(11) | NO | dock.id |
| driver_id | Chauffeur | int(11) | NO | driver.id |
| vehicle_id | Véhicule | int(11) | NO | vehicle.id |
| trailer_id | Remorque (facultative) | int(11) | YES | vehicle.id |
| operation | Opération | enum('reception','expedition') | NO |  |
| starts_at | Début | datetime | NO |  |
| ends_at | Fin | datetime | NO |  |
| status | État | enum('active','cancelled') | NO |  |

## truck_visit - Passages camions

Unicités : (id); (reference); (appointment_id).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| reference | Référence | varchar(40) | NO |  |
| appointment_id | Rendez-vous (facultatif) | int(11) | YES | appointment.id |
| driver_id | Chauffeur | int(11) | NO | driver.id |
| vehicle_id | Véhicule | int(11) | NO | vehicle.id |
| trailer_id | Remorque (facultative) | int(11) | YES | vehicle.id |
| operation | Opération | enum('reception','expedition') | NO |  |
| dock_id | Quai | int(11) | YES | dock.id |
| status | État | enum('arrived','checked','parking','called','working','finished','departed','rejected') | NO |  |
| document_note | Contrôle documentaire / observations | varchar(255) | NO |  |

## visit_event - Chronologie des passages

Unicités : (id); (visit_id, state).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| visit_id | Passage camion | int(11) | NO | truck_visit.id |
| state | Étape | enum('arrived','checked','parking','called','working','finished','departed','rejected') | NO |  |
| happened_at | Horodatage | datetime | NO |  |
| actor_id | Auteur | int(11) | NO | user_account.id |

## owner - Clients propriétaires

Unicités : (id); (code).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| code | Code | varchar(30) | NO |  |
| name | Nom | varchar(100) | NO |  |
| address | Adresse | varchar(255) | NO |  |
| email | Email | varchar(190) | NO |  |

## supplier - Fournisseurs

Unicités : (id); (code).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| code | Code | varchar(30) | NO |  |
| name | Nom | varchar(100) | NO |  |
| address | Adresse | varchar(255) | NO |  |
| phone | Téléphone | varchar(30) | NO |  |

## article - Articles

Unicités : (id); (owner_id, sku).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| owner_id | Propriétaire | int(11) | NO | owner.id |
| sku | Référence article | varchar(40) | NO |  |
| name | Nom | varchar(100) | NO |  |
| storage | Condition de stockage | enum('ambiant','froid','dangereux') | NO |  |
| packaging | Conditionnement | varchar(80) | NO |  |
| width_m | Largeur (m) | decimal(10,4) | NO |  |
| depth_m | Profondeur (m) | decimal(10,4) | NO |  |
| height_m | Hauteur (m) | decimal(10,4) | NO |  |
| unit_kg | Poids unitaire (kg) | decimal(10,3) | NO |  |
| units_per_pallet | Unités par palette | int(11) | NO |  |

## zone - Zones

Unicités : (id); (code).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| code | Code | varchar(30) | NO |  |
| name | Nom | varchar(100) | NO |  |
| storage | Condition de stockage | enum('ambiant','froid','dangereux') | NO |  |

## aisle - Allées

Unicités : (id); (code).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| zone_id | Zone | int(11) | NO | zone.id |
| code | Code | varchar(30) | NO |  |

## rack - Racks

Unicités : (id); (code).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| aisle_id | Allée | int(11) | NO | aisle.id |
| code | Code | varchar(30) | NO |  |

## rack_level - Niveaux

Unicités : (id); (code).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| rack_id | Rack | int(11) | NO | rack.id |
| code | Code | varchar(30) | NO |  |

## location - Emplacements

Unicités : (id); (code).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| level_id | Niveau | int(11) | NO | rack_level.id |
| code | Code | varchar(30) | NO |  |
| width_m | Largeur (m) | decimal(10,4) | NO |  |
| depth_m | Profondeur (m) | decimal(10,4) | NO |  |
| height_m | Hauteur (m) | decimal(10,4) | NO |  |
| max_kg | Capacité (kg) | decimal(12,3) | NO |  |
| max_pallets | Capacité (équiv. palettes) | decimal(10,3) | NO |  |

## lot - Lots

Unicités : (id); (article_id, code).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| article_id | Article | int(11) | NO | article.id |
| code | Code | varchar(40) | NO |  |
| expires_on | Date limite / validité | date | YES |  |
| blocked | Lot bloqué | tinyint(1) | NO |  |
| block_reason | Motif du blocage | varchar(255) | NO |  |

## supplier_notice - Avis fournisseurs

Unicités : (id); (reference).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| reference | Référence | varchar(40) | NO |  |
| supplier_id | Fournisseur | int(11) | NO | supplier.id |
| expected_on | Livraison prévue | date | NO |  |

## notice_line - Lignes attendues

Unicités : (id); (notice_id, article_id).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| notice_id | Avis fournisseur | int(11) | NO | supplier_notice.id |
| article_id | Article | int(11) | NO | article.id |
| expected_qty | Quantité attendue | int(11) | NO |  |

## receipt - Réceptions

Unicités : (id); (reference).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| reference | Référence | varchar(40) | NO |  |
| notice_id | Avis fournisseur | int(11) | NO | supplier_notice.id |
| visit_id | Passage camion | int(11) | NO | truck_visit.id |
| status | État | enum('draft','validated') | NO |  |
| validated_at | Validation | datetime | YES |  |

## receipt_line - Lignes de réception

Unicités : (id); (receipt_id, notice_line_id).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| receipt_id | Réception | int(11) | NO | receipt.id |
| notice_line_id | Ligne attendue | int(11) | NO | notice_line.id |
| expected_qty | Quantité attendue | int(11) | NO |  |

## receipt_item - Palettes reçues

Unicités : (id); (pallet_code).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| line_id | Ligne de réception | int(11) | NO | receipt_line.id |
| lot_id | Lot | int(11) | NO | lot.id |
| pallet_code | Code palette / fraction | varchar(50) | NO |  |
| accepted_qty | Quantité acceptée | int(11) | NO |  |
| damaged_qty | Quantité endommagée | int(11) | NO |  |
| pallet_state | État de palette | enum('bon','abime') | NO |  |
| reservation | Réserve transporteur | varchar(255) | NO |  |
| location_id | Emplacement | int(11) | NO | location.id |

## customer_order - Commandes

Unicités : (id); (reference).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| reference | Référence | varchar(40) | NO |  |
| owner_id | Propriétaire | int(11) | NO | owner.id |
| destination | Adresse de livraison | varchar(255) | NO |  |
| desired_on | Expédition souhaitée | date | NO |  |
| status | État | enum('draft','picking','ready','shipped','cancelled') | NO |  |
| preparer_id | Préparateur | int(11) | YES | user_account.id |
| picking_at | Début de préparation | datetime | YES |  |
| ready_at | Fin de préparation | datetime | YES |  |

## order_line - Lignes de commande

Unicités : (id); (order_id, article_id).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| order_id | Commande | int(11) | NO | customer_order.id |
| article_id | Article | int(11) | NO | article.id |
| qty | Quantité | int(11) | NO |  |

## pick - Prélèvements

Unicités : (id).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| order_line_id | Ligne de commande | int(11) | NO | order_line.id |
| receipt_item_id | Palette reçue / fraction | int(11) | NO | receipt_item.id |
| location_id | Emplacement | int(11) | NO | location.id |
| qty | Quantité | int(11) | NO |  |
| status | État | enum('planned','confirmed','shipped','cancelled') | NO |  |
| confirmed_at | Confirmation | datetime | YES |  |

## package - Colis et palettes de sortie

Unicités : (id); (code).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| order_id | Commande | int(11) | NO | customer_order.id |
| code | Code | varchar(50) | NO |  |
| type | Type | enum('colis','palette') | NO |  |

## package_pick - Contenu des colis

Unicités : (id); (pick_id).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| package_id | Colis / palette | int(11) | NO | package.id |
| pick_id | Prélèvement | int(11) | NO | pick.id |

## shipment - Expéditions

Unicités : (id); (order_id); (reference).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| order_id | Commande | int(11) | NO | customer_order.id |
| visit_id | Passage camion | int(11) | NO | truck_visit.id |
| reference | Référence | varchar(40) | NO |  |
| shipped_at | Expédition | datetime | NO |  |
| actor_id | Auteur | int(11) | NO | user_account.id |

## stock_movement - Mouvements de stock

Unicités : (id); (pick_id).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| operation_ref | Opération liée | varchar(64) | NO |  |
| receipt_item_id | Palette reçue / fraction | int(11) | NO | receipt_item.id |
| location_id | Emplacement | int(11) | NO | location.id |
| delta | Variation (unités) | int(11) | NO |  |
| kind | Nature | enum('entry','transfer','shipment','adjustment') | NO |  |
| pick_id | Prélèvement | int(11) | YES | pick.id |
| reason | Motif | varchar(255) | NO |  |
| actor_id | Auteur | int(11) | NO | user_account.id |
| created_at | Créé le | datetime | NO |  |

## audit_log - Journal automatique

Unicités : (id).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | bigint(20) | NO |  |
| entity | Entité | varchar(50) | NO |  |
| entity_id | Référence technique d’audit | int(11) | NO |  |
| operation | Opération | varchar(12) | NO |  |
| actor_id | Auteur | int(11) | YES | user_account.id |
| happened_at | Horodatage | datetime | NO |  |
| details | Description | varchar(255) | NO |  |

## site_lock - Verrou du site

Unicités : (id).

| Attribut | Sens | Type | NULL | Relation |
|---|---|---|---|---|
| id | Identifiant interne | int(11) | NO |  |
| label | Valeur interne documentée dans SQL | varchar(80) | NO |  |