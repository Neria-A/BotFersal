# import MongoClient
from pymongo import MongoClient
import appSettings as appsec

# Creating a client
client = MongoClient(appsec.mongo_connection_string)

mydb = client["bot_fersal"]
mycol = mydb["shovarim"]


def insert_to_mongo(code):
    mycol.insert_one(code)