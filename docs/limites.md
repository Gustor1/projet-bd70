# Limites et choix de portée

Tous les domaines obligatoires ont un accès web. Le rôle transporteur externe est facultatif et non retenu ; FEFO est une stratégie autorisée. Les commandes sont expédiées intégralement.

Application monosite, locale, PHP 8.2.12 / MariaDB 10.4.32 / Windows / Edge. Pas de déploiement public ni de test sur téléphone physique. Le planning se rafraîchit toutes les 30 secondes hors saisie.

SQL DATETIME stocke les heures civiles de Paris. Seules les heures locales ambiguës/inexistantes des changements saisonniers sont refusées. Changer le fuseau ne corrige pas une horloge système physiquement fausse.

Les invariants entre lignes reposent sur les services transactionnels et le verrou global. Un administrateur SQL peut les contourner. L’historique riche est simulé directement puis vérifié ; il ne représente pas 900 cycles saisis au navigateur.

Les sélecteurs sont limités à 2 000 propositions, avec une recherche préalable. Les mouvements de trace sont paginés ; ses réceptions et commandes restent des tableaux complets. Les propriétés structurelles utilisées et les historiques sont protégés ; corrections par reprise, annulation ou ajustement selon l’état.

Les documents consultent les libellés actuels ; ils ne constituent pas une archive réglementaire figée. GPS, EDI, facturation, signature électronique et chargement géométrique ne sont pas demandés ni réalisés.

Auteurs : ELIOTT LE, SEMIH TASKIN et Thomas VUILLIN. Répartition individuelle non communiquée, donc non inventée. Date de remise et modalités de soutenance A26 à confirmer par le groupe.
