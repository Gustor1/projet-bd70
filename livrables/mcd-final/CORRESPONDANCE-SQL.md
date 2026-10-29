# Correspondance MCD / SQL

Les cardinalités se lisent comme des participations : près de CLIENT, 0,N signifie qu’un client participe à zéro ou plusieurs occurrences de l’association. Les identifiants conceptuels sont soulignés ; leurs valeurs sont les id du modèle physique, sauf le type de véhicule (domaine énuméré).

## Associations

| Repère | Entité A | Participation A | Association | Entité B | Participation B | Traduction SQL |
|---|---|---|---|---|---|---|
| R01 | TRANSPORTEUR | 0,N | possède un contact | CONTACT | 1,1 | carrier_contact.carrier_id |
| R02 | TRANSPORTEUR | 0,N | signe un contrat | CONTRAT | 1,1 | carrier_contract.carrier_id |
| R03 | TRANSPORTEUR | 0,N | rattache un chauffeur | CHAUFFEUR | 1,1 | driver.carrier_id |
| R04 | TRANSPORTEUR | 0,N | exploite un véhicule | VÉHICULE | 1,1 | vehicle.carrier_id |
| R05 | QUAI | 0,N | subit une indisponibilité | INDISPONIBILITÉ | 1,1 | dock_downtime.dock_id |
| R06 | QUAI | 0,N | est prévu pour | RENDEZ-VOUS | 1,1 | appointment.dock_id |
| R07 | CHAUFFEUR | 0,N | est prévu pour | RENDEZ-VOUS | 1,1 | appointment.driver_id |
| R08 | VÉHICULE | 0,N | est prévu comme principal | RENDEZ-VOUS | 1,1 | appointment.vehicle_id |
| R09 | VÉHICULE | 0,N | est prévue comme remorque | RENDEZ-VOUS | 0,1 | appointment.trailer_id |
| R10 | RENDEZ-VOUS | 0,1 | donne lieu à | PASSAGE CAMION | 0,1 | truck_visit.appointment_id |
| R11 | CHAUFFEUR | 0,N | conduit le passage | PASSAGE CAMION | 1,1 | truck_visit.driver_id |
| R12 | VÉHICULE | 0,N | effectue (véhicule principal) | PASSAGE CAMION | 1,1 | truck_visit.vehicle_id |
| R13 | VÉHICULE | 0,N | accompagne (remorque) | PASSAGE CAMION | 0,1 | truck_visit.trailer_id |
| R14 | QUAI | 0,N | dessert le passage | PASSAGE CAMION | 0,1 | truck_visit.dock_id |
| R15 | PASSAGE CAMION | 1,N | comporte une étape | ÉVÉNEMENT DE PASSAGE | 1,1 | visit_event.visit_id |
| R16 | UTILISATEUR | 0,N | enregistre une étape | ÉVÉNEMENT DE PASSAGE | 1,1 | visit_event.actor_id |
| R17 | CLIENT PROPRIÉTAIRE | 0,N | possède | ARTICLE | 1,1 | article.owner_id |
| R18 | ZONE | 0,N | contient | ALLÉE | 1,1 | aisle.zone_id |
| R19 | ALLÉE | 0,N | contient | RACK | 1,1 | rack.aisle_id |
| R20 | RACK | 0,N | contient | NIVEAU | 1,1 | rack_level.rack_id |
| R21 | NIVEAU | 0,N | contient | EMPLACEMENT | 1,1 | location.level_id |
| R22 | ARTICLE | 0,N | définit | LOT | 1,1 | lot.article_id |
| R23 | UTILISATEUR | 0,N | clôture un avis | AVIS FOURNISSEUR | 0,1 | supplier_notice.closed_by |
| R24 | FOURNISSEUR | 0,N | émet un avis | AVIS FOURNISSEUR | 1,1 | supplier_notice.supplier_id |
| R25 | AVIS FOURNISSEUR | 0,N | détaille un avis | LIGNE D’AVIS | 1,1 | notice_line.notice_id |
| R26 | ARTICLE | 0,N | figure dans | LIGNE D’AVIS | 1,1 | notice_line.article_id |
| R27 | AVIS FOURNISSEUR | 0,N | livre tout ou partie | RÉCEPTION | 1,1 | receipt.notice_id |
| R28 | PASSAGE CAMION | 0,N | achemine une réception | RÉCEPTION | 1,1 | receipt.visit_id |
| R29 | RÉCEPTION | 0,N | détaille une réception | LIGNE DE RÉCEPTION | 1,1 | receipt_line.receipt_id |
| R30 | LIGNE D’AVIS | 0,N | alloue un attendu local | LIGNE DE RÉCEPTION | 1,1 | receipt_line.notice_line_id |
| R31 | LIGNE DE RÉCEPTION | 0,N | se répartit en fractions | FRACTION REÇUE | 1,1 | receipt_item.line_id |
| R32 | LOT | 0,N | identifie le lot reçu | FRACTION REÇUE | 1,1 | receipt_item.lot_id |
| R33 | EMPLACEMENT | 0,N | rangement initial | FRACTION REÇUE | 1,1 | receipt_item.location_id |
| R34 | CLIENT PROPRIÉTAIRE | 0,N | passe une commande | COMMANDE | 1,1 | customer_order.owner_id |
| R35 | UTILISATEUR | 0,N | prépare une commande | COMMANDE | 0,1 | customer_order.preparer_id |
| R36 | COMMANDE | 0,N | détaille une commande | LIGNE DE COMMANDE | 1,1 | order_line.order_id |
| R37 | ARTICLE | 0,N | figure dans | LIGNE DE COMMANDE | 1,1 | order_line.article_id |
| R38 | LIGNE DE COMMANDE | 0,N | est servie par | PRÉLÈVEMENT | 1,1 | pick.order_line_id |
| R39 | FRACTION REÇUE | 0,N | alimente le prélèvement | PRÉLÈVEMENT | 1,1 | pick.receipt_item_id |
| R40 | EMPLACEMENT | 0,N | est le lieu du prélèvement | PRÉLÈVEMENT | 1,1 | pick.location_id |
| R41 | COMMANDE | 0,N | est conditionnée en | COLIS / PALETTE | 1,1 | package.order_id |
| R42 | COMMANDE | 0,1 | donne lieu à | EXPÉDITION | 1,1 | shipment.order_id |
| R43 | PASSAGE CAMION | 0,N | emporte une expédition | EXPÉDITION | 1,1 | shipment.visit_id |
| R44 | UTILISATEUR | 0,N | confirme une expédition | EXPÉDITION | 1,1 | shipment.actor_id |
| R45 | FRACTION REÇUE | 0,N | fait l’objet de mouvements | MOUVEMENT DE STOCK | 1,1 | stock_movement.receipt_item_id |
| R46 | EMPLACEMENT | 0,N | est affecté par | MOUVEMENT DE STOCK | 1,1 | stock_movement.location_id |
| R47 | PRÉLÈVEMENT | 0,1 | produit une sortie | MOUVEMENT DE STOCK | 0,1 | stock_movement.pick_id |
| R48 | UTILISATEUR | 0,N | effectue un mouvement | MOUVEMENT DE STOCK | 1,1 | stock_movement.actor_id |
| R49 | RÉCEPTION | 0,N | porte une réserve générale | RÉSERVE | 0,1 | receipt_reserve.receipt_id |
| R50 | LIGNE DE RÉCEPTION | 0,N | porte une réserve de ligne | RÉSERVE | 0,1 | receipt_reserve.line_id |
| R51 | UTILISATEUR | 0,N | émet une réserve | RÉSERVE | 1,1 | receipt_reserve.actor_id |
| R52 | CHAUFFEUR | 0,N | est habilité : Date de fin de validité | HABILITATION | 0,N | driver_qualification.driver_id, driver_qualification.qualification_id |
| R53 | VÉHICULE | 0,N | est équipé de | ÉQUIPEMENT | 0,N | vehicle_equipment.vehicle_id, vehicle_equipment.equipment_id |
| R54 | QUAI | 0,N | dispose de | ÉQUIPEMENT | 0,N | dock_equipment.dock_id, dock_equipment.equipment_id |
| R55 | COLIS / PALETTE | 0,N | contient une quantité : Quantité affectée | PRÉLÈVEMENT | 0,N | package_pick.package_id, package_pick.pick_id |
| R56 | QUAI | 0,N | accepte le type | TYPE DE VÉHICULE | 0,N | dock_vehicle_type.dock_id, dock_vehicle_type.vehicle_type |
| R57 | TYPE DE VÉHICULE | 0,N | caractérise le véhicule | VÉHICULE | 1,1 | vehicle.type |

