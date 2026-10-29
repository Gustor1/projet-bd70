# Audit et choix du modèle entité-association final

Audit du 29 octobre 2026. Travail documentaire sur le contenu local actuel. Aucun changement de l’application, du SQL ou des données. Les anciens diagrammes sont conservés.

## Conclusion

Les six MCD existants constituent une base utile : les domaines, la provenance des lots, les mouvements de stock, les relations N:N, les réceptions partielles et l’expédition sont déjà représentés. Ils ne sont pas entièrement faux. En revanche, ils ne sont pas suffisamment explicites pour être recommandés seuls comme rendu final du modèle conceptuel.

La version recommandée est [BD70-MCD-FINAL.pdf](BD70-MCD-FINAL.pdf), avec sa source native [Draw.io](BD70-MCD-FINAL.drawio). Elle comprend un modèle global et dix vues détaillées, couvrant le même modèle. Les pages détaillées sont en A3 ou A2 selon la densité ; la page globale est un grand format vectoriel à consulter avec zoom. Il ne faut pas réduire la page globale sur A4.

## Sources effectivement vérifiées

- [Sujet A26](../../document%20projet/A26_Site_Logistique.pdf), pages 1-2 : huit domaines fonctionnels ; page 2 : toutes les fonctionnalités doivent être permises par la base, même si le minimum web est plus limité ; page 3 : MCD et MLD sont deux livrables distincts.
- [Grille d’évaluation](../../document%20projet/Éléments%20dévaluation%20projet%20BD70.docx) : cohérence cas d’utilisation / MCD / relationnel, identifiants, relations 1:N et N:N, jointures, absence de redondance et normalisation.
- [Cours BD70 A25](../../document%20cours/BD70_A25%20%284%29.pptx), diapositives 211-218 : concepts, attributs, identifiants, associations et conversion relationnelle ; diapositives 224-226 : plusieurs notations admises. Les exemples du cours et les conventions Merise ne placent pas toujours les multiplicités selon la même convention : une légende explicite évite l’ambiguïté.
- [Schéma SQL](../../sql/01_schema.sql), [métadonnées des diagrammes](../../docs/diagrammes/schema.json), [générateur existant](../../scripts/diagrams.py), [services métier](../../src/Warehouse.php), [hypothèses](../../docs/hypotheses-decisions.md) et [bilan de réalisation](../../docs/BILAN-AUDIT-ET-REALISATION.md).
- Les six sources DOT et leurs SVG ; les pages correspondantes du [recueil existant](../rapport/DIAGRAMMES-BD70.pdf).

## Ce qui est déjà réalisé

Le dépôt contient une application PHP/PDO, un schéma de 41 tables, des vues, procédures et triggers, les écrans de référentiels, planning, passages, réception, stocks, commandes, traçabilité et rapports, ainsi que des données de démonstration, des tests et un rapport de projet. Le modèle doit donc couvrir les huit domaines et pas seulement les cinq domaines de l’interface minimale demandée.

Le fichier `livrables/preuves/verification-finale.json` conserve les résultats d’une validation antérieure. Cette intervention ne rejoue pas les tests fonctionnels de l’application et ne prétend pas revalider un service en fonctionnement. Elle vérifie les sources, la couverture du modèle et les nouveaux documents.

## Tous les MCD retrouvés

| Version existante | Diagramme à consulter | Source modifiable | Page du recueil | Avis |
|---|---|---|---:|---|
| Modèle complet | [SVG](../../docs/diagrammes/mcd-complet.svg) | [DOT](../../docs/diagrammes/mcd-complet.dot) | 4 | Bonne couverture générale, mais identifiants et attributs incomplets ; certains liens manquent. |
| Personnel et transport | [SVG](../../docs/diagrammes/mcd-personnel-transport.svg) | [DOT](../../docs/diagrammes/mcd-personnel-transport.dot) | 5 | Relations transporteur / chauffeur / véhicule et N:N présentes ; utilisateur isolé dans cette vue et attributs limités. |
| Quais et passages | [SVG](../../docs/diagrammes/mcd-quais-passages.svg) | [DOT](../../docs/diagrammes/mcd-quais-passages.dot) | 6 | Rendez-vous facultatif et chronologie corrects ; remorque non représentée par une association distincte. |
| Articles et stockage | [SVG](../../docs/diagrammes/mcd-articles-stockage.svg) | [DOT](../../docs/diagrammes/mcd-articles-stockage.dot) | 2 | Structure et propriétaires présents ; dimensions/poids des articles et capacités des emplacements ne sont pas tous visibles. |
| Réceptions et stock | [SVG](../../docs/diagrammes/mcd-receptions-stock.svg) | [DOT](../../docs/diagrammes/mcd-receptions-stock.dot) | 7 | Bonne conservation des fractions et lots ; auteurs, dates et liens vers l’article ne sont pas tous visibles dans cette vue. |
| Commandes et expéditions | [SVG](../../docs/diagrammes/mcd-commandes-expeditions.svg) | [DOT](../../docs/diagrammes/mcd-commandes-expeditions.dot) | 3 | Prélèvements, colis et sorties présents ; propriétaire et article manquent dans cette vue, mais existent dans le schéma complet. |

