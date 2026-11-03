# Cas d’utilisation BD70 — version révisée

## Fichiers

- **BD70-USE-CASE-V2.drawio** : deux pages modifiables dans Draw.io / diagrams.net. Les acteurs, ovales, cadres, textes et connecteurs sont des objets natifs.
- **BD70-USE-CASE-V2.pdf** : deux pages A3 paysage, vectorielles, pour la lecture et le rendu.
- **BD70-USE-CASE-V2.html** : les deux pages dans un navigateur, avec défilement horizontal.
- **01-vue-generale.svg**, **02-relations-metier.svg** : exports vectoriels.
- **apercu-1.png**, **apercu-2.png** : aperçus rendus à partir du PDF.

Ouvrir le Draw.io via Fichier > Ouvrir depuis > Appareil. Les deux pages se sélectionnent dans les onglets. Enregistrer une copie sous un autre nom avant modification : le générateur reconstruit les sorties V2. Les versions précédentes restent conservées dans leurs dossiers.

## Page 1 — diagramme principal

Les huit domaines du sujet sont présents. La couleur des ovales est uniforme : elle n’indique pas une distinction entre fonctions réalisées et données simulées. Le diagramme représente le périmètre de l’application du dépôt, qui dépasse le minimum Web demandé.

Les répétitions d’un personnage sont des occurrences du même acteur, destinées à réduire les croisements. Le schéma d’héritage en bas s’applique à toutes ses occurrences. « Accueil » désigne l’agent d’accueil et « Responsable » le responsable d’exploitation. « Personnel » est un acteur général de modélisation, pas un profil supplémentaire dans la base.

- L’accueil et le magasinier reprennent les fonctions communes du Personnel.
- Le responsable reprend les fonctions de l’accueil et du magasinier.
- L’administrateur reprend les fonctions du responsable et administre les comptes.
- Le personnel non inscrit demande un compte ; celui-ci doit être activé par l’administrateur avant connexion.
- Le portail Transporteur, facultatif dans l’énoncé, n’est pas réalisé et ne figure pas comme acteur.

Les associations expriment les possibilités fonctionnelles, sous réserve des règles métier et des droits sur l’objet. Par exemple, le magasinier confirme uniquement une préparation qui lui est affectée. Les triangles creux expriment l’héritage de capacités du logiciel, pas un organigramme d’entreprise.

## Page 2 — relations sélectionnées

Cette vue complète la page 1 : les associations aux cas généraux et les droits hérités restent applicables. Elle n’est pas un diagramme d’enchaînement des étapes.

- Créer ou déplacer un rendez-vous inclut les vérifications de compatibilité véhicule/quai et de disponibilité du créneau.
- Annuler un rendez-vous est un cas distinct. L’annulation conserve ses propres contrôles (statut et utilisation du rendez-vous) mais ne recherche pas de créneau disponible.
- Traiter une arrivée sans rendez-vous étend l’enregistrement d’une arrivée lorsque aucun rendez-vous n’est associé. C’est une modélisation de la variante du scénario, pas une opération supplémentaire imposée à toutes les arrivées.
- Émettre une réserve étend la réception lorsqu’une réserve doit être consignée. Les écarts et avaries restent dans le scénario de réception ; ils ne sont pas assimilés automatiquement à une réserve.
- Lancer la préparation inclut la réservation du stock selon FEFO.
- Expédier inclut les contrôles du chargement : colis, validité des lots, compatibilité et capacité du véhicule.
- L’édition des documents reste une action accessible séparément : le diagramme n’impose pas leur impression à chaque chargement.

## Correspondance avec les consignes et le code

| Domaine | Cas de la vue générale | Éléments du dépôt consultés |
|---|---|---|
| A — Authentification | Inscription, connexion/déconnexion, comptes | `src/Auth.php`, `public/index.php` |
| B — Quais et rendez-vous | Quais, rendez-vous, planning | `src/Catalog.php`, `src/Warehouse.php`, `templates/planning.php` |
| C — Transport | Transporteurs, chauffeurs, véhicules | `src/Catalog.php` |
| D — Camions | Suivi de l’arrivée au départ et opérations à quai | `src/Warehouse.php` |
| E — Réception | Avis, lots, écarts, réserves et rangement | `src/Catalog.php`, `src/Warehouse.php` |
| F — Stocks | Structure, articles, propriétaires, recherche, transfert, inventaire | `src/Catalog.php`, `src/Warehouse.php` |
| G — Commandes | Préparation, colis, expédition, documents | `src/Warehouse.php`, `public/index.php` |
| H — Pilotage | Traçabilité, indicateurs et rapports | `public/index.php`, `templates/layout.php` |

Références pédagogiques : sujet `document projet/A26_Site_Logistique.pdf`, grille `document projet/Éléments dévaluation projet BD70.docx`, cours `document cours/BD70_A25 (4).pptx`, diapositives 204–210. Leurs extractions sont conservées sous `docs/sources/`.

Le sujet demande un diagramme UML et un modèle de données couvrant les huit domaines. Le cours présente frontière, acteurs, associations, généralisation, inclusion, extension et scénarios textuels. Aucune obligation d’utiliser une relation artificielle pour chaque cas n’est ajoutée.

Les scénarios existants sont dans `docs/02-cas-utilisation.md` ; leur ancienne référence graphique est historique. Les nouveaux intitulés regroupent ou explicitent certains de ces cas sans modifier le fonctionnement de l’application.

## Reconstruction et vérification

```powershell
python scripts/build-usecase-v2.py
pdftoppm -r 110 -png livrables/use-case-v2/BD70-USE-CASE-V2.pdf livrables/use-case-v2/apercu
```

Dépendances : ReportLab, svglib, pypdf, polices Arial de Windows ; Poppler pour les aperçus. Le script vérifie les identifiants, références des connecteurs, objets natifs, dimensions, largeur des textes et absence de chevauchement des ovales. Il vérifie aussi que le PDF contient deux pages avec du texte extractible.

Le rendu PDF est inspecté visuellement. Ces vérifications concernent les livrables documentaires ; elles ne constituent pas une nouvelle recette d’exécution de l’application. Le fichier Draw.io est vérifié structurellement, sans prétendre à une ouverture dans l’éditeur.