## Unicités complémentaires

Les id identifient les entités. Les unicités ci-dessous complètent le diagramme ; une association N:N est identifiée par le couple de ses participants. Les identifiants id des tables de jointure sont des choix techniques.

| Table | Attributs uniques hors id |
|---|---|
| user_account | email |
| carrier | code |
| carrier_contract | reference |
| qualification | code |
| driver | license_number |
| driver_qualification | driver_id + qualification_id |
| equipment | code |
| vehicle | plate |
| vehicle_equipment | vehicle_id + equipment_id |
| dock | code |
| dock_equipment | dock_id + equipment_id |
| dock_vehicle_type | dock_id + vehicle_type |
| appointment | reference |
| truck_visit | reference ; appointment_id |
| visit_event | visit_id + state |
| owner | code |
| supplier | code |
| article | owner_id + sku |
| zone | code |
| aisle | code |
| rack | code |
| rack_level | code |
| location | code |
| lot | article_id + code |
| supplier_notice | reference |
| notice_line | notice_id + article_id |
| receipt | reference |
| receipt_line | receipt_id + notice_line_id |
| receipt_item | pallet_code |
| customer_order | reference |
| order_line | order_id + article_id |
| package | code |
| package_pick | package_id + pick_id |
| shipment | order_id ; reference |
| stock_movement | pick_id |

Les unicités sur appointment_id et pick_id sont conditionnelles lorsque la valeur est NULL : elles ne sont pas des identifiants totaux. shipment.order_id est obligatoire et unique.

## Périmètre technique

audit_log et site_lock restent dans le MLD : journal d’audit générique et verrou de sérialisation. Les événements de passage et mouvements de stock restent dans le MCD car ce sont des faits métier demandés. Le rôle utilisateur et le statut sont des domaines finis ; aucune table ROLE n’est inventée. TYPE DE VÉHICULE est réalisé par les ENUM vehicle.type et dock_vehicle_type.vehicle_type, sans table supplémentaire.