Les fichiers `mld-*` sont des modèles relationnels, pas des MCD. Les fichiers `.drawio` antérieurs trouvés dans `uml-use-case`, `rendu-intermediaire` et `use-case-v2` sont des diagrammes de cas d’utilisation, pas des diagrammes entité-association. Aucun MCD natif Draw.io antérieur n’a été trouvé dans le dépôt.

## Constats et corrections

| Constat vérifiable | Portée | Correction finale |
|---|---|---|
| Le générateur élimine `id` puis limite les attributs à `[:4]`. Aucun identifiant n’est souligné. | Les six MCD. Cela masque notamment les clés composées article/propriétaire et lot/article. | Un identifiant explicite par entité et tous les attributs propres ; les autres unicités sont listées dans la correspondance SQL. |
| Les dimensions, le poids, les unités par palette et certaines capacités disparaissent de l’affichage. | Le modèle SQL contient ces données : il s’agit d’un défaut documentaire. | Attributs rétablis dans ARTICLE et EMPLACEMENT. Capacités des niveaux supérieurs obtenues par agrégation. |
| `appointment.trailer_id` n’a pas d’association et `truck_visit.trailer_id` est résumé dans le libellé du lien véhicule principal. | Le véhicule principal est obligatoire, la remorque est facultative : un seul lien ne décrit pas les deux rôles. | Deux associations distinctes à chaque étape : véhicule principal prévu/effectif et remorque prévue/effective. |
| `supplier_notice.closed_by` apparaît comme une propriété « Clôturé par » plutôt que comme un lien vers UTILISATEUR ; le lien `shipment.actor_id` manque. | MCD complet et vues concernées. | Associations d’auteur de clôture et de confirmation d’expédition. |
| Les associations N:N mentionnent validité/quantité dans leur nom, sans véritable propriété distincte. | Chauffeur / habilitation et colis / prélèvement. | Date de fin de validité et quantité affectée explicitement inscrites dans les losanges. |
| Certaines vues perdent les relations traversant leurs limites de domaine. | Par exemple propriétaire / commande et article / ligne de commande. | Les entités communes sont répétées comme points de raccordement ; chaque association du modèle global figure dans une vue détaillée. |
| L’ancien schéma complet est très large et sa légende de lecture est externe. | Lisibilité et soutenance. | Légende dans le document, repères R01-R57 et dix vues détaillées ; source Draw.io entièrement modifiable. |

Les cardinalités des sources actuelles ne sont pas globalement inversées : leur générateur les exprime comme des participations Merise. Je conserve cette convention et je l’écris sur les pages. Près de TRANSPORTEUR, `0,N` signifie « un transporteur peut participer à zéro ou plusieurs rattachements de chauffeurs » ; près de CHAUFFEUR, `1,1` signifie « chaque chauffeur est rattaché à exactement un transporteur ».

## Modèle retenu et correspondance avec la réalisation

35 entités conceptuelles, 57 associations et cinq associations N:N. Les 60 clés étrangères métier du schéma sont représentées. Les 213 colonnes métier retenues sont soit des attributs propres, soit traduites par des associations ; les id artificiels des tables de jointure et les deux tables purement techniques sont exclus de ce décompte.

34 entités correspondent directement à des tables métier. TYPE DE VÉHICULE formalise le domaine commun à `vehicle.type` et `dock_vehicle_type.vehicle_type` : il est implémenté par des ENUM, pas par une nouvelle table. L’association QUAI / TYPE DE VÉHICULE correspond à `dock_vehicle_type`. Les quatre autres N:N correspondent à `driver_qualification`, `vehicle_equipment`, `dock_equipment` et `package_pick`.

Les attributs de clé étrangère ne sont pas recopiés dans les rectangles : ils deviennent des associations. Les types SQL et contraintes d’index restent dans le MLD et dans [CORRESPONDANCE-SQL.md](CORRESPONDANCE-SQL.md). Le rôle utilisateur reste un domaine fini, conformément à l’application. Le journal technique `audit_log` et le verrou `site_lock` restent hors du modèle métier ; les événements de camion et mouvements de stock sont bien des faits métier et sont conservés.

| Exigence du sujet | Entités et associations qui la permettent | Vues |
|---|---|---|
| Comptes et profils | UTILISATEUR, rôle, activation, identifiant de connexion, empreinte ; auteurs et préparateur | 4, 6, 8, 9, 10 |
| Transporteurs, chauffeurs, véhicules | TRANSPORTEUR, CONTACT, CONTRAT, CHAUFFEUR, HABILITATION, VÉHICULE, ÉQUIPEMENT | 1-2 |
| Quais et rendez-vous | QUAI, TYPE DE VÉHICULE, INDISPONIBILITÉ, RENDEZ-VOUS, ressources prévues | 2-3 |
| Flux camions | PASSAGE, ÉVÉNEMENT, quai et ressources effectifs, rendez-vous facultatif | 3-4 |
| Réception et écarts | AVIS, LIGNE D’AVIS, RÉCEPTION, LIGNE, FRACTION, LOT, RÉSERVE | 6-8 |
| Emplacements et stock | ARTICLE, PROPRIÉTAIRE, ZONE, ALLÉE, RACK, NIVEAU, EMPLACEMENT, MOUVEMENT | 5, 7-8 |
| Préparation et expédition | COMMANDE, LIGNE, PRÉLÈVEMENT, COLIS, quantité affectée, EXPÉDITION, passage sortant | 9-10 |
| Traçabilité et indicateurs | Chaîne fraction / lot / mouvement / prélèvement / commande / expédition ; dates des événements et préparation | Ensemble |

