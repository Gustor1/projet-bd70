# Transit — préparation aux 10 minutes de questions

Le professeur choisit les questions. Préparer une réponse de 30 à 45 secondes, puis une preuve à montrer si la discussion se prolonge.

## Compréhension globale et fonctionnement du projet

| Question | Réponse à défendre |
|---|---|
| Pourquoi séparer rendez-vous et passage ? | Le rendez-vous est une prévision. Le passage est un fait horodaté. Une arrivée spontanée crée un passage sans rendez-vous, et une réservation peut ne jamais donner lieu à une arrivée. |
| Pourquoi distinguer lot et fraction reçue ? | Le même lot fournisseur peut arriver en plusieurs livraisons. La fraction identifie précisément quelle réception a fourni les unités prélevées. |
| Pourquoi un compte peut-il avoir zéro société ? | Les comptes internes n’ont aucune société de transport. Un compte de profil transporteur doit en avoir exactement une. Le portail filtre les données et le serveur revérifie l’appartenance lors des modifications. |
| Que devient une suppression demandée dans la grille ? | Le responsable peut supprimer un référentiel inutilisé. Dès qu’un historique en dépend, les références sont protégées. Selon l’objet, l’interface propose annulation, reprise, ajustement ou désactivation. |
| Que mesure le tableau de bord ? | Par exemple l’attente moyenne par transporteur, l’occupation des quais et le remplissage par zone. L’activité peut être filtrée sur une période. Le stock et les alertes DLC reflètent la situation actuelle. |
| Les données sont-elles réelles ? | Le jeu est fictif et reproductible. Il simule notamment 900 expéditions. Les scénarios navigateur vérifient des parcours choisis et les contrôles d’intégrité inspectent l’ensemble du jeu. |

## SQL et intégrité

| Question | Réponse à défendre |
|---|---|
| Pouvez-vous expliquer une relation N:N ? | Un prélèvement alimente plusieurs colis et un colis contient plusieurs prélèvements. La quantité allouée dépend de leur couple. Le détail chiffré de la diapositive 2 permet de le démontrer. |
| Comment défendez-vous la 3NF ? | Expliquer une dépendance précise et les anomalies évitées. La description d’une société reste dans carrier. La sortie référence le prélèvement, qui détermine ses valeurs. L’audit conserve intentionnellement des instantanés historiques. Le détail est dans docs/normalisation-3nf.md. |
| Pourquoi un mouvement est-il lié à 0 ou 1 fraction et 0 ou 1 emplacement (« 0,1 » écrit côté FRACTION REÇUE et côté EMPLACEMENT) ? | Une sortie obtient fraction et emplacement par son prélèvement, les autres mouvements les portent directement. Le minimum 0 exprime cette facultativité, et le CHECK SQL impose que les deux structures soient exclusives. |
| Pourquoi ne pas modifier un solde de stock directement ? | Le solde se calcule depuis les mouvements. Un transfert produit deux écritures opposées et une correction d’inventaire un ajustement motivé. On peut ainsi expliquer l’origine du solde. |
| Quel est le rôle des triggers ? | Trois familles : cohérence (refus d’un chevauchement de rendez-vous, sortie cohérente avec son prélèvement), protection des historiques (UPDATE/DELETE refusés) et audit. Les règles qui dépendent de plusieurs tables et du profil, comme la capacité disponible, sont contrôlées par PHP dans une transaction verrouillée. |
| Comment vérifiez-vous les saisies et la sécurité ? | Expliquer sur un rendez-vous le contrôle serveur du rôle, du propriétaire, des horaires, de la compatibilité et des conflits. Requêtes préparées, hachage des mots de passe, sessions et jetons CSRF couvrent des risques distincts. |

## Choix de conception et compromis

| Question | Réponse à défendre |
|---|---|
| Pourquoi FEFO ? | Pour un produit avec DLC, servir en priorité le lot utilisable dont l’échéance est la plus proche. Le sujet autorise FIFO ou FEFO. Une réservation réduit déjà la quantité disponible pour les autres préparateurs. |
| Pourquoi la mesure SQL ne prédit-elle pas le temps de la page ? | Les dix exécutions mesurent le travail SQL avec récupération des résultats. Le serveur web et le navigateur ajoutent leur propre coût. La machine, les index, la taille des données et le cache influencent les résultats. |
| Quelle amélioration choisiriez-vous ? | Pour davantage d’écritures simultanées, mesurer les attentes sur le verrou de site avant d’introduire des verrous par ressource. Il faudrait alors rejouer les tests concurrents pour les demandes portant sur plusieurs ressources. |

