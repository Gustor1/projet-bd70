# Rendu intermédiaire BD70 — analyse et choix du diagramme

## Conclusion

Le fichier existant `livrables/uml-use-case/Transit-Use-Case.drawio` constitue une base globalement correcte. Il représente les fonctions métier, les profils, les droits hérités et l'inscription. Ses trois pages doivent cependant être lues ensemble : la vue d'ensemble renvoie à une deuxième page pour les héritages et à une troisième pour les relations détaillées.

Pour rendre un diagramme autonome, la nouvelle version rassemble les acteurs et les principaux objectifs sur **une page A3 paysage**. Ce format est un choix de lisibilité ; le sujet n'impose ni format de page ni nombre de cas. Le fichier `UML-CAS-UTILISATION-BD70.pdf` est destiné au rendu, et `UML-CAS-UTILISATION-BD70.drawio` à la modification. Les versions SVG et PNG servent d'aperçus.

## Ce que demandent les documents

Le sujet `document projet/A26_Site_Logistique.pdf`, pages 1–2, décrit huit domaines fonctionnels. Sa remarque de page 2 distingue le **modèle de données complet**, qui doit permettre tous ces domaines, du minimum d'interface Web demandé. Il ne faut donc pas limiter l'analyse aux seuls écrans minimaux. Le diagramme de cas d'utilisation UML est explicitement demandé page 3, séparément du modèle conceptuel et du modèle logique.

La grille `document projet/Éléments dévaluation projet BD70.docx`, rubriques « Démarche de conception d'un système d'information » et « Rapport », demande l'identification des cas, leur représentation UML et la cohérence entre cas, données et traitements. Elle valorise aussi recherche, filtres, statistiques, états et gestion de plusieurs utilisateurs. Elle n'impose pas l'emploi d'`include` ou d'`extend`.

Dans `document cours/BD70_A25 (4).pptx` :

- Les diapositives **204–205** placent les cas d'utilisation dans l'analyse des besoins.
- La diapositive **206** demande de définir la frontière du système, les acteurs et leurs interactions.
- La diapositive **207** montre les acteurs hors du cadre, les cas en ovales et une généralisation entre acteurs, avec triangle creux vers l'acteur général.
- Les diapositives **208–209** expliquent l'inclusion et l'extension optionnelle.
- La diapositive **210** complète le dessin par des descriptions textuelles : objectifs, acteurs, préconditions, scénario, alternatives et postconditions.

Le support `BD70_Introduction Web_A25.pptx` traite de l'architecture Web, de HTML, PHP et des accès aux données ; il n'ajoute pas de convention UML. Cette analyse établit la conformité aux **supports fournis**, sans présumer de l'avancement oral réel du cours.

## Évaluation des versions existantes

| Version | Avis pour ce rendu |
|---|---|
| `docs/diagrammes/cas-utilisation.svg` | Vue métier utile, mais moins adaptée seule : inscription et administration des comptes ne sont pas explicites, acteurs dessinés par caractères et objectifs mêlés à des contrôles internes. Les inclusions utilisent un triangle creux, au lieu de la flèche ouverte habituelle des dépendances UML. Voir `scripts/diagrams.py`, lignes 63–71. |
| `livrables/uml-use-case/Transit-Use-Case.drawio` | Bonne base modifiable. Les rôles, l'inscription et les relations détaillées sont mieux explicités, mais répartis sur trois pages. Voir son `LIRE-MOI.md` et `scripts/build-usecase-drawio.py`, lignes 49–124. |
| Nouvelle vue générale | Version conseillée à rendre : périmètre, fonctions communes, spécialisation des acteurs et objectifs métier visibles ensemble. |

Les anciens fichiers restent disponibles ; la nouvelle livraison ne signifie pas que tous leurs choix étaient erronés.

## Choix de modélisation

La frontière représente le **logiciel de gestion de l'entrepôt**. Les quatre profils métier sont extérieurs à cette frontière, même s'ils travaillent dans l'entreprise. « Personnel » regroupe les fonctions communes. Les généralisations expriment des capacités fonctionnelles : le responsable possède celles de l'accueil et du magasinier ; l'administrateur possède celles du responsable et administre les comptes. Ce choix correspond à `src/Auth.php`, lignes 6–10, et non à une hiérarchie supposée des personnes.

Le personnel non inscrit est associé à « S'inscrire ». L'inscription crée un compte en attente ; l'administrateur doit l'activer avant la connexion (`src/Auth.php`, lignes 14–24). La consultation du planning et la traçabilité sont accessibles aux quatre profils actifs (`public/index.php`, ligne 45, et `src/Auth.php`, lignes 6–10).

Le portail transporteur est facultatif dans le sujet, page 1, et absent du périmètre réalisé : aucun acteur Transporteur n'est ajouté. Clients, fournisseurs, chauffeurs et véhicules restent des données gérées lorsqu'ils n'interagissent pas directement avec le logiciel.

Les cas métier supposent une session active et les droits nécessaires. La vue générale ne détaille pas `include`/`extend` : ces relations sont facultatives, et leur absence n'est pas un défaut UML. Les contrôles et variantes restent décrits dans `docs/02-cas-utilisation.md` ; on évite ainsi de présenter une succession d'étapes comme une inclusion.

## Couverture des huit domaines du sujet

| Domaine du sujet | Objectifs visibles dans la nouvelle vue |
|---|---|
| Connexion et authentification | S'inscrire ; se connecter ; se déconnecter ; administrer les comptes et les rôles. |
| Transporteurs, chauffeurs et véhicules | Gérer le référentiel de transport. |
| Quais et rendez-vous | Gérer les référentiels métier ; consulter le planning ; gérer les rendez-vous. |
| Flux de camions | Suivre les passages, de l'arrivée au départ, avec ou sans rendez-vous. |
| Réception des marchandises | Réceptionner et ranger les marchandises, avec lots, écarts et réserves. |
| Emplacements et stocks | Gérer les référentiels métier ; consulter et gérer les stocks. |
| Préparation et expédition | Gérer les commandes ; préparer les commandes ; expédier et éditer les documents de transport. |
| Traçabilité et tableaux de bord | Tracer un lot ; consulter les indicateurs et éditer les rapports. |

Les référentiels métier comprennent articles, clients propriétaires, quais et structure de stockage. Les formulations regroupent les opérations cohérentes ; elles ne représentent pas une ellipse par table ou par bouton. L'examen du code vérifie la cohérence documentaire du modèle, sans constituer une nouvelle validation d'exécution de l'application.
