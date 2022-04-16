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
    #"SELECT * FROM messages WHERE post_id=:post_id"
    sql = """
    SELECT u.id as user_id, m.id AS message_id, u.name, m.message, m.created, m.edited
    FROM messages m JOIN users u ON m.user_id = u.id
    WHERE m.post_id=:post_id
    ORDER BY m.id ASC
    """
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

def edit_message(message_content :str, message_id :int):
    try:
        sql = """
        UPDATE messages
        SET message=:message, edited = CURRENT_TIMESTAMP
        WHERE id=:id
        """
        print("content", message_content, "id", message_id)
        db.session.execute(sql, {
            "message": message_content,
            "id": message_id
        })
        db.session.commit()
    except Exception as e:
        print(e)
        return False
    return True

def can_user_edit_message(message_id :int, user_id):
    try:
        sql = """
        SELECT EXISTS 
        (select 1 from messages 
        where id=:message_id and user_id=:user_id)
        """
        result = db.session.execute(sql, {
            "message_id": message_id,
            "user_id": user_id
        })
        return result.fetchone()[0]
    except Exception as e:
        print(e)
        return False
        
    