# import MongoClient
from pymongo import MongoClient
import appSettings as appsec

# Creating a client
client = MongoClient(appsec.mongo_connection_string)

mydb = client["bot_fersal"]
mycol = mydb["shovarim"]


def insert_to_mongo(code):
    mycol.insert_one(code)

def check_if_exist(message):
    return False if mycol.mycollection.find({'_idS': {"$in": message}}) == 0 else True

def find_barcode(amount):
    result = mycol.find_one({"amount": amount, "is_used": False})
    if result == 0:
        return None
    else:
        return result