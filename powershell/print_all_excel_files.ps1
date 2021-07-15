function PrintExcelFiles($path = $pwd) 
{ 
    foreach ($item in Get-ChildItem $path )
    {
		$flag = $false
        if (Test-Path $item.FullName -PathType Container) 
        {
            #$item 
            PrintExcelFiles $item.FullName 
        } 
        else 
        { 
			if (($item.Extension -eq ".xls") -or ($item.Extension -eq ".xlsx"))
			{
				#print file
                foreach ($street in $blacklist)
                {
                    if ($item.BaseName -eq $street)
                    {
                        $flag = $true
                        break
                    }
                }
                if (-not $flag) 
                {
				    $wb = $xl.Workbooks.Open($item.FullName)
				    $wb.PrintOUT(1)
                    $wb.Close($false)
					Log "Print $item" "$filepath"
                }
                else
                {
					Log "Ignore $item" "$filepath"
                }
			}
        }
    } 
}


function Log($s, $f, $append=$true) {
#Log "Сообщение" "путь к лог-файлу" "Переписать или добавить $true (по умолчанию)- добавить"
  $k = get-date -UFormat "%b %e %T"
  if ($append) {
    $k + " " + $s | tee -filepath "$f" -Append
  }
  else {
    $k + " " + $s | tee -filepath "$f"
  }
}


$blacklist = "УЛ ШАГОЛЬСКАЯ 2-Я 36а",
"УЛ ШАГОЛЬСКАЯ 41а",
"УЛ КРАСНОЗНАМЕННАЯ 6 ",
"УЛ МЕЛЬНИЧНЫЙ ТУПИК 16 ",
"СВЕРДЛОВСКИЙ ПР-КТ 8в",
"УЛ СОЛНЕЧНАЯ 42 ",
"УЛ ЦИНКОВАЯ 12а",
"УЛ КРАСНОЗНАМЕННАЯ 6 ",
"УЛ КРАСНОГО УРАЛА 9 ",
"КОМСОМОЛЬСКИЙ ПРОСПЕКТ 88а",
"КОМСОМОЛЬСКИЙ ПР-КТ 48а"

$s = $args[0]
$filepath = $PSScriptroot + "\report.txt"
if (-not (Test-Path($filepath))) 
{
	Log "---------------------------" "$filepath" $False
	Log "Print all excel files from $s" "$filepath" $False
}
else
{
	Log "---------------------------" "$filepath"
	Log "Print all excel files from $s" "$filepath"
}
$xl = New-Object -comobject excel.application
$xl.visible = $false
$xl.DisplayAlerts = $false
if ($xl.ActivePrinter -notlike "Принтер ГИС*")
{
	Log "ERROR Set Printer Gis GKH as default printer" "$filepath" 
	exit 
}
try
{
#print on default printer
	PrintExcelFiles $s 
        $xl.Quit()
}
catch
{	
	$xl.Quit()
	$message = $_.Exception | format-list -force 
	Log "ERROR $message" "$filepath"
}