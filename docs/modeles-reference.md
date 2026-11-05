# Modèles du rendu final

Les trois modèles ci-dessous sont les références du rendu du 4 novembre 2026.

| Modèle | Version retenue | Sources modifiables |
|---|---|---|
| Cas d’utilisation UML | [PDF corrigé](../livrables/use-case/UML-CAS-UTILISATION-BD70-CORRIGE.pdf), cinq vues du même modèle | Draw.io dans le même dossier |
| Modèle entité-association | [PDF Chen](../livrables/entite-association/BD70-MCD-CHEN.pdf) | [Draw.io](../livrables/entite-association/BD70-MCD-CHEN.drawio) |
| Schéma relationnel | [PDF relationnel](../livrables/schema-relationnel/mld-complet.pdf) | [Draw.io](../livrables/schema-relationnel/mld-complet.drawio) |

Le [recueil PDF](../livrables/rapport/DIAGRAMMES-BD70.pdf) réunit uniquement ces trois modèles, soit sept pages. Les diagrammes globaux sont vectoriels et de grand format. Les lire avec zoom.

## Lecture du MCD Chen

Un rectangle représente une entité, un losange une association et un ovale un attribut. Les identifiants sont soulignés. Les cardinalités (min,max) indiquent la participation de l’entité située du même côté.

TRANSPORTEUR est associé à UTILISATEUR avec les participations 0,N et 0,1. Le CHECK SQL impose une société au profil transporteur et son absence pour les profils internes.

Pour une sortie de stock, le mouvement référence uniquement son prélèvement. Fraction reçue, emplacement et variation sont déduits de ce prélèvement par v_stock_movement. Les autres mouvements portent directement ces trois valeurs et aucun prélèvement. Cette règle exclusive complète les cardinalités facultatives R45, R46 et R47.

Une réserve concerne une réception OU une ligne de réception. Le CHECK XOR impose exactement un rattachement.

Les cinq associations N:N portent sur chauffeur/habilitation, véhicule/équipement, quai/équipement, quai/type de véhicule et colis/prélèvement. TYPE DE VÉHICULE est un domaine conceptuel traduit par des ENUM cohérents. audit_log et site_lock sont des tables techniques représentées dans le schéma relationnel.

Le MCD couvre 35 entités, 58 associations, 61 FK métier et 214 colonnes métier. Le fichier modele.json du dossier Chen conserve la correspondance des attributs et associations avec SQL pour le validateur.

## Cohérence et reconstruction

Le [SQL](../sql/01_schema.sql) définit la structure physique. Les vues, procédures, triggers et services transactionnels complètent les garanties. Les capacités cumulées, transitions, égalités d’articles et quantités ne sont pas exprimées par les seules cardinalités. Voir [normalisation](normalisation-3nf.md) et [hypothèses](hypotheses-decisions.md).

Après une évolution de la base, exporter les métadonnées depuis une installation neuve du schéma courant avec scripts/model.php. scripts/diagrams.py génère uniquement le schéma relationnel complet, puis scripts/render-diagrams.cjs produit son SVG. scripts/export-mld-drawio.py en reproduit les tables, attributs et relations sous forme d’objets éditables.

Le use case se reconstruit avec scripts/build-usecase-correction-prof.py, qui utilise scripts/usecase_layout.py. Le MCD Chen se modifie dans Draw.io ou dans sa source DOT. Après une modification du DOT, régénérer le SVG avec Graphviz et reporter les mêmes changements dans le Draw.io.

scripts/verify-models.py compare les métadonnées installées, le MLD et le modèle Chen. scripts/build-report-final.py reconstruit le rapport, les PDF des deux schémas globaux et le recueil. Les dépendances documentaires sont ReportLab, svglib, pypdf et Pillow. Les outils de rendu DOT utilisent @viz-js/viz, avec BD70_VIZ pour son chemin.

Les PDF sont générés depuis les SVG. Vérifier les exports et préserver les retouches manuelles du Draw.io avant toute reconstruction.
