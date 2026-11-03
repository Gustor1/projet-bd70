# Bilan de l’audit et de la réalisation

La version livrée couvre les huit domaines obligatoires du sujet dans l’interface. Le rôle transporteur externe est facultatif ; FEFO respecte l’alternative FIFO ou FEFO. Aucun autre manque obligatoire n’a été identifié dans la comparaison au sujet. Les limites de portée et de preuve restent décrites dans limites.md et recette.md.

## Traitement des constats

| Audit | Correction livrée | Preuve principale |
|---|---|---|
| D01 Rapports vides | État vide normal, sans exception de graphique | completion-navigateur.json |
| D02 Heure PHP/SQL | Référence Europe/Paris commune, été/hiver ; horloge fixe réservée aux tests | heure-paris.json |
| D03 Réserve sans réception physique | Réserve générale ou de ligne, auteur/date, même sans palette ; consultation dans réception/trace | completion.json |
| D04 Édition trop figée | Téléphone/libellés autorisés ; prolongation des habilitations ; structure protégée | completion.json |
| D05 Type de remorque | Compatibilité de la remorque avec le quai | completion.json |
| D06 Commande non modifiable | Reprise motivée en brouillon avant expédition, libération des réservations | completion.json |
| D07 Prélèvement indivisible | Affectations quantifiées dans plusieurs colis ; couverture exacte au chargement | completion-navigateur.json |
| D08 Dates de recette/DLC | Recette à date fixe ; DLC explicitement actuelles, indépendantes de la période d’activité | heure-paris.json ; parcours.json |
| D09 Avis non suivis | Attendu/alloué/reçu/reste, ouverture guidée, clôture motivée | completion.json |
| D10 Ressources en conflit | Chauffeur/véhicule/remorque contrôlés entre quais | completion.json |
| D11 Listes volumineuses | Réceptions brouillon paginées ; affinage des sélecteurs, filtres supplémentaires | navigateur-riche.json |
| D12 Audit trop générique | Instantanés JSON avant/après, sans hachage de mot de passe | completion.json |
| D13 Documentation | Rapport, auteurs, matrice, hypothèses, limites, modèles et preuves actualisés | livrables/rapport/ ; docs/ |
| D14 Petit jeu de données | 90 jours riches, SQL importable, contrôle d’intégrité et parcours réels | donnees-riches.json ; integrite-donnees.json |

La répartition individuelle des contributions n’a pas été communiquée : ce seul élément éditorial de D13 reste à renseigner. Les autres auteurs sont bien ELIOTT LE, SEMIH TASKIN et Thomas VUILLIN.

## Amélioration révélée par la recette riche

Le calcul du remplissage des zones dépassait le délai navigateur de 30 secondes avec 180 articles et 720 lots. La vue calcule désormais l’occupation directement depuis le stock physique, sans les jointures de réservation et de description inutiles. Les oracles métier et le navigateur riche ont été rejoués ; les résultats sont inchangés et les pages passent.

## État local

- Application : http://127.0.0.1:8070 ; base active bd70_demo_rich_final.
- Ancienne base bd70_demo_final conservée ; sauvegarde initiale externe et dump privé disponibles.
- Export pédagogique : sql/07_donnees_demo_riches.sql. Ne pas diffuser config/local.php ni .local/.
- Changements sur codex/completion-bd70 ; aucune publication distante effectuée.
- Les suggestions non obligatoires de l’audit (GPS, alertes dédiées, compte externe, etc.) ne sont pas toutes réalisées : elles ne constituent pas des exigences omises.
