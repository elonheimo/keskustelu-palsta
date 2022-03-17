from flask import flash
from db import db
import users

def create_topic(title:str, secret :bool):
    #add checks if topic already exists
    if users.is_admin():
        print(title)
        sql = "INSERT INTO topics (title, time, secret) VALUES (:title, current_timestamp, :secret)"
        db.session.execute(sql, {"title": title, "secret": secret})
        db.session.commit()
        return True
    return False

def get_list():
    if users.user_id() == 0: #user not logged in
        sql = "SELECT * FROM TOPICS WHERE secret = FALSE"
    elif users.is_admin():
        sql = "SELECT * FROM TOPICS"
    else: #user logged in
        sql = """ 
            SELECT * FROM topics WHERE secret = FALSE or id =
            (SELECT topic_id FROM secret_access where user_id=:user_id)
            """
        return db.session.execute(sql, {"user_id":users.user_id()}).fetchall()
    return db.session.execute(sql).fetchall()

def get_posts(title: str):
    sql = "select id from topics where title=:title"
    topic_id = db.session.execute(sql, {"title": title}).fetchone()[0]
    sql = "select * from posts where topic_id=:topic_id"
    return db.session.execute(sql, {"topic_id": topic_id}).fetchall()

def exists(title :str):
    sql = "select exists(select 1 from topics where title=:title)"
    return db.session.execute(sql, {"title": title}).fetchone()[0]

def is_secret(title :str):
    sql = "select secret from topics where title=:title"
    return db.session.execute(sql, {"title": title}).fetchone()[0]

def topic_id(title: str):
    if not exists(title):
        return False
    sql = "select id from topics where title=:title"
    id = db.session.execute(sql, {"title": title}).fetchone()[0]
    return id

def has_user_access(title :str):
    if not exists(title): 
        return False
    else:
        if users.is_admin():
            return True
        if is_secret(title):
            sql = "SELECT exists (SELECT 1 FROM secret_access where user_id=:user_id)"
            return db.session.execute(sql, {"user_id":users.user_id()}).fetchone()
        return True

#ADD remove_topic, that migrates all its posts to a general topic