let task_element;

//toggle a class
function add_class(element, class_name){
    element.classList.toggle(class_name)
}


//create a new task on the html and remove the tutorial
function create_task(element){
    
    let name = element[1].value;
    let date = element[3].value;
    let day = element[5].value;

    element[1].value = "";
    element[3].value = "";

    if (name === ""){
        name = "Task"
    }
    
    const task =
    '<div>' +
    '<input autocomplete="off" type="checkbox" class="checkmark" onclick="conclude_task(this.parentElement, \'success\');">' +
    '<span class="task-name">' + name + '</span>' +
    '<span class="task-date">' + date + '</span>' +
    '<input class="task-id" type="hidden" value="">' +
    '<button class="edit" onclick="add_class(document.getElementById(\'edit-task\'), \'open\'); task_element = this.parentElement">⚙</button>' +
    '</div>';
    
    const tasks_element = document.getElementById('tasks');

    if (document.getElementById('tutorial') != null){
        tasks_element.innerHTML = "";
    }
    
    tasks_element.innerHTML += task;
    
    db_create_task(name, date, day);
}

//create the task in the database
function db_create_task(name_value, date_value, day_value){
    const values = {
        name: name_value,
        date: date_value,
        day: day_value,
    }

    fetch('/create', {
        method: 'POST',
        headers:{
            'Content-type':'application/json',
        },
        body: JSON.stringify(values)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        task_id = data.task_id
        elements = document.getElementsByClassName("task-id")
        
        elements[elements.length - 1].value = task_id
    })
}



//delete the task on the html
function delete_task(element){

    const id = task_element.children[3].value;
    
    db_delete_task(id);

    element.remove();
}

//delete the task in the database
function db_delete_task(task_id){
    const value = {
        id: task_id
    }

    fetch('/delete', {
        method: 'DELETE',
        headers:{
            'Content-type':'application/json',
        },
        body: JSON.stringify(value)
    })
}



//delete all the tasks in the html and restore the tutorial message
function delete_all(){
    document.getElementById('tasks').innerHTML = 
    "<span id='tutorial'>Don't have any tasks? <br> Create one in the 'New Task' button!<span>";

    day = document.getElementById('day').value;

    db_delete_all(day)
}

//delete all tasks of the day in the database
function db_delete_all(day_value){
    const value = {
        day: day_value
    }

    fetch('/deleteall', {
        method: 'DELETE',
        headers:{
            'Content-type':'application/json',
        },
        body: JSON.stringify(value)
    })
}



//edit the task on the html
function edit_task(values, element){
    let name = values[1].value;
    let date = values[3].value;
    let id = task_element.children[3].value;

    values[1].value = "";
    values[3].value = "";

    db_edit_task(name, date, id)

    if (name != ""){
        element.children[1].innerHTML = name
    }
    if (date != ""){
        element.children[2].innerHTML = date
    }
}

//edit the task in the database
function db_edit_task(name_value, date_value, id_value){
    const values = {
        name: name_value,
        date: date_value,
        id: id_value,
    }

    fetch('/edit', {
        method: 'PUT',
        headers:{
            'Content-type':'application/json',
        },
        body: JSON.stringify(values)
    })
}



//conclude the task on the html
function conclude_task(element, class_name){
    const id = element.children[3].value

    db_conclude_task(id)

    element.classList.toggle(class_name)
}

//conclude the task in the database
function db_conclude_task(id_value){
    const value = {
        id: id_value
    }

    fetch('/conclude', {
        method: 'PUT',
        headers:{
            'Content-type':'application/json'
        },
        body: JSON.stringify(value)
    })
}