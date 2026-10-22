# Démonstration de 10 minutes (modalité A26 à confirmer)

1. 0:00–1:00 : connexion accueil, planning du 22/10/2026 ; expliquer les créneaux adjacents et le refus de chevauchement.
2. 1:00–2:00 : arrivée sans rendez-vous, contrôle documentaire, parking, appel et début d'opération.
3. 2:00–4:00 : rôle magasinier ; avis, réception et ligne, deux lots ou palettes ; avarie avec réserve, proposition d'emplacement et validation. Un second clic ne double pas le stock.
4. 4:00–5:00 : stock filtré par article/propriétaire/zone ; transfert et historique. Montrer le refus d'un rangement froid dans la zone ambiante.
5. 5:00–7:00 : commande, FEFO et affectation ; confirmer, créer un colis et son contenu ; camion sortant au chargement ; expédition et impression du bon.
6. 7:00–8:00 : trace du lot A, reçu deux fois, présent sur plusieurs emplacements et utilisé dans deux commandes.
7. 8:00–9:00 : statistiques du 22/10/2026 : 80 minutes d'occupation, 2 lignes avec écart sur 4 ; stock actuel par zone et DLC.
8. 9:00–10:00 : modèle/normalisation, déclencheur d'audit, quatre courses concurrentes et une comparaison avant/après de l'index.

Pour un déroulement reproductible entièrement enregistré par le navigateur : `tests/parcours.cjs`, sur une base de test séparée et un serveur dédié au port 8071. Les références créées y portent un préfixe UI. Ne pas exécuter les tests d'intégrité destructurant le jeu de test sur la démonstration présentée.

Questions à préparer : différence PK/clé candidate ; pourquoi la table prélèvement porte une quantité ; différence fournisseur/propriétaire/transporteur ; rôle du verrou et du rollback ; pourquoi le stock n'est pas un champ éditable ; politique de suppression ; calcul des unités d'un taux.
