

function toggleListVisibility(listId, type) {
    const listElement = document.getElementById(listId);
    const isHidden = listElement.style.display === 'none';
    
    // Toggle visibility of the list
    listElement.style.display = isHidden ? 'block' : 'none';

    const listbtn = document.getElementById(`${listId}-btn`);
    if (listbtn.style.cursor == 'zoom-in') {
        listbtn.style.cursor = 'zoom-out'
        listbtn.innerText = `Hide ${type}`
        listElement.parentElement.classList.remove('collapsed');
    } 
    else {
        listbtn.style.cursor = 'zoom-in'
        listbtn.innerText = `Show ${type}`
        listElement.parentElement.classList.add('collapsed');
    }

}