## Comment avez-vous optimisé la base et comment le savez-vous ?

**Réponse à dire.** « Nous avons mesuré huit requêtes métier sur une base de test d’environ 10 000 passages. Pour rechercher les conflits de rendez-vous, nous filtrons par quai, par statut et par horaires. Nous avons donc testé un index composé sur ces colonnes. Sur le même créneau, la médiane de dix lectures après chauffe est passée de 4,00 ms avec l’index simple à 0,90 ms après ajout de l’index composé. EXPLAIN confirme que MariaDB a choisi ce nouvel index. En contrepartie, une modification des créneaux doit aussi mettre l’index à jour. »

**Si le professeur veut voir la requête mesurée**, les trois paramètres sont le quai, la fin du créneau demandé et son début, dans cet ordre.

```sql
SELECT reference
FROM appointment
WHERE dock_id = ? AND status = 'active'
  AND starts_at < ? AND ends_at > ?;
```

L’index est `idx_appointment_slot(dock_id, status, starts_at, ends_at)`. Le plan estime 3335 lignes à examiner avec l’index simple sur le quai, puis 971 avec l’accès par plage sur l’index composé. Ce sont des estimations du plan. Les durées viennent du chronométrage. **À l’oral, utiliser 4,00 → 0,90 ms pour le comparatif avant/après** : ce sont les chiffres de la diapositive 7, du rapport et de docs/performances.md (même série de mesures).

**Autre choix d’optimisation.** Pour proposer un emplacement, la vue `v_location_usage` calcule le poids, le volume et les équivalents palettes depuis les quantités physiques. Elle évite de joindre les réservations nécessaires au calcul du disponible commercial. Une unité réservée occupe encore de la place jusqu’à son départ : c’est le stock physique qui compte ici.

[Index du projet](../../sql/05_index.sql) · [Mesures et plans EXPLAIN](../../docs/performances.md)

## Pourquoi avoir choisi cette requête plutôt qu’une autre ?

**Réponse à dire.** « Je pars du résultat métier attendu. Pour suivre un camion encore sur le site, je dois afficher son arrivée même si son départ n’existe pas encore. J’utilise donc un LEFT JOIN vers l’événement de départ. Avec un INNER JOIN, le camion disparaîtrait du résultat précisément au moment où l’accueil doit le suivre. Une fois le résultat correct, je peux comparer le coût des formulations équivalentes. »

**Exemples à choisir selon la notion du cours sur laquelle le professeur insiste.**

| Notion et écran | Choix dans Transit | Ce qui changerait avec l’autre requête |
|---|---|---|
| **WHERE** · conflit de créneau | Tester les deux bornes, comme dans la requête ci-dessus. | Pour une demande de 9 h à 10 h, une réservation de 8 h à 11 h est en conflit. Tester uniquement si son début tombe entre 9 h et 10 h la manquerait. Les inégalités strictes autorisent deux créneaux consécutifs qui se touchent à 10 h. |
| **INNER JOIN** · rangement | Dans `v_location`, suivre les clés de l’emplacement vers son niveau, son rack, son allée et sa zone. | Ces rattachements sont obligatoires. La jointure retrouve les conditions de la zone sans les recopier dans chaque emplacement, où elles pourraient diverger. |
| **LEFT JOIN et NULL** · passages | Dans `v_visit`, conserver le passage même si l’étape de départ manque. | Un INNER JOIN supprimerait le camion encore présent. Remplacer la durée inconnue par zéro fausserait ensuite la moyenne des durées. |
| **SUM et GROUP BY** · stock | Dans `v_balance`, sommer les variations par fraction reçue **et** par emplacement. | Un transfert de trois unités produit −3 à la source et +3 à destination. Un total global donnerait zéro variation et masquerait le changement d’emplacement. |
| **COALESCE** · disponible | Dans `v_stock`, joindre les réservations et utiliser `COALESCE(p.qty, 0)`. | Une fraction utilisable de 18 unités peut n’avoir aucune ligne de réservation. Ici, l’absence signifie zéro unité réservée. Sans COALESCE, la soustraction donnerait NULL au lieu de 18 disponibles. |
| **ORDER BY multicritère** · FEFO | Filtrer les lots utilisables, puis trier par `expires_on IS NULL, expires_on, received_at, receipt_item_id, location_id`. | Les lots datés passent avant ceux sans DLC. À DLC égale, la réception la plus ancienne passe d’abord. Trier seulement sur la réception appliquerait FIFO et pourrait laisser périmer un lot arrivé plus tard. |
| **COUNT, AVG et GROUP BY** · statistiques | Filtrer les passages sur la période, grouper par transporteur, compter les passages et calculer leur attente moyenne. | Une moyenne globale masquerait les écarts entre sociétés. COUNT(*) compte tous les passages retenus, tandis que AVG(wait_minutes) utilise seulement les attentes déjà connues. |
| **ORDER BY et LIMIT** · traçabilité | `trace_lot` filtre sur le lot, trie par date puis par identifiant et renvoie 20 mouvements par page. | Deux mouvements peuvent avoir le même horodatage. L’identifiant les départage. LIMIT sans ordre stable ne garantirait pas un parcours chronologique reproductible. |
| **SELECT FOR UPDATE** · concurrence | `lock_site` verrouille la ligne du site avant la vérification du créneau et l’insertion. | Avec une simple lecture suivie d’une insertion, deux utilisateurs pourraient lire « libre » avant que l’un ait validé. Le verrou évite cette course, mais peut aussi faire attendre des écritures indépendantes. |
| **Trigger ou procédure** · automatisation | `AFTER UPDATE` sur `carrier` alimente le journal ; PHP appelle explicitement `trace_lot` pour consulter un lot. | L’audit doit accompagner chaque modification. La recherche de trace, elle, doit s’exécuter seulement quand un utilisateur en demande le résultat. |

