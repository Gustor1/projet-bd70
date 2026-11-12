// Guide PDF « Tester et présenter Transit, de A à Z ».
// node scripts/build-guide-test.cjs
// Sources : docs/captures/guide/{scenario,complements,nouveautes}/ (captures Playwright sur une base de test neuve),
// docs/captures/guide/narration.json (phrases pour le professeur). Sortie : livrables/soutenance/GUIDE-TEST-ET-DEMO.pdf
const fs=require('fs');const path=require('path');const url=require('url');
const {chromium}=require(process.env.BD70_PLAYWRIGHT||'C:/Users/eliot/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'..');const G=path.join(root,'docs/captures/guide');
const img=p=>url.pathToFileURL(path.join(G,p)).href;
const esc=s=>String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const narr=JSON.parse(fs.readFileSync(path.join(G,'narration.json'),'utf8'));
const steps=JSON.parse(fs.readFileSync(path.join(G,'scenario/steps.json'),'utf8'));
const extra=JSON.parse(fs.readFileSync(path.join(G,'complements/steps.json'),'utf8'));
const ROLE={admin:'Administrateur',manager:'Responsable',gate:'Accueil',warehouse:'Magasinier',carrier1:'Transporteur'};
const MENU={catalog:'Référentiels',planning:'Quais & rendez-vous',visits:'Passages camions',receipts:'Réceptions',stock:'Stocks & rangement',orders:'Préparation & expédition',order_detail:'Préparation & expédition',trace:'Traçabilité des lots',reports:'Indicateurs & états',carrier_portal:'Mes rendez-vous',document:'Préparation & expédition'};
const TABLE={supplier_notice:'Avis fournisseurs',notice_line:'Lignes attendues',lot:'Lots',receipt:'Réceptions',receipt_line:'Lignes de réception',receipt_item:'Palettes reçues',customer_order:'Commandes',order_line:'Lignes de commande'};
const STATE={checked:'Contrôle des documents',parking:'Mise en attente sur le parking',called:'Appel à quai',working:'Début de l’opération à quai',finished:'Fin de l’opération à quai',departed:'Départ du site'};
const TODO={
 '21':'Réceptions → ouvrir la réception ORAL-CAFE-REC → cliquer sur le bouton encadré pour la valider.',
 '22':'Vérifier le message de confirmation et les quantités : 18 acceptées, 2 endommagées.',
 '23':'Stocks & rangement → formulaire de transfert. Saisir les valeurs ci-dessous puis cliquer sur le bouton encadré.',
 '28':'Préparation & expédition → commande ORAL-CAFE-CMD → choisir le préparateur ci-dessous → bouton encadré.',
 '29':'Se connecter avec le préparateur affecté (warehouse) → Préparation & expédition → ORAL-CAFE-CMD → bouton encadré (réservation FEFO).',
 '30':'Dans la même commande, confirmer les prélèvements avec le bouton encadré.',
 '31':'Dans le détail de la commande, section colis : saisir le code et le type → bouton encadré.',
 '32':'Répartir le prélèvement dans le colis : saisir la quantité ci-dessous → bouton encadré.',
 '37':'Préparation & expédition → ORAL-CAFE-CMD → choisir le camion au chargement ORAL-CAFE-SORTIE → bouton encadré.',
 '38':'Traçabilité des lots → choisir ORAL-CAFE-LOT → Retracer le lot. Lire la réception, le transfert et le camion de sortie.',
 '39':'Depuis la commande expédiée, ouvrir le bon de livraison (bouton encadré).',
};
function title(s){
 let t=s.title;
 const c=t.match(/^Créer · (\w+)$/);if(c)return 'Créer une fiche : '+(TABLE[c[1]]||c[1]);
 const v=t.match(/^(ORAL-CAFE-\w+) · (\w+)$/);if(v)return v[1]+' : '+(STATE[v[2]]||v[2]);
 const l=t.match(/^Connexion au compte (\w+)$/);if(l)return 'Se connecter : '+(ROLE[l[1]]||l[1]);
 return t;
}
function todo(s){
 if(TODO[s.id])return TODO[s.id];
 const c=s.title.match(/^Créer · (\w+)$/);
 if(c)return `Menu Référentiels → rubrique « ${TABLE[c[1]]||c[1]} » → Afficher → déplier « Ajouter une fiche ». Remplir les champs ci-dessous puis cliquer sur Enregistrer (encadré).`;
 if(/· (checked|parking|called|working|finished|departed)$/.test(s.title))return 'Menu Passages camions → retrouver la carte du passage → remplir si besoin les champs ci-dessous → cliquer sur le bouton encadré.';
 return s.note||'Cliquer sur l’élément encadré en orange.';
}
const page=u=>{const m=(u||'').match(/page=(\w+)/);return m?MENU[m[1]]:''};
function stepCard(s,num,phrase,dir){
 const who=s.role||(s.title.match(/compte (\w+)/)||[])[1];
 const fields=(s.fields||[]).filter(f=>!/^Email$/.test(f[0]));
 return `<section class="step"><div class="head"><span class="num">${num}</span><span class="role">${esc(ROLE[who]||who||'')}${who?` · ${esc(who)}@bd70.test`:''}</span>${page(s.url)?`<span class="menu">Menu : ${esc(page(s.url))}</span>`:''}</div>
<h3>${esc(title(s))}</h3><p class="todo"><b>À faire.</b> ${esc(todo(s))}</p>
${fields.length?`<table class="vals">${fields.map(f=>`<tr><td>${esc(f[0])}</td><td><b>${esc(f[1])}</b></td></tr>`).join('')}</table>`:''}
<img src="${img(dir+'/'+s.id+'.png')}">
${phrase?`<p class="say"><b>À dire :</b> « ${esc(phrase)} »</p>`:''}</section>`;
}
const code=(c,out)=>`<pre class="cmd">${esc(c)}</pre>${out?`<pre class="out">${esc(out)}</pre>`:''}`;
const shot=(f,cap)=>`<figure><img src="${img('nouveautes/'+f+'.png')}"><figcaption>${esc(cap)}</figcaption></figure>`;
const P='C:\\Users\\eliot\\Documents\\GitHub\\projet-bd70';

let scenario='';let n=0;
const groups=[[1,6,'E1 · Comptes, transporteur et planning'],[7,11,'E2 · Le fournisseur annonce la livraison'],[12,17,'E3 · Le camion arrive et se met à quai'],[18,25,'E4 · Réception, rangement, transfert, départ'],[26,32,'E5 · Commande, affectation, préparation FEFO, colis'],[33,41,'E6 · Camion de sortie, expédition, traçabilité, bon de livraison']];
for(const [a,b,t] of groups){scenario+=`<h2 class="sub">${esc(t)}</h2>`;for(const s of steps.filter(x=>+x.id>=a&&+x.id<=b)){n++;
 scenario+=stepCard(s,'E.'+String(n).padStart(2,'0'),narr.scenario[+s.id-1],'scenario');
 if(s.id==='08'){n++;scenario+=stepCard(extra[1],'E.'+String(n).padStart(2,'0'),narr.complements['2'],'complements');}
 if(s.id==='38'){for(const k of ['05']){n++;scenario+=stepCard(extra[+k-1],'E.'+String(n).padStart(2,'0'),narr.complements[String(+k)],'complements');}}
}}
n++;scenario+=stepCard(extra[5],'E.'+String(n).padStart(2,'0'),narr.complements['6'],'complements');

const html=`<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Transit — Guide de test et de démonstration</title><style>
@page{size:A4;margin:14mm 13mm 16mm}
body{font:10pt/1.42 "Segoe UI",Arial,sans-serif;color:#17324d;margin:0}
h1{font-size:30pt;color:#137c82;margin:0 0 4mm}h2{font-size:17pt;color:#137c82;margin:0 0 3mm;break-after:avoid}h2.part{break-before:page;border-bottom:2px solid #137c82;padding-bottom:2mm}
h2.sub{font-size:13pt;margin:5mm 0 2mm;break-after:avoid}h3{font-size:11.5pt;margin:1mm 0}
.cover{height:250mm;display:flex;flex-direction:column;justify-content:center}.cover p{font-size:12pt;margin:1mm 0}
.box{border:1px solid #c9d8e4;border-radius:3mm;padding:3mm 4mm;margin:3mm 0;background:#f5f8fb;break-inside:avoid}
.warn{border-color:#e7b56a;background:#fff6e6}.ok{border-color:#8cc5a2;background:#eef8f1}
pre{font:8.6pt/1.35 Consolas,monospace;white-space:pre-wrap;word-break:break-all;margin:1.5mm 0;padding:2mm 3mm;border-radius:2mm;break-inside:avoid}
pre.cmd{background:#0f2537;color:#f4f4e6}pre.cmd:before{content:"PS> ";color:#8fb6cf}pre.out{background:#eef3f7;color:#17324d;border-left:3px solid #8fa8be}
table{border-collapse:collapse;width:100%;margin:2mm 0;break-inside:avoid}td,th{border:1px solid #d4e0ea;padding:1.2mm 2mm;text-align:left;vertical-align:top;font-size:9pt}th{background:#e4eef5}
ol li,ul li{margin:.8mm 0}
.step{break-inside:avoid;border-top:1px solid #c9d8e4;padding-top:2mm;margin-top:2mm}
.step .head{display:flex;gap:4mm;align-items:center;font-size:8.6pt;color:#4f6b82}.num{background:#137c82;color:#fff;font-weight:700;border-radius:2mm;padding:.5mm 2mm}
.step img,figure img{width:100%;max-height:86mm;object-fit:contain;object-position:left top;border:1px solid #c9d8e4;border-radius:1.5mm;display:block;margin:1.5mm 0}
.todo{margin:1mm 0}.say{background:#dceade;border-radius:2mm;padding:1.5mm 3mm;margin:1mm 0;font-size:9.3pt}
table.vals{width:auto;min-width:60%}table.vals td{font-size:8.8pt;padding:.8mm 2mm}
figure{margin:2mm 0;break-inside:avoid}figcaption{font-size:8.6pt;font-style:italic;color:#4f6b82}
.toc li{margin:1.2mm 0}.small{font-size:8.8pt;color:#4f6b82}
</style></head><body>

<div class="cover"><h1>Transit</h1><h2>Guide de test et de démonstration, de A à Z</h2>
<p>Projet BD70 · Gestion d’un entrepôt logistique</p><p>Eliott LE · Semih TASKIN · Thomas VUILLIN</p>
<p class="small" style="margin-top:12mm">Captures réalisées le 7 novembre 2026 sur la version corrigée (historisation, indicateur HAVING, planification réservée au responsable), sur une base de test neuve. Les références ORAL-CAFE et les noms affichés proviennent du jeu de test (graine 70) : ils peuvent différer légèrement sur le jeu riche de démonstration.</p></div>

<h2 class="part">Sommaire</h2>
<ol class="toc"><li><b>A · Préparer le poste</b> : prérequis, comptes, conseils.</li><li><b>B · Démarrer et arrêter l’application</b> : commandes PowerShell et résultats attendus.</li><li><b>C · Vérifier la base en SQL</b> : évènement, trigger, historisation, nombre d’objets.</li><li><b>D · Vérifier les nouveautés dans l’application</b> : planification par le responsable, refus du chevauchement, HAVING, historique.</li><li><b>E · Scénario complet ORAL-CAFE</b>, de l’annonce fournisseur au camion de sortie, avec les phrases à dire au professeur.</li><li><b>F · Lancer les tests automatisés</b>.</li><li><b>G · Vérifier les livrables</b>.</li><li><b>H · Le jour de la soutenance</b> : préparation, déroulé minuté, plan de secours.</li></ol>
<div class="box">Convention : <b>PS&gt;</b> = commande à taper dans PowerShell. Un bloc gris clair = ce qui doit s’afficher. Un cadre orange sur une capture = l’élément sur lequel cliquer.</div>

<h2 class="part">A · Préparer le poste</h2>
<ul><li>XAMPP installé dans <b>C:\\xampp2</b> (MariaDB 10.4 dans C:\\xampp2\\mysql\\bin, PHP 8.2 dans C:\\xampp2\\php). Ailleurs : ajouter <code>-PhpPath</code> et <code>-MariaPath</code> à la commande de démarrage.</li>
<li>Le projet dans <b>${esc(P)}</b>, avec <b>config/local.php</b> (créé à la première installation, jamais dans Git).</li>
<li>Un navigateur récent (Edge ou Chrome). Pour la démo, préparer <b>un profil de navigateur par compte</b> : deux onglets d’un même profil partagent la session.</li>
<li>Python et Node ne servent qu’aux tests automatisés et à la reconstruction des documents, pas à l’application.</li></ul>
<h3>Comptes de démonstration</h3><p>Mot de passe commun : <b>Entrepot2026!</b></p>
<table><tr><th>Compte</th><th>Profil</th><th>Ce qu’il peut faire</th></tr>
<tr><td>admin@bd70.test</td><td>Administrateur</td><td>Comptes, activation, profils, journal. Aucun écran métier.</td></tr>
<tr><td>manager@bd70.test</td><td>Responsable</td><td>Référentiels, planning, commandes, affectation des préparateurs, indicateurs.</td></tr>
<tr><td>gate@bd70.test</td><td>Accueil</td><td>Arrivée (avec ou sans rendez-vous), documents, parking, appel à quai, départ. Consulte le planning sans le modifier.</td></tr>
<tr><td>warehouse@bd70.test</td><td>Magasinier</td><td>Début/fin à quai, réception, rangement, transferts, préparation des commandes affectées.</td></tr>
<tr><td>carrier1@bd70.test</td><td>Transporteur</td><td>Rendez-vous de sa société uniquement.</td></tr>
<tr><td>pending@bd70.test / inactive@bd70.test</td><td>—</td><td>Connexion refusée (compte en attente ou désactivé) : utile pour montrer le contrôle d’accès.</td></tr></table>

<h2 class="part">B · Démarrer et arrêter l’application</h2>
<h3>B1. Ouvrir PowerShell à la racine du projet</h3>${code(`Set-Location "${P}"`)}
<h3>B2. Démarrer MariaDB et le serveur PHP</h3>${code('powershell -ExecutionPolicy Bypass -File scripts/start.ps1')}
<p>Premier lancement après les corrections : la base de démonstration reçoit les objets d’historisation puis la table de soldes de stock, initialisée depuis l’historique dans une transaction (aucune donnée existante modifiée).</p>
${code('','Historisation ajoutée à bd70_demo_corrige_20261103b : appointment_archive, v_appointment_all, 2 triggers, archive_appointments, ev_archive_appointments.\nPour exécuter l\'évènement automatiquement : SET GLOBAL event_scheduler=ON (compte administrateur).\nOptimisation ajoutée à bd70_demo_corrige_20261103b : 10247 soldes initialisés, 0 écart avec le recalcul depuis l\'historique.\nApplication : http://127.0.0.1:8070').replace('<pre class="cmd"></pre>','')}
<p>Lancements suivants :</p>${code('','Historisation déjà installée dans bd70_demo_corrige_20261103b.\nOptimisation du stock déjà installée dans bd70_demo_corrige_20261103b.\nApplication : http://127.0.0.1:8070').replace('<pre class="cmd"></pre>','')}
<h3>B3. Ouvrir l’application</h3><p>Aller sur <b>http://127.0.0.1:8070</b>. La page de connexion s’affiche.</p>${shot('n00-connexion','Page de connexion : Email, Mot de passe, bouton Se connecter. Le formulaire d’inscription crée un compte en attente.')}
<h3>B4. Arrêter</h3>${code('powershell -ExecutionPolicy Bypass -File scripts/stop.ps1')}
<div class="box warn"><b>En cas de problème.</b><br>• « MariaDB introuvable » : ajouter <code>-MariaPath "chemin\\mysql\\bin"</code>.<br>• « Port occupé par un autre serveur » : arrêter l’autre MariaDB, ou lancer avec <code>-DbPort 3308</code>.<br>• « Migration de l’historisation échouée » : lire le message au-dessus ; la base n’est pas modifiée si la migration échoue avant la création des objets.<br>• Page blanche ou erreur PHP : consulter <b>.local/php-error.log</b>.</div>
<h3>B5. Base de répétition (pour refaire le scénario E sans toucher à la démo)</h3>
<p>MariaDB doit tourner (étape B2). Choisir un nom de base jamais utilisé, puis, dans une <b>nouvelle</b> fenêtre PowerShell à la racine du projet :</p>
${code(`$env:BD70_PORT='3307'; $env:BD70_DATABASE='bd70_test_repetition_01'`)}${code('& C:/xampp2/php/php.exe scripts/install.php $env:BD70_DATABASE')}${code('& C:/xampp2/php/php.exe scripts/seed.php')}${code('& C:/xampp2/php/php.exe scripts/comptes-demo.php')}${code(`$env:BD70_NOW='2026-10-22 12:00:00'; & C:/xampp2/php/php.exe -S 127.0.0.1:18079 -t public`)}
${code('','Base bd70_test_repetition_01 prête ; configuration locale exclue de Git.\nJeu BD70, graine 70, référence 2026-10-22 chargé.\ncarrier1 : TR-1 / Nord Transit\ncarrier2 : TR-2 / Froid Express').replace('<pre class="cmd"></pre>','')}
<p>Ouvrir <b>http://127.0.0.1:18079</b> et garder la fenêtre ouverte. BD70_NOW fixe la date au 22/10/2026 pour que les DLC et le FEFO soient reproductibles. Fermer la fenêtre arrête ce serveur ; la démo du port 8070 n’est pas touchée.</p>

<h2 class="part">C · Vérifier la base en SQL</h2>
<p>Ouvrir la console MariaDB sur la base de démonstration (ou sur la base de répétition) :</p>${code('C:\\xampp2\\mysql\\bin\\mysql.exe -h127.0.0.1 -P3307 -uroot bd70_demo_corrige_20261103b')}
<table><tr><th>Taper dans la console</th><th>Résultat attendu</th></tr>
<tr><td><code>SHOW EVENTS\\G</code></td><td>Name : ev_archive_appointments · Type : RECURRING · Interval : 1 DAY · Status : ENABLED</td></tr>
<tr><td><code>SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema=DATABASE();</code></td><td>127 (3 de cohérence, 11 de protection, 4 de calcul des soldes, 109 d’audit)</td></tr>
<tr><td><code>SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND table_type='BASE TABLE';</code></td><td>43</td></tr>
<tr><td><code>SELECT @@event_scheduler;</code></td><td>ON (start.ps1 lance MariaDB avec --event-scheduler=ON)</td></tr>
<tr><td><code>SELECT a.sku, stock_disponible(a.id, CURDATE()) FROM article a LIMIT 3;</code></td><td>trois articles et leur quantité disponible (fonction stockée)</td></tr>
<tr><td><code>SELECT COUNT(*) FROM (SELECT receipt_item_id,location_id FROM v_balance_controle UNION SELECT receipt_item_id,location_id FROM stock_balance) k LEFT JOIN v_balance_controle c USING(receipt_item_id,location_id) LEFT JOIN stock_balance b USING(receipt_item_id,location_id) WHERE COALESCE(c.qty,0)&lt;&gt;COALESCE(b.qty,0);</code></td><td>0 : chaque solde tenu par trigger est égal au recalcul depuis l’historique</td></tr>
<tr><td><code>SELECT origine, COUNT(*) FROM v_appointment_all GROUP BY origine;</code></td><td>une ligne « courant » (et « historique » après un archivage)</td></tr>
<tr><td><code>INSERT INTO appointment(reference,dock_id,driver_id,vehicle_id,operation,starts_at,ends_at) SELECT 'TEST-CHEV',dock_id,driver_id,vehicle_id,operation,starts_at,ends_at FROM appointment WHERE status='active' LIMIT 1;</code></td><td>ERROR 1644 (45000) : Ce créneau chevauche un rendez-vous actif sur ce quai. Rien n’est inséré.</td></tr>
<tr><td><code>SHOW GRANTS FOR CURRENT_USER;</code> puis <code>exit</code></td><td>Droits du compte connecté ; le compte de l’application est décrit dans sql/06_privileges.example.sql.</td></tr></table>
<h3>Tester l’archivage — uniquement sur une base de test</h3>
<div class="box warn"><b>Ne pas lancer <code>CALL archive_appointments(...)</code> sur la base de démonstration</b> : la procédure déplace réellement des rendez-vous. Sur la base de répétition (B5), créer deux rendez-vous anciens puis archiver :</div>
${code("INSERT INTO appointment(reference,dock_id,driver_id,vehicle_id,operation,starts_at,ends_at,status) VALUES ('RDV-ANCIEN-01',1,1,1,'reception','2025-06-02 08:00','2025-06-02 09:00','cancelled'),('RDV-ANCIEN-02',1,1,1,'reception','2025-06-03 08:00','2025-06-03 09:00','active');")}
${code('CALL archive_appointments(30);  SELECT origine, status, COUNT(*) FROM v_appointment_all GROUP BY origine, status;','rendez_vous_archives  total_historique\n2                     2\norigine     status     COUNT(*)\ncourant     active     1\nhistorique  active     1\nhistorique  cancelled  1')}
<p class="small">Un délai inférieur à 30 jours est refusé (« Délai d archivage minimal : 30 jours »). Seuls les rendez-vous sans passage camion sont déplacés.</p>

<h2 class="part">D · Vérifier les nouveautés dans l’application</h2>
<h3>D1. Le responsable planifie les quais</h3><p>Se connecter avec <b>manager@bd70.test</b> → menu <b>Quais & rendez-vous</b> → choisir la journée → le bouton <b>Nouveau rendez-vous</b> est visible. Avec <b>gate@bd70.test</b>, le même écran s’affiche en consultation, sans ce bouton : le sujet réserve la planification au responsable, l’accueil tient le poste de garde.</p>${shot('n01-manager-planning','Planning vu par le responsable, bouton Nouveau rendez-vous encadré.')}${shot('n01b-gate-planning','Le même planning vu par l’agent d’accueil : aucun bouton de création.')}
<h3>D2. Créer un rendez-vous</h3><p>Avec le responsable, cliquer sur <b>Nouveau rendez-vous</b>. Remplir : Référence <b>VERIF-01</b>, un quai, un chauffeur et un véhicule compatibles, l’opération, un début et une fin sur un créneau libre (ici le 24/10/2026 de 07:00 à 07:30). Cliquer sur <b>Enregistrer</b>.</p>${shot('n02-manager-rdv-saisie','Formulaire rempli.')}${shot('n03-manager-rdv-enregistre','Message « Opération enregistrée ».')}
<h3>D3. Refus du chevauchement</h3><p>Refaire exactement la même saisie avec la référence <b>VERIF-02</b>. Le refus s’affiche ; la base le refuserait aussi par trigger (partie C). Ensuite, dans le planning, <b>annuler VERIF-01</b> pour garder la démo propre.</p>${shot('n04-manager-rdv-conflit','Message « Ce créneau chevauche un rendez-vous actif ».')}
<h3>D4. Indicateur avec HAVING</h3><p>Se connecter avec <b>manager@bd70.test</b> → <b>Indicateurs & états</b> → choisir la période et un <b>Seuil d’attente (min)</b> → <b>Filtrer</b>. Sur le jeu riche : période 01/08/2026 – 29/10/2026, seuil <b>8</b> = les transporteurs apparaissent ; seuil <b>20</b> = tableau vide.</p>${shot('n05-indicateurs-seuil','Champ Seuil d’attente encadré.')}${shot('n06-having','Tableau « Transporteurs au-dessus du seuil d’attente » : GROUP BY puis HAVING AVG(wait_minutes) > seuil.')}
<h3>D5. Rendez-vous historisés</h3><p>Toujours en responsable → <b>Référentiels</b> → rubrique <b>Rendez-vous historisés</b> → <b>Afficher</b>. Lecture seule : aucun bouton de modification. Sur la démo, la liste est vide tant que l’évènement n’a rien archivé (rendez-vous de plus d’un an).</p>${shot('n07-historique','Rendez-vous déplacés par archive_appointments, avec la date d’historisation.')}
<h3>D6. Transporteur limité à sa société</h3><p>Se connecter avec <b>carrier1@bd70.test</b> : seuls ses rendez-vous apparaissent ; il peut en demander, modifier ou annuler.</p>${shot('n08-transporteur','Espace transporteur.')}

<h2 class="part">E · Scénario complet ORAL-CAFE</h2>
<p>Ce parcours suit un lot de café de bout en bout : le fournisseur annonce 20 unités, le magasinier en accepte 18 et en déclare 2 endommagées, transfère 3 unités, puis 10 unités sont préparées en FEFO, mises en colis et chargées dans le camion ORAL-CAFE-SORTIE ; la traçabilité retrouve ce camion à partir du lot.</p>
<div class="box"><b>Où le faire ?</b> Sur la base de répétition (B5, http://127.0.0.1:18079) pour <b>refaire</b> les saisies. Pour l’oral, <b>montrer</b> les fiches déjà créées (rechercher ORAL-CAFE dans chaque écran) plutôt que tout saisir en direct. Chaque étape indique le compte à utiliser : se déconnecter (en haut à droite) puis se reconnecter, ou utiliser un profil de navigateur par compte.</div>
${scenario}

<h2 class="part">F · Lancer les tests automatisés</h2>
<p>MariaDB doit tourner (B2). Toujours sur une <b>base de test neuve</b>, jamais sur la démo. Dans une nouvelle fenêtre PowerShell à la racine du projet :</p>
${code(`$env:BD70_PORT='3307'; $env:BD70_DATABASE='bd70_test_verif1'; $env:BD70_TEST_DATABASE='bd70_test_verif1'`)}${code('& C:/xampp2/php/php.exe scripts/install.php $env:BD70_DATABASE; & C:/xampp2/php/php.exe scripts/seed.php')}${code('& C:/xampp2/php/php.exe tests/integration.php','OK ...\n64 réussis, 0 échecs')}
<p>Pour chaque autre suite, recommencer les deux premières commandes avec un nouveau nom (bd70_test_verif2, 3…) puis lancer le test :</p>
<table><tr><th>Commande</th><th>Attendu</th></tr><tr><td><code>tests/reports.php</code></td><td>7 lignes OK</td></tr><tr><td><code>tests/corrections.php</code></td><td>19 lignes OK, aucune ECHEC (dont « Rendez-vous gérés par accueil et responsable »)</td></tr><tr><td><code>tests/completion.php</code></td><td>23 lignes OK</td></tr><tr><td><code>tests/finalisation.php</code></td><td>14 lignes OK</td></tr></table>
<p>Cohérence MCD / schéma relationnel / SQL :</p>${code('python scripts/verify-models.py docs/diagrammes/schema.json .local/verif-modeles.json','{"passed": true, "failed": [], "business_fk": 61, "business_columns": 214}')}
<p>Fermer ensuite la fenêtre (ou <code>Remove-Item Env:BD70_DATABASE, Env:BD70_TEST_DATABASE</code>) pour que l’application reprenne la base de config/local.php. Les bases de test peuvent être supprimées avec <code>DROP DATABASE bd70_test_verif1;</code>.</p>

<h2 class="part">G · Vérifier les livrables</h2>
<table><tr><th>Fichier</th><th>Ce qu’il faut vérifier</th></tr>
<tr><td>livrables/rapport/RAPPORT-PROJET-BD70.pdf</td><td>Couverture avec les trois noms, table des matières, cahier des charges, cas d’utilisation, MCD (extraits + complet), schéma relationnel (texte + figures), normalisation, implémentation, 8 fonctionnalités objectif / travail réalisé / conclusion avec captures, vérification, performances, conclusion. Relire l’orthographe.</td></tr>
<tr><td>livrables/rapport/DIAGRAMMES-BD70.pdf</td><td>Cas d’utilisation (1 page), MCD, MLD, 6 extraits. Zoomer fort : le texte reste net (vectoriel).</td></tr>
<tr><td>livrables/use-case, entite-association, schema-relationnel</td><td>Chaque diagramme en PDF, SVG et .drawio. Ouvrir un .drawio sur app.diagrams.net : chaque objet doit être modifiable.</td></tr>
<tr><td>docs/performances.md</td><td>10 requêtes, médianes sur la base volumétrique et sur la démo, EXPLAIN avant/après index (4,00 → 0,90 ms).</td></tr>
<tr><td>sql/01 à 08</td><td>01 schéma, 02 vues, 03 procédures, 04 triggers, 05 index, 06 droits (GRANT/REVOKE), 07 données, 08 historisation.</td></tr>
<tr><td>livrables/soutenance/</td><td>Transit-diapo.html (11 diapos), Guide-oral.md, Questions-prof.md, ce guide.</td></tr></table>

<h2 class="part">H · Le jour de la soutenance</h2>
<h3>H1. Avant d’entrer (15 minutes)</h3><ol>
<li>Lancer <b>scripts/start.ps1</b> (B2) et vérifier « Application : http://127.0.0.1:8070 ».</li>
<li>Si la démo se fait sur la base de soutenance préparée (avec ORAL-CAFE déjà enregistré), la mettre à jour une fois puis lancer son serveur :</li></ol>
${code('$env:BD70_PORT=\'3307\'; & C:/xampp2/php/php.exe scripts/migrate-historisation.php bd70_test_soutenance_20261105153225')}${code('& C:/xampp2/php/php.exe scripts/migrate-optimisation.php bd70_test_soutenance_20261105153225')}${code(`$env:BD70_DATABASE='bd70_test_soutenance_20261105153225'; $env:BD70_NOW='2026-10-22 12:00:00'; & C:/xampp2/php/php.exe -S 127.0.0.1:18079 -t public`)}
<ol start="3"><li>Ouvrir un profil de navigateur par compte déjà connecté : admin, manager, gate, warehouse (et carrier1).</li>
<li>Ouvrir <b>livrables/soutenance/Transit-diapo.html</b>, cliquer sur « Plein écran ». Avoir docs/soutenance/Transit.pdf en secours.</li>
<li>Garder ouverts : sql/08_historisation.sql, sql/02_vues.sql, docs/performances.md, Questions-prof.md.</li></ol>
<h3>H2. Déroulé minuté</h3>
<table><tr><th>Temps</th><th>Quoi</th><th>Où</th></tr>
<tr><td>0:00 – 5:00</td><td>Architecture, base et back-end : 11 diapositives (texte dans Guide-oral.md)</td><td>Transit-diapo.html</td></tr>
<tr><td>5:00 – 5:40</td><td>Comptes puis planning du responsable, bouton Nouveau rendez-vous</td><td>Étapes E.01–E.06, D1</td></tr>
<tr><td>5:40 – 6:35</td><td>Avis ORAL-CAFE-AVIS et sa ligne de 20 unités</td><td>Étapes E.08–E.12</td></tr>
<tr><td>6:35 – 7:25</td><td>Réception : 18 acceptées, 2 endommagées, transfert de 3</td><td>Étapes E.19–E.24</td></tr>
<tr><td>7:25 – 8:30</td><td>Commande de 10, affectation, FEFO, colis, bon de livraison</td><td>Étapes E.27–E.33, E.41</td></tr>
<tr><td>8:30 – 9:45</td><td>Traçabilité ORAL-CAFE-LOT jusqu’à ORAL-CAFE-SORTIE</td><td>Étapes E.39–E.40</td></tr>
<tr><td>9:45 – 10:00</td><td>Conclure, laisser la trace à l’écran</td><td>—</td></tr>
<tr><td>10:00 – 20:00</td><td>Questions individuelles</td><td>Questions-prof.md</td></tr></table>
<h3>H3. Plan de secours</h3><ul>
<li>L’application ne démarre pas : montrer ce guide (partie E) et le rapport, puis docs/soutenance/Transit.pdf.</li>
<li>Une saisie échoue en direct : lire le message (il est fait pour l’utilisateur), puis montrer la fiche déjà créée.</li>
<li>Question SQL : ouvrir le fichier sql/ correspondant ; pour un EXPLAIN, docs/performances.md.</li></ul>
<div class="box ok">Phrase de conclusion : « Nous sommes partis de la structure de la base et nous venons de retrouver la chaîne complète dans l’application. Nous sommes prêts pour vos questions. »</div>
</body></html>`;
const htmlFile=path.join(G,'guide.html');fs.writeFileSync(htmlFile,html);
(async()=>{const b=await chromium.launch({headless:true,channel:'msedge'});const p=await b.newPage();await p.goto(url.pathToFileURL(htmlFile).href,{waitUntil:'load'});
const out=path.join(root,'livrables/soutenance/GUIDE-TEST-ET-DEMO.pdf');
await p.pdf({path:out,format:'A4',printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font:8px Arial;color:#4f6b82;width:100%;padding:0 13mm;display:flex;justify-content:space-between"><span>TRANSIT · Guide de test et de démonstration</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',margin:{top:'14mm',bottom:'16mm',left:'13mm',right:'13mm'}});
await b.close();console.log(out);})().catch(e=>{console.error(e);process.exit(1)});
