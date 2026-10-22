"""Rapport fidèle aux preuves exécutées, source Markdown et exports PDF vectoriels."""
from pathlib import Path
import json,html,re,datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph,Table,TableStyle,Image,Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
import fitz
from PIL import Image as PILImage

root=Path('.');proof=root/'livrables/preuves';out=root/'livrables/rapport';out.mkdir(exist_ok=True,parents=True)
def read(name):return json.loads((proof/name).read_text(encoding='utf-8-sig'))
integ=read('integration.json');browser=read('navigateur.json');perf=read('performances.json');restore=read('restauration.json');journey=read('parcours.json');http=read('http.json');machine=read('machine.json')
assert integ['failed']==browser['failed']==journey['failed']==0
assert all(perf['checks'].values()) and all(restore['checks'].values())
fontdir=Path('C:/Windows/Fonts')
pdfmetrics.registerFont(TTFont('Arial',str(fontdir/'arial.ttf')));pdfmetrics.registerFont(TTFont('Arial-Bold',str(fontdir/'arialbd.ttf')))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial',boldItalic='Arial-Bold')
navy=HexColor('#17324d');blue=HexColor('#175fa6');muted=HexColor('#536a7e')
body=ParagraphStyle('Body',fontName='Arial',fontSize=10,leading=15,textColor=navy,spaceAfter=10)
small=ParagraphStyle('Small',parent=body,fontSize=8,leading=11)
head=ParagraphStyle('Head',parent=body,fontName='Arial-Bold',fontSize=13,leading=18,spaceBefore=14,spaceAfter=8)

