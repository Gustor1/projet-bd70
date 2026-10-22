# Matrice de conformité

S = sujet A26 (PDF), E = grille d’évaluation (DOCX). C = cours conception A25, W = cours web A25. Aucune pondération inventée. Toutes les fonctions ci-dessous possèdent une interface réelle ; seul le jeu volumétrique est une simulation SQL.

| Exigence | Cas | Tables principales | Traitement / écran | Preuve | Rapport | État |
|---|---|---|---|---|---|---|
| F01 | UC01 | user_account | Auth, utilisateurs | Rôles, inscription, CSRF, HTTP direct | 7 | réalisé et testé |
| F02 | UC02 | carrier, driver, vehicle, équipements et associations | Catalog / référentiels | CRUD SQL + navigateur, 39 rubriques visitées | 7 | réalisé et testé |
| F03 | UC03 | dock, appointment, dock_downtime | Planning / Warehouse | R01, R02, deux connexions | 8 | réalisé et testé |
| F04 | UC04 | truck_visit, visit_event | Poste de garde / transitions | R03, R04, parcours sans rendez-vous | 8 | réalisé et testé |
| F05 | UC05 | supplier_notice, notice_line, receipt, receipt_line, receipt_item | Réception et rangement | R05, R08, R12, avarie / manquant / excédent | 9 | réalisé et testé |
| F06 | UC06 | article, lot, structure, stock_movement | Stock, propositions, transfert et ajustement | R06–R09, concurrence capacité, filtres | 9 | réalisé et testé |
| F07 | UC07–08 | customer_order, order_line, pick, package, package_pick, shipment | Commandes, colis, expédition et documents | FEFO, R10, parcours 31 étapes, PDFs | 10 | réalisé et testé |
| F08 | UC09–10 | vues de stock, visites, écarts et procédures | Trace, tableaux, graphes, états et CSV | Oracles, filtres CSV et graphiques, HTTP | 10, 12–15 | réalisé et testé |

## Critères de E et livrables de S
| Critère | Réalisation et preuve |
|---|---|
| Identification des usages / UML | 10 cas textuels, diagramme avec acteurs, ellipses et frontière, sources DOT + SVG/PDF |
| MCD cohérent avec usages | MCD conceptuel distinct, complet et cinq vues de domaine |
| MLD cohérent avec MCD | 40 tables du moteur, PK/FK, unicités, nullabilité ; schéma SQL et exports |
| Clés, types, relations 1:N et N:N | Dictionnaire exhaustif ; associations équipements/habilitations/prélèvements |
| Erreurs, redondances et normalisation | DF et clés candidates par table ; stock/durées calculés, hypothèses expliquées |
| Qualité et quantité des informations | Référentiels utiles et jeu volumétrique contrôlé ; pas de quota artificiel |
| Ajout, édition, suppression de toutes les données | Formulaires sur fiches et brouillons ; historiques via corrections/annulations, matrice CRUD explicite |
| Contrôle des saisies | Validation serveur, contraintes, transactions et messages ; tests négatifs |
| Recherche multicritère | Période/transporteur/état, article/lot/zone/propriétaire, réception/fournisseur/écart |
| Tableaux et graphiques | Sept indicateurs définis, tableaux et barres issus des vues ; oracles |
| Génération d’états | Trois états CSV/imprimables et trois documents pédagogiques de sortie |
| Finition, menus, boutons, IDs masqués | Interface française, sélection des références, navigation et largeurs contrôlées |
| Plusieurs utilisateurs | Quatre profils, inscription contrôlée, sessions, droits URL/POST et quatre courses SQL |
| Rapport et forme | 18 pages, sommaire, introduction, conclusion ; objectif/travail/conclusion par paire de fonctions, sources éditables ; auteurs à compléter |
| Captures, grammaire, ergonomie | Captures réelles, contrôle des pages PDF et pages principales responsive ; limites explicites |
| Performances et optimisation S | Huit requêtes, chauffe + dix, EXPLAIN/volumes/paramètres ; comparaison index et observation écriture |
| Automatisation interne S | 116 déclencheurs et deux procédures ; audit et restauration testés |
| Reproductibilité | Installation sur base vierge puis copie sans configuration, huit routes authentifiées, sauvegarde restaurée |

## Points à compléter par les étudiants
Auteurs réels, répartition des contributions, échéance et modalités A26. Ces informations absentes ne sont jamais inventées. La liste des limites techniques et choix de portée est dans docs/limites.md.