from db import users_collection

def create_user(user):
    users_collection.insert_one(user)

def get_user(email):
    return users_collection.find_one({"email": email})