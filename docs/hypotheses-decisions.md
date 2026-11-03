# Hypothèses et décisions

1. Un entrepôt, en France, horaires civils Europe/Paris. SQL DATETIME stocke les heures locales du site. Seules les heures locales inexistantes ou ambiguës d’une transition saisonnière sont refusées ; pas de conversion implicite depuis le fuseau du poste.
2. Quantités entières en unités de conditionnement d'article, kg et mètres pour les dimensions ; volume calculé. Capacité palettes en équivalents rationnels quantité/unités_par_palette, sans arrondi par opération. Pas de reconditionnement automatique.
3. Un article appartient à un client propriétaire ; son SKU est unique chez ce propriétaire. Un lot est identifié par (article, code fabricant). Le fournisseur n'est ni le propriétaire ni le transporteur.
4. Chaque réception peut recevoir plusieurs lots sur une ligne. Un lot peut être reçu plusieurs fois. Le stock conserve l'identité de chaque fraction de réception, même lorsqu'un lot est réparti entre emplacements. C'est le lien de provenance exact des sorties.
5. Réceptions partielles autorisées : la quantité attendue affectée à chaque livraison ne dépasse pas le reste de l'avis. Les excédents reçus sont autorisés et signalés. Les endommagés sont décrits avec réserve, sans entrée au stock disponible.
6. Stratégie FEFO : DLC croissante, DLC absente en dernier, puis date de réception et identifiant de fraction. Lots périmés ou bloqués exclus. Une préparation réserve intégralement la commande ; pas d'expédition partielle dans cette version. Annulation libère les réservations avant expédition.
7. Stock calculé exclusivement par somme des mouvements immuables ; prélèvements non expédiés réservés séparément. Débit effectué une seule fois lors du chargement confirmé. Correction de stock par ajustement motivé, jamais édition du journal.
8. Sérialisation des mutations métier par verrou transactionnel sur la ligne unique `site_lock`, puis verrou des ressources. Choix pédagogique conservateur : concurrence sûre, débit d'écriture limité ; à mesurer. PHP possède les transactions, les procédures ne COMMIT jamais.
9. Quai hors service prioritaire sur occupé, réservé, libre. Une indisponibilité chevauchant une réservation active ou une occupation est refusée ; l'opérateur doit déplacer/annuler d'abord les réservations. Actualisation du planning toutes les 30 secondes quand aucun formulaire n'est modifié, et bouton manuel.
10. Inscription publique = compte en attente. Activation et rôle par administrateur. Quatre rôles internes ; rôle transporteur optionnel non retenu. Aucune donnée réelle de personnel ou contrat.
11. Les fiches métier déjà utilisées (dimensions d'article, capacités et structures de stockage, véhicules/quais opérationnels) sont protégées des changements structurels pouvant invalider des faits. Brouillons supprimables ; opérations validées annulables/corrigeables par service dédié.
12. L'état courant est une projection des événements conservée pour piloter les transitions. Les dates et indicateurs restent calculés depuis les faits. Les documents imprimés sont pédagogiques, sans revendication de conformité réglementaire.
13. PHP/PDO, MariaDB/InnoDB testés uniquement dans les versions indiquées. Pas d'ORM, CDN, API payante ni service extérieur nécessaire. Serveur PHP local réservé à la démonstration sur boucle locale.

Sources : S (sujet A26), E (grille non pondérée), C et W (cours A25). Les modalités de groupe et de soutenance de C sont anciennes : 10 minutes préparées à titre indicatif ; date de remise inconnue.


## Décisions complémentaires après audit

- Réserves : lien exclusif réception OU ligne (CHECK XOR), motif, type, auteur et date. La réception d’une réserve de ligne est obtenue par jointure, sans duplication.
- Avis : le reste est l’attendu non encore alloué aux réceptions validées. Un manquant validé reste un écart de cette livraison ; il ne relance pas automatiquement une commande fournisseur. Une relivraison peut faire l’objet d’un nouvel avis. Clôture motivée sans brouillon en attente.
- Colis : (colis, prélèvement) détermine la quantité. Un prélèvement peut alimenter plusieurs colis. Couverture exacte avant chargement ; reprise motivée avant expédition.
- Référentiels : les téléphones/libellés autorisés restent éditables ; les habilitations peuvent être prolongées sans réduction historique. Les propriétés structurelles utilisées restent protégées.
- Audit : instantanés JSON avant/après sans password_hash, dénormalisation technique volontaire distincte des relations métier.
- Indicateurs : activité sur la période ; stock/remplissage/DLC à la date actuelle du site. Le jeu riche est fictif et généré, avec contrôles d’intégrité ; les parcours de formulaires utilisent un jeu distinct.

## Consolidation du 3 novembre 2026

Les sorties du journal de stock répètent volontairement fraction, emplacement et quantité du prélèvement. Cette redondance conditionnelle est contrôlée par le service d’expédition et vérifiée par l’intégrité ; elle ne justifie pas une revendication de 3NF stricte de cette projection. Voir normalisation-3nf.md. Les modèles de référence et la distinction avec la cible corrigée pour le professeur sont dans modeles-reference.md. Les avis clôturés restent protégés même sans réception ; une correction après clôture passe par un nouvel avis.
