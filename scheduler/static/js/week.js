document.addEventListener("DOMContentLoaded", () => {
    let currentSlot = null;
    let startY = 0;
    let startHeight = 0;

    let defaultHeight = "60px";

    let holdTimer = null;
    let holdThreshold = 400; // 300ms hold duration
    let holdStartX = 0;
    let holdStartY = 0;

    document.addEventListener("contextmenu", function (e) {
        e.preventDefault();
    });

    document.querySelectorAll(".day-column").forEach(column => {
        column.addEventListener("mousedown", (e) => {
            if (e.target.classList.contains("slot")) return;
            
            holdStartX = e.clientX;
            holdStartY = e.clientY;
            
            holdTimer = setTimeout(() => {
                const rect = column.getBoundingClientRect();
                const y = e.clientY - rect.top;
                const snappedY = Math.floor(y / 15) * 15;
                
                const slot = document.createElement("div");
                slot.classList.add("slot");
                slot.style.top = snappedY + "px";
                slot.style.height = defaultHeight;
                const handle = document.createElement("div");
                handle.classList.add("resize-handle");
                slot.appendChild(handle);
                column.appendChild(slot);
                addSlotEvents(slot);
            }, holdThreshold);
        });
        
        // Add mouseup handler to cancel hold
        column.addEventListener("mouseup", () => {
            if (holdTimer) {
                clearTimeout(holdTimer);
                holdTimer = null;
            }
        });
        
        // Add mouseleave handler to cancel hold if mouse leaves element
        column.addEventListener("mouseleave", () => {
            if (holdTimer) {
                clearTimeout(holdTimer);
                holdTimer = null;
            }
        });
    });

    function checkCollision(slot, container) {
        const slotRect = slot.getBoundingClientRect();
        const slotTop = parseInt(slot.style.top);
        const slotBottom = slotTop + slot.offsetHeight;
        
        // Check collisions with all slots in the container
        const existingSlots = Array.from(container.querySelectorAll('.slot'));
        
        for (const existingSlot of existingSlots) {
            if (existingSlot === slot) continue; // Skip self
            
            const existingTop = parseInt(existingSlot.style.top);
            const existingBottom = existingTop + existingSlot.offsetHeight;
            
            // Check if there's any overlap
            if (slotTop < existingBottom && slotBottom > existingTop) {
                return true;
            }
        }
        
        return false;
    }
    
    function moveSlot(e) {
        if (!currentSlot) return;
            
        // Get container bounds
        const container = currentSlot.parentElement;
        const containerRect = container.getBoundingClientRect();
        const maxBottom = containerRect.bottom + 15;
        
        // Calculate new Y position
        let newY = e.clientY - startY;
        newY = Math.max(0, Math.min(newY, maxBottom - containerRect.top - currentSlot.offsetHeight));
        newY = Math.floor(newY / 15) * 15; // Maintain 15-minute grid
        
        // Check collision before moving
        if (!checkCollision(currentSlot, currentSlot.parentElement)) {
            currentSlot.style.top = newY + "px";
        } else {
            // Move back to previous position if collision detected
            newY = parseInt(currentSlot.style.top);
        }
    }
    
    function resizeSlot(e) {
        if (!currentSlot) return;
        
        // Get container bounds
        const container = currentSlot.parentElement;
        const containerRect = container.getBoundingClientRect();
        const maxBottom = containerRect.bottom;
        
        // Calculate new height
        const newHeight = startHeight + (e.clientY - startY);
        const minHeight = 15; // Minimum height in pixels
        const maxHeight = maxBottom - containerRect.top - parseInt(currentSlot.style.top);
        const snappedHeight = Math.max(minHeight, Math.min(Math.floor(newHeight / 15) * 15, maxHeight));
        
        // Only update height if it doesn't cause collision
        if (!checkCollision(currentSlot, container)) {
            currentSlot.style.height = snappedHeight + "px";
        }
    }
    
    function moveSlotBetweenDays(e) {
        if (!currentSlot) return;
    
        // Get all day columns
        const dayColumns = document.querySelectorAll('.day-column');
        
        // Find which day we're over
        let targetDay = null;
        dayColumns.forEach(dayColumn => {
            if (dayColumn.getBoundingClientRect().left <= e.clientX &&
                e.clientX <= dayColumn.getBoundingClientRect().right) {
                targetDay = dayColumn;
            }
        });
    
        // Handle movement within same column
        if (!targetDay || targetDay === currentSlot.parentElement) {
            moveSlot(e);
            return;
        }
    
        // Try to move to new day
        const originalParent = currentSlot.parentElement;
        const originalTop = parseInt(currentSlot.style.top);
        
        // Temporarily move slot to check collision
        targetDay.appendChild(currentSlot);
        
        if (!checkCollision(currentSlot, targetDay)) {
            // Move successful - update position
            currentSlot.style.top = originalTop + "px";
        } else {
            // Move failed - revert to original position
            originalParent.appendChild(currentSlot);
        }
        
    }
    
    function stopSlot() {
        document.removeEventListener("mousemove", moveSlotBetweenDays);
        document.removeEventListener("mousemove", resizeSlot);
        document.removeEventListener("mouseup", stopSlot);
        currentSlot = null;
    }
    
    // Update event listeners in addSlotEvents
    function addSlotEvents(slot) {
        slot.addEventListener("mousedown", (e) => {
            if (e.target.classList.contains("resize-handle")) return;
            
            currentSlot = slot;
            startY = e.clientY - slot.offsetTop;
            
            document.addEventListener("mousemove", moveSlotBetweenDays);
            document.addEventListener("mouseup", stopSlot);
        });
        
        slot.querySelector(".resize-handle").addEventListener("mousedown", (e) => {
            e.stopPropagation();
            currentSlot = slot;
            startHeight = slot.offsetHeight;
            startY = e.clientY;
            
            document.addEventListener("mousemove", resizeSlot);
            document.removeEventListener("mousemove", moveSlotBetweenDays); // Prevent conflict
            document.addEventListener("mouseup", stopSlot);
        });

        slot.addEventListener("contextmenu", (e) => {
            e.preventDefault();
            holdStartX = e.clientX;
            holdStartY = e.clientY;
            
            slot.classList.add('holding');
            
            holdTimer = setTimeout(() => {
                slot.remove();
            }, holdThreshold);
        });
        
        // Add mouseup handler to cancel hold
        slot.addEventListener("mouseup", () => {
            if (holdTimer) {
                clearTimeout(holdTimer);
                holdTimer = null;
                slot.classList.remove('holding');
            }
        });
        
        // Add mouseleave handler to cancel hold if mouse leaves element
        slot.addEventListener("mouseleave", () => {
            if (holdTimer) {
                clearTimeout(holdTimer);
                holdTimer = null;
                slot.classList.remove('holding');
            }
        });

        slot.addEventListener("dblclick", () => {
            defaultHeight = slot.style.height;
        });
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
