# Transit — questions du professeur, à réviser

## Comment le professeur va interroger

Il sait que l’IA a pu écrire du code. Il note donc surtout **la compréhension** : pourquoi ce choix, comment ça marche, que se passe-t-il si… Ses questions suivent souvent ce schéma :

1. **« Pourquoi ? »** — un choix de la présentation (« pourquoi une table de soldes ? »).
2. **« Montrez-moi. »** — la ligne de SQL, la vue, le trigger, l’écran qui l’utilise.
3. **« Et si… ? »** — un cas limite (« deux personnes réservent en même temps ? », « on supprime un transporteur ? »).
4. **« Sans ça, quoi ? »** — l’alternative écartée et ce qu’on aurait perdu.

**Répondre en 3 temps** : ce qu’on a fait → pourquoi → la contrepartie (ou l’alternative). Toujours un exemple concret du projet.
**Si on ne sait pas** : « Je ne suis pas sûr, mais je pense que… parce que… ». Ne jamais inventer : une réponse fausse dite avec assurance est pire qu’un raisonnement honnête.

Chaque membre doit pouvoir répondre sur **toutes** les parties, pas seulement la sienne.

**Chiffres à connaître** : 43 tables · 68 clés étrangères · 22 CHECK · 38 UNIQUE · 11 vues · 127 triggers (3 cohérence, 11 protection, 4 calcul, 109 audit) · 3 procédures · 1 fonction · 1 évènement · 8 index secondaires · 1 806 passages · 24 917 mouvements · 924 commandes · 720 lots · stock 72,3 → 2,0 ms · créneaux 7,2 → 1,4 ms.

---

## 0. Les 12 questions les plus probables

| # | Question | Réponse courte | Détail |
|---|---|---|---|
| 1 | Le front est en quoi, le back en quoi ? | Front : HTML, CSS, un peu de JS. Back : PHP 8.2 avec PDO, sans framework. Base : MariaDB 10.4 (InnoDB). Servi en local avec XAMPP. | §1 |
| 2 | Pourquoi le stock n’est pas une simple colonne ? | C’est la somme des mouvements, jamais modifiés : on sait toujours pourquoi il vaut ce qu’il vaut. | §4 |
| 3 | Alors pourquoi `stock_balance` ? | Pour la vitesse (72 → 2 ms). Tenue par trigger dans la même transaction, contrôlée contre le recalcul : 0 écart. | §10 |
| 4 | Expliquez 1NF, 2NF, 3NF avec votre projet. | Atomicité (équipements d’un quai en lignes), dépendance à toute la clé (quantité attendue sur avis+article), pas de dépendance transitive (zone par jointure). | §3 |
| 5 | Différence trigger / procédure / fonction / évènement ? | Trigger : automatique sur une écriture. Procédure : appelée (CALL), fait un traitement. Fonction : appelée, renvoie une valeur. Évènement : à heure fixe. | §6-8 |
| 6 | Le retard ou les écarts, c’est un trigger ? | Non : calculés à la lecture (vues + PHP), car déductibles des données. Les stocker = redondance. | §5 |
| 7 | Vos vues sont-elles utilisées par le site ? | Oui, 9 sur 11 : `v_stock` (Stock, FEFO), `v_visit` (Indicateurs), `v_location_usage` (emplacements), `v_receipt_discrepancy` (écarts)… | §5 |
| 8 | Deux personnes réservent le même quai en même temps ? | Transaction + `lock_site` (SELECT … FOR UPDATE) : la 2ᵉ attend, relit, voit le conflit, ROLLBACK. Et le trigger refuse en dernier recours. | §9 |
| 9 | Comment avez-vous optimisé ? | Mesurer, EXPLAIN, optimiser, re-mesurer. Table de soldes (−97 %) et index composé sur les créneaux (−81 %). | §10 |
| 10 | Comment protégez-vous l’application ? | Requêtes préparées, mots de passe hachés, CSRF, échappement HTML, droits revérifiés côté serveur, compte SQL limité. | §11 |
| 11 | Une N:N chez vous ? | Colis ↔ prélèvement : table `package_pick` avec la quantité (12 = 7 + 5). | §2 |
| 12 | Qu’est-ce que vous feriez mieux ? | Verrou par quai au lieu d’un verrou global, expéditions partielles, audit limité aux tables sensibles. | §14 |

---

## 1. Architecture et technologies

**Q. Le front est en quoi ? Le back en quoi ?**
Front : HTML et CSS générés par des gabarits PHP (`templates/`), avec un tout petit JavaScript (`public/assets/app.js` : imprimer, confirmer une suppression, rafraîchir la page des quais toutes les 30 s). Back : PHP 8.2, classes dans `src/`, connexion PDO. Base : MariaDB 10.4 avec le moteur InnoDB. En local : XAMPP fournit PHP et MariaDB, notre script `start.ps1` lance les serveurs.

**Q. Pourquoi trois couches (formulaire → PHP → MariaDB) ? Pourquoi pas le navigateur directement vers la base ?**
Le navigateur est chez l’utilisateur : il peut tout modifier. S’il parlait à la base, il faudrait lui donner les identifiants SQL. Le front saisit, le back décide (qui, quels droits, valeurs valides), la base garantit (contraintes, triggers, transactions).
*Il creuse →* « Les contrôles HTML (`required`, `min`) suffisent ? » Non, ils servent au confort : on les contourne avec les outils du navigateur. Tout est revérifié en PHP.

