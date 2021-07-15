param (
    [string]$db = "",
    [string]$password = "",
    [string]$excludeCollectionsWithPrefix = "",
    [string]$OutDir = "",
    [string]$filePrefix = "",
    [string]$logfile = "process.log",
    [string]$mongoDumpPath = "C:\Program Files\MongoDB\Server\3.4\bin\mongodump.exe",
    [string]$archiverPath = "C:\Program Files\7-Zip\7z.exe"
 )

function New-TemporaryDirectory {
    $parent = [System.IO.Path]::GetTempPath()
    [string] $name = [System.Guid]::NewGuid()
    New-Item -ItemType Directory -Path (Join-Path $parent $name)
}

mkdir $OutDir
$scriptPath = split-path -parent $MyInvocation.MyCommand.Definition
$temp = (New-TemporaryDirectory).FullName
$datePattern = get-date -UFormat %Y-%m-%d_%H-%M
$filename = $filePrefix + "_" + $datePattern
$archivePath = $OutDir + "\" + $filename + ".zip"
if ($excludeCollectionsWithPrefix -ne "") {
  start-process "$mongoDumpPath" "/excludeCollectionsWithPrefix:$excludeCollectionsWithPrefix /db:$db /out:$temp" -wait
} else {
  start-process "$mongoDumpPath" "/db:$db /out:$temp" -wait
}
$msg = (Get-Date).ToString()
$msg += " MongoDump completed"
Echo $msg | Out-file -Append -FilePath $scriptPath\$logfile
if ($password -ne "" ) {
  start-process "$archiverPath" "a $archivePath -p$password $temp\$db\*" -wait
} else {
    start-process "$archiverPath" "a $archivePath $temp\$db\*" -wait
}
$msg = (Get-Date).ToString()
$msg += " " + $archivepath + " completed"
Echo $msg | Out-file -Append -FilePath $scriptPath\$logfile
rm -Recurse $temp