# Rapport Markdown structuré ; chaque section correspond à une page contrôlée.
sections=[]
def section(title,paras,table=None,image=None):sections.append({'title':title,'paras':paras,'table':table,'image':image})
section('Contexte et cahier des charges',[
 'Le projet répond au sujet A26 « Système de Gestion d’un Entrepôt Logistique ». Il organise les rendez-vous, les passages de camions, la réception, le stockage, la préparation et l’expédition. L’objectif est de pouvoir expliquer la provenance d’une quantité et de piloter l’activité depuis des faits fiables.',
 'Le sujet de trois pages définit les exigences et autorise MySQL/MariaDB ou PostgreSQL. La grille d’évaluation demande notamment UML, MCD, MLD, normalisation, formulaires CRUD, recherche multicritère, tableaux, graphiques et états. Elle ne donne pas de pondération. Les supports de cours A25 expliquent la méthode et PHP/PDO ; leurs exemples d’agence de voyage ne sont pas le domaine à réaliser.',
 'Le modèle couvre F01 à F08. L’interface couvre les cinq domaines minimaux de S et ajoute les référentiels, les commandes, les expéditions, les documents et les indicateurs pour répondre à la grille. Un compte transporteur externe est optionnel dans S et n’est pas retenu.',
 'Les originaux sont préservés ; les extractions textuelles des quatre supports, y compris les SmartArt, sont livrées dans docs/sources/. Les auteurs réels et la date de remise n’étaient pas fournis. La soutenance de 10 minutes est préparée à titre indicatif, sous réserve des modalités A26.'
],table=[['Exigence','Résultat cible'],['F01 / F02','Personnel authentifié et référentiels transport'],['F03 / F04','Planning sans conflit et chronologie des camions'],['F05 / F06','Réception multilots, rangement et mouvements'],['F07 / F08','Préparation FEFO, expédition, traçabilité et pilotage']])
section('Acteurs et cas d’utilisation',[
 'L’administrateur active les comptes et possède tous les droits. Le responsable gère les référentiels, le planning et les opérations. L’accueil gère les rendez-vous et les passages. Le magasinier réceptionne, déplace, prépare et expédie. L’inscription seule ne donne aucun droit métier.',
 'Le diagramme UML livré utilise des acteurs, des ellipses et une frontière système. Les généralisations indiquent que le responsable reprend les opérations de l’accueil et du magasinier, et que l’administrateur reprend celles du responsable. La vérification de disponibilité est incluse dans la réservation et le déplacement. L’arrivée sans rendez-vous étend le suivi des camions.',
 'Les dix cas textuels détaillent acteur, objectif, préconditions, scénario, variantes et postconditions dans docs/02-cas-utilisation.md. La session authentifiée est une précondition : il ne s’agit pas de se reconnecter pour chaque clic.',
 'Exemple UC05 : un camion entrant est en opération ; l’agent saisit les lignes et les fractions par lot, les avaries et réserves, puis valide. La capacité et la provenance sont vérifiées sous transaction. Si une deuxième fraction ne peut pas être rangée, la première entrée est annulée par rollback. Un rejeu de validation est refusé.'
],table=[['Cas','Acteurs','Données principales'],['UC01 / UC02','Personnel / A, R','Comptes, référentiels'],['UC03 / UC04','A, R, accueil','Rendez-vous, passages, événements'],['UC05 / UC06','A, R, magasinier','Réceptions, lots, mouvements'],['UC07 / UC08','A, R, magasinier','Commandes, prélèvements, expéditions'],['UC09 / UC10','Personnel / A, R','Trace / indicateurs et états']])
section('Règles et hypothèses',[
 'Le site est unique et utilise l’heure civile Europe/Paris. Les quantités sont des unités entières de conditionnement ; poids en kg, dimensions en mètres, volume calculé en m³. Une capacité palette est un équivalent rationnel quantité/unités_par_palette, sans addition avec les kg ou les m³.',
 'Un article appartient à un client propriétaire et possède une référence unique chez celui-ci. Le fournisseur livre ; le transporteur achemine. Ces trois acteurs restent séparés. Un lot est identifié par article et code fabricant, avec DLC facultative et blocage motivé.',
 'Réceptions partielles autorisées : l’attendu d’une livraison est une allocation du reste de l’avis. Les excédents et avaries sont visibles ; les avaries ne sont pas mises au stock disponible. Une fraction reçue possède un code palette interne unique et peut être déplacée entre plusieurs emplacements.',
 'Le FEFO réserve toute la commande : DLC croissante, sans DLC en dernier, puis date de réception, fraction et emplacement. Les lots bloqués ou périmés sont exclus. Aucune expédition partielle n’est proposée ; l’annulation avant expédition libère les réservations.',
 'Les historiques sont immuables. Les brouillons et fiches inutilisées peuvent être supprimés ; les FK protègent les fiches référencées. Une correction d’inventaire crée un mouvement motivé. Certaines caractéristiques structurelles utilisées sont figées pour préserver les faits. Le détail est dans docs/hypotheses-decisions.md et docs/matrice-crud-droits.md.'
])
section('MCD et chemin de traçabilité',[
 'Les concepts se répartissent en cinq domaines : transport/personnel, quais/passages, articles/structure de stockage, réceptions/mouvements, commandes/expéditions. Les MCD sont distincts des MLD : concepts, attributs métier et associations à cardinalités ; pas de types SQL ni de FK.',
 'Une ligne de réception se décompose en plusieurs fractions portant des lots. Un lot peut être reçu plusieurs fois. Chaque mouvement et chaque prélèvement référence la fraction de réception, ce qui conserve une provenance exacte quand un même lot est mélangé dans plusieurs réceptions.',
 'Une ligne de commande peut être servie par plusieurs fractions et donc plusieurs lots ; une fraction peut servir plusieurs commandes. Le prélèvement quantifié est l’association qui porte cette relation N:N. Les équipements et habilitations sont aussi des relations structurées, jamais des listes de valeurs dans une cellule.',
 'Chemin complet : fournisseur → avis → ligne attendue → ligne de réception → fraction → lot/article/propriétaire. La fraction rejoint les mouvements et les emplacements successifs, puis les prélèvements, lignes de commande, expédition et passage du camion sortant.',
 'Les exports vectoriels détaillés et complets sont dans docs/diagrammes/. Le recueil DIAGRAMMES-BD70.pdf les conserve à leur taille native : lecture par zoom à 100 %, sans réduction illisible sur une feuille A4.'
],table=[['Relation','Cardinalité et justification'],['Avis → réceptions','1:N, livraisons partielles'],['Ligne reçue → fractions','1:N, plusieurs lots/palettes'],['Lot → fractions','1:N, plusieurs réceptions du même lot'],['Commande → lignes → prélèvements','1:N puis 1:N, plusieurs fractions par ligne'],['Fraction → prélèvements','1:N, un lot alimente plusieurs commandes'],['Commande → expédition','0..1, expédition intégrale unique']])
section('MLD, dictionnaire et normalisation',[
 'Le MLD installé comporte 40 tables, dont le verrou de site et le journal technique. Les types sont explicites : entiers pour les clés et quantités, DECIMAL pour mesures et capacités, DATETIME/DATE pour les faits temporels, VARCHAR bornés pour références et libellés. Les quantités, intervalles et capacités élémentaires sont contrôlés.',
 '1NF : les contacts, équipements, habilitations et lignes sont des occurrences distinctes. 2NF : dans une association chauffeur/habilitation, la validité dépend du couple entier ; les coordonnées du chauffeur restent dans driver. 3NF : les noms de transporteur, d’article et de propriétaire ne sont pas recopiés dans les lignes ; les jointures les retrouvent.',
 'Exemples de DF : (owner_id, sku) → caractéristiques de l’article ; (article_id, code) → DLC et blocage du lot ; (driver_id, qualification_id) → expires_on ; référence de commande → propriétaire, destination et date souhaitée. Le dictionnaire et la justification table par table sont fournis en annexes Markdown.',
 'Les unicités nullable ne sont pas présentées comme des clés candidates totales. Le rendez-vous est distinct du passage réel. Le statut courant est une projection de pilotage ; les événements conservent les faits horodatés. Les soldes, durées et totaux sont calculés par vues. L’attendu local d’une réception partielle n’est pas une redondance de l’attendu total de l’avis.'
],table=[['Relation','Clés métier et associations'],['article','UNIQUE(owner_id, sku), FK propriétaire'],['lot','UNIQUE(article_id, code), FK article'],['receipt_item','UNIQUE(pallet_code), FK ligne, lot et emplacement'],['pick','FK ligne de commande, fraction et emplacement'],['shipment','UNIQUE(order_id), FK passage sortant'],['stock_movement','FK fraction, emplacement, auteur, prélèvement optionnel']])
section('Architecture et sécurité',[
 f'L’application suit l’architecture trois tiers enseignée : navigateur HTML/CSS, contrôleur PHP et services métier, accès PDO explicite vers MariaDB/InnoDB. Versions vérifiées : PHP {perf["php"]}, MariaDB {perf["engine"]}, Windows 11. Aucune bibliothèque distante ou API n’est nécessaire à l’usage du site.',
 'Le seul répertoire exposé est public/. Database.php centralise PDO et les transactions ; Catalog.php décrit les fiches et protège les données validées ; Warehouse.php applique les transitions, capacités, FEFO et opérations atomiques ; Reports.php contient les recherches et indicateurs. Les vues sont dans templates/.',
 'Les mots de passe sont hachés et vérifiés par les fonctions PHP adaptées. Les sessions sont renouvelées à la connexion, cookies HttpOnly/SameSite, écritures protégées par CSRF, HTML échappé et SQL préparé. Les droits sont contrôlés à chaque route et action, indépendamment des menus. Un compte en attente ne peut pas s’octroyer un rôle.',
 'Le compte applicatif SQL possède SELECT/EXECUTE et les écritures par table nécessaires, sans droit DDL. Les journaux ne sont pas modifiables ; les mouvements, événements et expéditions n’acceptent pas UPDATE/DELETE. Le secret SQL est généré dans config/local.php hors dépôt. Les comptes du jeu sont fictifs.',
 'Le serveur de démonstration PHP et l’instance MariaDB isolée écoutent seulement sur 127.0.0.1. Aucun déploiement public ou validation de serveur de production n’est revendiqué.'
])
section('F01 et F02 - Personnel et transport',[
 '<b>Objectif.</b> Identifier le personnel et gérer les transporteurs, contacts, contrats, chauffeurs, habilitations et véhicules avec des droits distincts.',
 '<b>Travail réalisé.</b> Inscription en attente, activation et profils par administrateur, connexion/déconnexion. Les référentiels disposent de formulaires d’ajout/modification/suppression d’éléments inutilisés. Les véhicules portent type, immatriculation et capacités ; les équipements et habilitations sont gérés par associations. Un tracteur demande une remorque du même transporteur.',
 '<b>Contrôles.</b> Emails et références uniques, FK valides, dates de contrat cohérentes, compte actif, données structurantes protégées. Les entrées avec apostrophe et balises HTML ont été créées, recherchées, modifiées et supprimées dans un navigateur réel sans exécution de HTML.',
 '<b>Conclusion.</b> Quatre profils réellement utilisables. Les requêtes directes aux comptes et les tentatives d’écriture privilégiée sont refusées pour responsable, accueil et magasinier. Les formulaires masquent les clés techniques ; l’utilisateur sélectionne noms, références et plaques.'
],image='connexion.png')
section('F03 et F04 - Quais et flux camions',[
 '<b>Objectif.</b> Planifier sans chevauchement et suivre chaque étape du camion, y compris sans rendez-vous.',
 '<b>Travail réalisé.</b> Planning journée/quai, création, déplacement et annulation de rendez-vous ; types compatibles, équipements et indisponibilités. L’état actuel suit la priorité hors service, occupé, réservé, libre ; rafraîchissement à 30 secondes hors saisie et bouton manuel.',
 '<b>Contrôles.</b> Intervalles [début, fin[, durée positive ; dates saisonnières ambiguës refusées. Arrivée → contrôle → parking facultatif → appel → début → fin → départ. Les étapes erronées ou rétrogrades sont refusées. Une indisponibilité chevauchant une réservation exige son déplacement préalable.',
 '<b>Conclusion.</b> Les tests à deux connexions admettent une seule réservation conflictuelle et une seule occupation d’un quai. L’attente, l’immobilisation et le retard se déduisent des dates réelles et prévues, sans mélange entre rendez-vous et passage.'
],image='planning.png')
section('F05 et F06 - Réception, rangement et stocks',[
 '<b>Objectif.</b> Accepter les marchandises contrôlées, signaler les écarts et conserver des stocks compatibles avec les capacités.',
 '<b>Travail réalisé.</b> Avis et lignes, réceptions partielles, plusieurs lots/palettes par ligne, DLC et réserve pour les avaries. Validation unique et atomique ; propositions d’emplacements contrôlant condition de stockage, dimensions, poids, volume et équivalents palettes.',
 '<b>Contrôles.</b> Les avaries ne créent pas de disponible. Les lots bloqués/périmés ne sont pas réservables. Un transfert débite et crédite dans la même transaction, avec référence commune. Les quantités réservées ne peuvent pas être consommées par un ajustement ou un transfert. L’inventaire se corrige par mouvement motivé.',
 '<b>Conclusion.</b> R05 à R09 et R12 vérifiés, dont réception partiellement écrite puis intégralement annulée, conservation de quantité et deux rangements concurrents dans un emplacement limité. Recherche article + lot + propriétaire + zone et historique disponibles.'
],image='stock.png')
section('F07 et F08 - Sorties, trace et pilotage',[
 '<b>Objectif.</b> Préparer et expédier les quantités réellement prélevées, puis retrouver les lots et les indicateurs.',
 '<b>Travail réalisé.</b> Commandes et lignes, affectation à un préparateur, réservation FEFO complète, confirmation, colis/palettes et contenu, chargement sortant et expédition unique. Liste de prélèvement, bon de livraison et lettre de voiture imprimables avec données réelles du jeu fictif.',
 '<b>Contrôles.</b> Lot bloqué ou périmé exclu, départage stable, stock insuffisant sans réservation partielle, colis et capacité véhicule exigés. Le mouvement de sortie référence le prélèvement et la fraction reçue ; une deuxième expédition est refusée.',
 '<b>Conclusion.</b> Le lot A est reçu deux fois, déplacé sur deux emplacements et sert deux commandes. Le parcours navigateur supplémentaire confirme 31 étapes par formulaires jusqu’au camion et au bon. Les tableaux de bord et trois états CSV/imprimables utilisent les faits enregistrés, sans données graphiques codées en dur.'
],image='orders.png')
section('SQL, automatismes et transactions',[
 'Les scripts ordonnés installent schéma, vues, procédures, triggers et index. Les privilèges sont séparés. PK, FK, UNIQUE, NOT NULL, ENUM et CHECK rendent explicites les domaines et règles élémentaires. La suppression référencée est restrictive.',
 'PHP est l’unique propriétaire du BEGIN/COMMIT/ROLLBACK. La procédure lock_site() prend le verrou sur la ligne du site ; elle ne valide aucune transaction. Tous les services critiques et le CRUD suivent ce protocole. La sérialisation conservatrice garantit les contrôles d’agrégats contre les écritures concurrentes.',
 f'{restore["triggers"]} déclencheurs installés : journal automatique après mutations et refus de mutation des historiques. Les entrées du journal contiennent entité, opération, référence technique, auteur et date, jamais mot de passe ou secret. La procédure trace_lot(lot, offset) fournit l’historique des mouvements par pages de 20.',
 'Les vues v_balance et v_reserved calculent le physique et les réservations ; v_stock joint provenance, article, propriétaire et emplacement, et masque le disponible bloqué/périmé. v_location_usage calcule trois capacités indépendantes. v_visit reconstitue les dates et durées. v_receipt_discrepancy calcule manquants, excédents et avaries.',
 'Les règles multiligne ne sont pas prétendues être toutes des CHECK SQL : elles appartiennent aux services transactionnels. Les scripts administratifs ne doivent pas insérer des opérations arbitraires en contournant ces services.'
])
section('Données et résultats attendus',[
 'Les jeux sont fictifs et reproductibles (graine 70, référence 22/10/2026). La démonstration est créée principalement par les services réellement utilisés dans l’interface. Elle comprend les quatre profils, trois transporteurs, quatre types de véhicules, trois zones, lots normaux/bloqués/périmés/sans DLC, écarts et deux expéditions.',
 'Oracle du petit jeu avant les manipulations de recette : 255 unités acceptées, 50 sorties, 205 physiques. Le lot A représente 120 unités reçues et 50 sorties, soit 70 restantes réparties entre réceptions et emplacements. Dix unités sont périmées, dix bloquées, quarante froides proches de DLC et quinze sans DLC.',
 'Les quatre lignes validées comportent deux écarts : 5 unités excédentaires, 5 endommagées et 5 manquantes. Occupation des quais : 80 minutes / 4 320 minutes disponibles (trois quais sur une journée 24 h/24). Nord Transit : attente moyenne 17,5 minutes, immobilisation 55 minutes. Froid Express : 15 et 50 minutes.',
 'Productivité : 50 unités préparées sur 20 minutes observées, soit 150 unités/heure. Remplissage physique actuel : ambiant 150 unités (7,5 équivalents palettes), froid 40 (2 palettes), dangereux 15 (0,75 palette). Les numérateurs/dénominateurs sont dans les écrans et tests.',
 f'Le volume de performance est séparé : {perf["volumes"]["truck_visit"]:,} passages, {perf["volumes"]["receipt_line"]:,} lignes de réception, {perf["volumes"]["stock_movement"]:,} mouvements et {perf["volumes"]["visit_event"]:,} événements. Il s’agit de simulations SQL contrôlées, avec rapprochement du stock, capacités et somme nulle des transferts, pas d’une preuve de saisie manuelle de ce volume.'
])
section('Recette et restauration',[
 f'<b>Résultats exécutés.</b> {integ["passed"]} contrôles d’intégrité/métier réussis ; {browser["passed"]} contrôles navigateur réussis ; {journey["passed"]} étapes de parcours par formulaires réussies. Les fichiers JSON et les captures authentiques sont dans livrables/preuves/. Les courses utilisent deux connexions SQL distinctes, identifiées dans concurrence.json.',
 'R01 : création/déplacement, adjacence et chevauchement ; R02 : type, indisponibilité et refus de fermeture d’un quai réservé ; R03 : occupation concurrente ; R04 : transitions et dates. R05 : validation unique ; R06 : négatif et réservation concurrente ; R07 : transfert conservatif ; R08 : compatibilité/capacité concurrente ; R09 : avaries et blocage ; R10 : sorties liées et unicité ; R11 : trigger et droits ; R12 : rollback multiétapes.',
 'La recette HTTP contrôle l’inscription sans privilège, l’accès direct par rôle, l’absence de CSRF, les apostrophes/balises, les filtres CSV, le CRUD réel et les états. Les pages sont visitées à 1440 px et les principales pages à 390 px, sans débordement global. Les tableaux larges défilent dans leur propre conteneur.',
 f'Restauration : {len(restore["tables"])} tables comparées par nombre et checksum entre la démonstration et {restore["target"]}. Les {restore["triggers"]} triggers et {restore["procedures"]} procédures sont présents ; une modification contrôlée dans la copie ajoute automatiquement une entrée d’audit. Aucun écrasement de la démonstration.',
 'Les contrôles ne constituent pas une certification de production, un test sur téléphone physique ou une validation sur d’autres moteurs. La recette reste reproductible depuis une base vierge portant un nouveau nom de test.'
])
perfrows=[['Requête','Médiane (ms)','Min–max (ms)']]
for key,q in perf['queries'].items():perfrows.append([key.replace('_',' '),f'{q["median_ms"]:.3f}',f'{q["min_ms"]:.3f}–{q["max_ms"]:.3f}'])
before=perf['comparison']['before']['median_ms'];after=perf['comparison']['after']['median_ms']
section('Performances mesurées',[
 f'Machine : {machine["cpu"]}, {machine["logical_processors"]} processeurs logiques, {machine["ram_bytes"]/1024**3:.1f} Gio de RAM. Buffer pool InnoDB : {perf["config"]["buffer_pool_bytes"]/1024**2:.0f} Mio ; isolation READ COMMITTED. Le type exact de stockage n’a pas été relevé.',
 'Méthode : une chauffe et dix exécutions mesurées à paramètres et jeu identiques, horloge monotone hrtime. Le temps couvre le tour PDO local avec récupération des résultats ; ce n’est pas un temps CPU serveur isolé. Les SQL, paramètres, plans EXPLAIN, index et mesures brutes sont archivés dans performances.json.',
 f'Comparaison contrôlée sur la base de performance : seul idx_appointment_slot change, un index FK simple restant en place. La disponibilité passe d’une médiane de {before:.3f} ms à {after:.3f} ms ({before/after:.2f} fois plus rapide sur cet essai). L’index composite filtre quai/état puis borne la plage de dates ; le plan avant/après est conservé.',
 f'Observation d’écriture : INSERT de rendez-vous avec trigger suivi de ROLLBACK, avant {perf["comparison"]["write_before"]["median_ms"]:.3f} ms et après {perf["comparison"]["write_after"]["median_ms"]:.3f} ms en médiane. Le bruit et le rollback empêchent d’en déduire un coût universel de commit. Les agrégats de v_visit dominent les lectures ; une charge industrielle justifierait d’abord une agrégation ciblée par période. Aucun partitionnement ni réplication ajouté sans besoin mesuré.'
],table=perfrows)
section('Indicateurs et états imprimables',[
 'Les indicateurs définissent période, unité et exclusions : occupation réelle intersectée à la période / capacité disponible des quais ; attente jusqu’au début d’opération ; immobilisation jusqu’au départ ; remplissage par zone dans chaque unité ; lignes avec écarts / lignes reçues ; productivité sur durée de préparation observée ; DLC dans un horizon inclusif.',
 'Le stock et le remplissage sont une photographie actuelle, même si une période passée est sélectionnée pour les flux. Les données sans DLC et périmées sont isolées. Les opérations sans fin restent ouvertes. Les dénominateurs nuls et durées absentes produisent une valeur explicitement absente, sans division invalide.',
 'Les mesures HTTP sont séparées des temps PDO volumétriques : une chauffe puis dix réponses authentifiées sur le petit jeu. Médianes locales : '+', '.join(k+' '+f'{v["median_ms"]:.1f}'+' ms' for k,v in http.items())+'. Elles incluent PHP et le transfert du HTML, sans les ressources ni le rendu du navigateur.',
 'Les états stock, activité et écarts sont imprimables et exportables en CSV. Les exports réutilisent les filtres et les droits ; les clés techniques ne sont pas exportées. Les champs susceptibles d’être interprétés comme des formules sont neutralisés. Les documents de transport reprennent la commande, le propriétaire, les lots, les colis et le camion.'
],image='reports.png')
section('Conclusion et limites',[
 'La chaîne logistique est implémentée et démontrée localement, avec modèle relationnel, SQL lisible, formulaires, règles atomiques, historiques, recherche, pilotage et documents. Les quatre sources sont reliées aux livrables dans la matrice de conformité et le suivi par lots.',
 'Les choix pédagogiques sont explicites : monosite, rôle unique par compte, FEFO, expédition intégrale, verrou global, heures civiles du site et documents non réglementaires. Les fiches structurantes utilisées sont protégées, et les faits se corrigent sans effacement silencieux. Le débit d’écriture et les agrégats historiques constituent les principaux axes d’évolution mesurable.',
 'Les listes proposent jusqu’à 2 000 références à la fois, avec affinage par nom/référence sur les grands jeux. Les mouvements de la trace sont paginés ; les réceptions et commandes liées à un lot restent des tableaux complets. La navigation mobile a été testée dans Edge, pas sur un appareil physique.',
 'Pour la remise, le groupe doit renseigner ses vrais noms, sa répartition des contributions et la date demandée. Les modalités A26 restent à confirmer. Aucun score attendu ni conformité réglementaire n’est annoncé.',
 'Reprise : lancer scripts/start.ps1 ; ouvrir http://127.0.0.1:8070 ; choisir la journée 22/10/2026 pour les indicateurs. Le README donne les comptes fictifs, les commandes de recette, les sauvegardes et les emplacements des preuves. Le script de démonstration de dix minutes est dans docs/demonstration.md.'
],table=[['Annexe livrée','Contenu'],['DIAGRAMMES-BD70.pdf + DOT/SVG','UML, MCD, MLD complets et par domaine'],['docs/dictionnaire-donnees.md','Attributs, types, unicités, FK, nullabilité'],['docs/normalisation-3nf.md','Clés candidates et DF table par table'],['docs/matrice-conformite.md','Exigence → cas → tables → écran → test → rapport'],['livrables/preuves/*.json','Tests, concurrence, mesures et restauration']])

