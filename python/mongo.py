# coding: utf-8
import pymongo
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
with open('E:/experiments/mongodb/awesomemoscow_report_moscow.js', 'r') as myfile:
    data = myfile.read()
msc = client['AwesomeMoscow'].eval(data)
for x in msc['_batch']:
    print(x['Название_класса'])

