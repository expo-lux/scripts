import re
import binascii
import telnetlib
import argparse
import time
HOST = "192.168.222.251"
USER = "root"
PASSWORD = "router"
TIMEOUT = 10


telnet = telnetlib.Telnet(HOST)
telnet.read_until(b"Login: ", 5)
telnet.write((USER + "\n").encode('utf-8'))
if PASSWORD:
    telnet.read_until(b"Password: ")
    telnet.write((PASSWORD + "\n").encode('utf-8'))

telnet.write(b"enable\n")
time.sleep(1)
telnet.write(b"gsm 0 1 sms message  list all\n")
time.sleep(1)
telnet.write(b"gsm 0 1 sms message  list all\n")
data = telnet.read_until(b"GS1002#", TIMEOUT)
#data = telnet.read_until(b"GS1002#", TIMEOUT)[:-2]
if not data:
    print("Timeout expired\n")
    exit(1)
print(data)

telnet.write(b"exit\n" * 2)