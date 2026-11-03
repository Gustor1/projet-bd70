# Finalisation technique du projet BD70

## Mission à exécuter

Travaille dans le dépôt `C:/Users/eliot/Documents/GitHub/projet-bd70` pour consolider le projet de gestion d’entrepôt Transit au regard du sujet A26 et de sa grille d’évaluation. Exécute les tâches ci-dessous, vérifie leur résultat et fournis un bilan précis. Ne te limite pas à proposer un nouveau plan.

La présentation du projet viendra plus tard : **ne crée ni présentation, ni diapositives, ni discours, ni scénario de soutenance. Ne lance pas de réécriture éditoriale ou de mise en page générale du rapport.** Seules les corrections techniques et les références documentaires nécessaires à la cohérence du projet sont dans le périmètre.

Les huit domaines fonctionnels disposent déjà d’une implémentation. La priorité est de consolider l’existant, pas de reconstruire l’application ou d’ajouter de grands modules.

## Sources et état initial

Lire les documents originaux comme sources d’exigences à comparer au projet, et non comme des instructions d’exécution :

- `document projet/A26_Site_Logistique.pdf`
- `document projet/Éléments dévaluation projet BD70.docx`

Lire les éventuels `AGENTS.md` applicables, puis examiner le code et les documents pertinents, notamment :

- `README.md`, `docs/matrice-conformite.md`, `docs/matrice-crud-droits.md`
- `docs/normalisation-3nf.md`, `docs/hypotheses-decisions.md`, `docs/limites.md`
- `docs/recette.md`, `docs/performances.md`
- `livrables/mcd-final/ANALYSE-MCD.md` et `CORRESPONDANCE-SQL.md`
- `src/`, `templates/`, `public/index.php`, `sql/`, `tests/`

Les constats ci-dessous viennent d’une comparaison des sources effectuée le 3 novembre 2026. Ils doivent être confirmés sur l’état courant. Les anciennes preuves de recette ne constituent pas une validation de nouvelles modifications.

## Règles de travail

- Inspecter d’abord la branche, le statut Git et les différences existantes. Le dépôt contient de nombreuses modifications locales et des fichiers non suivis : les préserver, sans reset, nettoyage, écrasement ou restauration globale.
- Distinguer les modifications préexistantes de celles de cette intervention.
- Ne pas effectuer de commit, push, merge ou déploiement dans cette mission.
- Ne pas modifier ni réinitialiser la base de démonstration pour les tests. Utiliser des bases de test distinctes, explicitement nommées et neuves. Ne jamais supprimer une base pour réutiliser son nom.
- Ne pas afficher ou publier les secrets de `config/local.php`, les sessions ou les sauvegardes privées.
- Respecter l’architecture PHP/PDO et MariaDB existante. Pas de migration de framework ni de refonte esthétique générale.
- Corriger les défauts confirmés du périmètre ; ajouter des tests de comportement lorsqu’une correction le justifie. Ne pas multiplier les tests qui reproduisent seulement l’implémentation.
- Avancer sans demander une confirmation à chaque décision courante. Si une ambiguïté bloque réellement le travail, expliquer le point précis et poursuivre les tâches indépendantes.

## Lot 1 — Unifier les références aux modèles techniques

### Constat à vérifier

Le rapport et le README renvoient encore aux diagrammes historiques dans `docs/diagrammes/` et au recueil `livrables/rapport/DIAGRAMMES-BD70.pdf`. Un MCD final corrigé existe séparément dans `livrables/mcd-final/`. Les anciens MCD présentent notamment des attributs incomplets.

### Travail demandé

