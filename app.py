from flask import Flask, render_template, request, session, redirect, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, handle_db, task_own
from datetime import datetime
import mysql.connector
from mysql.connector.cursor import MySQLCursorDict
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

# If the database is still not created or empty we create her
def init_db():
    connection = mysql.connector.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWD"],
        database=os.environ["DB_DATABASE"],
        charset="utf8mb4",
        collation="utf8mb4_general_ci",
    )
    cursor = connection.cursor()

    with open("database/schema.sql") as schema:
        cursor.execute(schema.read(), multi=True)

    cursor.close()
    connection.close()

app = Flask(__name__)

with app.app_context():
    init_db()

# Get secret Key
app.secret_key = os.environ["SECRET_KEY"]

# Log the user in
@app.route("/login", methods=["GET", "POST"])
@handle_db
def login(cursor):

    session.clear()
    error = None

    if request.method == "POST":

        # Check if user input is valid
        if not request.form.get("name"):
            error="Blank names are not allowed!"
            return render_template('login.html', error=error)

        elif not request.form.get("password"):
            error="Blank passwords are not allowed!"
            return render_template('login.html', error=error)

        cursor.execute("SELECT * FROM users WHERE name = %s", (str(request.form.get('name')),))
        user = cursor.fetchone()

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
def register(cursor: MySQLCursorDict):

    error = None

    if request.method == "POST":

        # Check if user input is valid
        username = str(request.form.get('name'))

        cursor.execute("SELECT name FROM users WHERE name = %s", (username,))

        if username == "":
            error = "Blank names are not allowed!"
            return render_template("register.html", error=error)

        elif len(username) > 20:
            error = "Name longer than 20 characters are not allowed!"
            return render_template("register.html", error=error)

        elif cursor.fetchall() != []:
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
        cursor.execute("INSERT INTO users (name,hash) VALUES (%s,%s)",
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
def home(id, cursor: MySQLCursorDict):

    # Check if the id is valid
    try:
        id = int(id)
    except ValueError:
        id = 1
    if id < 1 or id > 7:
        id = 1

    # Get the user tasks
    cursor.execute("SELECT * FROM tasks WHERE user_id = %s AND week = %s ORDER BY date ASC", (session["user_id"], id))
    tasks = cursor.fetchall()
    return render_template('index.html', tasks=tasks, day=id)

# Create a new task in the database
@app.route("/create", methods=["POST"])
@login_required
@handle_db
def create(cursor: MySQLCursorDict):

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
    cursor.execute("INSERT INTO tasks (name, date, week, user_id) VALUES (%s,%s,%s,%s)",
               (name, date, day, id))

    # Get the ID of this new task
    cursor.execute("SELECT id FROM tasks WHERE user_id = %s ORDER BY id DESC LIMIT 1", (id,))
    task_id = cursor.fetchone()

    # Check if task_id exists
    if task_id is None:
        return jsonify({'status': 'failure'}), 404

    # Send back the id for the HTML
    return jsonify({'task_id': task_id["id"]}), 200


# Edit the task in the database
@app.route("/edit", methods=["PUT"])
@login_required
@handle_db
def edit(cursor: MySQLCursorDict):

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
        cursor.execute("UPDATE tasks SET date = %s WHERE id= %s", (date, id))
    if name != "":
        cursor.execute("UPDATE tasks SET name = %s WHERE id= %s", (name, id))

    return jsonify({'status': 'success'}), 200

# Conclude the task in the database
@app.route("/conclude", methods=["PUT"])
@login_required
@handle_db
def conclude(cursor: MySQLCursorDict):

    if task_own(cursor, request) == False:
        return jsonify({'status': 'failure'}), 401

    # Get the task id from the user
    id = str(request.get_json()['id'])

    # Get the state of the task
    cursor.execute("SELECT state FROM tasks WHERE id = %s", (id, ))
    task_state = cursor.fetchone()

    # Check if task_state exists
    if task_state is None:
        return jsonify({'status': 'failure'}), 404

    # If the task is concluded in the database, then undo, else conclude
    if task_state["state"] == 1:
        cursor.execute("UPDATE tasks SET state = %s WHERE id = %s", (0, id))
    else:
        cursor.execute("UPDATE tasks SET state = %s WHERE id = %s", (1, id))

    return jsonify({'status': 'success'}), 200

# Delete the task in the database
@app.route("/delete", methods=["DELETE"])
@login_required
@handle_db
def delete(cursor: MySQLCursorDict):

    if task_own(cursor, request) == False:
        return jsonify({'status': 'failure'}), 401

    # Get the task id from the user
    id = str(request.get_json()['id'])

    # Delete the task from the database
    cursor.execute("DELETE FROM tasks WHERE id = %s", (id, ))

    return jsonify({'status': 'success'}), 200

# Delete ALL the tasks of a day in the database
@app.route("/deleteall", methods=["DELETE"])
@login_required
@handle_db
def deleteall(cursor: MySQLCursorDict):

    # Get the day of the week from the user
    day = str(request.get_json()['day'])

    # Get delete all the tasks of this day
    cursor.execute("DELETE FROM tasks WHERE week = %s AND user_id = %s", (day, session['user_id']))

    return jsonify({'status': 'success'}), 200
