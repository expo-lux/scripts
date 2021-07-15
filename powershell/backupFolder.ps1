param (
    [string]$password = "",
    [string]$InDir = "",
    [string]$OutDir = "",
    [string]$filePrefix = "",
    [string]$logfile = "process.log",
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
if ($password -ne "" ) {
  start-process "$archiverPath" "a $archivePath -p$password $InDir\*" -wait
} else {
    start-process "$archiverPath" "a $archivePath $InDir\*" -wait
}
$msg = (Get-Date).ToString()
$msg += " " + $InDir + " Compress completed"
Echo $msg | Out-file -Append -FilePath $scriptPath\$logfile
rm -Recurse $temp
