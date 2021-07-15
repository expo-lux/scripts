$fname = "Дарья"
$sname = "Иванова"
$full_name = $sname + " " + $fname
$login = "d.ivanova"
$pass = "hardpass"
$email = $login + "@x.ru"
$UPN = $login + "@x.LOCAL"

new-aduser `
-SamAccountName $login `
-Name $full_name `
-DisplayName $full_name `
-AccountPassword (ConvertTo-SecureString -AsPlainText $pass -Force) `
-Path "OU=Отдел аналитики,OU=x,DC=x,DC=LOCAL" `
-EmailAddress $email `
-GivenName $fname `
-Surname $sname `
-UserPrincipalName $UPN `
-Enabled $true 
#change pass at the next login
Set-ADUser -Identity TestUser -ChangePasswordAtNextLogon $true
