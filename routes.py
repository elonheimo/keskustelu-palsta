from crypt import methods
import string
from app import app
from flask import abort, render_template, request, redirect, session, flash
import topics, users, posts
from db import db

@app.route("/", methods = ["GET","POST"])
def index():
    return render_template(
        "index.html",
        topics = topics.get_list(),
        is_admin = users.is_admin()
    )

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    if not users.login(username,password):
        flash('Wrong username or password')
    else: flash('Succesful login') 
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
    password_again = request.form["password2"]
    if request.form.get("admin", False): admin = True
    else: admin = False

    if password != password_again:
        flash("Passwords do not match try again")
        return redirect("/register")
    if len(password)<8:
        flash("Minimum password length 8 chars")
        return redirect("/register")
    if not 1<= len(username) <= 10: 
        flash("Username should be 1-10 characters")
        return redirect("/register")
    letters = string.ascii_letters + "äöåÄÖÅ" + "1234567890"
    for username_char in username:
        if username_char not in letters:
            flash("username should only contain finnish letters")
            return redirect("/register")
    
    if users.register(username, password, admin):
        return redirect("/")
    else:
        flash(f"Username '{username}' is taken. Try another")
        return redirect("/register")    

@app.route("/create_topic", methods=["POST"])
def create_topic():
    topic_title = request.form["topic_title"]
    if topic_title == "": 
        flash("empty topic name")
        return redirect("/admin_panel")
    for title_char in topic_title:
        if title_char not in (string.ascii_letters+string.digits):
            flash("use only ascii letters or numbers in topic name")
            return redirect("/admin_panel")
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
    if session["csrf_token"] != request.form["csrf_token"]: abort(403)

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
    if session["csrf_token"] != request.form["csrf_token"]: abort(403)

    if topics.exists(topic_title) and topics.has_user_access(topic_title):
        if posts.exists(post_id):
            message = request.form.get("message_message")
            posts.send_message(int(post_id), message)
        return redirect(f"/topic/{topic_title}/{post_id}")
    return redirect("/") # fix

@app.route("/topic/<topic_title>/<post_id>/edit_message/<int:message_id>", methods=["POST"])
def edit_message(topic_title, post_id, message_id):
    if session["csrf_token"] != request.form["csrf_token"]: abort(403)

    if not posts.can_user_edit_message(message_id, session.get("user_id")):
        print(f"User {session.get('user_id')} not allowed to edit message")
        return redirect(f"/topic/{topic_title}/{post_id}")
    message = request.form.get("message")
    if posts.edit_message(message, message_id):
        return redirect(f"/topic/{topic_title}/{post_id}")
    return redirect("/")

@app.route("/admin_panel", methods=["GET", "POST"])
def admin_panel():
    if users.is_admin():
        selected_topic_query = request.args.get("selected_topic")
        print(selected_topic_query)
        if request.method == "POST":
            selected_topic = request.form.get("selected_topic")
            print(request.form.getlist("users"))
            [print(k,v) for k,v in request.form.items()]
            print(request.form.items())
            return render_template(
                "/admin_panel.html",
                is_admin = users.is_admin(),
                topics = topics.get_list(),
                user_list = users.users_by_secret_access(selected_topic),
                selected_topic = selected_topic
            )

        if selected_topic_query:
            #print("users")
            #print(users.users_by_secret_access(selected_topic_query))
            return render_template(
                "/admin_panel.html",
                is_admin = users.is_admin(),
                topics = topics.get_list(),
                user_list = users.users_by_secret_access(selected_topic_query),
                selected_topic = selected_topic_query
            )
        return render_template(
            "/admin_panel.html",
            is_admin = users.is_admin(),
            topics = topics.get_list(),
            selected_topic = selected_topic_query
        )
    return("/")
