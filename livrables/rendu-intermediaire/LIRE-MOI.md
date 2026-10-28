# Diagramme à rendre

- **UML-CAS-UTILISATION-BD70.pdf** : version de remise, une page A3 paysage, texte vectoriel. Choisir A3 paysage pour l'impression à taille prévue ; l'A4 réduit les caractères.
- **UML-CAS-UTILISATION-BD70.drawio** : version modifiable dans Draw.io / diagrams.net. Ouvrir le fichier directement : acteurs, ellipses, libellés et connecteurs sont des objets natifs. Conserver une copie avant toute modification manuelle.
- **UML-CAS-UTILISATION-BD70.png** : aperçu produit à partir du PDF.
- **UML-CAS-UTILISATION-BD70.svg** et **.html** : versions vectorielle et navigateur.
- **ANALYSE-ET-CHOIX.md** : analyse du sujet, des supports et des anciens diagrammes ; utile pour expliquer les choix, sans obligation de la joindre au rendu.

## Vérification effectuée

Une page PDF A3 paysage, 15 cas, 6 acteurs (quatre profils, Personnel commun et personnel non inscrit), 15 associations et 5 généralisations. Texte du PDF contrôlé ; page rendue avec Poppler puis inspectée visuellement. XML Draw.io analysé : objets natifs, identifiants uniques et références des connecteurs valides. Relecture indépendante de la notation et de la couverture du sujet. Le fichier n'a pas été ouvert dans l'éditeur Draw.io durant ce contrôle.

Les versions antérieures sont conservées. Aucune modification de l'application ni nouvelle validation de son exécution n'a été effectuée.

## Reconstruction

Le script `scripts/build-usecase-submission.py` utilise Python et ReportLab, avec les polices Arial de Windows. Il reconstruit les fichiers Draw.io, SVG, HTML et PDF à partir des mêmes libellés et positions, et écrase uniquement ces sorties dans ce dossier. Le PNG est un rendu du PDF effectué avec `pdftoppm -r 135 -singlefile -png`.

Ne pas relancer le générateur sur une version Draw.io modifiée manuellement sans en garder une copie.
