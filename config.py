"""This module is to configure app to connect with database."""
from pymongo import MongoClient
import os

authenticated_user = ""

DATABASE = MongoClient()['DEV'] # DB_NAME
DEBUG = True

# client = MongoClient('localhost')
user = str(os.environ.get('mongoUser', 'aiapiUser'))
pwd = str(os.environ.get('mongoPwd', 'aiapiPassword'))
print(user, pwd)
client = MongoClient(
    "mongodb+srv://" +
    user + ":" + pwd + 
    "@cluster0-qqfj4.mongodb.net/")