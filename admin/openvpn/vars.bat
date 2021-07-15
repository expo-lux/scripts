@echo off
rem Edit this variable to point to
rem the openssl.cnf file included
rem with easy-rsa.

set HOME=D:\Program Files\OpenVPN\easy-rsa
set KEY_CONFIG=openssl-1.0.0.cnf

rem Edit this variable to point to
rem your soon-to-be-created key
rem directory.
rem
rem WARNING: clean-all will do
rem a rm -rf on this directory
rem so make sure you define
rem it correctly!
set KEY_DIR=keys

rem Increase this to 2048 if you
rem are paranoid.  This will slow
rem down TLS negotiation performance
rem as well as the one-time DH parms
rem generation process.
set KEY_SIZE=2048

rem These are the default values for fields
rem which will be placed in the certificate.
rem Change these to reflect your site.
rem Don't leave any of these parms blank.

set KEY_COUNTRY=RU
set KEY_PROVINCE=CH
set KEY_CITY=Chelyabinsk
set KEY_ORG=x
set KEY_EMAIL=info@x.ru
set KEY_CN=office.x.ru
set KEY_NAME=x
set KEY_OU=""
set PKCS11_MODULE_PATH=changeme
set PKCS11_PIN=1234
