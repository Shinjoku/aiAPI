"""This module is to configure app to connect with database."""
from pymongo import MongoClient


DATABASE = MongoClient()['DEV'] # DB_NAME
DEBUG = True
client = MongoClient('localhost')
