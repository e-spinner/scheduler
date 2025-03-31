
document.addEventListener("DOMContentLoaded", () => {
    taskView(tyear,tmonth,tday);

    document.getElementById('event-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const eventId = e.target.dataset.eventId;
        const url = eventId ? `/update_event/${eventId}` : '/add_event';
    
        fetch(url, {
            method: 'POST',
            body: JSON.stringify(Object.fromEntries(formData)),
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message || 'Event saved!');
            location.reload();
        })
        .catch(err => console.error('Error:', err));
    });
});

function optimize() {
    fetch('/optimize')
        .then(response => response.json())
        .then(data => {
            console.log(data.message || 'Schedule optimized successfully');
            location.reload();
        })
}

function taskView(y, m, day) {
    fetch(`/events_on_day?year=${y}&month=${m}&day=${day}`)
        .then(response => response.json())
        .then( events => {
            const list = document.getElementById('tasks-list');
            document.getElementById('tasks-heading').innerText = `${m}/${day}, ${y}`;
            if (list) {
                list.innerHTML = "";
                events.forEach( event  => {

                    const task = document.createElement('div');
                    task.id = event.id;

                    if (event.completed){
                        task.classList.add(`priority-6a`);
                    } else {
                        task.classList.add(`priority-${event.priority}a`);
                    }
                    task.classList.add("task");
                    task.addEventListener("click", () => {
                        if (event.completed) {
                            event.completed = 0;
                            task.classList.remove(`priority-6a`);
                            task.classList.add(`priority-${event.priority}a`);
                            toggleTask(event.id, 0)
                        }
                        else {
                            event.completed = 1;
                            task.classList.remove(`priority-${event.priority}a`);
                            task.classList.add(`priority-6a`);
                            toggleTask(event.id, 1)
                        }
                    })

                    task.innerHTML = `
                        <span class="task-name">${event.name}</span>
                        <span class="task-time">${event.start} - ${event.end}</span>
                    `

                    list.appendChild(task);
                });
            };               
        });
};

function toggleTask(eventId, done) {
    fetch(`/set_done/${eventId}/${done}`, { method: 'POST' })
        .then(response => response.json())
}

function openEventPopup(eventId) {
    const popup = document.getElementById('popup');
    const form = document.getElementById('event-form');
    const deleteButton = document.getElementById('delete-event-btn');

    if (eventId) {
        fetch(`/get_event/${eventId}`)
            .then(response => response.json())
            .then(event => {
                document.getElementById('event-name').value = event.name;
                document.getElementById('event-due-date').value = event.due_date;
                document.getElementById('event-min-time').value = event.min_time;
                document.getElementById('event-max-time').value = event.max_time;
                document.getElementById('event-priority').value = event.priority;
                deleteButton.style.display = 'inline';
            })
            .catch(err => console.error('Error fetching event:', err));
    } else {
        form.reset();
        deleteButton.style.display = 'none';
    }
    form.dataset.eventId = eventId || '';
    popup.classList.remove('hidden');
}

function closeEventPopup() {
    document.getElementById('popup').classList.add('hidden');
}

function deleteEvent() {
    const eventId = document.getElementById('event-form').dataset.eventId;
    if (!eventId) {
        alert('No event selected to delete!');
        return;
    }

    if (confirm('Are you sure you want to delete this event?')) {
        fetch(`/delete_event/${eventId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message || 'Event deleted successfully');
            closeEventPopup();
            location.reload();
        })
        .catch(err => console.error('Error:', err));
    }
}

function toggleDone(eventId, done) {
    fetch(`/set_done/${eventId}/${done}`, { method: 'POST' })
        .then(response => response.json())
        .then(() => location.reload());
}


