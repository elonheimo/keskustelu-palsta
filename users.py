from os import access
import secrets
from db import db
from werkzeug.security import check_password_hash, generate_password_hash
from flask import session
import topics
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
  
def register(username:str, password:str, admin: bool):
    #chech if username already exists
    sql = f"SELECT exists (select 1 FROM users where name = :name);"
    result = db.session.execute(sql, {"name":username})
    if result.fetchone()[0] == False:
        hash_value = generate_password_hash(password)
        sql = "INSERT INTO users (name, password, time, admin) VALUES (:name, :password, current_timestamp, :admin)"
        db.session.execute(
            sql,
            {"name":username, "password":hash_value, "admin":admin}
        )
        db.session.commit()
        return login(username,password)
    return False

def user_id():
    return session.get("user_id",0)

def users_by_secret_access(topic_name :str):
    """
    Returns a table with user name, id and bool if has access to topic
    |name|id|has_access
    """
    topic_id = topics.topic_id(topic_name)
    sql = """
    select name, id, 
        exists(select 1 FROM secret_access 
        WHERE topic_id =:topic_id and user_id = u.id )
        as has_access
    FROM users u;
    """
    return db.session.execute(sql, {"topic_id": topic_id}).fetchall()
    
def grant_users_secret_access(topic_name :str, user_ids: list):
    sql = """
    INSERT INTO secret_access 
    (topic_id, user_id) VALUES (:topic_id, :user_id);
    """
    topic_id= topics.topic_id(topic_name)
    for user_id in user_ids:
        db.session.execute(sql,
            {"topic_id":topic_id,
            "user_id":user_id}    
        )
    db.session.commit()

def deny_users_secret_access(topic_name :str, user_ids: list):
    sql = """
    DELETE FROM secret_access 
    WHERE topic_id=:topic_id AND user_id=:user_id
    """
    topic_id= topics.topic_id(topic_name)
    for user_id in user_ids:
        db.session.execute(sql,
            {"topic_id":topic_id,
            "user_id":user_id}    
        )
    db.session.commit()


def is_admin():
    sql = f"""
    select exists(select 1 from users where id =:user_id and admin=True)
    """
    return db.session.execute(sql,
        {"user_id":user_id()}    
    ).fetchone()[0]
    return db.session.fetchone()[0]
    if session.get("username") == "admin":
        return True
    return False
