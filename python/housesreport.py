import requests
import pymongo

from pymongo import MongoClient

s = requests.Session()
url = 'http://localhost:9900/Auth/SignInInternal'
payload = {'UserName': 'x', 'Password': 'hardpass'}
res = s.post(url, json=payload)

client = MongoClient('localhost', 27017)
db = client['reformagkh']
houses = db['GetHouseProfile988Response']
pjreo_houses = houses.find({"inn": "7448078549", "_header._deleted": {"$exists": False}})
for item in pjreo_houses:
    id1 = item['_id']
    url = 'http://localhost:9900/CustomService/ReportManager/GetReportHouse/?FormName=Form23PrintView&DocumentId='
    url += id1
    a = s.get(url)
    filepath = "F:/out/выполн_"
    filepath += item['full_address']['street_formal_name'] + '_'
    filepath += item['full_address']['house_number'] + '.pdf'
    f = open(filepath, 'wb')
    f.write(a.content)
    f.close()
    url = 'http://localhost:9900/CustomService/ReportManager/GetReportHouse/?FormName=Form24PrintView&DocumentId='
    url += id1
    a = s.get(url)
    filepath = "F:/out/коммун_"
    filepath += item['full_address']['street_formal_name'] + '_'
    filepath += item['full_address']['house_number'] + '.pdf'
    f = open(filepath, 'wb')
    f.write(a.content)
    f.close()

