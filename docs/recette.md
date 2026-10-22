# Recette exécutée

Trois niveaux complémentaires : services et contraintes SQL ; pages/contrôles navigateur ; parcours métier complet par formulaires. Chaque résultat est produit par un script livré, sans capture inventée.

- Intégration : **64 réussis, 0 échec** (tests/integration.php).
- Navigateur Edge : **71 réussis, 0 échec** (tests/browser.cjs).
- Parcours complet : **31 étapes réussies**, 0 échec (tests/parcours.cjs sur serveur de test distinct).
- Copie propre : nouvelle configuration et nouveau compte SQL ; **8 routes authentifiées** vérifiées.
- Sauvegarde/restauration : 40 tables par comptes et checksums, 116 triggers et 2 procédures ; historisation réellement déclenchée dans la copie.

## Invariants et scénarios
| Règle | Preuve exécutée |
|---|---|
| R01 | Chevauchement, modification conflictuelle, adjacence, course à deux connexions |
| R02 | Type de quai, indisponibilité, fermeture sur réservation refusée ; froid/ADR dans seed et parcours |
| R03 | Course à deux affectations : un seul quai occupé |
| R04 | Transition impossible et horodatage rétrograde refusés |
| R05 | Rejeu de réception sans nouvelle entrée |
| R06 | Négatif refusé ; deux commandes tentent de réserver le même disponible |
| R07 | Transfert conserve la somme de la fraction |
| R08 | Zone incompatible et deux rangements concurrents en capacité limitée |
| R09 | Disponible bloqué/périmé nul ; avaries conservées hors stock |
| R10 | Deux commandes du même lot, liens vers camion, double expédition refusée |
| R11 | Journal automatique auteur/date/opération ; droits SQL et immuabilité |
| R12 | Réception annulée après première fraction, transfert sans débit partiel, préparation insuffisante sans réservation, rendez-vous modifié annulé |

## Résultats d’intégration détaillés
- F08 occupation 80 minutes
- F08 dénominateur trois quais 24h
- F08 attente par transporteur 17,5 et 15 min
- F08 immobilisation par transporteur 55 et 50 min
- F08 écarts 2/4 lignes, 5 manquant/excédent/avariées
- F08 productivité 150 unités/h
- Conservation démo 255 entrées - 50 sorties = 205
- F08 horizon DLC : 40 unités froid
- F08 périmés 10, sans DLC 15
- R09 aucun disponible bloqué/périmé
- F05 même lot reçu dans deux réceptions
- F07 même lot pour deux commandes
- F08 provenance vers deux sorties et camion
- UNIQUE clé métier transporteur
- FK chauffeur transporteur
- CHECK quantité négative
- R11 mouvement non éditable par compte applicatif
- R11 journal non effaçable
- DCL compte applicatif sans DDL
- R05 réception validée une fois
- R05 aucun double comptage
- R10 double expédition refusée
- CRUD modification et apostrophe
- CRUD suppression inutilisée
- CRUD référentiel utilisé protégé
- R11 trigger auteur opération date
- R11 aucun mot de passe journalisé
- R01 chevauchement refusé
- R01 créneaux adjacents autorisés
- R01 modification conflictuelle refusée
- R12 modification rollback conserve ancien créneau
- R02 type quai incompatible
- R01 durée nulle refusée
- R02 indisponibilité refusée
- R02 indisponibilité sur réservation refusée
- R01 deux connexions : une seule réservation
- R04 début avant contrôle refusé
- R03 deux connexions : une seule occupation
- R04 horodatage rétrograde refusé
- R08/R12 réception multi-fractions rollback
- R12 aucune entrée partielle ni validation
- R07 transfert conserve quantité
- R08 zone incompatible
- R12 transfert refusé sans débit
- R06 stock négatif refusé
- R08 capacité concurrente : une seule entrée de 4
- R08 capacité non dépassée
- R06 deux préparations : aucune sur-réservation
- R06 rapprochement réservé <= physique
- Annulation libère toutes les réservations
- R12 stock insuffisant refuse préparation
- R12 prélèvement sans état partiel
- FEFO choisit LOT-A stable
- F01 rôle admin accès traçabilité
- F01 rôle admin comptes protégés
- F01 rôle manager accès traçabilité
- F01 rôle manager comptes protégés
- F01 rôle gate accès traçabilité
- F01 rôle gate comptes protégés
- F01 rôle warehouse accès traçabilité
- F01 rôle warehouse comptes protégés
- F01 inscription sans élévation de privilèges
- F06 filtres stock combinés
- F06 aucun résultat

## Limites de la preuve
Les tests sont locaux et ne constituent pas une validation sur appareil physique, un autre moteur SQL ou une infrastructure publique. Les scénarios d’erreur sont dans une base dédiée ; la démo reste lisible. Les impressions ont été rendues en PDF ; le rapport et les captures sont revus visuellement. Les procédures de reprise sont dans le README.