**Q. Pourquoi PHP sans framework ?**
On voit et on écrit chaque requête SQL, ce qui est l’objet du cours. Pas de dépendance à installer : ça tourne sur XAMPP. Contrepartie : plus de code à écrire nous-mêmes (routage, formulaires).

**Q. Pourquoi MariaDB ? Pourquoi InnoDB ?**
Le sujet autorise MySQL/MariaDB, fourni avec XAMPP. InnoDB apporte ce dont on a besoin : transactions (COMMIT/ROLLBACK), clés étrangères, verrous de lignes (FOR UPDATE).

**Q. Que se passe-t-il entre le clic et la base ?** (à savoir dérouler)
1. Le formulaire envoie un POST à `public/index.php` avec le jeton CSRF.
2. PHP vérifie la session, le jeton (`hash_equals`), puis les droits du profil (`Auth::demand`).
3. Le service métier (`Warehouse`, `Catalog`…) contrôle les valeurs.
4. `Database::transaction()` : BEGIN, `SET @actor_id`, `CALL lock_site()`, les requêtes préparées, puis COMMIT (ou ROLLBACK si une erreur).
5. Dans la base, les triggers s’exécutent (contrôle, audit, solde).
6. PHP redirige et affiche un message.

**Q. Où est écrit le SQL ?**
Le schéma et les objets dans `sql/` (01 schéma, 02 vues, 03 procédures, 04 triggers, 05 index, 08 historisation, 09 optimisation). Les requêtes de l’application dans `src/` et `templates/`, toujours avec des `?` (requêtes préparées).

---

## 2. Démarche et modèle (UML, MCD, MLD)

**Q. Quelle a été votre démarche ?**
Cahier des charges → cas d’utilisation UML (5 acteurs) → MCD en notation de Chen → schéma relationnel (MLD) → SQL et données factices → interface. Le MCD et le diagramme UML ont été corrigés après vos remarques (Chen strict, plus d’héritage entre acteurs).

**Q. Comment passe-t-on du MCD au schéma relationnel ?**
Une entité devient une table, son identifiant la clé primaire. Une association 1:N devient une clé étrangère **du côté N** (ex. `driver.carrier_id`). Une association N:N devient une **table de jointure** avec deux clés étrangères et ses propres attributs (ex. `package_pick.qty`).

**Q. Lisez-moi une cardinalité.**
Comme dans le cours, la cardinalité écrite près d’une entité dit combien de fois l’**autre** entité peut lui être liée. Transporteur–chauffeur : « 0,N » près du chauffeur (une société emploie 0 à N chauffeurs), « 1,1 » près du transporteur (un chauffeur appartient à une seule société). Le côté N reçoit la clé étrangère.

**Q. Expliquez votre N:N.**
Un prélèvement de 12 unités est réparti dans deux colis : 7 et 5. La quantité ne dépend ni du colis seul ni du prélèvement seul, mais du couple. D’où `package_pick(package_id, pick_id, qty)` avec `UNIQUE(package_id, pick_id)` et `CHECK(qty>0)`.
*Autres N:N :* chauffeur ↔ habilitation (`driver_qualification`, avec date d’expiration), quai ↔ équipement, quai ↔ type de véhicule, véhicule ↔ équipement.

**Q. Pourquoi un `id` artificiel dans les tables de jointure ?**
Le couple reste unique grâce à UNIQUE. L’id simplifie l’interface générique et les références dans le journal. Une clé primaire composée serait aussi correcte.

**Q. Vos clés primaires et vos types ?**
`INT AUTO_INCREMENT` partout (BIGINT pour le journal, très volumineux). DECIMAL pour les poids et dimensions (`unit_kg DECIMAL(10,3)`) : pas d’erreurs d’arrondi comme avec FLOAT. DATETIME pour les horaires, DATE pour les DLC, ENUM pour les états (`arrived`, `checked`…), VARCHAR pour les codes. Les clés naturelles (email, immatriculation, référence) sont en UNIQUE.

**Q. Pourquoi séparer rendez-vous et passage ?**
Le rendez-vous est une **prévision**, le passage un **fait** horodaté. Un camion peut arriver sans rendez-vous (27 % du jeu), et un rendez-vous peut ne jamais donner d’arrivée.

---

## 3. Normalisation

**Q. C’est quoi la 1NF ? Un exemple chez vous ?**
Chaque valeur est atomique, pas de liste dans une colonne. Les équipements d’un quai sont des lignes de `dock_equipment`, pas un texte « niveleur, hayon ». *Sinon* : impossible de chercher « tous les quais avec hayon » proprement.

**Q. La 2NF ?**
En 1NF, et tout attribut non clé dépend de **toute** la clé, pas d’une partie. Dans une ligne d’avis, clé (avis, article) → quantité attendue. Le nom de l’article ne dépend que de l’article : il reste dans `article`. *Sinon* : renommer un article obligerait à modifier toutes les lignes d’avis.

