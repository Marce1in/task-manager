from flask import Flask, redirect, session
from functools import wraps
import sqlite3

# Check if the user is logged
def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return func(*args, **kwargs)
    return inner

# Create a connection between the database and ensure that the database is closed safetly
def handle_db(func):
    @wraps(func)
    def inner(*args, **kwargs):
        connection = sqlite3.connect("database/task.db")  
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        result = func(*args, cursor=cursor, **kwargs)

        connection.commit()
        cursor.close()
        connection.close()
        return result

    return inner

# Check if the user is the real owner of the task
def task_own(cursor: sqlite3.Cursor, request: Flask.request_class):
    task_user_id = cursor.execute("SELECT user_id FROM tasks WHERE id = ?", (request.get_json()["id"], )).fetchone()
    if task_user_id["user_id"] != session['user_id']:
        return False
    else:
        return True
