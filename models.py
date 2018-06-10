import datetime
import uuid

from pymongo import MongoClient
from common import config


class Organization:
    def __init__(self, name, org_type, description, address, phone):
        self.name = name
        self.org_type = org_type
        self.description = description
        self.address = address
        self.phone = phone

    def get_by_id(self, id):
        return

    def insert(self):
        return


client = MongoClient()
db = client[config.APP_NAME]