**Q. La 3NF ?**
En 2NF, et pas de dépendance transitive : un attribut non clé ne dépend pas d’un autre attribut non clé. La zone d’un emplacement se retrouve par jointure (emplacement → niveau → rack → allée → zone), elle n’est pas recopiée dans `location`. *Sinon* : changer la zone d’une allée obligerait à corriger chaque emplacement, avec un risque d’incohérence.

**Q. Et la BCNF ?**
Plus stricte : tout déterminant doit être une clé candidate. Nos clés naturelles sont déclarées UNIQUE, ce qui couvre ces cas.

**Q. Votre base est-elle vraiment en 3NF ?** (question piège)
Oui, avec **4 dénormalisations assumées** et contrôlées :
1. `stock_balance` : le solde stocké pour la performance, écrit uniquement par trigger, comparé au recalcul (0 écart).
2. Les états courants (`truck_visit.status`, `receipt.status`, `customer_order.status`) : la dernière étape, mise à jour dans la même transaction que l’évènement.
3. `truck_visit.driver_id / vehicle_id` : indispensables aux arrivées sans rendez-vous ; recopiés quand le rendez-vous existe, mais un rendez-vous utilisé est figé, donc pas d’incohérence possible.
4. `receipt_line.expected_qty` : l’attendu **de cette livraison** (un avis peut arriver en plusieurs fois).
Le journal d’audit garde aussi des instantanés JSON : c’est un historique technique, pas une relation métier.

**Q. Une dénormalisation, ce n’est pas une faute ?**
Non si elle est volontaire, justifiée et contrôlée. Le cours (TD Automatisation) fait exactement ça avec une table de statistiques tenue par trigger.

---

## 4. Choix de conception (les « pourquoi »)

| Le prof demande… | Réponse |
|---|---|
| Pourquoi on ne modifie jamais un mouvement ? | C’est un historique : corriger = ajouter un mouvement (ajustement avec motif), comme en comptabilité. Des triggers refusent UPDATE et DELETE (« Historique immuable »). |
| Pourquoi séparer `lot` et `receipt_item` (palette reçue) ? | Un même lot peut arriver dans plusieurs livraisons. Chaque palette garde sa réception, son fournisseur et son camion : la provenance n’est jamais perdue. |
| Pourquoi un transfert = 2 lignes ? | −3 à la source, +3 à la destination, avec le même numéro d’opération. Le total ne bouge pas mais on sait où est passée la marchandise. |
| Pourquoi garder l’attendu ET le reçu ? | Pour calculer manquants, excédents, avariés. Écraser l’attendu ferait perdre l’écart. |
| Où sont les produits endommagés ? | `receipt_item.damaged_qty`, à côté de `accepted_qty`. CHECK : s’il y a de l’endommagé, une réserve est obligatoire. Seul l’accepté entre en stock. |
| Pourquoi FEFO et pas FIFO ? | Produits datés : on sort d’abord ce qui périme le plus tôt. À DLC égale, la réception la plus ancienne (FIFO en départage). Les lots bloqués ou périmés ne sont jamais réservés. |
| Quand le stock est-il débité ? | Une seule fois, au chargement confirmé. Avant, il est **réservé** : plus disponible pour les autres, mais encore physiquement là. |
| Pourquoi une commande = une expédition ? | Simplification assumée. Les expéditions partielles demanderaient une table de répartition commande/expédition. |
| Pourquoi aucun ON DELETE CASCADE ? | Supprimer un transporteur ne doit jamais effacer ses passages. La suppression est refusée s’il est utilisé (RESTRICT par défaut). |
| Pourquoi 5 profils, et l’admin sans accès métier ? | Moindre privilège : chacun voit ce dont il a besoin. L’admin gère les comptes, pas l’entrepôt. |
| Pourquoi l’accueil ne planifie pas ? | Le sujet confie la planification au responsable d’exploitation ; l’accueil gère le poste de garde (arrivée, documents, parking, appel à quai, départ). |
| Pourquoi l’inscription reste « en attente » ? | On ne peut pas se donner un rôle soi-même : l’admin active le compte et choisit le profil. |
| Pourquoi un portail transporteur ? | Il prend ses propres rendez-vous et ne voit que ceux de sa société (filtre + revérification serveur). |

---

## 5. Les vues

**Q. C’est quoi une vue ?**
Une requête enregistrée qu’on interroge comme une table. Elle ne stocke pas de données : elle est recalculée à chaque lecture. Intérêt : un calcul écrit une seule fois, réutilisé partout.

**Q. Lesquelles utilisez-vous, et où sur le site ?**

| Vue | Ce qu’elle calcule | Où sur le site |
|---|---|---|
| `v_stock` | Physique, réservé, disponible par lot et emplacement | Stock, préparation FEFO |
| `v_balance`, `v_reserved` | Solde et réservations (lisent `stock_balance`) | À travers `v_stock` |
| `v_visit` | Attente et immobilisation de chaque passage | Indicateurs |
| `v_location`, `v_location_usage` | Zone d’un emplacement ; poids, volume, palettes occupés | Suggestion d’emplacement, remplissage par zone |
| `v_receipt_discrepancy` | Manquants, excédents, avariés | Détail réception, taux d’écart |
| `v_notice_line_progress` | Reste à recevoir d’un avis | Avis fournisseurs |
| `v_stock_movement` | Mouvements complétés (une sortie lit son prélèvement) | Traçabilité (dans `trace_lot`) |
| `v_balance_controle` | Recalcul complet du stock depuis l’historique | Contrôle seulement (pas sur le site) |
| `v_appointment_all` | Rendez-vous courants + archivés (UNION ALL) | Consultation SQL de l’historique |

