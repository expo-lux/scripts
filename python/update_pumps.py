# coding=utf-8
import re
import csv
import pymongo
import os
import sys
from pymongo import MongoClient


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def get_house_number(s):
    pattern = re.compile('(\d+)(\D*)')
    res = pattern.search(s)
    return res.group(1)


def get_house_block(s):
    pattern = re.compile('(\d+)(\D*)')
    res = pattern.search(s)
    return res.group(2)


# hpat = re.compile(".*комсомольский.*", re.IGNORECASE)
# npat = re.compile("71а", re.IGNORECASE)
# h = col.find_one({"HouseDisplayAddress": {"$regex": regx}, "FiasHouseAddress.HOUSENUM": {"$regex": npat}})


csv_path = get_script_path() + "/pumps.csv"
f = open(csv_path, "r")
reader = csv.reader(f)
client = MongoClient('localhost', 27017)
db = client['reformagkh']
houses_collection = db['GetHouseProfile988Response']

adr = []
blacklist = ["ШАГОЛЬСКАЯ 2-Я 36а",
             "ШАГОЛЬСКАЯ 41а",
             "КРАСНОЗНАМЕННАЯ 6",
             "1-Й КВАРТАЛ ШАГОЛЬСКАЯ 6",
             "1-Й КВАРТАЛ ШАГОЛЬСКАЯ 8",
             "МЕЛЬНИЧНЫЙ ТУПИК 16",
             "СВЕРДЛОВСКИЙ ПР-КТ 8в",
             "СОЛНЕЧНАЯ 42",
             "ЦИНКОВАЯ 12а",
             "КРАСНОЗНАМЕННАЯ 6",
             "КРАСНОГО УРАЛА 9",
             "КОМСОМОЛЬСКИЙ ПРОСПЕКТ 88а",
             "КОМСОМОЛЬСКИЙ ПРОСПЕКТ 48а",
             "ПР-КТ ПОБЕДЫ 192"]

for row in reader:
    values = row[0].split(';')
    street = values[0].strip()
    housenum = values[1].strip()
    raw = values[2].strip()
    pump = int(values[2].strip()) if (values[2].strip()) else 0
    pump_exists = True if (pump > 0) else False

    street_pattern = re.compile(".*" + street + ".*", re.IGNORECASE)

    house_number = get_house_number(housenum)
    house_block = get_house_block(housenum)
    hash = street + ' ' + housenum
    if hash in blacklist:
        adr.append("BLACKLIST " + hash + " " + str(pump_exists))
        continue

    h = {}
    if house_block:
        block_pattern = re.compile(house_block, re.IGNORECASE)
        h = houses_collection.find_one(
            {"HouseDisplayAddress": {"$regex": street_pattern}, "full_address.house_number": house_number,
             "full_address.block": {"$regex": block_pattern}})
    else:
        h = houses_collection.find_one(
            {"HouseDisplayAddress": {"$regex": street_pattern}, "full_address.house_number": house_number,
             "$or": [{"full_address.block": {"$exists": False}}, {"full_address.block": ""}]})
    if not h:
        adr.append("ERROR " + hash + " " + str(pump_exists))
        continue
    if pump_exists:
        h['GeneralInfo'] = {"IsPumpExist": True}
        print("+Pump added " + hash)
    else:
        h['GeneralInfo'] = {"IsPumpExist": False}
        print("-Pump is not present " + hash)
    id = h['_id']
    houses_collection.update_one({'_id': id}, {"$set": h}, upsert=False)

print('')

for i in adr:
    print(i)
