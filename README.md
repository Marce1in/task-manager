# Task Manager
> Task Manager is a website that helps users organize their lives using tasks!

![image](https://github.com/Marce1in/task-manager/assets/98642728/39849ad7-7dc4-4421-9399-86ab2d953ed8)

## Runnning:

Ensure that you have *python*, *git* and *docker* installed.

#### running pulling the image from docker hub
- run in the terminal <br>
`docker run -dp 127.0.0.1:8080:8080 -e SKEY="*your secret key*" -v task.db:/app/database marce1in/flask-task-manager`

Now acess **127.0.0.1:8080** in your browser, also don't forget to change your secret key ;)
#### running building the image locally
- Clone this repository <br>
`git clone git@github.com:Marce1in/task-manager.git`

- cd into the directory <br>
`cd task-manager`

- Build your image <br>
`docker build -t task-manager .`

- run your container <br>
`docker run -d -p 127.0.0.1:8080:8080 -e SKEY="*your secret key*" -v task.db:/app/database task-manager`

Now you can acess **127.0.0.1:8080** in your browser.
#### running locally
- Clone this repository <br>
`git clone git@github.com:Marce1in/task-manager.git`

- cd into the directory <br>
`cd task-manage`

- ###### On Unix Systems (Linux, Mac, BSD)
  - Create a virtual environment <br>
  `python3 -m venv .venv`

  - Activate the environment <br>
  `source ./.venv/bin/activate`

- ###### On Windows
  - Create a virtual environment <br>
  `python -m venv .venv`

  - Activate the environment <br>
  `.\.venv\Scripts\activate`

- Install the dependencies <br>
`pip install -r requirements.txt`

- running for development
  - `flask run`
- running for production
  - `waitress-serve --host *your host* --port *your port* app:app`

# Especification
## The back-end:
The back-end is created using Flask and SQLite3 as the database.<br>

### The database
Before we delve into anything else, it's crucial to understand how the database operates.

The database is divided into two tables: the **Users** and the **Tasks**:

#### Users:
The **Users** table is where each user's login information is stored. Each row contains:

- **id:** Unique identifier for each user.
- **name:** The name of the user
- **hash:** The hashed password of the user.

#### Tasks:
The **Tasks** table is where users's tasks are stored. Each row contains:

- **id:** Unique identifier to that task.
- **user_id:** The id of the user that owns that task.
- **name:** The name of the task.
- **date:** The expiration time of that task.
- **week:** The day of the week that this task belongs.
- **state:** The state of this task (if is concluded or not).

### Helpers
Helper functions are implemented to prevent code repetition:

- **task_own():** Checks if the user is rightful owner of a specific task.
- **@login_required:** Verifies if the user is logged in before accessing a route.
- **@handle_db:** Create a connection between the database and ensure that the database is closed safetly

### The Flask
Inside **app.py**, you'll find the back-end routes, which consist of functions that:

- Render and redirect the user to other pages.
- Pull and push information within the database.

#### register()
We take user input, validate it, and if it's valid, save the data in the database. Then, we redirect the user to the **login** route.

#### login()
We process the user input and, if it exists in the "users" database, log the user in using Flask's "session" extension. Afterward, we redirect the user to the **week** route.

#### week()
We determine the current day of the week for the user and send this day as an "id" to the **home** route.

#### home(id)
Taking the received "id" from the route, we verify if it's an actual day of the week. If not, we default it to Monday. Then, we select all tasks that the user has for that day and load them into the HTML.

#### create()
This function creates a new task in the database:

- **First:** Retrieve user data.
- **Second:** Check the task name; if it's longer than 20 characters, it gets truncated to 20 characters, and if the user didn't provide a name, it defaults to "Task".
- **Third:** Validate the expiration time; if it's not valid, it's set to an empty string.
- **Fourth:** Verify the day of the week; if it's not valid, it defaults to Monday.
- **Fifth:** Create a new row in the Tasks table using this data.
- **Sixth:** Send the ID of the newly created task back to the front-end.

#### edit()
This function allows users to edit the name or expiration time of a task in the database:

- **First:** Obatin user data.
- **Second:** Check if the task name is shorter than 20 characters; if it's longer, it's capped at 20 characters.
- **Third:** Validate the expiration time; if it's not valid, it's set to an empty string.
- **Fourth:** Update the task with the new data while ignoring any variable set to an empty string.

#### conclude()
Users can use this function to mark a task as concluded or incomplete in the database:

- **First:** Get task ID.
- **Second:** Retrieve the current task state in the database.
- **Third:** If the state in the database is 1, update it to 0; otherwise, update the state to 1.

#### delete()
This function allows users to delete a task from the database:

- **First:** Get task ID.
- **Second:** Delete the task from the database.

#### deleteall()
This function enables users to delete all tasks for a specific day of the week:

- **First:** Retrieve the day of the week the user is in.
- **Second:** Delete all tasks associated with that day.

## The Front-End
The front-end is built using only HTML, CSS, JavaScript, and a little AJAX, utilizing the JavaScript Fetch API.

### The HTML
#### account-Layout.html
This serves as the Register and Login layouts. This page can receive an **error** message from the back-end and display it on the screen.

+ **register.html**<br>
This is the Registration page, requiring a username, password, and password confirmation to create a new user. If any of this information is missing, an error message is displayed.
+ **login.html**<br>
This is the Login page, which asks for a username and password. If any of this information is incorrect or invalid, an error is displayed.

#### index.html
This is the main page, divided into multiple sections:

+ **week.html**<br>
Here, users can select the day of the week they want to create tasks. It features seven buttons, each representing a day of the week. Clicking a button redirects the user to the respective day's page. If the screen width is less than 900px, this section remains hidden.
+ **tasks.html**<br>
This is where users' created tasks are displayed. Each task includes a name, a hidden ID, a checkbox to mark completion status, a button that opens the **edit_task** section, and an optional expiration time that orders the tasks. If the user has no tasks, a **Tutorial** message is shown.
+ **config.html**<br>
This is where most site options are found. Here, users can open the **new_task** section, log out, or delete all tasks related to the current day of the week. If the screen width is less than 900px, a hamburger button appears, revealing the **week** section when clicked.
+ **new_task.html**<br>
This is where users input data to create a new task. They can specify the name and the expiration time, also there's a hidden input containing the current day of the week.
+ **edit_task.html**<br>
This is where users can edit an already created task. They can change the name, expiration time, or delete the task if desired.

### The javascript
JavaScript is used to edit, delete, conclude, and create tasks in the HTML, allowing users to see changes without needing to reload the page. Data is sent to the back-end using the JavaScript Fetch API.

#### add_class()
This helper function toggles classes in the HTML, primarily used to hide and show elements.

#### create_task()
This function extracts user input data and injects a new task element into the HTML. If this is the first task created, the function also removes the **Tutorial** message from the HTML.

#### db_create_task()
It sends the name, expiration time, and day of the week to the /create route using AJAX. The route returns the task ID inside the database, which is then injected into the HTML task element.

#### delete_task()
This function removes a task element from the HTML.

#### db_delete_task()
It sends the task ID to the **/delete** route using AJAX.
#### edit_task()
This function updates the task element with the new user-inputted data.

#### db_edit_task()
It sends the name, expiration date, and task ID to the **/edit** route using AJAX.

#### conclude_task()
This function toggles the task color to green to indicate completion status.

#### db_conclude_task()
It sends the task ID to the **/conclude** route using AJAX.

#### delete_all()
This function deletes all tasks in the HTML and restores the **Tutorial** message.

#### db_delete_all()
It sends the day of the week to the **/deleteall** route using AJAX.