md=['# Transit - Gestion d’un entrepôt logistique','\nProjet BD70 - 22 octobre 2026','\nAuteurs réels : à renseigner par le groupe. Noms de démonstration fictifs.','\n## Table des matières']
for i,s in enumerate(sections,1):md.append(f'{i}. {s["title"]}')
for i,s in enumerate(sections,1):
 md+=['\n## '+str(i)+'. '+s['title']]+['\n'+re.sub('<[^>]+>','',p)+'\n' for p in s['paras']]
 if s['table']:
  md+=['\n|'+'|'.join(s['table'][0])+'|','|'+'|'.join(['---']*len(s['table'][0]))+'|']+['|'+'|'.join(map(str,row))+'|' for row in s['table'][1:]]
 if s['image']:md+=['\nCapture authentique : ../preuves/'+s['image']]
(out/'RAPPORT-PROJET-BD70.md').write_text('\n'.join(md),encoding='utf-8')

W,H=A4;c=canvas.Canvas(str(out/'RAPPORT-PROJET-BD70.pdf'),pagesize=A4);c.setTitle('Transit - Projet BD70');pagecount=2+len(sections);qa=[]
def chrome(title,page):
 c.setFillColor(navy);c.rect(0,H-13,W,13,fill=1,stroke=0);c.setFont('Arial',8);c.setFillColor(muted);c.drawString(42,H-34,'Transit / Projet BD70 / 22 octobre 2026');c.drawRightString(W-42,26,f'{page} / {pagecount}');c.setFont('Arial-Bold',19);c.setFillColor(navy);c.drawString(42,H-75,title)
