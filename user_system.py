import json, os

USERS_FILE = "data/users.json"

def load_users():
    if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
        # Ha nem létezik vagy üres, hozzunk létre egy üres dict-et
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE,"w") as f:
        json.dump(users,f,indent=4)

def register(username,password):
    users = load_users()
    if username in users:
        return False,"Username already exists!"
    users[username] = {"password":password,"coins":1000,"squad":[]}
    save_users(users)
    return True,"Registration successful!"

def login(username,password):
    users = load_users()
    if username in users and users[username]["password"]==password:
        return True, users[username]
    return False, None

def add_coins(username,amount):
    users = load_users()
    if username in users:
        users[username]["coins"] += amount
        save_users(users)

def spend_coins(username,amount):
    users = load_users()
    if username in users and users[username]["coins"] >= amount:
        users[username]["coins"] -= amount
        save_users(users)
        return True
    return False