[Vues et jointures](../../sql/02_vues.sql) · [Procédures](../../sql/03_procedures.sql) · [Sélection FEFO](../../src/Warehouse.php)

## Questions difficiles probables (ajoutées après la revue)

| Le professeur demande… | Réponse à défendre |
|---|---|
| Où est l’historisation au sens du cours ? | Table appointment_archive, procédure archive_appointments (INSERT … SELECT puis DELETE dans une transaction, ROLLBACK en cas d’erreur), évènement nocturne, vue v_appointment_all en UNION ALL. On n’archive que les rendez-vous terminés sans passage, sinon la clé étrangère du passage serait cassée. |
| Que se passe-t-il si quelqu’un insère un rendez-vous en conflit directement en SQL ? | Le trigger BEFORE INSERT appointment_no_overlap_insert le refuse avec SIGNAL SQLSTATE '45000'. PHP fait le même contrôle avant, pour afficher un message clair. |
| 109 triggers d’audit, ce n’est pas trop ? Le cours dit d’être parcimonieux. | Ils sont générés depuis le schéma, identiques, et font chacun un seul INSERT dans audit_log. Le coût est mesuré : une insertion de rendez-vous, trigger compris, prend environ 10 ms. Si le volume l’exigeait, on limiterait l’audit aux tables sensibles (comptes, rendez-vous, stock). |
| truck_visit recopie le chauffeur et le véhicule du rendez-vous : violation de la 3NF ? | C’est une dénormalisation assumée et limitée. Ces colonnes sont obligatoires pour les arrivées sans rendez-vous (appointment_id NULL, 27 % des passages du jeu), donc on ne peut pas les supprimer. Quand le rendez-vous existe, elles sont recopiées à l’arrivée ; aucune divergence n’est possible, car un rendez-vous déjà utilisé est figé (modification refusée). Le quai effectif, lui, est choisi à l’appel et peut différer du prévu. Alternative normalisée : une table « arrivée spontanée » séparée, au prix de requêtes plus complexes. |
| truck_visit.status est-il redondant ? | Oui, c’est une dénormalisation assumée : c’est la dernière étape de visit_event. Elle est mise à jour dans la même transaction que l’événement et évite de rechercher la dernière étape à chaque affichage. |
| Pourquoi un id artificiel dans les tables de jointure ? | Le couple reste clé candidate grâce à UNIQUE(a, b). L’id simplifie l’interface générique et les références dans le journal. Une clé primaire composée serait aussi correcte. |
| Lisez-moi l’EXPLAIN de la recherche de stock. | Les lignes DERIVED montrent que v_balance, qui contient un GROUP BY, est matérialisée : parcours complet (ALL) de stock_movement. C’est le prix d’un solde jamais stocké ; la solution serait une table de soldes mise à jour dans la même transaction. |
| Écrivez une requête avec HAVING. | `SELECT carrier_name, AVG(wait_minutes) FROM v_visit WHERE arrived_at>=? AND arrived_at<? GROUP BY carrier_id, carrier_name HAVING AVG(wait_minutes) > 30;` WHERE filtre les lignes avant le regroupement, HAVING filtre les groupes après. Elle est utilisée dans Indicateurs, « Transporteurs au-dessus du seuil d’attente ». |
| Différence entre 3NF et BCNF ? | 3NF : aucun attribut non clé ne dépend d’un autre attribut non clé. BCNF : tout déterminant est une clé candidate, y compris pour les attributs de clé. Exemple du cours : Author → Author Nationality doit sortir dans une table Author. |
| Pourquoi un seul utilisateur SQL pour l’application ? | Les profils métier sont des lignes de user_account contrôlées par PHP. Le SGBD connaît des comptes techniques par usage : application, reporting limité à des vues, sauvegarde. Le cours le recommande : l’application a son propre compte, avec le moindre privilège et une connexion limitée à 127.0.0.1. |
| Comment lisez-vous vos cardinalités ? | Comme dans le cours (« Client 1 — Possède — 0,N Facture ») : la cardinalité écrite près d’une entité dit combien de fois l’AUTRE entité peut lui être liée. Entre TRANSPORTEUR et CHAUFFEUR : « 0,N » près du chauffeur (une société emploie 0 à N chauffeurs), « 1,1 » près du transporteur (un chauffeur appartient à une seule société). Le côté « N » reçoit la clé étrangère : carrier_id est dans driver. |
| Qu’avez-vous changé après ma remarque sur le formalisme du MCD ? | La V1 mélangeait Merise (attributs dans les rectangles) et Chen (losanges), en PNG. Nous l’avons refaite entièrement en Chen, comme dans le cours : attributs en ovales, identifiants soulignés, attributs d’association reliés au losange, cardinalités placées comme dans vos exemples, et rendu vectoriel (PDF, SVG) avec une source Draw.io. |
| Pourquoi l’accueil ne planifie-t-il pas les quais ? | Le sujet attribue la planification au responsable d’exploitation et le poste de garde à l’agent d’accueil. L’accueil gère en revanche les arrivées sans rendez-vous et l’appel à quai, avec le contrôle de disponibilité du quai. |
| Qu’avez-vous changé après mes remarques sur le diagramme de cas d’utilisation ? | Quatre corrections : suppression de tout héritage (un acteur dessiné une fois, relié à ses seuls cas ; administrateur limité aux comptes) ; ajout du transporteur ; commandes réparties (le responsable gère et affecte, le préparateur prépare ses commandes affectées) ; quatre cas éclatés en sous-cas avec include et extend (passage d’un camion, commandes, expédition, traçabilité), le tout sur une seule page. Et, comme le demande le sujet, la planification des quais revient au responsable. |
| Pourquoi les temps d’attente sont-ils presque identiques entre transporteurs ? | Le jeu de démonstration est généré avec un rythme régulier : il sert à vérifier les calculs et les volumes, pas à simuler une activité réaliste. Le seuil HAVING permet quand même de le montrer. |