**Q. Le retard, l’attente, les écarts de réception : c’est un trigger ?**
Non. **Attente et immobilisation** : `v_visit` calcule la différence entre les étapes horodatées (TIMESTAMPDIFF). **Retard** : PHP compare l’heure d’arrivée à l’heure du rendez-vous, sur la page Passages. **Écarts** : `v_receipt_discrepancy` compare l’attendu au reçu. Ces valeurs se **déduisent** des données déjà là ; les stocker par trigger créerait une redondance à maintenir (et une possibilité d’incohérence). Les triggers servent à **refuser, journaliser, ou tenir le solde** (le seul calcul trop coûteux à refaire).

**Q. Pourquoi un LEFT JOIN dans `v_visit` ?**
Un camion encore sur le site n’a pas d’étape « départ ». Avec un INNER JOIN, il disparaîtrait du résultat au moment où l’accueil doit le suivre. Avec LEFT JOIN, la valeur manquante est NULL, et AVG ignore les NULL (pas de faux zéro).

**Q. Pourquoi `COALESCE` dans `v_stock` ?**
Une palette sans réservation n’a pas de ligne de réservation : sans COALESCE, `qty − NULL` donnerait NULL au lieu du disponible.

**Q. Une vue avec GROUP BY, c’est lent ?** (lien optimisation)
Oui, MariaDB doit la **matérialiser** (table temporaire, `<derived>` dans EXPLAIN) avant de filtrer. C’est ce qu’on a vu sur l’ancienne `v_balance` et corrigé avec `stock_balance`. Une vue sans GROUP BY est **fusionnée** dans la requête et peut utiliser les index.

**Q. Peut-on faire un INSERT dans une vue ?**
Seulement dans une vue simple (une table, pas d’agrégat). Les nôtres servent en lecture ; on écrit toujours dans les tables.

---

## 6. Les triggers

**Q. C’est quoi un trigger ? BEFORE ou AFTER ?**
Du code exécuté automatiquement par la base lors d’un INSERT, UPDATE ou DELETE sur une table, pour chaque ligne (`FOR EACH ROW`). **BEFORE** : avant l’écriture, peut la **refuser** (SIGNAL) ou corriger NEW. **AFTER** : après, pour **réagir** (journal, calcul).

**Q. NEW et OLD ?**
NEW : la ligne après modification (INSERT, UPDATE). OLD : la ligne avant (UPDATE, DELETE). Le trigger d’audit écrit `OLD` dans « avant » et `NEW` dans « après ».

**Q. Vos triggers ?**
- **Cohérence (3, BEFORE)** : `appointment_no_overlap_insert` / `_update` refusent un chevauchement sur le même quai ; `normalize_shipment` vérifie qu’une sortie correspond à son prélèvement.
- **Protection (11, BEFORE UPDATE/DELETE)** : historiques immuables (mouvements, étapes de passage, expéditions, réserves, journal d’audit) et prélèvement expédié figé.
- **Calcul (4, AFTER)** : `balance_movement_insert` ajoute chaque mouvement au solde (`INSERT … ON DUPLICATE KEY UPDATE`) ; 3 triggers sur `pick` tiennent la quantité réservée.
- **Audit (109, AFTER)** : un par table et par opération, écrit ancienne/nouvelle valeur dans `audit_log`.

**Q. Comment le trigger refuse-t-il ?**
`SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '…'` : erreur, l’écriture est annulée, PHP reçoit l’exception et fait ROLLBACK.

**Q. Comment l’audit sait-il qui a fait la modification ?**
PHP fait `SET @actor_id = ?` au début de chaque transaction ; le trigger lit `@actor_id` (variable de session MySQL).

**Q. Pourquoi contrôler en PHP ET par trigger ?**
PHP donne un message clair à l’utilisateur. Le trigger protège même contre un bug ou une requête SQL directe : défense en profondeur.

**Q. 109 triggers d’audit, ce n’est pas trop ?**
Ils sont générés depuis le schéma (`scripts/build_triggers.py`), identiques, un seul INSERT chacun. Coût mesuré faible. Si besoin, on limiterait l’audit aux tables sensibles.

**Q. Limites d’un trigger ?**
Un trigger ne peut pas modifier la table sur laquelle il est déclenché (erreur MySQL). Il ralentit chaque écriture, est « invisible » (on l’oublie en lisant le code PHP) et ne doit pas contenir de règle qui dépend du profil de l’utilisateur — ça, c’est PHP.

---

## 7. Procédures et fonction

**Q. Différence procédure / fonction ?**
Procédure : un traitement, appelée par `CALL`, peut renvoyer des lignes et faire des écritures. Fonction : renvoie **une valeur** (`RETURNS INT`), utilisable dans un SELECT.

