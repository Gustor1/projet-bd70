# Matrice des opérations et droits

Vérification du 3 novembre 2026 après correction du use case : A = administrateur technique ; R = responsable ; G = accueil ; M = magasinier ; T = transporteur. A gère les comptes et consulte le journal, sans droit métier. R gère les référentiels, le planning, les commandes et l’affectation, sans exécuter la préparation. M ne peut exécuter ou conditionner que ses commandes affectées. G suit les passages sauf début/fin à quai, réservés à M. T n’accède qu’aux rendez-vous et ressources de sa société via son espace dédié. Les requêtes directes et les changements de parent sont vérifiés côté serveur.

| Entité | Profils | Opérations et restrictions réelles |
|---|---|---|
| `user_account` | A | Créer, activer, éditer profil/coordonnées, réinitialiser le mot de passe ; désactiver. Pas de suppression ; conserver son propre accès administrateur. |
| `carrier` | R | Créer/éditer coordonnées et code ; supprimer seulement sans référence. |
| `carrier_contact` | R | Créer/éditer contact et rattachement ; supprimer si aucune référence. |
| `carrier_contract` | R | Créer/éditer référence, dates, conditions et rattachement ; supprimer si aucune référence. |
| `qualification` | R | Créer/éditer code et nom ; supprimer sans habilitation liée. |
| `driver` | R | CRUD sans usage ; après rendez-vous/passage, nom et téléphone uniquement. Suppression référencée interdite. |
| `driver_qualification` | R | CRUD avant usage du chauffeur ; après usage, prolonger la validité sans la raccourcir, ni déplacer le couple. Suppression interdite. |
| `equipment` | R | Créer/éditer code et nom ; supprimer sans association. |
| `vehicle` | R | CRUD avant usage ; immatriculation, type, capacités et transporteur figés après rendez-vous/passage (véhicule principal ou remorque). |
| `vehicle_equipment` | R | Créer une association ; modifier/supprimer avant usage du véhicule, y compris remorque. Après usage, couple protégé. |
| `dock` | R | CRUD avant usage ; après rendez-vous/passage, nom seul modifiable. Suppression référencée interdite. |
| `dock_equipment` | R | Créer ; modifier/supprimer avant usage du quai. Après rendez-vous/passage, association protégée. |
| `dock_vehicle_type` | R | Créer ; modifier/supprimer avant usage du quai. Après rendez-vous/passage, compatibilité protégée. |
| `dock_downtime` | R | Créer/éditer période et motif sous contrôle de disponibilité ; supprimer une indisponibilité. Pas d’annulation historisée dédiée. |
| `appointment` | R | Créer/déplacer/modifier seulement actif et sans passage ; contrôler ressources et chevauchement. Annuler avant arrivée ; aucune suppression. |
| `truck_visit` | G,M | Arrivée et transitions sur écran Camions, avec contrôle documentaire et affectation du quai. Catalogue en lecture seule ; ni édition libre ni suppression. |
| `visit_event` | G,M | Ajout par arrivée/transition uniquement ; ni édition ni suppression. Un état par passage ; consulter la chronologie. |
| `owner` | R | Créer/éditer coordonnées et code ; suppression sans article/commande lié. |
| `supplier` | R | Créer/éditer coordonnées et code ; suppression sans avis lié. |
| `article` | R | CRUD avant existence d’un lot ; ensuite désignation seule modifiable. Propriétaire, SKU, stockage, conditionnement, dimensions et poids protégés. |
| `zone` | R | CRUD avant mouvements dans la sous-structure ; après usage, nom seul modifiable. Suppression sans allée liée. |
| `aisle` | R | CRUD sans mouvement dans sa sous-structure ; sinon code/rattachement protégés. Suppression sans rack lié. |
| `rack` | R | CRUD sans mouvement dans sa sous-structure ; sinon code/rattachement protégés. Suppression sans niveau lié. |
| `rack_level` | R | CRUD sans mouvement dans sa sous-structure ; sinon code/rattachement protégés. Suppression sans emplacement lié. |
| `location` | R | CRUD avant mouvement ; après usage, identité, rattachement, dimensions et capacités protégés. Suppression sans référence. |
| `lot` | M | Créer/éditer/supprimer sans fraction reçue ; après réception, seul blocage/déblocage motivé reste modifiable. Identité/DLC protégées. |
| `supplier_notice` | M | Créer/éditer/supprimer avant réception et avant clôture, en retirant d’abord ses lignes. Dès réception, édition interdite. Clôture motivée sans réception brouillon ; historique conservé. |
| `notice_line` | M | Créer sur avis ouvert ; éditer/supprimer avant réception de l’avis et clôture. Références de réception protégées par FK. |
| `receipt` | M | Créer/éditer un brouillon sur avis ouvert ; supprimer après retrait des enfants. Validation unique ; ensuite ajustement de stock motivé, jamais effacement de la réception. |
| `receipt_line` | M | Créer/éditer/supprimer sur réception brouillon et avis ouvert ; attendu local ajustable. Retirer fractions et réserves liées avant suppression ; validé protégé. |
| `receipt_item` | M | Créer/éditer/supprimer une fraction en brouillon et avis ouvert ; contrôler cohérence article/lot. Validée immuable ; transfert ou ajustement motivé. |
| `customer_order` | R | Créer/éditer/supprimer en brouillon sans enfants. Dès lancement, reprise motivée en brouillon ou annulation avant expédition. Expédiée immuable. |
| `order_line` | R | Créer/éditer/supprimer en brouillon, même propriétaire que l’article. Rattachement non déplaçable. Les prélèvements historiques empêchent la suppression ; corriger quantité/article après reprise selon contraintes. |
| `pick` | M | Généré par préparation FEFO ; confirmation par préparateur affecté (ou A/R). Annulé par reprise/annulation ; expédié au chargement. Aucun CRUD libre. |
| `package` | M | Créer/éditer/supprimer quand commande prête uniquement ; retirer contenu avant suppression. Reprise retire les colis et leurs allocations ; expédition les fige. |
| `package_pick` | M | Créer/éditer/supprimer quand commande prête ; quantité positive et cumul borné, même commande et prélèvement confirmé. Reprise supprime allocations ; expédition les fige. |
| `shipment` | M | Créée uniquement par chargement/expédition intégrale ; ni édition, ni suppression, ni nouvelle expédition de la même commande. |
| `stock_movement` | M | Créé par validation, transfert, ajustement ou expédition ; ni édition ni suppression. Correction par nouveau mouvement motivé sous contrôle de stock. |
| `audit_log` | A en lecture | Produit par triggers ; aucun ajout manuel via interface, aucune édition/suppression applicative. |
| `receipt_reserve` | M | Ajout motivé par écran réception, même après validation ; parent réception OU ligne. Réserve immuable, correction par réserve complémentaire. |
| `site_lock` | Technique | Pas de rubrique ni opération utilisateur ; ligne de verrou transactionnel, non administrable par CRUD. |