## « Pourquoi n’avez-vous pas utilisé… ? » — notions du cours absentes

Réponse type : reconnaître que la notion existe, dire pourquoi elle n’était pas nécessaire ici, puis montrer où on l’utiliserait. Ne jamais prétendre l’avoir faite.

| Le professeur demande… | Réponse à défendre |
|---|---|
| Pourquoi aucune fonction stockée (CREATE FUNCTION) ? | Nos calculs réutilisés sont des ensembles de lignes (stock, temps d’attente par passage) : une vue les expose directement et MariaDB peut l’optimiser, alors qu’une fonction appelée ligne par ligne dans un SELECT est évaluée pour chaque ligne et empêche l’usage des index. Où on l’utiliserait : `CREATE FUNCTION wait_minutes(p_visit INT) RETURNS DECIMAL(10,2) DETERMINISTIC READS SQL DATA` pour obtenir l’attente d’un seul passage, ou une fonction de calcul d’occupation d’un emplacement réutilisée par plusieurs procédures. |
| Pourquoi pas de tables temporaires (CREATE TEMPORARY TABLE) ? | Nos traitements tiennent en une requête ou une vue. MariaDB crée d’ailleurs lui-même une table temporaire quand il le faut : on la voit dans EXPLAIN (« Using temporary », lignes DERIVED de v_balance). On en créerait une pour un calcul en plusieurs étapes sur un gros volume, par exemple préparer les soldes d’un inventaire avant de générer les ajustements. |
| Pourquoi pas de partitionnement ? | Le cours le présente pour des tables très volumineuses. Nos tables les plus grosses comptent quelques dizaines de milliers de lignes, et nos requêtes durent moins de 50 ms. Nous avons préféré l’historisation (appointment_archive), que le cours compare au partitionnement. Candidat naturel : stock_movement partitionnée par année de created_at (PARTITION BY RANGE). |
| Pourquoi pas d’index full-text ? | Nos recherches portent sur des codes et références courts (LIKE sur SKU, lot, immatriculation), pas sur des textes longs. Un index full-text servirait à chercher dans les motifs de réserve ou les conditions des contrats (MATCH … AGAINST). |
| Pourquoi pas de CROSS JOIN ni de sous-requêtes partout ? | Le cours recommande de les éviter pour les performances. Nous utilisons des jointures explicites et quelques sous-requêtes ciblées (EXISTS dans les contrôles de chevauchement, agrégation préalable dans la productivité). |
| Pourquoi l’héritage (UML relationnel) n’apparaît pas ? | Nos profils ne sont pas des entités différentes : ils partagent les mêmes attributs et diffèrent par leurs droits. Une seule table user_account avec une colonne role suffit (stratégie « par la classe mère » du cours, sans colonnes nulles). Le professeur a d’ailleurs demandé de supprimer l’héritage entre métiers dans le diagramme de cas d’utilisation. |
| Pourquoi pas d’entités faibles (double rectangle) dans le MCD ? | Chaque ligne (de commande, d’avis, de réception) possède son propre identifiant et une clé candidate composée (par exemple order_id, article_id). Elles auraient pu être modélisées comme entités faibles identifiées par leur parent ; nous avons gardé une clé artificielle pour simplifier les références et l’interface. |
| Pourquoi pas d’attributs dérivés en pointillés dans le MCD ? | Les valeurs dérivées (stock disponible, temps d’attente, taux de remplissage) ne sont pas stockées : elles sont calculées par les vues. On aurait pu les faire figurer en pointillés sur le MCD ; nous les documentons dans le rapport, section Implémentation. |
| Pourquoi pas de réplication ni d’équilibrage de charge ? | Hors du périmètre d’un site unique sur un poste. Nous avons traité la sauvegarde : scripts/backup-restore.py sauvegarde puis restaure dans une base neuve et compare les tables et les automatismes. |
| Pourquoi pas d’expéditions partielles ni de multi-site ? | Limites assumées du périmètre (voir la conclusion du rapport). Il faudrait une table de répartition commande/expédition et revoir les verrous par ressource. |