def flow(obj,y):
 ow,oh=obj.wrap(W-84,y-52)
 if oh>y-52:raise RuntimeError(f'Débordement page {c.getPageNumber()}, hauteur {oh}, reste {y-52}')
 obj.drawOn(c,42,y-oh);return y-oh-10
def table(rows,y):
 count=len(rows[0]);widths=[(W-84)*v for v in ([.44,.24,.32] if count==3 else [.34,.66])]
 cells=[[Paragraph(html.escape(str(x)),small) for x in row] for row in rows]
 t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#e8f0f7')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.6,HexColor('#abc1d4')),('LINEBELOW',(0,1),(-1,-1),.3,HexColor('#dce4eb'))]));return flow(t,y)
chrome('Transit',1);c.setFillColor(blue);c.setFont('Arial-Bold',29);c.drawString(42,H-160,'Gestion d’un entrepôt');c.drawString(42,H-200,'logistique');y=H-250
for p in ['Rapport de conception, de réalisation et de vérification','Projet BD70 · Sujet A26','Auteurs réels : à renseigner par le groupe','Date du rapport : 22 octobre 2026','Application locale PHP/PDO et MariaDB','40 tables · chaîne réception-stock-expédition · preuves exécutées'] :y=flow(Paragraph(html.escape(p),body),y)
c.setFillColor(HexColor('#eaf2fa'));c.roundRect(42,100,W-84,95,8,fill=1,stroke=0);note=Paragraph('Le rapport documente les réalisations locales et leurs limites. Les comptes et opérations sont fictifs. Les noms des auteurs et les modalités de remise doivent être complétés par les étudiants.',body);note.wrap(W-114,75);note.drawOn(c,57,124)
c.showPage();chrome('Table des matières',2);y=H-110
for i,s in enumerate(sections,3):y=flow(Paragraph(f'{i-2}. {html.escape(s["title"])} <font color="#536a7e">(p. {i})</font>',body),y)
c.showPage()
for page,s in enumerate(sections,3):
 chrome(s['title'],page);y=H-110
 for p in s['paras']:y=flow(Paragraph(p,body),y)
 if s['table']:y=table(s['table'],y)
 if s['image']:
  source=proof/s['image'];im=PILImage.open(source);im=im.crop((0,0,im.width,min(im.height,1000)))
  tmp=Path('.local')/('report-'+s['image']);im.save(tmp);iw,ih=im.size;maxh=y-75
  if maxh>100:
   scale=min((W-84)/iw,maxh/ih);img=Image(str(tmp),width=iw*scale,height=ih*scale);y=flow(img,y);y=flow(Paragraph('Capture réelle du navigateur local, jeu de démonstration ; extrait de la page.',small),y)
 qa.append({'page':page,'title':s['title'],'remaining_points':round(y-52,1)})
 c.showPage()