## Règles indispensables au-delà des cardinalités

1. **Brouillons** : avis, réceptions, commandes et colis peuvent exister avant leurs lignes ou affectations. Les minima `0,N` sont donc intentionnels. Les services contrôlent leur complétude avant validation, préparation et chargement.
2. **Ressources** : chauffeur et véhicules doivent être compatibles avec le transporteur, le quai, l’opération, les équipements et les habilitations valides. Une remorque est un VÉHICULE du type remorque et ne doit pas être le véhicule principal. Les conflits temporels de quai, chauffeur, véhicule et remorque ne se déduisent pas des seules cardinalités.
3. **Passages** : un rendez-vous concerne au plus un passage ; les arrivées sans rendez-vous restent possibles. Le quai peut être inconnu à l’arrivée. Le minimum `1,N` d’événements est une règle de création de l’application (événement d’arrivée), pas une garantie obtenue par la seule clé étrangère SQL.
4. **Réceptions** : la ligne d’avis doit appartenir à l’avis de la réception ; l’article du lot doit être celui de la ligne attendue. Plusieurs réceptions peuvent concerner le même avis, plusieurs fractions le même lot, et une fraction garde sa réception d’origine.
5. **Réserves** : XOR total entre cible réception et cible ligne. Une réserve existe même en l’absence de marchandise reçue, notamment pour un manquant. L’observation d’avarie portée par une fraction n’est pas le remplacement de ces réserves structurées.
6. **Stock** : solde physique calculé par somme des variations, disponible calculé après déduction des prélèvements encore réservés. Aucun solde éditable ajouté au MCD. Un transfert est un couple d’écritures opposées reliées par une référence d’opération. Le rangement initial n’est pas la position actuelle après transfert.
7. **Sorties** : un mouvement de type sortie référence exactement un prélèvement ; les autres mouvements n’en référencent aucun. Le lien est `0,1` à chacun des deux bouts sur l’ensemble des types de mouvements. La fraction, l’emplacement et la quantité débitée doivent correspondre au prélèvement.
8. **Commandes** : le propriétaire de l’article doit être celui de la commande ; la fraction prélevée doit porter le bon article. Les lots périmés ou bloqués sont exclus du FEFO. Le préparateur facultatif au brouillon devient obligatoire lors de la préparation.
9. **Colis** : un colis et chacun de ses prélèvements appartiennent à la même commande. La somme des quantités affectées aux colis couvre exactement chaque prélèvement au chargement. Un prélèvement peut alimenter plusieurs colis.
10. **Expédition** : aucune expédition partielle dans cette réalisation ; une commande est liée à zéro ou une expédition. Un passage sortant peut emporter plusieurs expéditions. Documents de transport et indicateurs sont calculés depuis les données, sans entités artificielles pour les impressions ou graphiques.

La représentation des liens ne constitue pas, à elle seule, une démonstration de 3NF ou une garantie d’intégrité. Plusieurs chemins doivent rester cohérents (réception/avis/lignes, commande/article/propriétaire, mouvement/prélèvement/fraction). Le schéma existant conserve aussi des projections d’état et des références communes aux différents types de mouvements : ces choix sont expliqués dans les hypothèses du projet et doivent être défendus avec leurs contraintes métier. Cet audit ne refond pas le SQL et ne prétend pas fournir une nouvelle preuve formelle exhaustive de normalisation.

## Vérifications du livrable

- Égalité entre les 41 tables, les listes de colonnes et les liens FK du SQL et les métadonnées utilisées pour dessiner.
- Couverture des 60 FK métier, des 213 colonnes retenues et des cinq jointures ; aucun lien compté deux fois.
- Chaque association du modèle global figure dans exactement une vue détaillée ; les entités partagées conservent les mêmes attributs.
- PDF vectoriel et source Draw.io de onze pages ; objets, associations et liens natifs, sans image aplatie dans le Draw.io.
- Inspection visuelle des rendus finaux ; contrôle des pages, du texte et des bornes du document.
- Empreintes des sources et décomptes dans [verification.json](verification.json).

Le générateur [build-mcd-final.py](../../scripts/build-mcd-final.py) ne réécrit que ce nouveau livrable. Copier le fichier Draw.io avant de le modifier manuellement : une régénération remplacerait ces retouches. Les versions antérieures du projet ne sont pas écrasées. Aucun commit, push ni déploiement n’est effectué par cette intervention.
