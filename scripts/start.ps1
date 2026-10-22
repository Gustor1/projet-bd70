param([string]$PhpPath='C:/xampp2/php/php.exe',[string]$MariaPath='C:/xampp2/mysql/bin',[int]$WebPort=8070,[int]$DbPort=3307)
$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
$dataPath=Join-Path $projectRoot '.local/mariadb'
if(!(Test-Path -LiteralPath $PhpPath)){throw 'PHP introuvable : préciser -PhpPath.'}
if(!(Test-Path -LiteralPath (Join-Path $MariaPath 'mysqld.exe'))){throw 'MariaDB introuvable : préciser -MariaPath.'}
New-Item -ItemType Directory -Force (Join-Path $projectRoot '.local') | Out-Null
if(!(Test-Path -LiteralPath (Join-Path $dataPath 'my.ini'))){
 & (Join-Path $MariaPath 'mysql_install_db.exe') "--datadir=$dataPath" "--port=$DbPort" --silent
 if($LASTEXITCODE -ne 0){throw 'Initialisation MariaDB échouée.'}
}
$listening=Get-NetTCPConnection -LocalPort $DbPort -State Listen -ErrorAction SilentlyContinue
if(!$listening){
 $arguments=@(('"--defaults-file='+$dataPath+'/my.ini"'),'--bind-address=127.0.0.1',"--port=$DbPort",'--console')
 $dbProcess=Start-Process -FilePath (Join-Path $MariaPath 'mysqld.exe') -ArgumentList $arguments -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $projectRoot '.local/mariadb-out.log') -RedirectStandardError (Join-Path $projectRoot '.local/mariadb-error.log')
 $dbProcess.Id | Set-Content (Join-Path $projectRoot '.local/mariadb.pid')
 for($i=0;$i -lt 40;$i++){if(Get-NetTCPConnection -LocalPort $DbPort -State Listen -ErrorAction SilentlyContinue){break};Start-Sleep -Milliseconds 250}
} else {
 $process=Get-CimInstance Win32_Process -Filter "ProcessId=$($listening[0].OwningProcess)"
 if($process.CommandLine -notlike '*projet-bd70*.local*mariadb*'){throw 'Port occupé par un autre serveur : choisir un port libre, ne pas réutiliser une base existante.'}
}
if(!(Test-Path -LiteralPath (Join-Path $projectRoot 'config/local.php'))){
 $env:BD70_PORT="$DbPort"
 Push-Location $projectRoot
 try{& $PhpPath scripts/install.php bd70_demo;if($LASTEXITCODE -ne 0){throw 'Installation échouée.'};& $PhpPath scripts/seed.php;if($LASTEXITCODE -ne 0){throw 'Chargement du jeu échoué.'}}finally{Pop-Location}
}
$webListening=Get-NetTCPConnection -LocalPort $WebPort -State Listen -ErrorAction SilentlyContinue
if(!$webListening){
 $webProcess=Start-Process -FilePath $PhpPath -ArgumentList @('-S',"127.0.0.1:$WebPort",'-t',('"'+$projectRoot+'/public"')) -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $projectRoot '.local/php-out.log') -RedirectStandardError (Join-Path $projectRoot '.local/php-error.log')
 $webProcess.Id | Set-Content (Join-Path $projectRoot '.local/php.pid')
}
Write-Output "Application : http://127.0.0.1:$WebPort"
