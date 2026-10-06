import json

from werkzeug.security import generate_password_hash, check_password_hash

USERS_FILE = "web/users.json"

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password, password_hash):
    return check_password_hash(password_hash, password)

def load_users():
    with open(USERS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)
def authenticate_user(username, password):
    users = load_users()

    for user in users:
        if user["username"] == username:
            if verify_password(password, user["password_hash"]):
                return user

            return None

    return None