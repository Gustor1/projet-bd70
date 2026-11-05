# Correction après retour du professeur

Le PDF et le Draw.io corrigés contiennent cinq pages A3 : vue d'ensemble, passages des camions, commandes et préparation, expédition, traçabilité. Ouvrir le Draw.io dans diagrams.net ; chaque objet et connecteur est modifiable. Cette version constitue le use case du rendu final.

## Réponses aux remarques

1. Suppression des héritages entre métiers. Le responsable ne récupère plus les tâches du préparateur ; l'administrateur gère les comptes et les droits, sans accès métier implicite. Personnel désigne les fonctions de session communes. Les occurrences répétées d'un même acteur désignent le même rôle.
2. Ajout du Transporteur, limité aux demandes de rendez-vous de sa société (création, modification, annulation). Le portail transporteur correspondant est implémenté. Son accès suppose un compte autorisé.
3. Gestion des commandes et affectation/réaffectation des préparateurs réservées au responsable. Le préparateur exécute les commandes affectées, prélève les articles et constitue les colis. Le sujet regroupe magasinier/préparateur ; ces fonctions restent rassemblées dans la vue générale.
4. Les quatre cas signalés sont détaillés : arrivée et contrôles, appel à quai, opérations et départ ; commandes, affectation et préparation ; contrôles du chargement, confirmation et sortie de stock ; identification, provenance, mouvements et destinations d'un lot. Les inclusions sont orientées vers les traitements nécessaires. L'arrivée sans rendez-vous est une extension conditionnelle de l'enregistrement de l'arrivée. Les résultats vides sont possibles en traçabilité.

Le suivi du passage est un regroupement de cas réalisés à différents moments, et non un cas exécutant obligatoirement toutes les étapes en une seule action. La mise en attente, les retards, les écarts et autres variantes doivent être décrits dans les scénarios textuels. L'impression des documents reste une action indépendante, après expédition.

## Portée

Ce modèle est désormais la référence du logiciel corrigé. Les comptes et leurs rattachements, l’affectation des commandes, les étapes de passage et le portail transporteur sont contrôlés côté serveur. Voir docs/recette.md pour les preuves de cette mise en cohérence.

## Modification et reconstruction

Conserver une copie du Draw.io avant modification manuelle : `python scripts/build-usecase-correction-prof.py` reconstruit uniquement ce dossier. Le générateur utilise les primitives de `scripts/usecase_layout.py` sans en exécuter le programme principal.

Contrôles effectués : cinq pages PDF, objets Draw.io natifs, identifiants et extrémités des connecteurs, géométrie et largeur des textes, inspection des aperçus PDF. Le Draw.io n'a pas été ouvert dans l'éditeur lors de cette vérification. Aucun push GitHub n'est inclus.
