# Contrat de conception avant implémentation

Références techniques consolidées : [index des modèles](modeles-reference.md). Le recueil PDF actualisé réunit le diagramme de cas d’utilisation V2, le MCD Chen V2 et le schéma relationnel complet.

Le modèle comporte cinq sous-domaines reliés : personnel/référentiels, quais/passages, avis/réception, rangement/mouvements, commandes/prélèvement/expédition. Les noms SQL sont anglais pour éviter les identifiants accentués ; l'interface utilise les termes français.

Associations N:N : chauffeur/habilitation avec date de validité ; quai/équipement ; véhicule/équipement ; quai/type de véhicule ; colis/prélèvement avec quantité. Les contacts/contrats restent des enfants 1:N de transporteur. Rôle unique par utilisateur, choix explicite adapté aux cinq profils.

Chaîne de provenance : fournisseur → avis → ligne d'avis → ligne de réception → fraction de réception → lot/article/propriétaire ; fraction → mouvement → emplacement → niveau → rack → allée → zone ; fraction → prélèvement → ligne de commande → commande → expédition → passage sortant → véhicule/transporteur. Une réception peut recevoir plusieurs fractions d'un lot, et un même lot peut provenir de plusieurs réceptions.

Le stock est une vue agrégée sur un journal de mouvements, jamais un solde éditable. Les prélèvements ouverts sont déduits de cette somme pour obtenir le disponible. Les quantités endommagées sont conservées à la réception mais n'entrent pas dans le journal disponible. Une fraction est identifiée par un code de palette interne unique, y compris pour un colis non palettisé.

PK techniques entières, clés métier uniques et FK restrictives par défaut. Suppression en cascade limitée aux associations et enfants de brouillons explicitement supprimés par service. Dates optionnelles seulement lorsque l'événement n'a pas eu lieu ; DLC facultative. Quantités entières positives, poids/dimensions DECIMAL positifs. Toutes les tables métier InnoDB, utf8mb4. Les tableaux exhaustifs des clés, attributs et DF sont dérivés du schéma exécuté et relus.

Les mutations prennent un verrou sur `site_lock` dans la transaction PHP ; il protège aussi les agrégats (capacité et disponible) contre les écritures concurrentes. Procédures de lecture/verrouillage sans COMMIT ; triggers d'audit et d'immuabilité. Le compte SQL applicatif n'a aucun droit DDL ni droit de mutation du journal d'audit ou d'UPDATE/DELETE sur les mouvements.


## Extensions finalisées

42 tables installées (dont appointment_archive, historique des rendez-vous). receipt_reserve porte un lien exclusif vers une réception ou une ligne (CHECK XOR). package_pick porte une quantité et l’unicité (package_id,pick_id), ce qui permet plusieurs colis par prélèvement. Les avis ont une clôture motivée ; les commandes une note de reprise. Les snapshots JSON du journal technique sont une dénormalisation volontaire, exclue de l’argumentation 3NF des relations métier.

v_visit joint les événements uniques (passage, état). v_location_usage agrège directement les quantités physiques et caractéristiques d’articles, sans utiliser les réservations et descriptions de v_stock. Ces vues ne stockent aucun solde supplémentaire.

Convention des MCD : la cardinalité placée près d’une entité indique le nombre de participations de cette entité à l’association (exemple : un transporteur emploie 0..N chauffeurs ; un chauffeur dépend de 1 transporteur). Les MLD utilisent la multiplicité de l’extrémité de relation.
