# Transit — conducteur oral

**0:00–5:00 · Projection de Transit-diapo.html.** Six diapositives sur le backend et la base. **5:00–10:00 · Application dans le navigateur.** À 5:00, quitter le plein écran et basculer vers Transit. **10:00–20:00 · Questions du professeur.** Ouvrir [le diaporama](Transit-diapo.html), l’application et [le parcours illustré](Parcours-application.pdf) pour la répétition. [Transit.pdf](../../docs/soutenance/Transit.pdf) est la copie statique des six diapositives.

## Première partie — paroles et diapositives dans le même ordre

**1 · 0:00–0:35 · Transit.** « Un client nous donne un lot. Peut-on retrouver le camion qui l’a emporté ? C’est la question qui a guidé notre base. Le navigateur envoie les formulaires au backend PHP. PHP contrôle le profil et les valeurs, puis utilise PDO pour interroger MariaDB. Une opération qui touche plusieurs tables, comme valider une réception, est regroupée dans une transaction. Pour expliquer le modèle, prenons une commande dont il faut répartir le contenu. »

**2 · 0:35–1:30 · Où stocker la quantité mise en colis ?** Pointer les douze unités. « Un prélèvement fournit douze unités. Sept vont dans le premier colis et cinq dans le second. Si on enregistre seulement douze sur le prélèvement, on perd la répartition. Si on enregistre seulement sept sur le colis, on ne sait plus quel prélèvement l’a alimenté lorsqu’il en contient plusieurs. La quantité appartient donc à l’association. Les deux minima zéro permettent d’ouvrir un colis ou un prélèvement avant le conditionnement. À l’expédition, une règle supplémentaire vérifie que les quantités sont entièrement réparties. »

**3 · 1:30–2:20 · Une association devient une table.** « Dans le MLD, package_pick matérialise cette relation N:N. Les deux clés étrangères garantissent que le colis et le prélèvement existent. Leur couple est unique et détermine la quantité affectée. À l’inverse, pour le lien 1:N entre société et chauffeur, il suffit de placer la clé de la société sur le chauffeur. Pour normaliser les sorties de stock, on applique le même raisonnement sur les dépendances. Une sortie référence son prélèvement, depuis lequel une vue retrouve la fraction reçue, l’emplacement et la quantité. »

**4 · 2:20–3:15 · Qui enregistre le changement ?** « Quand le responsable modifie le téléphone d’un transporteur, PHP transmet l’UPDATE. Le trigger AFTER UPDATE lit l’ancien et le nouveau contenu et inscrit le changement dans audit_log, avec l’auteur de l’opération. Cette règle s’applique à chaque modification de cette table. La procédure trace_lot répond à un autre besoin. Elle est appelée explicitement pour joindre réception, mouvements, commande et camion lorsqu’un utilisateur demande l’historique du lot. Enfin, le stock disponible est calculé depuis les mouvements et les réservations. On évite ainsi de tenir deux soldes qu’il faudrait synchroniser. »

**5 · 3:15–4:12 · Deux utilisateurs demandent le même quai.** « Les deux utilisateurs voient initialement le même créneau libre. Le serveur ouvre une transaction et appelle lock_site, qui prend un verrou avec SELECT FOR UPDATE. La première demande vérifie le créneau et enregistre le rendez-vous. Quand la deuxième obtient le verrou, elle relit le planning et détecte le chevauchement. Si un contrôle échoue, la transaction est annulée. Le compromis est volontaire pour notre entrepôt : on protège des décisions qui dépendent de plusieurs lignes, mais deux écritures indépendantes peuvent aussi s’attendre. »

**6 · 4:12–5:00 · Combien coûte une recherche ?** « Sur une base de dix mille passages, nous avons effectué une chauffe puis dix exécutions par requête. Les médianes affichées incluent la récupération des résultats. Chercher la disponibilité d’un quai prend environ 1,26 ms, retrouver l’historique d’un lot 38,45 ms, et sélectionner le prélèvement FEFO 65,78 ms. On utilise EXPLAIN pour comprendre le plan d’exécution et l’utilité des index. Ces chiffres mesurent SQL dans notre environnement. Passons maintenant à l’application pour suivre un lot réellement enregistré. » **Quitter le diaporama.**

## Deuxième partie — cinq minutes dans l’application

Préparer les sessions dans des profils de navigateur distincts avant le passage. Le parcours complet avec les identifiants, champs, boutons et captures est dans [Parcours-application.pdf](Parcours-application.pdf). Pour la démonstration courte, utiliser la base préparée indiquée dans le PDF. Les écritures de création détaillées dans le guide servent à la répétition sur une base neuve.

| Temps absolu | Écran à montrer | Phrase ou geste |
|---|---|---|
| 5:00–5:40 | Comptes puis planning | Montrer la liste des profils depuis la session admin. Basculer sur le responsable et montrer la journée du 22/10/2026. Expliquer qui planifie et qui reçoit le camion. |
| 5:40–6:35 | Avis fournisseur | Depuis la session magasinier, ouvrir Référentiels, rubrique Avis fournisseurs, rechercher ORAL-CAFE-AVIS. Montrer sa ligne attendue de 20 unités de café. Pour illustrer la saisie, ouvrir « Ajouter une fiche » et montrer les champs, puis revenir à l’avis existant. |
| 6:35–7:25 | Réception et stock | Retrouver ORAL-CAFE-REC et ORAL-CAFE-PAL. Montrer 18 acceptées et 2 endommagées, puis le transfert de 3 unités. Expliquer pourquoi les unités endommagées ne deviennent pas disponibles. |
| 7:25–8:30 | Commande et préparation | Montrer ORAL-CAFE-CMD, sa quantité de 10 et son affectation à Noah Bernard. Expliquer la réservation FEFO, le colis, puis la confirmation du chargement. Montrer le bon de livraison déjà généré. |
| 8:30–9:45 | Traçabilité des lots | Choisir ORAL-CAFE-LOT puis « Retracer le lot ». Montrer la réception, le transfert, la sortie de 10 unités et ORAL-CAFE-SORTIE. Dire : « Voici la réception d’origine et le passage du camion sortant pour le même lot. » |
| 9:45–10:00 | Garder la trace à l’écran | « Nous sommes partis de la structure de la base et nous venons de retrouver la chaîne complète dans l’application. Nous sommes prêts pour vos questions. » |

**Répartition possible.** Eliott explique le modèle jusqu’à 2:20. Semih présente audit, concurrence et mesures jusqu’à 5:00. Thomas pilote la démonstration. Répéter avec les changements de fenêtre, puis relire [Questions-prof.md](Questions-prof.md) pour les dix minutes d’échange.
