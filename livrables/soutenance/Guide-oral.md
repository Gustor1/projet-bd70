# Transit — conducteur oral

**0:00–5:00 · Projection de Transit-diapo.html.** Onze diapositives : architecture (front et back), démarche et modèle, choix de conception, normalisation, automatisation, triggers, procédures et fonction, évènement, vues et calculs, fonctions PHP, optimisation. Chaque diapositive dit aussi où le mécanisme sert sur le site, pour anticiper les questions. **5:00–10:00 · Application dans le navigateur.** À 5:00, quitter le plein écran et basculer vers Transit. **10:00–20:00 · Questions du professeur.** Ouvrir [le diaporama](Transit-diapo.html), l’application et [le parcours illustré](Parcours-application.pdf) pour la répétition. [Transit.pdf](../../docs/soutenance/Transit.pdf) est la copie PDF vectorielle des onze diapositives.

## Première partie — paroles et diapositives dans le même ordre

Environ 530 mots, soit 4,1 minutes à 130 mots par minute. Parler posément, mais sans s’attarder : chaque diapositive tient en 15 à 35 secondes.

**1 · 0:00–0:30 · Transit — front et back.** « Transit gère un entrepôt : camions, réception, stock et expédition. Question de départ : à partir d’un lot, retrouver sa réception et le camion qui l’a emporté. Le front, c’est le navigateur : HTML, CSS et un peu de JavaScript. Le back, c’est PHP 8.2 avec PDO. La base, c’est MariaDB 10.4 avec InnoDB, le tout servi en local par XAMPP. Le front saisit, le back décide, la base garantit. »

**2 · 0:30–0:55 · Démarche et modèle Chen.** « Nous sommes partis des cas d’utilisation UML, cinq acteurs, puis du MCD en notation de Chen, puis du schéma relationnel. Exemple : douze unités réparties en sept et cinq dans deux colis. La quantité appartient au couple colis–prélèvement : la relation N:N devient la table package_pick. »

**3 · 0:55–1:20 · Quatre choix.** « Le stock est la somme des mouvements, jamais modifiés. Le lot est séparé de la palette reçue, qui garde sa provenance. Les quantités réparties ont leur table. Et rien ne s’efface en cascade. »

**4 · 1:20–1:50 · Normalisation.** « En première forme normale, les valeurs sont atomiques : les équipements d’un quai sont des lignes, pas une liste. En deuxième, ce qui dépend du couple avis–article, la quantité attendue, reste sur ce couple, et le nom de l’article reste dans article. En troisième, pas de dépendance transitive : la zone d’un emplacement se retrouve par jointure. Quatre dénormalisations sont assumées et contrôlées. »

**5 · 1:50–2:05 · Automatisation.** « La base travaille de trois façons : les triggers à chaque écriture, les procédures quand on les appelle, l’évènement à heure fixe. Et chaque écriture du site est une transaction. »

**6 · 2:05–2:35 · Triggers.** « Sur la capture phpMyAdmin, la table des rendez-vous a deux triggers BEFORE et trois AFTER. BEFORE agit avant l’écriture et peut refuser : il bloque par SIGNAL un rendez-vous qui chevauche un autre sur le même quai, même en SQL direct. AFTER réagit après : il écrit l’ancienne et la nouvelle valeur dans le journal, qui refuse toute modification. Un AFTER INSERT tient le solde du stock à jour. »

**7 · 2:35–3:05 · Procédures et fonction.** « La capture montre nos trois procédures et notre fonction, qui retourne un entier. lock_site pose un verrou au début de chaque écriture du site. trace_lot affiche le parcours d’un lot : c’est la page Traçabilité. La fonction stock_disponible renvoie la quantité disponible, utilisée avant chaque préparation de commande. archive_appointments est appelée par l’évènement. »

**8 · 3:05–3:25 · Évènement.** « Voici l’évènement dans phpMyAdmin : récurrent, chaque jour à deux heures, il appelle archive_appointments. Il archive les rendez-vous de plus d’un an sans passage de camion, dans une transaction. Une vue UNION ALL réunit courants et archivés. »

