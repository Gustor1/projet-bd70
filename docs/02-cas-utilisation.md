# Cas d'utilisation

Tous les cas métier présupposent une session active et un rôle autorisé. Un refus ne modifie aucune donnée. Le diagramme UML est dans `diagrammes/cas-utilisation.svg`.

| Cas | Objectif / acteur | Préconditions | Déroulement nominal | Variantes et erreurs | Postconditions et données |
|---|---|---|---|---|---|
| UC01 | Accéder au système / personnel | Compte actif, ou inscription | Inscription en attente ; activation admin ; connexion ; déconnexion | Doublon email, mot de passe incorrect, tentative de rôle privilégié | Session renouvelée ; user_account |
| UC02 | Maintenir les référentiels / admin, responsable | Données métier valides | Ajouter, sélectionner des références lisibles, modifier, supprimer une fiche inutilisée | FK utilisée, structure figée, doublon, valeur négative | Référentiel cohérent et journal |
| UC03 | Réserver/déplacer/annuler / accueil, responsable | Quai et véhicule compatibles | Choisir date et quai, vérifier intervalle, enregistrer sous verrou | Deux sessions : un seul créneau admis ; hors service ; déplacement en conflit ; créneaux adjacents autorisés | appointment et audit atomiques |
| UC04 | Accueillir et servir un camion / accueil | Chauffeur/véhicule cohérents | Arrivée, contrôle documentaire, parking, appel à quai, début, fin, départ | Sans rendez-vous ; contrôle refusé ; quai occupé ; transition arrière interdite | truck_visit, visit_event ; durées calculables |
| UC05 | Réceptionner avec écart / magasinier | Avis et passage entrant en opération | Créer réception, lignes attendues, fractions par lot/palette ; renseigner avaries/réserve ; proposer emplacement ; valider | Partiel, excédent, dommage ; second clic ; capacité insuffisante sur deuxième ligne : rollback total | receipt, receipt_line, receipt_item et stock_movement ; validation unique |
| UC06 | Transférer/corriger / magasinier | Stock libre suffisant | Sélectionner fraction et source, destination compatible, quantité ; enregistrer deux mouvements liés | Stock réservé, zone inadaptée, capacité ; concurrence ; ajustement négatif non disponible | Conservation de quantité, motif et acteur |
| UC07 | Préparer / responsable, magasinier | Commande brouillon avec lignes | Affecter préparateur, réserver FEFO, afficher liste, confirmer les prélèvements | Lot bloqué/périmé, stock insuffisant : aucune réservation partielle ; annulation libère le stock | pick et customer_order, horodatages de productivité |
| UC08 | Expédier / magasinier | Tout prélevé, colis créés, passage sortant en opération | Constituer colis/palettes, charger, confirmer, imprimer bon et lettre | Capacité camion, colis manquant, deuxième clic, lot devenu bloqué : refus | shipment, package, stock_movement ; liens vers lot et camion |
| UC09 | Tracer / personnel autorisé | Lot existant | Choisir lot, afficher réceptions, déplacements, commandes et expédition | Lot réparti sur deux emplacements et deux commandes | Lecture sans mutation, provenance au niveau de la fraction |
| UC10 | Piloter / responsable, admin | Période valide | Combiner filtres, trier, paginer, consulter graphiques, imprimer/exporter | Aucun résultat, dénominateur nul, export interdit | Résultats filtrés, unités et exclusions explicites |

Le lien « inclut » du diagramme représente un traitement systématique (contrôler les droits ou la disponibilité) ; l'authentification est une précondition de session, pas une connexion répétée à chaque action.