| Objet | Rôle | Où sur le site |
|---|---|---|
| `lock_site()` | `SELECT id FROM site_lock WHERE id=1 FOR UPDATE` : verrou de site | Au début de **chaque** écriture (`Database::transaction`) |
| `trace_lot(lot, offset)` | Parcours d’un lot : réception, emplacements, transferts, commande, expédition, camion ; 20 lignes par page | Page Traçabilité (« Retracer le lot ») |
| `stock_disponible(article, jour)` | Fonction : disponible = solde − réservé, lots non bloqués et non périmés | Préparation de commande, avant de réserver |
| `archive_appointments(jours)` | INSERT … SELECT vers l’archive puis DELETE, dans une transaction | Appelée par l’évènement nocturne |

**Q. Pourquoi une procédure plutôt que du PHP ?**
Le traitement reste dans la base : moins d’allers-retours, réutilisable même sans l’application (phpMyAdmin, script), et on peut donner `EXECUTE` sans donner l’accès aux tables.

**Q. Pourquoi `stock_disponible` n’est pas utilisée dans les listes ?**
Dans un SELECT, une fonction est appelée pour **chaque ligne** et empêche l’usage des index. Pour des ensembles de lignes, une vue est meilleure ; la fonction sert à un contrôle ponctuel.

**Q. C’est quoi `DELIMITER` ?**
Dans un script, `;` termine une instruction. Le corps d’une procédure contient des `;`, donc on change temporairement le délimiteur (`$$`) pour envoyer toute la définition d’un coup.

**Q. `READS SQL DATA`, `DETERMINISTIC` ?**
Indications pour MariaDB : la fonction lit des tables sans les modifier. Elle n’est pas déterministe, car le résultat change avec le stock.

---

## 8. L’évènement (historisation)

**Q. Comment fonctionne-t-il ?**
`ev_archive_appointments` : `ON SCHEDULE EVERY 1 DAY`, à 2 h, `DO CALL archive_appointments(365)`. Il archive les rendez-vous terminés depuis plus d’un an **et sans passage de camion**.

**Q. Pourquoi « sans passage » ?**
Un passage a une clé étrangère vers son rendez-vous : le déplacer casserait le lien. On ne déplace que ce qui n’est référencé par rien.

**Q. Et si `event_scheduler` est à OFF ?**
L’évènement ne s’exécute pas. Notre `start.ps1` lance MariaDB avec `--event-scheduler=ON`. Vérification : `SELECT @@event_scheduler;`. On peut aussi lancer à la main : `CALL archive_appointments(365);`.

**Q. Pourquoi archiver ?**
La table utilisée tous les jours reste petite, donc rapide ; l’historique est conservé. Le cours le compare au partitionnement. La vue `v_appointment_all` (UNION ALL) permet de tout consulter.

**Q. UNION ou UNION ALL ?**
UNION ALL : pas de recherche de doublons (plus rapide), et il n’y en a pas puisqu’une ligne est soit courante soit archivée.

---

## 9. Transactions et accès simultanés

**Q. C’est quoi une transaction ? ACID ?**
Un groupe d’écritures en tout ou rien. Atomicité (tout ou rien), Cohérence (contraintes respectées), Isolation (les autres ne voient pas l’état intermédiaire), Durabilité (après COMMIT, c’est enregistré).

**Q. Un exemple où c’est indispensable ?**
Valider une réception : statut de la réception, création des palettes, mouvements d’entrée, soldes. Si une étape échoue, ROLLBACK : pas de réception à moitié validée.

**Q. Deux utilisateurs réservent le même quai au même instant ?**
Les deux voient le créneau libre. Chaque écriture ouvre une transaction et appelle `lock_site` (SELECT … FOR UPDATE). La 1ʳᵉ prend le verrou, vérifie, insère, COMMIT. La 2ᵉ attendait ; elle relit le planning, voit le chevauchement, ROLLBACK avec un message. Testé avec deux processus en parallèle (`tests/race_worker.php`).

**Q. Inconvénient du verrou global ?**
Deux écritures sans rapport (une réception et un rendez-vous) s’attendent aussi. Pour un gros site : verrou par quai ou par emplacement. Contrepartie : plus de risques d’interblocage (deadlock) à gérer.

**Q. Niveau d’isolation ?**
Celui par défaut d’InnoDB, REPEATABLE READ. Le FOR UPDATE force la lecture de la dernière version et bloque les autres écrivains sur cette ligne.

---

## 10. Optimisation

**Q. Votre démarche ?**
Celle du TD : mesurer (médiane de 15 exécutions après une chauffe), lire EXPLAIN, optimiser, re-mesurer sur les mêmes données. Gain absolu = avant − après ; gain relatif = (avant − après) / avant.

**Q. Qu’est-ce qu’EXPLAIN montrait ?**
Pour la recherche de stock, une table `<derived>` et un accès **ALL** : la vue `v_balance` (GROUP BY) recalculait les 24 917 mouvements à chaque recherche. Après : lecture de `stock_balance` par clé primaire, plus de table dérivée.

**Q. Les résultats ?**

