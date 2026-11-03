# Recette et preuves

La recette courante après correction du retour enseignant est dans [CORRECTIONS-RENDU-2026-11-03.md](CORRECTIONS-RENDU-2026-11-03.md). La précédente recette du **3 novembre 2026** est détaillée dans [FINALISATION-2026-11-03.md](FINALISATION-2026-11-03.md), avec commandes, empreintes et nouvelles preuves séparées. Les chiffres ci-dessous sont les relevés antérieurs, conservés comme historique ; ils ne valident pas de nouvelles modifications.

## Relevés antérieurs

Résultats exécutés par les scripts livrés. Bases mutantes dédiées ; démonstration riche consultée en lecture.

| Vérification | Réussis | Échecs | Preuve |
|---|---:|---:|---|
| Intégration métier/SQL | 64 | 0 | integration.json |
| Nouveaux cas métier | 23 | 0 | completion.json |
| Navigateur général | 71 | 0 | navigateur.json |
| Parcours complet | 31 | 0 | parcours.json |
| Parcours guidés ajoutés | 34 | 0 | completion-navigateur.json |
| Base riche en lecture | 16 | 0 | navigateur-riche.json |

Horloge Paris : 8 contrôles. Intégrité riche : 82 contrôles métier/FK. Migration : 42 contrôles des colonnes préexistantes et allocations.

Restauration : 41 tables comparées par comptes et checksums, 119 déclencheurs et 2 procédures. Une mutation vérifie l’audit dans la copie.

Installation propre : configuration et compte SQL neufs, trois refus de booléens invalides, CRUD d’une relation inutilisée et huit routes authentifiées.

Les 64 assertions initiales incluent quatre courses entre deux connexions, la conservation du stock, les rollbacks et les oracles des indicateurs. Les 23 nouveaux cas couvrent réserves, restes, clôtures, ressources, modifications permises, reprise et colis. Les contrôles mobiles sont effectués dans Edge à 390 px, pas sur appareil physique.

Reproduction : installer une base neuve, charger scripts/seed.php. integration.php utilise BD70_TEST_DATABASE ; completion.php utilise BD70_DATABASE. Les tests fixent le 22/10/2026 à midi ; le serveur navigateur dédié doit recevoir BD70_NOW=2026-10-22 12:00:00 et une base bd70_test*. Ne jamais figer la démonstration.
