from flask import redirect, session, Request
from functools import wraps
import mysql.connector
from mysql.connector.cursor import MySQLCursorDict
import os

# Check if the user is logged
def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return func(*args, **kwargs)
    return inner

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


# Create a connection between the database and ensure that the database is closed safetly
def handle_db(func):
    @wraps(func)
    def inner(*args, **kwargs):
        connection = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWD"],
            database=os.environ["DB_DATABASE"],
            charset="utf8mb4",
            collation="utf8mb4_general_ci",
        )

        cursor = connection.cursor(dictionary=True)

        result = func(*args, cursor=cursor, **kwargs)

        connection.commit()
        cursor.close()
        connection.close()
        return result

    return inner

# Check if the user is the real owner of the task
def task_own(cursor: MySQLCursorDict, request: Request):
    cursor.execute("SELECT user_id FROM tasks WHERE id = %s", (request.get_json()["id"], ))
    task_user_id = cursor.fetchone()

    if task_user_id is None:
        return False
    elif task_user_id["user_id"] != session['user_id']:
        return False
    else:
        return True
