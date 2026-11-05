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
| Pourquoi deux cardinalités 0,1 sur le mouvement ? | Une sortie obtient fraction et emplacement par le prélèvement. Les autres mouvements les portent directement. Les cardinalités expriment la facultativité et le CHECK impose les deux structures exclusives. |
| Pourquoi ne pas modifier un solde de stock directement ? | Le solde se calcule depuis les mouvements. Un transfert produit deux écritures opposées et une correction d’inventaire un ajustement motivé. On peut ainsi expliquer l’origine du solde. |
| Quel est le rôle des triggers ? | Ils historisent automatiquement les changements et protègent certains faits. Les règles portant sur plusieurs lignes, comme la capacité disponible, sont revérifiées dans une transaction. |
| Comment vérifiez-vous les saisies et la sécurité ? | Expliquer sur un rendez-vous le contrôle serveur du rôle, du propriétaire, des horaires, de la compatibilité et des conflits. Requêtes préparées, hachage des mots de passe, sessions et jetons CSRF couvrent des risques distincts. |

## Choix de conception et compromis

| Question | Réponse à défendre |
|---|---|
| Pourquoi FEFO ? | Pour un produit avec DLC, servir en priorité le lot utilisable dont l’échéance est la plus proche. Le sujet autorise FIFO ou FEFO. Une réservation réduit déjà la quantité disponible pour les autres préparateurs. |
| Pourquoi la mesure SQL ne prédit-elle pas le temps de la page ? | Les dix exécutions mesurent le travail SQL avec récupération des résultats. Le serveur web et le navigateur ajoutent leur propre coût. La machine, les index, la taille des données et le cache influencent les résultats. |
| Quelle amélioration choisiriez-vous ? | Pour davantage d’écritures simultanées, mesurer les attentes sur le verrou de site avant d’introduire des verrous par ressource. Il faudrait alors rejouer les tests concurrents pour les demandes portant sur plusieurs ressources. |

## Comment avez-vous optimisé la base et comment le savez-vous ?

**Réponse à dire.** « Nous avons mesuré huit requêtes métier sur une base de test d’environ 10 000 passages. Pour rechercher les conflits de rendez-vous, nous filtrons par quai, par statut et par horaires. Nous avons donc testé un index composé sur ces colonnes. Sur le même créneau, la médiane de dix lectures après chauffe est passée de 13,32 ms avec l’index simple à 2,87 ms après ajout de l’index composé. EXPLAIN confirme que MariaDB a choisi ce nouvel index. En contrepartie, une modification des créneaux doit aussi mettre l’index à jour. »

**Si le professeur veut voir la requête mesurée**, les trois paramètres sont le quai, la fin du créneau demandé et son début, dans cet ordre.

```sql
SELECT reference
FROM appointment
WHERE dock_id = ? AND status = 'active'
  AND starts_at < ? AND ends_at > ?;
```

L’index est `idx_appointment_slot(dock_id, status, starts_at, ends_at)`. Le plan estime 3 335 lignes à examiner avec l’index simple sur le quai, puis 971 avec l’accès par plage sur l’index composé. Ce sont des estimations du plan. Les durées viennent du chronométrage. **À l’oral, utiliser 13,32 → 2,87 ms pour le comparatif avant/après.** Les 1,26 ms de la diapositive proviennent d’une autre série de dix mesures sur cette requête.

**Autre choix d’optimisation.** Pour proposer un emplacement, la vue `v_location_usage` calcule le poids, le volume et les équivalents palettes depuis les quantités physiques. Elle évite de joindre les réservations nécessaires au calcul du disponible commercial. Une unité réservée occupe encore de la place jusqu’à son départ : c’est le stock physique qui compte ici.

[Index du projet](../../sql/05_index.sql) · [Mesures et plans EXPLAIN](../../docs/preuves/corrections-rendu-2026-11-03/performances.json)

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

## Relances à pratiquer

| Le professeur demande… | Exemple à donner |
|---|---|
| Que se passe-t-il entre un clic et la base ? | Le navigateur envoie un formulaire à PHP. Le serveur vérifie la session, les droits et les valeurs, puis utilise PDO pour interroger MariaDB. Pour une validation métier, les écritures liées sont regroupées dans une transaction. |
| Quelle différence entre trigger, procédure et événement ? | Le trigger d’audit AFTER UPDATE s’exécute quand un transporteur change. PHP appelle explicitement la procédure trace_lot pour retrouver le parcours d’un lot. Un événement planifié s’exécuterait à une date ou fréquence définie. Transit utilise les deux premiers mécanismes. |
| Pouvez-vous écrire une requête ? | Dans package_pick, regrouper les lignes par pick_id et calculer SUM(qty) donne la quantité déjà conditionnée par prélèvement. Pour inclure les prélèvements sans colis, partir de pick et utiliser LEFT JOIN. |
| Pourquoi MariaDB et PHP ? | Le sujet A26 autorise MariaDB. Les clés étrangères, transactions InnoDB, vues, procédures et triggers répondent aux règles métier. PHP/PDO permet de les utiliser depuis les formulaires de la démonstration locale. |
| Comment démontrez-vous l’intérêt de l’index ? | Expliquer le filtre de recherche des créneaux, consulter EXPLAIN puis comparer les mesures dans des conditions similaires. Un index accélère certaines lectures et a un coût en écriture. |
| Quelle limite avez-vous acceptée ? | L’expédition est intégrale. Une commande a au plus une expédition. Autoriser des expéditions partielles demanderait de représenter la part servie dans chaque départ et de revoir les contrôles de clôture. |

**Pièces à ouvrir sur demande** · Recueil des modèles, pages 6 et 7 pour Chen et le schéma relationnel. sql/03_procedures.sql pour lock_site et trace_lot. sql/04_triggers.sql pour l’audit. docs/performances.md pour les temps et la méthode. Pour les contributions, chacun prépare un exemple qu’il a réellement réalisé ou vérifié.
