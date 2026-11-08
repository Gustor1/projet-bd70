# Dictionnaire des données du schéma corrigé
42 tables ; sorties projetées par v_stock_movement. appointment_archive reprend les colonnes de appointment plus archived_at (date d’historisation) ; elle est alimentée uniquement par la procédure archive_appointments (sql/08_historisation.sql). Schéma installé, 3 novembre 2026.

## user_account

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| email | Email | varchar(190) | NO |
| name | Nom | varchar(100) | NO |
| password_hash | password_hash | varchar(255) | NO |
| role | Profil | enum('pending','admin','manager','gate','warehouse','carrier') | NO |
| active | Compte actif | tinyint(1) | NO |
| created_at | Créé le | datetime | NO |
| carrier_id | Transporteur | int(11) | YES |

## carrier

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| code | Code | varchar(30) | NO |
| name | Nom | varchar(100) | NO |
| address | Adresse | varchar(255) | NO |
| phone | Téléphone | varchar(30) | NO |
| email | Email | varchar(190) | NO |

## carrier_contact

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| carrier_id | Transporteur | int(11) | NO |
| name | Nom | varchar(100) | NO |
| phone | Téléphone | varchar(30) | NO |
| email | Email | varchar(190) | NO |

## carrier_contract

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| carrier_id | Transporteur | int(11) | NO |
| reference | Référence | varchar(40) | NO |
| starts_on | Date de début | date | NO |
| ends_on | Date de fin | date | NO |
| terms | Conditions du contrat | text | NO |

## qualification

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| code | Code | varchar(30) | NO |
| name | Nom | varchar(100) | NO |

## driver

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| carrier_id | Transporteur | int(11) | NO |
| name | Nom | varchar(100) | NO |
| phone | Téléphone | varchar(30) | NO |
| license_number | Numéro de permis | varchar(60) | NO |

## driver_qualification

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| driver_id | Chauffeur | int(11) | NO |
| qualification_id | Habilitation | int(11) | NO |
| expires_on | Date limite / validité | date | NO |

## equipment

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| code | Code | varchar(30) | NO |
| name | Nom | varchar(100) | NO |

## vehicle

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| carrier_id | Transporteur | int(11) | NO |
| plate | Immatriculation | varchar(30) | NO |
| type | Type | enum('tracteur','remorque','porteur','fourgon') | NO |
| max_kg | Capacité (kg) | decimal(12,3) | NO |
| max_pallets | Capacité (équiv. palettes) | decimal(10,3) | NO |

## vehicle_equipment

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| vehicle_id | Véhicule | int(11) | NO |
| equipment_id | Équipement | int(11) | NO |

## dock

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| code | Code | varchar(30) | NO |
| name | Nom | varchar(100) | NO |
| type | Type | enum('reception','expedition','mixte') | NO |

## dock_equipment

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| dock_id | Quai | int(11) | NO |
| equipment_id | Équipement | int(11) | NO |

## dock_vehicle_type

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| dock_id | Quai | int(11) | NO |
| vehicle_type | Type de véhicule | enum('tracteur','remorque','porteur','fourgon') | NO |

## dock_downtime

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| dock_id | Quai | int(11) | NO |
| starts_at | Début | datetime | NO |
| ends_at | Fin | datetime | NO |
| reason | Motif | varchar(255) | NO |

## appointment

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| reference | Référence | varchar(40) | NO |
| dock_id | Quai | int(11) | NO |
| driver_id | Chauffeur | int(11) | NO |
| vehicle_id | Véhicule | int(11) | NO |
| trailer_id | Remorque (facultative) | int(11) | YES |
| operation | Opération | enum('reception','expedition') | NO |
| starts_at | Début | datetime | NO |
| ends_at | Fin | datetime | NO |
| status | État | enum('active','cancelled') | NO |

## truck_visit

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| reference | Référence | varchar(40) | NO |
| appointment_id | Rendez-vous (facultatif) | int(11) | YES |
| driver_id | Chauffeur | int(11) | NO |
| vehicle_id | Véhicule | int(11) | NO |
| trailer_id | Remorque (facultative) | int(11) | YES |
| operation | Opération | enum('reception','expedition') | NO |
| dock_id | Quai | int(11) | YES |
| status | État | enum('arrived','checked','parking','called','working','finished','departed','rejected') | NO |
| document_note | Contrôle documentaire / observations | varchar(255) | NO |

## visit_event

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| visit_id | Passage camion | int(11) | NO |
| state | Étape | enum('arrived','checked','parking','called','working','finished','departed','rejected') | NO |
| happened_at | Horodatage | datetime | NO |
| actor_id | Auteur | int(11) | NO |

## owner

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| code | Code | varchar(30) | NO |
| name | Nom | varchar(100) | NO |
| address | Adresse | varchar(255) | NO |
| email | Email | varchar(190) | NO |

## supplier

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| code | Code | varchar(30) | NO |
| name | Nom | varchar(100) | NO |
| address | Adresse | varchar(255) | NO |
| phone | Téléphone | varchar(30) | NO |

## article

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| owner_id | Propriétaire | int(11) | NO |
| sku | Référence article | varchar(40) | NO |
| name | Nom | varchar(100) | NO |
| storage | Condition de stockage | enum('ambiant','froid','dangereux') | NO |
| packaging | Conditionnement | varchar(80) | NO |
| width_m | Largeur (m) | decimal(10,4) | NO |
| depth_m | Profondeur (m) | decimal(10,4) | NO |
| height_m | Hauteur (m) | decimal(10,4) | NO |
| unit_kg | Poids unitaire (kg) | decimal(10,3) | NO |
| units_per_pallet | Unités par palette | int(11) | NO |

