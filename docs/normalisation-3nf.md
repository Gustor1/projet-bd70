# Normalisation et dépendances fonctionnelles

Les relations représentent les faits décrits dans le contrat de conception. Pour chaque table, toutes les valeurs sont atomiques (1NF). Les associations N:N portent des unicités composées ; leurs attributs dépendent de la totalité de ces clés (2NF). Les attributs descriptifs du parent restent dans le parent : aucun nom de transporteur, d’article ou de propriétaire n’est recopié dans les lignes (3NF). Une PK artificielle ne constitue pas à elle seule cette justification.

Les clés UNIQUE contenant NULL sont des unicités conditionnelles, pas des clés candidates totales (appointment_id d’un passage, pick_id d’un mouvement). Le passage conserve les faits réels distincts du planning ; ses copies initiales constituent un instantané de l’affectation réelle. `status` est une projection opérationnelle conservée, vérifiée par les transitions ; durées, totaux et soldes ne sont pas stockés. L’attendu local d’une ligne de réception est l’allocation de la livraison partielle, et non la copie de l’attendu total de l’avis.


## user_account
Clés candidates : (id), (email). DF : chaque clé candidate → email, name, password_hash, role, active, created_at.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## carrier
Clés candidates : (id), (code). DF : chaque clé candidate → code, name, address, phone, email.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## carrier_contact
Clés candidates : (id). DF : chaque clé candidate → carrier_id, name, phone, email.
Les déterminants externes (carrier_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## carrier_contract
Clés candidates : (id), (reference). DF : chaque clé candidate → carrier_id, reference, starts_on, ends_on, terms.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (carrier_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## qualification
Clés candidates : (id), (code). DF : chaque clé candidate → code, name.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## driver
Clés candidates : (id), (license_number). DF : chaque clé candidate → carrier_id, name, phone, license_number.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (carrier_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## driver_qualification
Clés candidates : (id), (driver_id, qualification_id). DF : chaque clé candidate → driver_id, qualification_id, expires_on.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (driver_id, qualification_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## equipment
Clés candidates : (id), (code). DF : chaque clé candidate → code, name.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## vehicle
Clés candidates : (id), (plate). DF : chaque clé candidate → carrier_id, plate, type, max_kg, max_pallets.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (carrier_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## vehicle_equipment
Clés candidates : (id), (vehicle_id, equipment_id). DF : chaque clé candidate → vehicle_id, equipment_id.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (vehicle_id, equipment_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## dock
Clés candidates : (id), (code). DF : chaque clé candidate → code, name, type.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## dock_equipment
Clés candidates : (id), (dock_id, equipment_id). DF : chaque clé candidate → dock_id, equipment_id.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (dock_id, equipment_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## dock_vehicle_type
Clés candidates : (id), (dock_id, vehicle_type). DF : chaque clé candidate → dock_id, vehicle_type.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (dock_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## dock_downtime
Clés candidates : (id). DF : chaque clé candidate → dock_id, starts_at, ends_at, reason.
Les déterminants externes (dock_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## appointment
Clés candidates : (id), (reference). DF : chaque clé candidate → reference, dock_id, driver_id, vehicle_id, trailer_id, operation, starts_at, ends_at, status.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (dock_id, driver_id, vehicle_id, trailer_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## truck_visit
Clés candidates : (id), (reference). DF : chaque clé candidate → reference, appointment_id, driver_id, vehicle_id, trailer_id, operation, dock_id, status, document_note.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (appointment_id, driver_id, vehicle_id, trailer_id, dock_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## visit_event
Clés candidates : (id), (visit_id, state). DF : chaque clé candidate → visit_id, state, happened_at, actor_id.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (visit_id, actor_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## owner
Clés candidates : (id), (code). DF : chaque clé candidate → code, name, address, email.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## supplier
Clés candidates : (id), (code). DF : chaque clé candidate → code, name, address, phone.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## article
Clés candidates : (id), (owner_id, sku). DF : chaque clé candidate → owner_id, sku, name, storage, packaging, width_m, depth_m, height_m, unit_kg, units_per_pallet.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (owner_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## zone
Clés candidates : (id), (code). DF : chaque clé candidate → code, name, storage.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## aisle
Clés candidates : (id), (code). DF : chaque clé candidate → zone_id, code.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (zone_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## rack
Clés candidates : (id), (code). DF : chaque clé candidate → aisle_id, code.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (aisle_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## rack_level
Clés candidates : (id), (code). DF : chaque clé candidate → rack_id, code.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (rack_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## location
Clés candidates : (id), (code). DF : chaque clé candidate → level_id, code, width_m, depth_m, height_m, max_kg, max_pallets.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (level_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## lot
Clés candidates : (id), (article_id, code). DF : chaque clé candidate → article_id, code, expires_on, blocked, block_reason.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (article_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## supplier_notice
Clés candidates : (id), (reference). DF : chaque clé candidate → reference, supplier_id, expected_on.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (supplier_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## notice_line
Clés candidates : (id), (notice_id, article_id). DF : chaque clé candidate → notice_id, article_id, expected_qty.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (notice_id, article_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## receipt
Clés candidates : (id), (reference). DF : chaque clé candidate → reference, notice_id, visit_id, status, validated_at.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (notice_id, visit_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## receipt_line
Clés candidates : (id), (receipt_id, notice_line_id). DF : chaque clé candidate → receipt_id, notice_line_id, expected_qty.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (receipt_id, notice_line_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## receipt_item
Clés candidates : (id), (pallet_code). DF : chaque clé candidate → line_id, lot_id, pallet_code, accepted_qty, damaged_qty, pallet_state, reservation, location_id.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (line_id, lot_id, location_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## customer_order
Clés candidates : (id), (reference). DF : chaque clé candidate → reference, owner_id, destination, desired_on, status, preparer_id, picking_at, ready_at.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (owner_id, preparer_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## order_line
Clés candidates : (id), (order_id, article_id). DF : chaque clé candidate → order_id, article_id, qty.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (order_id, article_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## pick
Clés candidates : (id). DF : chaque clé candidate → order_line_id, receipt_item_id, location_id, qty, status, confirmed_at.
Les déterminants externes (order_line_id, receipt_item_id, location_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## package
Clés candidates : (id), (code). DF : chaque clé candidate → order_id, code, type.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (order_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## package_pick
Clés candidates : (id), (pick_id). DF : chaque clé candidate → package_id, pick_id.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (package_id, pick_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## shipment
Clés candidates : (id), (order_id), (reference). DF : chaque clé candidate → order_id, visit_id, reference, shipped_at, actor_id.
La clé naturelle composée éventuelle identifie une occurrence de relation ; aucun libellé du parent ne dépend d’une seule de ses composantes dans cette table.
Les déterminants externes (order_id, visit_id, actor_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## stock_movement
Clés candidates : (id). DF : chaque clé candidate → operation_ref, receipt_item_id, location_id, delta, kind, pick_id, reason, actor_id, created_at.
Les déterminants externes (receipt_item_id, location_id, pick_id, actor_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## audit_log
Clés candidates : (id). DF : chaque clé candidate → entity, entity_id, operation, actor_id, happened_at, details.
Les déterminants externes (actor_id) ne déterminent ici que des liens, pas des attributs descriptifs recopiés. Les libellés sont obtenus par jointure.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.

## site_lock
Clés candidates : (id). DF : chaque clé candidate → label.
Sous ces règles métier, aucune DF non triviale entre attributs non clés n’est retenue ; 3NF. Les calculs dérivés sont dans les vues.