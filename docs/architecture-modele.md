# Contrat de conception avant implémentation

Le modèle comporte cinq sous-domaines reliés : personnel/référentiels, quais/passages, avis/réception, rangement/mouvements, commandes/prélèvement/expédition. Les noms SQL sont anglais pour éviter les identifiants accentués ; l'interface utilise les termes français.

Associations N:N : chauffeur/habilitation avec date de validité ; quai/équipement ; véhicule/équipement ; quai/type de véhicule ; ligne de commande/fraction de réception via prélèvement quantifié. Les contacts/contrats restent des enfants 1:N de transporteur. Rôle unique par utilisateur, choix explicite adapté aux quatre profils.

Chaîne de provenance : fournisseur → avis → ligne d'avis → ligne de réception → fraction de réception → lot/article/propriétaire ; fraction → mouvement → emplacement → niveau → rack → allée → zone ; fraction → prélèvement → ligne de commande → commande → expédition → passage sortant → véhicule/transporteur. Une réception peut recevoir plusieurs fractions d'un lot, et un même lot peut provenir de plusieurs réceptions.

Le stock est une vue agrégée sur un journal de mouvements, jamais un solde éditable. Les prélèvements ouverts sont déduits de cette somme pour obtenir le disponible. Les quantités endommagées sont conservées à la réception mais n'entrent pas dans le journal disponible. Une fraction est identifiée par un code de palette interne unique, y compris pour un colis non palettisé.

PK techniques entières, clés métier uniques et FK restrictives par défaut. Suppression en cascade limitée aux associations et enfants de brouillons explicitement supprimés par service. Dates optionnelles seulement lorsque l'événement n'a pas eu lieu ; DLC facultative. Quantités entières positives, poids/dimensions DECIMAL positifs. Toutes les tables métier InnoDB, utf8mb4. Les tableaux exhaustifs des clés, attributs et DF seront dérivés du schéma stabilisé et relus.

Les mutations prennent un verrou sur `site_lock` dans la transaction PHP ; il protège aussi les agrégats (capacité et disponible) contre les écritures concurrentes. Procédures de lecture/verrouillage sans COMMIT ; triggers d'audit et d'immuabilité. Le compte SQL applicatif n'a aucun droit DDL ni droit de mutation du journal d'audit ou d'UPDATE/DELETE sur les mouvements.
