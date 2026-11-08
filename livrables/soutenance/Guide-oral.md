# Transit — conducteur oral

**0:00–5:00 · Projection de Transit-diapo.html.** Sept diapositives sur le backend et la base. **5:00–10:00 · Application dans le navigateur.** À 5:00, quitter le plein écran et basculer vers Transit. **10:00–20:00 · Questions du professeur.** Ouvrir [le diaporama](Transit-diapo.html), l’application et [le parcours illustré](Parcours-application.pdf) pour la répétition. [Transit.pdf](../../docs/soutenance/Transit.pdf) est la copie PDF vectorielle des sept diapositives.

## Première partie — paroles et diapositives dans le même ordre

Environ 490 mots, soit 3 min 50 à 130 mots par minute : plus d’une minute de marge pour respirer et montrer l’écran.

**1 · 0:00–0:35 · Transit.** « Un client nous donne un lot. Peut-on retrouver le camion qui l’a emporté ? C’est la question qui a guidé notre base. Le navigateur envoie les formulaires au backend PHP. PHP contrôle le profil et les valeurs, puis utilise PDO pour interroger MariaDB. Une opération qui touche plusieurs tables, comme valider une réception, est regroupée dans une transaction. Pour expliquer le modèle, prenons une commande dont il faut répartir le contenu. »

**2 · 0:35–1:20 · Où stocker la quantité mise en colis ?** Pointer les douze unités. « Un prélèvement fournit douze unités. Sept vont dans le premier colis et cinq dans le second. Si on enregistre seulement douze sur le prélèvement, on perd la répartition. Si on enregistre seulement sept sur le colis, on ne sait plus quel prélèvement l’a alimenté. La quantité appartient donc à l’association, en notation de Chen. Les deux minima zéro permettent d’ouvrir un colis ou un prélèvement avant le conditionnement. »

**3 · 1:20–2:00 · Une association devient une table.** « Dans le schéma relationnel, package_pick matérialise cette relation N:N, comme le cours le demande : une table de jointure avec deux clés étrangères, l’unicité du couple et la quantité. À l’inverse, pour le lien 1:N entre société et chauffeur, il suffit de placer la clé de la société du côté N, sur le chauffeur. Notre schéma compte 42 tables et 66 clés étrangères. »

**4 · 2:00–2:50 · Que fait la base sans qu’on le lui demande ?** « Trois mécanismes. Un trigger BEFORE INSERT refuse par SIGNAL un rendez-vous qui chevauche un autre sur le même quai, même si quelqu’un écrit directement en SQL. Des triggers AFTER UPDATE écrivent l’ancienne et la nouvelle valeur dans le journal d’audit. Enfin, pour l’historisation, un évènement planifié appelle chaque nuit une procédure qui déplace, dans une transaction, les vieux rendez-vous vers une table d’archive ; une vue UNION ALL réunit les deux. Le stock, lui, n’est jamais stocké : des vues le calculent depuis les mouvements. »

**5 · 2:50–3:35 · Deux utilisateurs demandent le même quai.** « Les deux utilisateurs voient le même créneau libre. Le serveur ouvre une transaction et appelle lock_site, qui prend un verrou avec SELECT FOR UPDATE. La première demande vérifie le créneau et fait COMMIT. Quand la deuxième obtient le verrou, elle relit le planning, détecte le chevauchement, et sa transaction fait ROLLBACK. Le compromis : deux écritures indépendantes peuvent aussi s’attendre. »

**6 · 3:35–4:15 · Peut-on faire confiance aux données ?** « La base est en troisième forme normale : la zone d’un emplacement se retrouve par jointure, jamais recopiée, et aucun total calculé n’est stocké. Trois dénormalisations sont assumées, comme l’état courant d’un passage, et justifiées dans le rapport. Côté sécurité, le compte SQL de l’application n’a aucun droit de structure et seulement INSERT sur les historiques ; le script de droits montre GRANT et REVOKE. Les requêtes sont préparées et les mots de passe hachés. »

**7 · 4:15–5:00 · Combien coûte une recherche ?** « Sur une base de dix mille passages, une chauffe puis dix exécutions par requête. Chercher la disponibilité d’un quai prend 0,50 ms, l’historique d’un lot 23,38 ms, la sélection FEFO 34,64 ms. L’index composé sur les créneaux fait passer la recherche de 4,00 à 0,90 ms : EXPLAIN montre un accès par plage au lieu de toutes les lignes du quai. Passons à l’application pour suivre un lot réellement enregistré. » **Quitter le diaporama.**

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

**Répartition possible.** Eliott explique le modèle jusqu’à 2:00. Semih présente automatisation, concurrence, normalisation et mesures jusqu’à 5:00. Thomas pilote la démonstration. Répéter avec les changements de fenêtre, puis relire [Questions-prof.md](Questions-prof.md) pour les dix minutes d’échange.