| Requête | Avant | Après | Gain |
|---|---|---|---|
| Recherche de stock | 72,3 ms | 2,0 ms | −97 % |
| Sélection FEFO | 75,1 ms | 2,0 ms | −97 % |
| Stock libre avant transfert | 63,8 ms | 0,4 ms | −99 % |
| Remplissage par zone | 101,4 ms | 20,0 ms | −80 % |
| Créneaux (index composé) | 7,2 ms | 1,4 ms | −81 % |
| Écriture d’un mouvement | 5,2 ms | 5,9 ms | dans le bruit |

**Q. Pourquoi pas juste un index pour le stock ?**
L’index accélère la recherche de lignes, mais la vue devait de toute façon additionner tous les mouvements avant de filtrer. Il fallait supprimer l’agrégation à la lecture, donc la faire au fil de l’eau (trigger, coût constant par mouvement).

**Q. Expliquez l’index composé `idx_appointment_slot(dock_id, status, starts_at, ends_at)`.**
La requête de conflit filtre `dock_id = ?`, `status = 'active'`, puis une plage sur les horaires. L’index est utilisé de gauche à droite (préfixe gauche) : égalités d’abord, plage ensuite. Dans un autre ordre (horaires en premier), il serait beaucoup moins efficace.

**Q. Un index, ça coûte ?**
Oui : chaque INSERT/UPDATE doit le mettre à jour, et il prend de la place. D’où seulement 8 index secondaires, chacun justifié (créneaux, statut des passages, étapes par période, mouvements, lots FEFO, réservations, avis par date).

**Q. Les clés étrangères sont-elles indexées ?**
Oui, InnoDB crée automatiquement un index sur chaque clé étrangère.

**Q. La table de soldes peut-elle devenir fausse ?**
Elle est écrite dans la même transaction que le mouvement (tout ou rien), seulement par trigger, et le compte de l’application n’a pas le droit d’y écrire. Contrôle : `v_balance_controle` recalcule tout, `validate-data.php` compare : 0 écart.

---

## 11. Le back-end PHP et la sécurité

**Q. Comment est organisé le PHP ?**
Une classe par métier dans `src/` :
- `Database` : `run()`, `all()`, `one()`, `scalar()` (requêtes préparées) et `transaction()` (BEGIN, `@actor_id`, `lock_site`, COMMIT/ROLLBACK).
- `Auth` : `register()`, `login()`, `can()` / `demand()` (droits par profil), `orderAccess()` (un préparateur ne voit que ses commandes).
- `Warehouse` : `appointment()`, `arrive()`, `transition()`, `validateReceipt()`, `suggestions()`, `transfer()`, `adjust()`, `prepare()` (FEFO), `ship()`.
- `Catalog` : `save()` et `delete()` génériques pour les référentiels, avec contrôles.
- `Reports` : `stock()`, `visits()`, `receipts()`, `dashboard()` : filtres, pagination, export CSV.
- `templates/helpers.php` : `dataTable()`, `pagination()`, champs de formulaire ; `h()` échappe l’affichage.

**Q. Injection SQL ?**
Toutes les valeurs passent par des requêtes préparées PDO (`?`), avec `ATTR_EMULATE_PREPARES => false` : la requête et les valeurs sont envoyées séparément, la valeur ne peut pas devenir du SQL.

**Q. Mots de passe ?**
`password_hash()` (bcrypt) à l’inscription, `password_verify()` à la connexion. Jamais en clair, jamais dans le journal. Longueur 10 à 72 caractères : 72 est la limite de bcrypt.

**Q. CSRF, c’est quoi ?**
Un site malveillant qui fait envoyer un formulaire par le navigateur d’un utilisateur connecté. Chaque formulaire contient un jeton aléatoire stocké en session ; PHP le compare avec `hash_equals`. Cookie de session `HttpOnly` et `SameSite=Lax`.

**Q. XSS ?**
Afficher du texte saisi par un utilisateur pourrait injecter du HTML/JS. La fonction `h()` (htmlspecialchars) échappe toute valeur affichée.

**Q. Sessions ?**
`session_regenerate_id(true)` à la connexion (contre le vol de session), nouveau jeton CSRF, destruction de la session à la déconnexion.

**Q. Comment empêchez-vous un profil d’accéder à une page interdite ?**
Les droits sont dans `Auth::RIGHTS` et revérifiés **à chaque page et chaque action** côté serveur, pas seulement dans le menu. Ex. : l’accueil peut faire `arrived → checked → parking → called → departed`, le magasinier seulement `working` et `finished` (`transitionAllowed`).

**Q. Quels droits a le compte SQL de l’application ?**
Moindre privilège : SELECT, EXECUTE, INSERT seul sur les historiques, aucun droit de structure ni d’écriture sur `stock_balance`. Exemple GRANT/REVOKE dans `sql/06_privileges.example.sql`. Les profils (admin, manager…) ne sont pas des comptes SQL : ce sont des lignes de `user_account`.