## zone

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| code | Code | varchar(30) | NO |
| name | Nom | varchar(100) | NO |
| storage | Condition de stockage | enum('ambiant','froid','dangereux') | NO |

## aisle

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| zone_id | Zone | int(11) | NO |
| code | Code | varchar(30) | NO |

## rack

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| aisle_id | Allée | int(11) | NO |
| code | Code | varchar(30) | NO |

## rack_level

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| rack_id | Rack | int(11) | NO |
| code | Code | varchar(30) | NO |

## location

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| level_id | Niveau | int(11) | NO |
| code | Code | varchar(30) | NO |
| width_m | Largeur (m) | decimal(10,4) | NO |
| depth_m | Profondeur (m) | decimal(10,4) | NO |
| height_m | Hauteur (m) | decimal(10,4) | NO |
| max_kg | Capacité (kg) | decimal(12,3) | NO |
| max_pallets | Capacité (équiv. palettes) | decimal(10,3) | NO |

## lot

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| article_id | Article | int(11) | NO |
| code | Code | varchar(40) | NO |
| expires_on | Date limite / validité | date | YES |
| blocked | Lot bloqué | tinyint(1) | NO |
| block_reason | Motif du blocage | varchar(255) | NO |

## supplier_notice

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| reference | Référence | varchar(40) | NO |
| supplier_id | Fournisseur | int(11) | NO |
| expected_on | Livraison prévue | date | NO |
| closed_at | Clôturé le | datetime | YES |
| closed_by | Clôturé par | int(11) | YES |
| closure_note | Motif de clôture | varchar(255) | NO |

## notice_line

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| notice_id | Avis fournisseur | int(11) | NO |
| article_id | Article | int(11) | NO |
| expected_qty | Quantité attendue | int(11) | NO |

## receipt

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| reference | Référence | varchar(40) | NO |
| notice_id | Avis fournisseur | int(11) | NO |
| visit_id | Passage camion | int(11) | NO |
| status | État | enum('draft','validated') | NO |
| validated_at | Validation | datetime | YES |

## receipt_line

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| receipt_id | Réception | int(11) | NO |
| notice_line_id | Ligne attendue | int(11) | NO |
| expected_qty | Quantité attendue | int(11) | NO |

## receipt_item

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| line_id | Ligne de réception | int(11) | NO |
| lot_id | Lot | int(11) | NO |
| pallet_code | Code palette / fraction | varchar(50) | NO |
| accepted_qty | Quantité acceptée | int(11) | NO |
| damaged_qty | Quantité endommagée | int(11) | NO |
| pallet_state | État de palette | enum('bon','abime') | NO |
| reservation | Réserve transporteur | varchar(255) | NO |
| location_id | Emplacement | int(11) | NO |

## customer_order

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| reference | Référence | varchar(40) | NO |
| owner_id | Propriétaire | int(11) | NO |
| destination | Adresse de livraison | varchar(255) | NO |
| revision_note | Motif de reprise | varchar(255) | NO |
| desired_on | Expédition souhaitée | date | NO |
| status | État | enum('draft','picking','ready','shipped','cancelled') | NO |
| preparer_id | Préparateur | int(11) | YES |
| picking_at | Début de préparation | datetime | YES |
| ready_at | Fin de préparation | datetime | YES |

## order_line

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| order_id | Commande | int(11) | NO |
| article_id | Article | int(11) | NO |
| qty | Quantité | int(11) | NO |

## pick

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| order_line_id | Ligne de commande | int(11) | NO |
| receipt_item_id | Palette reçue / fraction | int(11) | NO |
| location_id | Emplacement | int(11) | NO |
| qty | Quantité | int(11) | NO |
| status | État | enum('planned','confirmed','shipped','cancelled') | NO |
| confirmed_at | Confirmation | datetime | YES |

## package

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| order_id | Commande | int(11) | NO |
| code | Code | varchar(50) | NO |
| type | Type | enum('colis','palette') | NO |

## package_pick

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| package_id | Colis / palette | int(11) | NO |
| pick_id | Prélèvement | int(11) | NO |
| qty | Quantité | int(11) | NO |

## shipment

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| order_id | Commande | int(11) | NO |
| visit_id | Passage camion | int(11) | NO |
| reference | Référence | varchar(40) | NO |
| shipped_at | Expédition | datetime | NO |
| actor_id | Auteur | int(11) | NO |

## stock_movement

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| operation_ref | Opération liée | varchar(64) | NO |
| receipt_item_id | Palette reçue / fraction | int(11) | YES |
| location_id | Emplacement | int(11) | YES |
| delta | Variation (unités) | int(11) | YES |
| kind | Nature | enum('entry','transfer','shipment','adjustment') | NO |
| pick_id | Prélèvement | int(11) | YES |
| reason | Motif | varchar(255) | NO |
| actor_id | Auteur | int(11) | NO |
| created_at | Créé le | datetime | NO |

## audit_log

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | bigint(20) | NO |
| entity | Entité | varchar(50) | NO |
| entity_id | Référence technique d’audit | int(11) | NO |
| operation | Opération | varchar(12) | NO |
| actor_id | Auteur | int(11) | YES |
| happened_at | Horodatage | datetime | NO |
| details | Description | text | NO |

## receipt_reserve

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| receipt_id | Réception | int(11) | YES |
| line_id | Ligne de réception | int(11) | YES |
| kind | Nature | enum('manquant','excedent','avarie','autre') | NO |
| reason | Motif | varchar(255) | NO |
| actor_id | Auteur | int(11) | NO |
| created_at | Créé le | datetime | NO |

## site_lock

| Attribut | Sens | Type | NULL |
|---|---|---|---|
| id | Identifiant interne | int(11) | NO |
| label | label | varchar(80) | NO |
