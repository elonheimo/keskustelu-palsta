from db import db
import users, topics

def create_post(topic_title :str,post_title :str, message :str):
    topic_id = topics.topic_id(topic_title)
    try:
        sql = """
        INSERT INTO posts (user_id, title, message, topic_id, created) 
        VALUES (:user_id, :post_title, :message, :topic_id, current_timestamp)"""
        db.session.execute(sql, {
            "user_id":users.user_id(),
            "post_title":post_title,
            "message":message,
            "topic_id":topic_id
            })
        db.session.commit()
    except:
        return False
    return True

def get_title(post_id):
    sql = "SELECT title FROM posts WHERE id=:post_id"
    return db.session.execute(sql, {"post_id": post_id}).fetchone()[0]

def exists(id):
    sql = "select exists(select 1 from posts where id=:id)"
    return db.session.execute(sql, {"id": id}).fetchone()[0]

def get_message_list(post_id):
    sql = "SELECT * FROM messages WHERE post_id=:post_id"
    return db.session.execute(sql, {"post_id": post_id}).fetchall()

def send_message(post_id :int,message :str):
    try:
        sql = """
        INSERT INTO messages (user_id, message, created, post_id) 
            VALUES (:user_id, :message, current_timestamp, :post_id )
        """
        db.session.execute(sql, {
                "user_id":users.user_id(),
                "message":message,
                "post_id":post_id,
                })
        db.session.commit()
    except:
        return False
    return True