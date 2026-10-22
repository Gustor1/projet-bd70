<?php require __DIR__.'/helpers.php'; ?>
<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Transit · Entrepôt BD70</title><link rel="stylesheet" href="/assets/app.css"><script src="/assets/app.js" defer></script></head>
<body>
<?php if($user): ?>
<aside class="sidebar no-print"><a class="brand" href="/"><span class="brand-symbol" aria-hidden="true">T</span><span>Transit<small>Gestion d’entrepôt</small></span></a><nav aria-label="Menu principal">
<?php $nav=['home'=>['Vue d’ensemble',null],'planning'=>['Quais & rendez-vous','trace'],'visits'=>['Passages camions','visits'],'receipts'=>['Réceptions','stock'],'stock'=>['Stocks & rangement','stock'],'orders'=>['Préparation & expédition','orders'],'trace'=>['Traçabilité des lots','trace'],'reports'=>['Indicateurs & états','reports'],'catalog'=>['Référentiels',null]];
foreach($nav as $key=>[$label,$right])if(!$right||Auth::can($user,$right))echo '<a '.($page===$key?'aria-current="page"':'').' href="'.h(url(['page'=>$key])).'">'.h($label).'</a>'; ?>
</nav><div class="sidebar-bottom"><span class="site-dot"></span> Site de démonstration<br><small>Données fictives · BD70</small></div></aside>
<?php endif; ?>
<div class="shell <?= $user?'':'anonymous' ?>"><header class="topbar no-print"><span><?= $user?'Entrepôt de Belfort':'Transit / BD70' ?></span><div class="account"><?php if($user): ?><span><?= h($user['name']) ?><small><?= h(Catalog::VALUES[$user['role']]) ?></small></span><?php startForm('logout'); ?><button class="text-button">Déconnexion</button></form><?php else: ?><span>Application pédagogique</span><?php endif; ?></div></header>
<main id="main"><?php if($message): ?><div role="status" class="notice success"><?= h($message) ?></div><?php endif; ?><?php if($error): ?><div role="alert" class="notice error"><?= h($error) ?></div><?php endif; ?>
<?php try {
 if($user&&in_array($page,['catalog','stock','orders','visits'],true)&&(int)$db->scalar('SELECT (SELECT COUNT(*) FROM truck_visit)+(SELECT COUNT(*) FROM receipt_item)+(SELECT COUNT(*) FROM customer_order)')>2000){
  echo '<details class="panel no-print"><summary>Affiner les listes de sélection</summary><p>Retrouvez une référence ou un nom dans les listes volumineuses avant de remplir le formulaire.</p><form method="get" class="filters"><input type="hidden" name="page" value="'.h($page).'">';
  if($page==='catalog')echo '<input type="hidden" name="t" value="'.h($_GET['t']??'carrier').'">';
  inputField('ref_search','Référence ou nom',$_GET['ref_search']??'','search',false);echo '<button>Rechercher les références</button></form></details>';
 }
 if($page!=='error')require __DIR__.'/'.(in_array($page,['home','login','catalog','planning','visits','receipts','stock','orders','reports','trace','document'],true)?$page:'home').'.php';
}catch(Throwable $viewError){http_response_code(422);echo '<div role="alert" class="notice error">'.h($viewError instanceof DomainException?$viewError->getMessage():'Impossible de présenter ces données.').'</div>';error_log('BD70 vue : '.$viewError->getMessage());} ?>
</main><footer>Transit · Projet BD70 · Heure du site : Europe/Paris · <?= h(date('d/m/Y H:i')) ?></footer></div></body></html>
