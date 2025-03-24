
Object.entries(num_per_priority).forEach(([day, priorities]) => {
    const box = document.getElementById(day);
    if (box) {
        priorities.forEach((num, index) => {
        if (num > 0) { // Only display if there are events
            const circle = document.createElement('div');
            circle.classList.add('event');
            circle.classList.add(`priority-${index + 1}a`);
            circle.innerText = `${num}`;
            box.appendChild(circle);
        }
        
        box.addEventListener("click", () => {
            openPopup(day);
        });
    });
    }
});

function openPopup(day) {
    fetch(`/events_on_day?year=${year}&month=${month}&day=${day}`)
        .then(response => response.json())
        .then( events => {
            console.log(events);
        });

    document.getElementById('popup').classList.remove('hidden');
};

function closePopup() {
    document.getElementById('popup').classList.add('hidden');
};