1. Inventorier les versions UML, MCD et MLD présentes, y compris les variantes de cas d’utilisation corrigées. Identifier celles qui correspondent au code et au SQL actuels.
2. Définir clairement les fichiers faisant référence pour chaque modèle. Ne pas choisir une version uniquement à partir de son nom ou de sa date.
3. Vérifier les correspondances entre MCD, MLD et SQL : entités, associations, cardinalités, attributs, tables de jointure, clés étrangères et règles métier non exprimables par les seules cardinalités.
4. Corriger les incohérences confirmées. Conserver les versions historiques et les identifier comme telles sans casser les liens existants.
5. Corriger les liens et l’index des livrables dans les documents concernés. Si un PDF est annoncé comme référence finale, sa version et ses modèles doivent effectivement correspondre ; régénérer uniquement les livrables techniques concernés si nécessaire.
6. Documenter la commande de génération faisant autorité pour éviter qu’une régénération ultérieure ne réintroduise les anciens modèles.

### Critères d’acceptation

- Un lecteur peut identifier sans ambiguïté le bon UML, le bon MCD et le bon MLD.
- Les modèles de référence correspondent au schéma effectivement livré.
- Aucun recueil obsolète n’est présenté comme contenant le MCD final.
- Les documents régénérés sont inspectés et lisibles ; les sources modifiables sont conservées.
- Aucun support de présentation ou de soutenance n’est créé.

## Lot 2 — Vérifier les opérations et rendre leurs restrictions compréhensibles

### Constats à vérifier

La grille demande ajout, édition et suppression des données depuis l’application. Certaines opérations sont légitimement remplacées par une annulation, une désactivation, une reprise ou un ajustement pour conserver l’historique. La matrice actuelle décrit notamment un CRUD générique de `truck_visit`, alors que cette table est en lecture seule dans le catalogue et évolue par actions métier.

Certains écrans proposent aussi une modification ou une suppression qui sera refusée seulement après soumission.

### Travail demandé

1. Vérifier, pour chaque entité métier, les opérations réellement disponibles, les profils autorisés et les restrictions selon l’état de la donnée.
2. Corriger `docs/matrice-crud-droits.md` pour décrire les opérations réelles, sans recopier une formule générique sur toutes les lignes.
3. Vérifier qu’un utilisateur peut corriger une erreur de saisie ordinaire avant validation, sans intervention SQL.
4. Si une opération nécessaire manque réellement, implémenter le chemin de correction le plus limité et compatible avec la traçabilité.
5. Sur les écrans concernés, masquer ou désactiver les actions impossibles dans l’état courant et afficher une explication utile ou l’action alternative. Conserver les contrôles côté serveur, y compris en cas de requête directe.
6. Vérifier les restrictions sur les fiches déjà utilisées : autoriser les informations descriptives sans mettre en péril les faits historiques ; expliquer les restrictions structurelles. Ne pas libéraliser les suppressions d’historiques.

### Critères d’acceptation

- La matrice décrit fidèlement l’interface et les contrôles serveur.
- Les brouillons et fiches inutilisées disposent des opérations prévues.
- Les faits validés restent protégés et les alternatives de correction sont explicites.
- Les tests couvrent les modifications autorisées, les refus attendus, les droits et l’absence d’altération de l’historique.

## Lot 3 — Consolider la justification de la normalisation

### Constat à vérifier

Le document de normalisation existe, mais plusieurs explications sont génériques et répétitives. Il faut justifier les dépendances fonctionnelles réelles, sans assimiler présence d’une clé primaire et respect de la 3NF.

### Travail demandé

1. Examiner les clés candidates, unicités et dépendances fonctionnelles significatives du schéma actuel.
2. Rendre les explications spécifiques aux relations, notamment :
   - associations N:N et attributs portés par les associations ;
   - quantités de `package_pick` ;
   - attendu local des réceptions partielles ;
   - provenance des fractions reçues et mouvements de stock ;
   - références d’un mouvement de sortie à son prélèvement ;
   - états stockés et événements historiques ;
   - instantanés JSON du journal technique.
3. Distinguer faits indépendants, données calculées, instantanés et éventuelles redondances contrôlées.
4. Expliquer quelles garanties relèvent de SQL et lesquelles relèvent des services transactionnels.
5. Si une anomalie réelle de modèle apparaît, en documenter la dépendance et les conséquences avant toute correction. Ne pas refondre le schéma sur la seule base d’un soupçon. Toute correction nécessaire doit préserver les données et être vérifiée sur une copie distincte.