**9 · 3:25–3:55 · Calculer plutôt que stocker.** « Le retard, l’attente et les écarts de réception ne sont pas des triggers : ils se déduisent des données déjà présentes, donc on les calcule à la lecture. v_visit donne l’attente, PHP compare l’arrivée à l’heure du rendez-vous, et v_receipt_discrepancy compare l’attendu au reçu. Les stocker créerait une redondance. »

**10 · 3:55–4:25 · Fonctions PHP.** « Côté PHP, une classe par métier. Database exécute les requêtes préparées et ouvre les transactions. Auth gère inscription, connexion et droits. Warehouse porte les opérations : rendez-vous, arrivée, réception, transfert, préparation FEFO. Catalog et Reports gèrent ajout, modification, suppression, recherches et exports. Les saisies sont contrôlées côté serveur. »

**11 · 4:25–5:00 · Optimisation.** « Enfin, la démarche du TD : mesurer, lire EXPLAIN, optimiser. Chaque recherche de stock recalculait les vingt-cinq mille mouvements. Un trigger tient maintenant le total à jour : de 72 à 2 millisecondes, sans ralentir les écritures, et on vérifie qu’il reste égal au recalcul. » **Quitter le diaporama.**

## Deuxième partie — cinq minutes dans l’application

Préparer les sessions dans des profils de navigateur distincts avant le passage. Le parcours complet avec les identifiants, champs, boutons et captures est dans [Parcours-application.pdf](Parcours-application.pdf). Pour la démonstration courte, utiliser la base préparée indiquée dans le PDF. Les écritures de création détaillées dans le guide servent à la répétition sur une base neuve.

| Temps absolu | Écran à montrer | Phrase ou geste |
|---|---|---|
| 5:00–5:40 | Comptes puis planning | Montrer la liste des profils depuis la session admin. Basculer sur le responsable et montrer la journée du 22/10/2026 avec le bouton « Nouveau rendez-vous ». Expliquer que le responsable planifie les quais et que l’accueil reçoit le camion. |
| 5:40–6:35 | Avis fournisseur | Depuis la session magasinier, ouvrir Référentiels, rubrique Avis fournisseurs, rechercher ORAL-CAFE-AVIS. Montrer sa ligne attendue de 20 unités de café. Pour illustrer la saisie, ouvrir « Ajouter une fiche » et montrer les champs, puis revenir à l’avis existant. |
| 6:35–7:25 | Réception et stock | Retrouver ORAL-CAFE-REC et ORAL-CAFE-PAL. Montrer 18 acceptées et 2 endommagées, puis le transfert de 3 unités. Expliquer pourquoi les unités endommagées ne deviennent pas disponibles. |
| 7:25–8:30 | Commande et préparation | Montrer ORAL-CAFE-CMD, sa quantité de 10 et son affectation à Noah Bernard. Expliquer la réservation FEFO, le colis, puis la confirmation du chargement. Montrer le bon de livraison déjà généré. |
| 8:30–9:45 | Traçabilité des lots | Choisir ORAL-CAFE-LOT puis « Retracer le lot ». Montrer la réception, le transfert, la sortie de 10 unités et ORAL-CAFE-SORTIE. Dire : « Voici la réception d’origine et le passage du camion sortant pour le même lot. » |
| 9:45–10:00 | Garder la trace à l’écran | « Nous sommes partis de la structure de la base et nous venons de retrouver la chaîne complète dans l’application. Nous sommes prêts pour vos questions. » |

**Répartition possible.** Eliott présente architecture, démarche, choix et normalisation jusqu’à 1:50. Semih présente automatisation, triggers, procédures, évènement, calculs, PHP et optimisation jusqu’à 5:00. Thomas pilote la démonstration. Répéter avec les changements de fenêtre, puis relire [Questions-prof.md](Questions-prof.md) pour les dix minutes d’échange.
