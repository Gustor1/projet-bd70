# Cas d'utilisation

Références techniques consolidées : [index des modèles](modeles-reference.md). Le recueil PDF historique ne contient pas le MCD final.

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

Le diagramme de synthèse exprime les objectifs des rôles ; la session et les droits sont des préconditions. Les flèches triangulaires entre rôles expriment une généralisation.

## Variantes ajoutées après audit

- UC02 : téléphone d’un chauffeur utilisé et prolongation d’habilitation autorisés ; modification structurelle ou réduction du passé refusée.
- UC03 : remorque compatible et chauffeur/véhicule/remorque libres sur les autres quais.
- UC05 : ouverture depuis l’avis, lignes automatiques, ajustement de l’attendu partiel, lot et fraction depuis la fiche ; réserve de manquant total sans palette. Suivi du reste et clôture motivée sans brouillon.
- UC07 : confirmation par prélèvement, dernier prélèvement rendant la commande prête. Reprise motivée en brouillon avant expédition ; libération des réservations et suppression des allocations de colis, prélèvements annulés conservés.
- UC08 : un prélèvement réparti entre plusieurs colis par quantités ; somme exacte requise avant chargement. Documents avec totaux, poids et nombre de colis.
- UC09 : réserves générales et réserves des lignes du lot, en plus des réserves initiales sur palettes.
- UC10 : période vide sans erreur ; DLC explicitement rattachées à la date actuelle de Paris.