**Q. Contrôle des saisies, un exemple ?**
Nouveau rendez-vous (`Warehouse::compatible`) : profil autorisé, fin > début, quai du bon type (réception, expédition ou mixte), chauffeur et véhicule du même transporteur, type de véhicule accepté par le quai, tracteur ⇒ remorque, équipements du véhicule présents sur le quai, quai pas en indisponibilité, pas de chevauchement. À la réception : produit froid ⇒ quai et véhicule frigorifiques ; produit dangereux ⇒ chauffeur avec habilitation ADR valide. Côté base : CHECK `ends_at > starts_at` et trigger anti-chevauchement.

---

## 12. Fonctionnalités et consignes du sujet

| Consigne / critère | Où dans Transit |
|---|---|
| Ajouter, modifier, supprimer | Référentiels (formulaires génériques) ; suppression refusée si l’objet est utilisé ; pour les historiques, annulation ou ajustement |
| Rechercher, filtres multicritères | Stock : texte libre (SKU, nom, lot, palette) + article, propriétaire, zone, lot, emplacement + tri ; indicateurs par période ; réceptions « écarts seulement » |
| Statistiques, graphiques | Indicateurs : attente par transporteur (graphique en barres), remplissage par zone (barres), écarts, productivité, DLC proches |
| États / documents | Bon de livraison, lettre de voiture, impression, export CSV |
| Multi-utilisateurs, inscription | Inscription en attente, activation par l’admin, 5 profils |
| 3NF | §3 |
| Historisation automatique | §8 |
| Optimisation + rapport de performance | §10, `docs/performances.md` |
| Données factices en quantité | 90 jours : 1 806 passages, ~25 000 mouvements, 924 commandes |
| Finition (menu, id internes cachés, boutons) | Menu par profil, références métier affichées à la place des id |

**Q. Le sujet demande le front pour 5 parties, vous en avez fait plus ?**
Oui : connexion, quais et rendez-vous, flux de camions, réception, stocks (obligatoires), plus préparation/expédition, traçabilité, indicateurs et portail transporteur.

**Q. Écrivez une requête avec GROUP BY / HAVING.**
```sql
SELECT carrier_name, COUNT(*) passages, AVG(wait_minutes) attente
FROM v_visit
WHERE arrived_at >= ? AND arrived_at < ?
GROUP BY carrier_id, carrier_name
HAVING AVG(wait_minutes) > 30;
```
WHERE filtre les lignes **avant** le regroupement, HAVING filtre les **groupes** après. Utilisée dans Indicateurs, « Transporteurs au-dessus du seuil d’attente ».

---

## 13. Questions pour vérifier que vous avez compris (anti-IA)

Préparez-les **à voix haute**, sans lire.

| Le prof demande… | Ce qu’il attend |
|---|---|
| « Qui a fait quoi dans le groupe ? » | Chacun cite une partie précise qu’il a faite ou vérifiée, avec un exemple concret. |
| « Montrez-moi où est vérifié le chevauchement. » | `sql/04_triggers.sql` (`appointment_no_overlap_insert`) et le contrôle PHP dans `Warehouse::saveAppointmentInside()` (appelée par `appointment()`). |
| « Dessinez-moi au tableau le chemin d’un lot. » | Avis → réception → palette (`receipt_item`) → mouvement d’entrée → transfert → réservation (`pick`) → colis → expédition → camion. |
| « Si je supprime la ligne `CALL lock_site()`, que se passe-t-il ? » | Plus de verrou : deux réservations simultanées pourraient passer le contrôle PHP en même temps. Le trigger bloquerait encore le chevauchement de rendez-vous, mais pas une double réservation de stock. |
| « Si j’enlève le trigger de solde ? » | `stock_balance` ne serait plus mise à jour : le stock affiché deviendrait faux. Le contrôle `v_balance_controle` le détecterait. |
| « Si `event_scheduler` est OFF ? » | Rien n’est archivé automatiquement ; tout reste dans `appointment`. Pas de perte de données. |
| « Pourquoi ce CHECK sur `damaged_qty` ? » | Endommagé ⇒ réserve obligatoire : on ne peut pas enregistrer de casse sans motif écrit pour le transporteur. |
| « Modifiez cette requête pour… » | Savoir lire une requête du projet et la modifier : ajouter un filtre WHERE, un ORDER BY, un GROUP BY. Voir les exercices §15. |
| « Que fait `INSERT … ON DUPLICATE KEY UPDATE` ? » | Insère la ligne ; si la clé primaire existe déjà, met à jour à la place (ici : ajoute la variation au solde existant). |
| « Pourquoi 2 navigateurs pour la démo ? » | Les deux serveurs sont sur 127.0.0.1 : le cookie de session est partagé, une connexion en écraserait une autre. |
| « Vous avez utilisé l’IA ? » | Rester honnête : « On s’est aidé d’outils, mais chaque choix a été discuté et on sait l’expliquer », puis le prouver avec un exemple précis. |

---

## 14. Limites et améliorations

| Limite | Pourquoi on l’a acceptée | Amélioration |
|---|---|---|
| Verrou global | Simple et sûr | Verrous par quai/emplacement |
| Une expédition par commande | Modèle plus simple | Table de répartition commande/expédition |
| Un seul site | Périmètre du sujet | Ajouter un identifiant de site partout |
| 109 triggers d’audit | Traçabilité complète | Limiter aux tables sensibles |
| Données régulières (attentes proches) | Jeu généré pour tester volumes et calculs | Générateur avec aléas réalistes |

