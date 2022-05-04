import secrets
from db import db
from werkzeug.security import check_password_hash, generate_password_hash
from flask import session

"""
True = success
False = no success
"""
def login(username:str, password:str):
    sql = f"select password, id FROM users where name = :name;"
    result = db.session.execute(sql, {"name":username})
    user = result.fetchone() #[0] password [1] id 
    if not user:
        return False #wrong username
    elif check_password_hash(user[0],password):
        session["messages"] = None
        session["username"] = username
        session["user_id"] = user[1]
        session["csrf_token"] = secrets.token_hex(16)
        return True  #succesfull login
    else:
        return False #wrong password

def logout():
    if session.get("user_id"): del session["user_id"]
    if session.get("username"): del session["username"]
  
def register(username:str, password:str):
    #chech if username already exists
    sql = f"SELECT exists (select 1 FROM users where name = :name);"
    result = db.session.execute(sql, {"name":username})
    if result.fetchone()[0] == False:
        hash_value = generate_password_hash(password)
        sql = "INSERT INTO users (name, password, time) VALUES (:name, :password, current_timestamp)"
        db.session.execute(sql, {"name":username, "password":hash_value})
        db.session.commit()
        return login(username,password)
    return False

def is_admin():
    if session.get("username") == "admin":
        return True
    return False

def user_id():
    return session.get("user_id",0)