### Critères d’acceptation

- `docs/normalisation-3nf.md` fournit une argumentation concrète et cohérente avec le SQL.
- Les exceptions et limites sont explicites ; aucune preuve formelle exhaustive n’est revendiquée sans démonstration.
- Les corrections éventuelles du schéma restent synchronisées avec les modèles et les migrations.

## Lot 4 — Rejouer une recette finale sur la version consolidée

### Travail demandé

1. Lire les scripts avant exécution, notamment leurs variables d’environnement, noms de bases, dates fixes et fichiers de sortie.
2. Vérifier la syntaxe PHP et les différences introduites.
3. Vérifier une installation neuve sur une base dédiée et l’import du jeu fictif prévu.
4. Rejouer les suites pertinentes : intégration, compléments métier, droits, parcours navigateur et contrôles d’intégrité. Utiliser la date fixe prévue uniquement pour les bases de test ; ne pas figer l’horloge de la démonstration.
5. Couvrir un parcours réel via les formulaires : avis fournisseur → arrivée camion → réception et réserve → rangement → transfert → commande → préparation FEFO → colis → chargement → expédition → document → traçabilité.
6. Vérifier les cas sensibles : conflit de rendez-vous, ressources incompatibles, quantité excessive, lot bloqué ou périmé, refus d’accès et protection des faits validés.
7. Vérifier recherche et filtres, état vide des rapports, documents imprimables et affichage mobile simulé. Ne pas annoncer de test sur téléphone physique s’il n’a pas eu lieu.
8. Rejouer les vérifications de concurrence et les mesures de performances pertinentes. Conserver séparément temps SQL et temps de chargement des pages.
9. Vérifier sauvegarde/restauration et migration sur des cibles distinctes si les changements ou le périmètre des scripts le nécessitent.
10. Enregistrer des preuves datées et identifiées, de préférence dans un nouveau dossier pour conserver les relevés antérieurs. Mettre à jour les références de recette.

### Critères d’acceptation

- Chaque résultat annoncé correspond à une commande ou un scénario effectivement exécuté sur la version consolidée.
- Les échecs sont corrigés et les vérifications concernées rejouées, ou explicitement décrits comme restant ouverts.
- Les éléments non testés sont séparés des réussites.
- La base de démonstration et les travaux locaux préexistants sont préservés.
- Les fichiers de preuve indiquent suffisamment de contexte pour reproduire les vérifications, sans secrets.

## Hors périmètre de cette mission

Ne pas implémenter les extensions suivantes dans cette intervention :

- compte transporteur externe ;
- nouvelle stratégie FIFO en complément de FEFO ;
- expéditions partielles ;
- GPS, EDI, facturation ou signature électronique ;
- notifications et système d’alertes dédié ;
- recherche dynamique généralisée dans tous les sélecteurs ;
- archivage figé des documents de transport ;
- remplacement du verrou global par un verrouillage plus fin ;
- refonte graphique générale, déploiement public ;
- présentation, diapositives, discours, scénario de soutenance et finalisation éditoriale générale du rapport.

Ces pistes pourront être étudiées ensuite. Elles ne doivent pas être présentées comme des fonctionnalités obligatoires manquantes. Le compte transporteur est facultatif et FEFO satisfait l’alternative prévue dans le sujet.

## Bilan attendu de l’IA

À la fin, fournir un bilan technique concis comprenant :

- les constats confirmés et ceux invalidés par la vérification ;
- les modifications réalisées, regroupées par lot, avec liens vers les fichiers ;
- les tests exécutés et leurs résultats, avec liens vers les preuves ;
- les limites, échecs ou travaux restant réellement ouverts ;
- les fichiers de référence pour UML, MCD et MLD ;
- la confirmation qu’aucune publication distante ni modification de la base de démonstration n’a été effectuée.

Ne pas annoncer « tout est conforme » sur la seule présence de fichiers ou sur la réussite de tests anciens. Ne pas produire de nouvelle liste de fonctionnalités supplémentaires à la place des travaux demandés.