## « Pourquoi n’avez-vous pas utilisé… ? »

Reconnaître la notion, dire pourquoi elle n’était pas utile ici, montrer où on l’utiliserait. Ne jamais prétendre l’avoir faite.

| Notion | Réponse |
|---|---|
| FULLTEXT | On cherche des codes courts et des morceaux (« LOT-04 ») ; le full-text découpe en mots et ignore les mots courts. Utile pour les motifs de réserve. |
| Partitionnement | Tables de quelques dizaines de milliers de lignes ; on a préféré l’archivage. Candidat : `stock_movement` par année. |
| Tables temporaires | Nos traitements tiennent en une requête ; MariaDB en crée lui-même (« Using temporary » dans EXPLAIN). |
| Héritage | Les profils ont les mêmes attributs, seuls les droits changent : une table `user_account` avec un rôle. |
| Entités faibles | Les lignes (de commande, d’avis) ont leur propre id + UNIQUE sur la clé composée. |
| Réplication | Hors périmètre ; on a traité la sauvegarde/restauration (`scripts/backup-restore.py`). |

---

## 15. Exercices pour s’entraîner

Répondre **sans regarder**, puis vérifier.

<details><summary>1. Écrire la requête : quantité déjà mise en colis pour chaque prélèvement, y compris ceux sans colis.</summary>

```sql
SELECT p.id, p.qty, COALESCE(SUM(pp.qty), 0) AS en_colis
FROM pick p LEFT JOIN package_pick pp ON pp.pick_id = p.id
GROUP BY p.id, p.qty;
```
LEFT JOIN pour garder les prélèvements sans colis, COALESCE pour afficher 0 au lieu de NULL.
</details>

<details><summary>2. Pourquoi ce test de chevauchement est-il juste : <code>starts_at &lt; :fin AND ends_at &gt; :debut</code> ?</summary>

Deux créneaux se chevauchent si chacun commence avant la fin de l’autre. Une réservation 8 h–11 h chevauche une demande 9 h–10 h, ce que « le début tombe entre 9 h et 10 h » manquerait. Les inégalités strictes autorisent deux créneaux qui se touchent (fin 10 h, début 10 h).
</details>

<details><summary>3. Écrire un trigger qui refuse une quantité commandée supérieure à 1 000.</summary>

```sql
DELIMITER $$
CREATE TRIGGER order_line_max BEFORE INSERT ON order_line FOR EACH ROW
BEGIN
  IF NEW.qty > 1000 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantité trop grande';
  END IF;
END$$
DELIMITER ;
```
</details>

<details><summary>4. Écrire une fonction qui renvoie le nombre de passages d’un transporteur.</summary>

```sql
DELIMITER $$
CREATE FUNCTION nb_passages(p_carrier INT) RETURNS INT
READS SQL DATA
BEGIN
  RETURN (SELECT COUNT(*) FROM truck_visit v JOIN vehicle ve ON ve.id = v.vehicle_id
          WHERE ve.carrier_id = p_carrier);
END$$
DELIMITER ;
SELECT nb_passages(1);
```
</details>

<details><summary>5. Remplissage par zone : écrire le GROUP BY.</summary>

```sql
SELECT l.zone_name, SUM(u.used_pallets) / SUM(l.max_pallets) AS taux
FROM v_location l JOIN v_location_usage u ON u.id = l.id
GROUP BY l.zone_id, l.zone_name;
```
`v_location` donne la zone de chaque emplacement par jointure, `v_location_usage` ce qu’il contient.
</details>

<details><summary>6. Quelle forme normale viole une table <code>emplacement(code, allee, zone, condition_zone)</code> ?</summary>

3NF : `condition_zone` dépend de `zone`, qui dépend de `allee`, qui dépend de la clé `code` : dépendance transitive. On sort `zone(code, condition)` dans sa propre table.
</details>

<details><summary>7. Écrire l’évènement qui appelle une procédure chaque semaine.</summary>

```sql
CREATE EVENT ev_hebdo ON SCHEDULE EVERY 1 WEEK
STARTS CURRENT_DATE + INTERVAL 1 DAY
DO CALL archive_appointments(365);
```
Puis `SET GLOBAL event_scheduler = ON;`.
</details>

<details><summary>8. Lire un EXPLAIN : que signifient <code>ALL</code>, <code>ref</code>, <code>range</code>, <code>&lt;derived&gt;</code> ?</summary>

`ALL` : toute la table est lue. `ref` : accès par index sur une égalité. `range` : accès par index sur une plage. `<derived>` : résultat d’une sous-requête ou d’une vue matérialisée en table temporaire.
</details>

---

**Pièces à ouvrir si le prof veut voir** : `sql/02_vues.sql` (vues), `sql/03_procedures.sql` (lock_site, trace_lot), `sql/04_triggers.sql` (triggers), `sql/08_historisation.sql` (évènement), `sql/09_optimisation.sql` (soldes, fonction), `src/Warehouse.php` (FEFO, réception), `src/Auth.php` (droits), `docs/performances.md` (mesures), phpMyAdmin (Procédures stockées, Évènements, Déclencheurs).
