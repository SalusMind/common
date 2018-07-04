import datetime
import uuid

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


db = config.db


def login(email, password):
    try:
        user = db.users.find_one({'email': email})
        if user and config.g.bcrypt.check_password_hash(user['password'], password):
            if user['isConfirmed']:
                if not user['isSuspended']:
                    user['_id'] = str(user['_id'])
                    return config.Success().custom(user)
                else:
                    return config.Errors().user_suspended()
            else:
                return config.Errors().confirm_email(email)
        else:
            return config.Errors().credentials_invalid()
    except:
        return config.Errors().missing_parameters()


def signup(fname, lname, email, password):
    print(fname, lname, email, password)
    try:
        exist = db.users.find_one({'email': email})
        if not exist:
            confirm_key = str(uuid.uuid4().hex)
            user_id = db.users.insert_one({
                'fname': fname,
                'lname': lname,
                'email': email,
                'password': config.g.bcrypt.generate_password_hash(password),
                'isConfirmed': False,
                'isSuspended': False,
                'confirmKey': confirm_key
            })
            config.send_confirmation_email(fname, email, confirm_key)
            return config.Errors().confirm_email(email)
        else:
            return config.Errors().user_exists(email)
    except:
        return config.Errors().missing_parameters()



def confirm(email, confirm_key):
    try:     
        updated = db.users.update_one({'email': email, 'confirmKey': confirm_key}, {'$set': {'isConfirmed': True}}, upsert=False)
        if updated.matched_count > 0:
            return config.Success().confirmation()
        else:
            return config.Error().confirmation()
    except:
        return config.Errors().missing_parameters()


def forgot(email):
    pass


def connect_account(email, media, account):
    try:
        updated = db.users.update_one({'email': email}, {'$set': {media: account}}, upsert=False)
        if updated.matched_count > 0:
            return config.Success().custom(media+" has been added successfully")
        else:
            return config.Error().custom("Failed to add "+media+" account")
    except:
        return config.Errors().custom("Service unavailable")

