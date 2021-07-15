cd /d "D:\Program Files\OpenVPN\easy-rsa"
call vars.bat
set /p user="Enter username:"
mkdir %user%
call build-key.bat %user%
echo %user%
cp keys\ca.crt %user%\
cp keys\client.ovpn  %user%\ 
cp keys\%user%.key %user%\
cp keys\%user%.crt %user%\
cp keys\auth.cfg %user%
vim -c 'startinsert' ".\%user%\auth.cfg"
vim -c 'startinsert' ".\%user%\client.ovpn"
7z a %user%\%user%.zip .\%user%\*
cat ".\%user%\auth.cfg"