c.save()
# Recueil des diagrammes à la taille vectorielle native : aucune réduction de textes.
dc=canvas.Canvas(str(out/'DIAGRAMMES-BD70.pdf'));dc.setTitle('BD70 - UML, MCD et MLD vectoriels')
for file in sorted(Path('docs/diagrammes').glob('*.svg')):
 drawing=svg2rlg(str(file));dw,dh=drawing.width,drawing.height;dc.setPageSize((dw+60,dh+90));dc.setFont('Arial-Bold',15);dc.setFillColor(navy);dc.drawString(30,dh+60,file.stem);dc.setFont('Arial',10);dc.drawString(30,dh+42,'Format vectoriel natif - lire à 100 % / zoom - source DOT dans docs/diagrammes')
 renderPDF.draw(drawing,dc,30,25);dc.showPage()
dc.save()
# Pages et bornes des PDF ; rendus pour revue visuelle.
qa_dir=Path('.local/pdf-review');qa_dir.mkdir(exist_ok=True)
files=[out/'RAPPORT-PROJET-BD70.pdf',*sorted(proof.glob('document-*.pdf')),proof/'etat-indicateurs.pdf']
pdfinfo=[]
for file in files:
 doc=fitz.open(file);pdfinfo.append({'file':str(file),'pages':len(doc)})
 for num,page in enumerate(doc):
  page.get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(qa_dir/(file.stem+'-'+str(num+1)+'.png'))
  for block in page.get_text('dict')['blocks']:
   if block['type']==0:
    x0,y0,x1,y1=block['bbox'];assert x0>=-1 and y0>=-1 and x1<=page.rect.width+1 and y1<=page.rect.height+1,(file,num,block['bbox'])
 doc.close()
Path('livrables/preuves/verification-pdf.json').write_text(json.dumps({'report_layout':qa,'files':pdfinfo,'text_bounds_ok':True},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Rapport {pagecount} pages, recueil de {len(list(Path("docs/diagrammes").glob("*.svg")))} diagrammes ; bornes et rendus vérifiés.')
