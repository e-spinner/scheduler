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

document.getElementById('event-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const eventId = event.target.dataset.eventId;
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
    fetch(`/mark_done/${eventId}/${done}`, { method: 'POST' })
        .then(response => response.json())
        .then(() => location.reload());
}
