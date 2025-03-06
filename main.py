from database import SchedulerStorage
from datetime import datetime, timedelta
from models import Slot, Event

storage = SchedulerStorage()

# Faux user input
new_slot = Slot(datetime(2025, 3, 6, 9, 0), datetime(2025, 3, 6, 12, 0), 3, 1.0)
new_event = Event(None, None, 3, timedelta(minutes=30), timedelta(minutes=90))

# Add slot & event
storage.add_slot(new_slot)
storage.add_event(new_event)

# Run optimization
storage.optimize_schedule()

# Display updated schedule
storage.display_schedule()
