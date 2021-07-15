param (
    [string]$InDir = "",
    [string]$OutDir = "",
	[int]$PurgeRetentionLocal = -15,
	[int]$PurgeRetentionNAS = -60,
    [string]$logfile = "process.log"
 )
 
 if(!(Test-Path $OutDir -PathType Container)) { 
   mkdir $OutDir
 }
 
 $scriptPath = split-path -parent $MyInvocation.MyCommand.Definition
 
 $limit = (Get-Date).AddDays($PurgeRetentionLocal)
 Get-ChildItem $InDir -Recurse | ? {
    -not $_.PSIsContainer -and $_.LastWriteTime -lt $limit
 } | Remove-Item
  start-process "robocopy.exe" "$InDir $OutDir /E /Z /COPY:TDA /DCOPY:T  /R:2 /W:5 /UNILOG+:$logfile" -wait
 $limit = (Get-Date).AddDays($PurgeRetentionNAS)
 Get-ChildItem $OutDir -Recurse | ? {
    -not $_.PSIsContainer -and $_.LastWriteTime -lt $limit
 } | Remove-Item
 
$msg = (Get-Date).ToString()
$msg += " " + $InDir + " backup to " + $OutDir + " completed"
Echo $msg | Out-file -Append -FilePath $scriptPath\$logfile

 