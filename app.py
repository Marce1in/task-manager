from flask import Flask, render_template, request, session, redirect, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, handle_db, task_own
from datetime import datetime
import sqlite3
import os

# If the database is still not created or empty we create her
def init_db(): 
    connection = sqlite3.connect("database/task.db")
    cursor = connection.cursor()

    with open("schema.sql") as schema:
        cursor.executescript(schema.read())

    cursor.close()
    connection.close()

app = Flask(__name__)

with app.app_context():
    init_db()

# try to get the secret key, if not set, warn and generate a random hash
try:
    app.secret_key = os.environ["SKEY"]
except:
    print('\033[91m' + "SECRET KEY IS NOT SET, THIS IS UNSAFE FOR PRODUCTION" + '\033[0m')

    import secrets
    app.secret_key = secrets.token_hex()


# Log the user in
@app.route("/login", methods=["GET", "POST"])
@handle_db
def login(cursor: sqlite3.Cursor):

    session.clear()
    error = None

    if request.method == "POST":

        # Check if user input is valid
        if not request.form.get("username"):
            error="Blank names are not allowed!"

        elif not request.form.get("password"):
            error="Blank passwords are not allowed!"

        user = cursor.execute("SELECT * FROM users WHERE name = ?",
                          (str(request.form.get('name')), ) ).fetchone()
        if not user:
            error="Invalid username and/or password"
            return render_template('login.html', error=error)

        if not check_password_hash(user["hash"], str(request.form.get("password"))):
            error="Invalid username and/or password"
            return render_template('login.html', error=error)

        # Log the user in
        session["user_id"] = user["id"]

        return redirect("/")

    return render_template('login.html', error=error)


# Register a new user
@app.route("/register", methods=["GET", "POST"])
@handle_db
def register(cursor: sqlite3.Cursor):

    error = None

    if request.method == "POST":

        # Check if user input is valid
        username = str(request.form.get('name'))
        if username == "":
            error = "Blank names are not allowed!"
            return render_template("register.html", error=error)

        elif len(username) > 20:
            error = "Name longer than 20 characters are not allowed!"
            return render_template("register.html", error=error)

        elif cursor.execute("SELECT name FROM users WHERE name = ?",
                        (username,)).fetchall() != []:
            error = "Sorry, this username is already in use :("
            return render_template("register.html", error=error)


        password = str(request.form.get('password1'))
        if password == "":
            error = "Blank passwords are not allowed!"
            return render_template("register.html", error=error)

        elif len(password) > 30:
            error = "Password longer than 30 characters are not allowed!"
            return render_template("register.html", error=error)

        elif password != request.form.get('password2'):
            error = "Your passwords don't match!"
            return render_template("register.html", error=error)

        # Hash the password
        hash = generate_password_hash(password)

        # Create a new user in the database
        cursor.execute("INSERT INTO users (name,hash) VALUES (?,?)",
                   (username, hash))

        return redirect("/login")

    return render_template("register.html", error=error)

# Get the currently day of the week
@app.route("/")
@login_required
def week():
   dt = datetime.now()
   day = dt.isoweekday()
   return redirect(f"/{day}")

# Load all the tasks that are linked with the choosed day
@app.route("/<id>")
@login_required
@handle_db
def home(id, cursor: sqlite3.Cursor):

    # Check if the id is valid
    try:
        id = int(id)
    except ValueError:
        id = 1
    if id < 1 or id > 7:
        id = 1

    # Get the user tasks
    tasks = cursor.execute("SELECT * FROM tasks WHERE user_id = ? AND week = ? ORDER BY date ASC", (session["user_id"], id)).fetchall()
    return render_template('index.html', tasks=tasks, day=id)

# Create a new task in the database
@app.route("/create", methods=["POST"])
@login_required
@handle_db
def create(cursor: sqlite3.Cursor):

    # Get user data
    data = request.get_json()
    name, date, day, id = data['name'], data['date'], data['day'], session['user_id']

    # Check if user input is valid
    if len(name) > 20:
        name = name[:20]
    elif name == "":
        name = "Task"

    if date != "":
        if date[2] != ":":
            date = ""
        elif not date[:2].isdigit() or not date[3:].isdigit():
            date = ""

    try:
        day = int(day)
    except ValueError:
        day = 1
    if day < 1 or day > 7:
        day = 1

    # Create a new task on the database
    cursor.execute("INSERT INTO tasks (name, date, week, user_id) VALUES (?,?,?,?)",
               (name, date, day, id))

    # Get the ID of this new task
    task_id = cursor.execute("SELECT id FROM tasks WHERE user_id = ? ORDER BY id DESC LIMIT 1", (id, )).fetchone()

    # Send back the id for the HTML
    return jsonify({'task_id': task_id["id"]}), 200


# Edit the task in the database
@app.route("/edit", methods=["PUT"])
@login_required
@handle_db
def edit(cursor: sqlite3.Cursor):

    if task_own(cursor, request) == False:
        return jsonify({'status': 'failure'}), 401

    # Get user data
    data = request.get_json()
    name, date, id = data['name'], data['date'], data['id']


    # Check if user input is valid
    if len(name) > 20:
        name = name[:20]

    if date != "":
        if date[2] != ":":
            date = ""
        elif not date[:2].isdigit() or not date[3:].isdigit():
            date = ""

    # Edit the task name and the date if necessary
    if date != "":
        cursor.execute("UPDATE tasks SET date = ? WHERE id= ?", (date, id))
    if name != "":
        cursor.execute("UPDATE tasks SET name = ? WHERE id= ?", (name, id))

    return jsonify({'status': 'success'}), 200

# Conclude the task in the database
@app.route("/conclude", methods=["PUT"])
@login_required
@handle_db
def conclude(cursor: sqlite3.Cursor):

    if task_own(cursor, request) == False:
        return jsonify({'status': 'failure'}), 401

    # Get the task id from the user
    id = str(request.get_json()['id'])

    # Get the state of the task
    task_state = cursor.execute("SELECT state FROM tasks WHERE id = ?", (id, )).fetchall()

    # If the task is concluded in the database, then undo, else conclude
    if task_state[0]["state"] == 1:
        cursor.execute("UPDATE tasks SET state = ? WHERE id = ?", (0, id))
    else:
        cursor.execute("UPDATE tasks SET state = ? WHERE id = ?", (1, id))

    return jsonify({'status': 'success'}), 200

# Delete the task in the database
@app.route("/delete", methods=["DELETE"])
@login_required
@handle_db
def delete(cursor: sqlite3.Cursor):

    if task_own(cursor, request) == False:
        return jsonify({'status': 'failure'}), 401

    # Get the task id from the user
    id = str(request.get_json()['id'])

    # Delete the task from the database
    cursor.execute("DELETE FROM tasks WHERE id = ?", (id, ))

    return jsonify({'status': 'success'}), 200

# Delete ALL the tasks of a day in the database
@app.route("/deleteall", methods=["DELETE"])
@login_required
@handle_db
def deleteall(cursor: sqlite3.Cursor):

    # Get the day of the week from the user
    day = str(request.get_json()['day'])

    # Get delete all the tasks of this day
    cursor.execute("DELETE FROM tasks WHERE week = ? AND user_id = ?", (day, session['user_id']))

    return jsonify({'status': 'success'}), 200
