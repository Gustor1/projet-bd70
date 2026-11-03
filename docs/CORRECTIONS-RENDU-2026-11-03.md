# Corrections du rendu BD70 — 3 novembre 2026

Le use case corrigé après retour du professeur est la référence des responsabilités. Le dernier MCD réalisé est conservé, conformément à la demande du groupe, en attendant le retour de l’enseignant.

## Corrections réalisées

- Administrateur technique limité aux comptes et au journal ; responsable chargé des référentiels, du planning et des commandes.
- Affectation/réaffectation en brouillon par le responsable, sans réservation. Lancement FEFO et exécution par le magasinier affecté ; refus des identifiants d’une autre commande et contrôle des parents des colis.
- Arrivée/contrôle/appel/départ par l’accueil ; début et fin à quai par le magasinier. Les menus et les requêtes directes suivent ces droits.
- Portail transporteur : création, modification et annulation des rendez-vous de sa société. Chauffeur, véhicule et remorque sont revérifiés côté serveur ; aucun accès aux routes internes.
- Sorties normalisées : seule la référence au prélèvement est enregistrée, avec les informations propres à l’événement. Fraction, emplacement et quantité sont projetés par v_stock_movement. Le CHECK impose leur absence physique pour une sortie ; l’import ancien est vérifié et normalisé par trigger.
- Références documentaires, dictionnaire et MLD actualisés ; rapport PDF de 11 pages et recueil de 23 pages reconstruits puis rendus et inspectés.
- Catalogue : les références SQL inverses sont recherchées dans la seule base courante et mises en cache pendant la requête, pour éviter les lenteurs observées avec de nombreuses bases locales de test.

## Données et utilisation locale

La démonstration active est `bd70_demo_corrige_20261103b`, sur http://127.0.0.1:8070. La copie a transféré les 41 tables et comparé tous les faits métier (sorties via leur projection). Les checksums de `bd70_demo_rich_final` restent identiques avant/après ; cette source est conservée. La configuration précédente est sauvegardée dans `.local/corrections-rendu/config-avant.php`, hors Git. Le retour arrière consiste à rétablir l’ancien dbname et à utiliser la version du code correspondante : le nouveau code requiert le schéma corrigé.

Pour le pilotage, se connecter avec `manager@bd70.test` ; pour l’exécution avec `warehouse@bd70.test` ; pour l’accueil avec `gate@bd70.test`. L’administrateur gère les comptes. Mot de passe pédagogique : `Entrepot2026!`. Un transporteur se crée/active depuis Utilisateurs avec son rattachement à une société ; les comptes internes gardent ce rattachement vide.

## Vérifications de la version finale

Preuves dans `livrables/preuves/corrections-rendu-2026-11-03/` : commandes/codes de sortie, JSON, captures, plans SQL et empreintes des sources.

| Vérification | Résultat |
|---|---|
| Syntaxe PHP | 43 fichiers, aucun échec |
| Intégration métier, SQL et concurrence | 64/64 |
| Compléments métier | 23/23 |
| Régressions de protection des faits | 14/14 |
| Droits, isolation et normalisation | 18/18 |
| Navigateur : droits, requêtes directes et portail | 32/32 |
| Parcours complet avec changement de profils | 32/32 |
| Horloge | 8/8 |
| Import riche sur base neuve et intégrité | 83 contrôles, aucune anomalie |
| Copie migrée | 41 tables, faits identiques, source inchangée |
| Sauvegarde/restauration | 41 tables identiques, 120 triggers, 2 procédures, audit déclenché dans la copie |
| Démonstration en lecture | Connexion réussie pour les quatre profils internes |
| Performances | Huit requêtes, chauffe puis dix exécutions sur base distincte de 10 000 passages |
| PDF | 11 + 23 pages rendues et inspectées |

Les premiers essais du nouveau parcours ont révélé des attentes de navigation manquantes et une sélection de prélèvement absente dans le script. La recette finale sur bases neuves corrige ces problèmes et passe. La requête de métadonnées trop large a également été corrigée. Les anciens résultats racine restent conservés ; les preuves de cette correction sont dans leur dossier propre.

## Modèle entité-association en attente

Le PDF et les sources du dernier MCD restent inchangés. Le SQL et les MLD sont cohérents avec le schéma installé. Le contrôle comparant le MCD conservé au nouveau schéma signale quatre écarts attendus : couverture du nouveau lien `user_account.carrier_id`, couverture de cette colonne, et deux cardinalités physiques des mouvements devenues conditionnelles aux sorties. Ces différences sont documentées dans `modeles.json` et ne sont pas présentées comme une validation du MCD actuel. Elles seront à intégrer lors du retour enseignant ; le dernier MCD reste le document de travail demandé.

Aucun commit, push, merge ni déploiement public. Pas de test sur téléphone physique. La conformité pédagogique finale et la note restent appréciées par l’enseignant.
