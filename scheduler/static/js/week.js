document.addEventListener("DOMContentLoaded", () => {
    let currentSlot = null;
    let startY = 0;
    let startHeight = 0;

    document.querySelectorAll(".day-column").forEach(column => {
        column.addEventListener("mousedown", (e) => {
            if (e.target.classList.contains("slot")) return;

            const rect = column.getBoundingClientRect();
            const y = e.clientY - rect.top;
            const snappedY = Math.floor(y / 15) * 15; // Snap to 15 minutes

            const slot = document.createElement("div");
            slot.classList.add("slot");
            slot.style.top = snappedY + "px";
            slot.style.height = "60px"; // Default 1-hour height

            const handle = document.createElement("div");
            handle.classList.add("resize-handle");
            slot.appendChild(handle);

            column.appendChild(slot);
            addSlotEvents(slot);
        });
    });

    function addSlotEvents(slot) {
        slot.addEventListener("mousedown", (e) => {
            if (e.target.classList.contains("resize-handle")) return;

            currentSlot = slot;
            startY = e.clientY - slot.offsetTop;
            document.addEventListener("mousemove", moveSlot);
            document.addEventListener("mouseup", stopSlot);
        });

        slot.querySelector(".resize-handle").addEventListener("mousedown", (e) => {
            e.stopPropagation();
            currentSlot = slot;
            startHeight = slot.offsetHeight;
            startY = e.clientY;
            document.addEventListener("mousemove", resizeSlot);
            document.addEventListener("mouseup", stopSlot);
        });

        slot.addEventListener("contextmenu", (e) => {
            e.preventDefault();
            slot.remove();
        });

        slot.addEventListener("dblclick", () => {
            const copy = slot.cloneNode(true);
            slot.parentElement.appendChild(copy);
            addSlotEvents(copy);
        });
    }

    function moveSlot(e) {
        if (!currentSlot) return;
        let newY = e.clientY - startY;
        newY = Math.max(0, Math.floor(newY / 15) * 15);
        currentSlot.style.top = newY + "px";
    }

    function resizeSlot(e) {
        if (!currentSlot) return;
        let newHeight = startHeight + (e.clientY - startY);
        newHeight = Math.max(15, Math.floor(newHeight / 15) * 15);
        currentSlot.style.height = newHeight + "px";
    }

    function stopSlot() {
        document.removeEventListener("mousemove", moveSlot);
        document.removeEventListener("mousemove", resizeSlot);
        document.removeEventListener("mouseup", stopSlot);
        currentSlot = null;
    }

    document.getElementById("saveBtn").addEventListener("click", () => {
        const slots = [];
        document.querySelectorAll(".slot").forEach(slot => {
            const day = slot.parentElement.dataset.day;
            const start = parseInt(slot.style.top) / 60 + startHour;
            const duration = parseInt(slot.style.height) / 60;

            slots.push({ day, start, duration });
        });

        fetch("/save_slots", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ slots }),
        }).then(response => response.json()).then(data => {
            alert(data.message);
        });
    });
});