## Correction et explication dans l’interface

Les listes masquent Modifier lorsque l’état interdit toute édition et expliquent la reprise, le mouvement ou la conservation de l’historique. Supprimer est masqué en présence de références, pour les associations utilisées ou les faits protégés. Un accès direct à edit sur un fait figé affiche la raison sans formulaire. Pour les fiches partiellement éditables, les champs structurels sont désactivés et les champs descriptifs autorisés restent disponibles ; les contrôles de structure restent serveur. Les valeurs nouvelles (créneau, capacité, quantité, propriétaire) sont nécessairement revérifiées à la soumission.

Une fiche brouillon avec enfants n’est pas effacée en cascade : retirer d’abord les enfants inutilisés. Une réserve append-only peut empêcher la suppression d’un brouillon ; conserver alors le dossier, corriger ses fractions et compléter la réserve. Une commande reprise conserve les prélèvements annulés : modifier les lignes existantes reste possible, leur effacement peut être bloqué par ces faits historiques. Les restrictions ne signifient pas que l’utilisateur doit intervenir en SQL.

Le responsable gère les commandes et l’affectation ; le magasinier affecté confirme les prélèvements, conditionne et expédie. Les contrôles de propriété couvrent les commandes, colis et allocations. Le modèle corrigé après retour du professeur est désormais la référence des droits livrés.

Transporteur : création/modification/annulation de ses rendez-vous uniquement ; aucune suppression d’historique ni accès au catalogue interne. Toute affectation à une autre société est refusée.
