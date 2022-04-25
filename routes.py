from crypt import methods
from app import app
from flask import render_template, request, redirect, session, flash
import topics, users, posts
from db import db

@app.route("/", methods = ["GET","POST"])
def index():
    return render_template("index.html", topics = topics.get_list())

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    if not users.login(username,password):
        flash('Wrong username or password')
    flash('Succesful login') 
    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/logout")
def logout():
    users.logout()
    flash("Succesfully logged out")
    return redirect("/")

@app.route("/register_user", methods=["POST"])
def register_user():
    username = request.form["username"]
    password = request.form["password"]
    if users.register(username, password):
        return redirect("/")
    else:
        flash(f"Username '{username}' is taken. Try another")
        return redirect("/register")    

@app.route("/create_topic", methods=["POST"])
def create_topic():
    topic_title = request.form["topic_title"]
    secret = request.form.get("secret", False)
    topics.create_topic(topic_title,secret)
    return redirect("/")

@app.route("/topic/<title>")
def topic_page(title):
    if topics.exists(title) and topics.has_user_access(title):
        posts = topics.get_posts(title)
        return render_template("/topic.html", title = title, posts = posts)
    flash( f"No access to topic '{title}' or no such topic" )
    return redirect("/")

@app.route("/topic/<title>/send_post", methods=["POST"])
def send_post(title):
    if topics.exists(title) and topics.has_user_access(title):
        topic_title = title
        post_title = request.form.get("post_title")
        message = request.form.get("post_message")
        posts.create_post(topic_title,post_title,message)
    return redirect(f"/topic/{title}")

@app.route("/topic/<topic_title>/<int:post_id>")
def post_page(topic_title, post_id):
    if topics.exists(topic_title) and topics.has_user_access(topic_title):
        messages = posts.get_message_list(post_id)
        post_title = posts.get_title(post_id)
        return render_template("/post.html",
            messages=messages,
            post_title = post_title,
            post_id = post_id,
            topic_title = topic_title)
    error_message = f"""No access to topic '{topic_title}' or no such topic \n
                        or access to post '{post_id}' or no such post"""
    flash(error_message)
    return redirect("/")

@app.route("/topic/<topic_title>/<post_id>/send_message", methods=["POST"])
def send_message(topic_title, post_id):
    if topics.exists(topic_title) and topics.has_user_access(topic_title):
        if posts.exists(post_id):
            message = request.form.get("message_message")
            posts.send_message(int(post_id), message)
        return redirect(f"/topic/{topic_title}/{post_id}")
    return redirect("/") # fix

@app.route("/topic/<topic_title>/<post_id>/edit_message/<int:message_id>", methods=["POST"])
def edit_message(topic_title, post_id, message_id):
    if not posts.can_user_edit_message(message_id, session.get("user_id")):
        print(f"User {session.get('user_id')} not allowed to edit message")
        return redirect(f"/topic/{topic_title}/{post_id}")
    message = request.form.get("message")
    if posts.edit_message(message, message_id):
        return redirect(f"/topic/{topic_title}/{post_id}")
    return redirect("/")

@app.route("/admin_panel")
def admin_panel():
    return render_template("/admin_panel.html")