## Relances à pratiquer

| Le professeur demande… | Exemple à donner |
|---|---|
| Que se passe-t-il entre un clic et la base ? | Le navigateur envoie un formulaire à PHP. Le serveur vérifie la session, les droits et les valeurs, puis utilise PDO pour interroger MariaDB. Pour une validation métier, les écritures liées sont regroupées dans une transaction. |
| Quelle différence entre trigger, procédure et événement ? | Le trigger d’audit AFTER UPDATE s’exécute quand un transporteur change. PHP appelle explicitement la procédure trace_lot pour retrouver le parcours d’un lot. L’évènement ev_archive_appointments s’exécute chaque nuit (ON SCHEDULE EVERY 1 DAY) et appelle archive_appointments. Transit utilise les trois. |
| Pouvez-vous écrire une requête ? | Dans package_pick, regrouper les lignes par pick_id et calculer SUM(qty) donne la quantité déjà conditionnée par prélèvement. Pour inclure les prélèvements sans colis, partir de pick et utiliser LEFT JOIN. |
| Pourquoi MariaDB et PHP ? | Le sujet A26 autorise MariaDB. Les clés étrangères, transactions InnoDB, vues, procédures et triggers répondent aux règles métier. PHP/PDO permet de les utiliser depuis les formulaires de la démonstration locale. |
| Comment démontrez-vous l’intérêt de l’index ? | Expliquer le filtre de recherche des créneaux, consulter EXPLAIN puis comparer les mesures dans des conditions similaires. Un index accélère certaines lectures et a un coût en écriture. |
| Quelle limite avez-vous acceptée ? | L’expédition est intégrale. Une commande a au plus une expédition. Autoriser des expéditions partielles demanderait de représenter la part servie dans chaque départ et de revoir les contrôles de clôture. |

**Pièces à ouvrir sur demande** · Recueil des modèles, pages 6 et 7 pour Chen et le schéma relationnel. sql/03_procedures.sql pour lock_site et trace_lot. sql/04_triggers.sql pour l’audit. docs/performances.md pour les temps et la méthode. Pour les contributions, chacun prépare un exemple qu’il a réellement réalisé ou vérifié.
