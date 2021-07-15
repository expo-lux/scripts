#только приватный доступ
import requests
import munch

#получить список доменов
#i.ivanov
headers = { 'PddToken': 'F4KTVIPLCFULRWCDFGJIKNGUPEWQUEMSKDG7DDFJZDPILB3JXLOQ'}
#x@yandex
headers = { 'PddToken': 'E7UIU2AHR33EOXDJ5W6R2Q2WRNW4TGCI5MZ2U6DOX5YKBEJW334A' }
url = 'https://pddimp.yandex.ru/api2/admin/domain/domains?'
r=requests.get(url,headers=headers)
obj = munch.munchify(r.json())
print(r.json())
#добавить ящик
url = 'https://pddimp.yandex.ru/api2/admin/email/add'
payload = {'domain': 'bellatrix.xyz', 'login': 'test2', 'password' : 'hardpass'}
headers = { 'PddToken': 'F4KTVIPLCFULRWCDFGJIKNGUPEWQUEMSKDG7DDFJZDPILB3JXLOQ'}
r=requests.post(url,data=payload,headers=headers)

#домен bellatrix.xyz
#заблокировать почтовый ящик
headers = { 'PddToken': 'F4KTVIPLCFULRWCDFGJIKNGUPEWQUEMSKDG7DDFJZDPILB3JXLOQ'}
payload = {'domain': 'bellatrix.xyz', 'login': 'test2', 'enabled': 'no' }
url = 'https://pddimp.yandex.ru/api2/admin/email/edit'
r=requests.post(url,data=payload,headers=headers)

#добавить зам. администратора домена
url = 'https://pddimp.yandex.ru/api2/admin/deputy/list?domain=mrtkt74.ru'
#получить список замов
r = requests.get(url,headers=headers)

#добавить зама
url = 'https://pddimp.yandex.ru//api2/admin/deputy/add'
payload = {'domain': 'mrtkt74.ru', 'login': 'i.ivanov'}
headers = { 'PddToken': 'E7UIU2AHR33EOXDJ5W6R2Q2WRNW4TGCI5MZ2U6DOX5YKBEJW334A' }
r=requests.post(url,data=payload,headers=headers)

