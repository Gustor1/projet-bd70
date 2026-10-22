$ErrorActionPreference='Stop'
$projectRoot=Split-Path $PSScriptRoot -Parent
foreach($name in @('php','mariadb')){
 $pidFile=Join-Path $projectRoot ".local/$name.pid"
 if(Test-Path -LiteralPath $pidFile){
  $taskPid=[int](Get-Content -LiteralPath $pidFile)
  $taskProcess=Get-CimInstance Win32_Process -Filter "ProcessId=$taskPid" -ErrorAction SilentlyContinue
  $normalizedRoot=$projectRoot.Replace('\','/')
  if($taskProcess -and $taskProcess.CommandLine.Replace('\','/').IndexOf($normalizedRoot,[System.StringComparison]::OrdinalIgnoreCase) -ge 0){
   if($name -eq 'mariadb'){throw 'Arrêter MariaDB proprement avec la commande mysqladmin du README avant de fermer le processus.'}
   Stop-Process -Id $taskPid
  }
 }
}
