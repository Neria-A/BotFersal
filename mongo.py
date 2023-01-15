# import MongoClient
from pymongo import MongoClient
import appSettings as appsec
from ShovarFromMongo import ShovarFromMongo
from Shovar import Shovar
import datetime

amounts = ['30', '40', '50', '100', '200']



# Creating a client
client = MongoClient(appsec.mongo_connection_string)

mydb = client["bot_fersal"]
mycol = mydb["shovarim"]


def insert_to_mongo(code):
    mycol.insert_one(code)

def check_if_exist(message):
    return mycol.find_one({"_id": message})

def find_barcode(amount):
    result = mycol.find_one({"amount": amount, "is_used": False})
    if result == 0:
        return None
    else:
        return result

def update_db(shovar):
    myquery  = mycol.find_one({"_id": shovar.code})
    new_value = {"$set": {"is_used": True, "date_used": datetime.datetime.now()}}
    mycol.update_one(myquery, new_value)

def check_how_much_money():
    amounts_dict = {}
    for amount in amounts:
        amounts_dict[amount] = 0
    for amount in amounts:
        coupons = mycol.find({"amount": amount, "is_used": False})
        for coupon in coupons:
            new_shovar = convert_mongo_to_shovar(coupon)
            amounts_dict[new_shovar.amount] = amounts_dict[new_shovar.amount] + 1
    return amounts_dict

def coupons_sum(amounts):
    sum = 0
    for key, value in amounts.items():
        for _ in range(value):
            sum += float(key)
    return sum



def convert_mongo_to_shovar(barcode):
    shovar = ShovarFromMongo.dict_to_shovar(barcode)
    new_shovar = Shovar(shovar._id, shovar.code, shovar.amount, shovar.expiry_date, shovar.is_used, shovar.date_added, shovar.date_used)
    return new_shovar