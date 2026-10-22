# Suivi du projet BD70

Réalisation locale du 22 octobre 2026. Originaux et plan préservés. Dépôt initial sans commit ni code ; quatre sources lues, SmartArt inclus. Sources et résultats réels priment sur les recommandations du plan.

| Lot | État | Livrables et tests de sortie |
|---|---|---|
| 0 Inventaire | validé | Versions, outils XAMPP existants, instance isolée port 3307 ; exclusions/configuration, sources extraites |
| 1 Analyse | validé | Cahier des charges, dix cas, UML DOT/SVG, hypothèses et droits |
| 2 Modèle | validé | MCD/MLD distincts, 40 tables, dictionnaire, DF et 3NF, matrice CRUD, recueil vectoriel |
| 3 Base | validé | Installation vierge, CHECK/PK/FK/UNIQUE, deux procédures, 116 triggers, privilèges limités |
| 4 Données | validé | Démo graine 70 et volume séparé : 10 003 passages, 22 011 mouvements, rapprochements sans anomalie |
| 5 Socle web | validé | Connexion/inscription/activation, quatre profils, 39 rubriques, CRUD et sécurité HTTP |
| 6 Quais/camions | validé | Planning/annulation/modification, chronologie, R01–R04 et deux courses SQL |
| 7 Réceptions/stock | validé | Réception multilots/partielle, dommages, capacité et transferts, R05–R09/R12 |
| 8 Préparation/expédition | validé | FEFO, affectation, colis, chargement, documents, double sortie refusée et trace paginée |
| 9 Recherches/restitution | validé | Filtres, tri, pagination, sept indicateurs, graphiques, CSV et états |
| 10 Recette | validé | 64 tests métier, 71 contrôles navigateur, 31 étapes formulaires, huit requêtes mesurées, restauration et copie propre |
| 11 Remise | validé | Rapport éditable et PDF 18 pages, diagrammes vectoriels, README, recette, démonstration et limites |

## État de reprise
Application : http://127.0.0.1:8070 ; configuration locale de ce poste : bd70_demo_final. Lanceur : scripts/start.ps1. Serveur secondaire 8071 réservé à la recette UI ; les tests d’intégrité emploient bd70_test_remise. Le jeu de performance est dans bd70_perf. Les copies de restauration restent distinctes.
Les bases de test précédentes et sauvegardes se trouvent uniquement dans l’instance isolée/.local, ne sont pas publiées. Aucun reset/clean du dépôt ni déploiement public. À la fin de la réalisation initiale, aucun commit n’avait encore été poussé. Les scripts d’installation refusent les bases non vides.
Prochaine action humaine : compléter les noms, contributions et modalités de remise puis répéter la démonstration. Pour une nouvelle recette, installer un nouveau nom bd70_test*, charger seed et suivre README. Aucun lot fonctionnel obligatoire reporté. Les limites sont des choix explicites ou bornes de validation locale, consignés dans limites.md.

## Contrôle de reprise du 23 octobre 2026 (Asia/Shanghai)

Après l'interruption, les serveurs locaux étaient arrêtés. Le lanceur a redémarré l'instance MariaDB du projet et PHP sans réinstaller ni recharger les données. La connexion administrateur et huit pages authentifiées ont été revérifiées sans erreur HTTP ou alerte applicative. Les deux PDF de livraison sont présents. Les résultats antérieurs des suites métier, navigateur, parcours, performances et restauration restent conservés ; ces suites complètes n'ont pas été relancées à cette reprise. Preuve supplémentaire : `livrables/preuves/reprise-livraison.json`.

## Versionnement GitHub demandé le 23 octobre 2026

Dépôt distant : https://github.com/Gustor1/projet-bd70, branche `main`. Le périmètre de publication comprend le code, le SQL, les scripts, les tests, les supports fournis, la documentation et les livrables vérifiés. La configuration privée `config/local.php`, le dossier `.local/`, les bases, sessions et sauvegardes locales restent exclus par `.gitignore`. L'historique Git et la référence distante permettent de vérifier le commit effectivement publié.
