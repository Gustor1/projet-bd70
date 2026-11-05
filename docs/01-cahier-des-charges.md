# Cahier des charges

## Contexte et objectif
Un entrepôt reçoit des camions, contrôle leurs documents, réceptionne et range les marchandises de plusieurs propriétaires puis prépare et expédie les commandes. Le système doit conserver la provenance de chaque quantité et fournir des indicateurs de pilotage.

## Sources et périmètre
S est le sujet A26 dans document projet/A26_Site_Logistique.pdf. E est la grille DOCX fournie dans le même dossier. Les supports de cours ont guidé la conception. Le sujet prime sur leurs exemples. La grille autorise un langage approprié et ne donne aucune pondération.

F01 : inscription, authentification, quatre rôles. F02 : transporteurs, contacts, contrats, chauffeurs, habilitations, véhicules. F03 : quais, équipements, compatibilités, indisponibilités, réservation sans chevauchement. F04 : étapes horodatées du passage avec ou sans rendez-vous. F05 : avis, réceptions multilots, palettes, avaries et réserves. F06 : structure physique, propriétaires, articles, stock et mouvements. F07 : commandes, FEFO, préparateur, colis/palettes, chargement, bon et lettre. F08 : traçabilité, indicateurs, états et graphiques.

L'interface inclut les compléments de F02/F07 afin de couvrir la grille E. Le minimum de S n'est pas considéré comme une dispense de recherche, statistiques ou gestion des référentiels.

## Acteurs
Administrateur technique : comptes et journal. Responsable : référentiels, planning, commandes, affectation et analyses. Accueil : arrivée, contrôle, appel à quai et départ. Magasinier : opérations à quai, réception, stock et préparation/expédition de ses commandes affectées. Transporteur : rendez-vous de sa société. Compte en attente : aucun accès métier.

## Exigences transversales
SQL préparé, validation serveur et contraintes relationnelles ; sessions renouvelées, CSRF, mots de passe hachés, droits contrôlés côté serveur ; transactions atomiques et contrôle concurrent ; journal automatique en base ; interface française responsive, ressources locales, valeurs métier à la place des clés internes ; filtres combinables, pagination, export respectant les droits.

## Acceptation
Installation sur base vierge, données cohérentes reproductibles, tests R01–R12 du plan, tests HTTP par rôle et concurrence, restauration dans une base distincte, huit requêtes mesurées (chauffe + dix passages), rapport fidèle et diagrammes éditables. Les résultats non exécutés restent identifiés.
