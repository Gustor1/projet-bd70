<?php
declare(strict_types=1);
require_once __DIR__.'/Database.php';
require_once __DIR__.'/Auth.php';
require_once __DIR__.'/Catalog.php';
require_once __DIR__.'/Warehouse.php';
require_once __DIR__.'/Reports.php';
function h(mixed $v): string { return htmlspecialchars((string)($v??''),ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8'); }
function url(array $p): string { return '/?'.http_build_query($p); }
