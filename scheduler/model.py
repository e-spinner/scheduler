from dataclasses import dataclass, field
from typing import List, Literal
from datetime import datetime, timedelta

from database import SchedulerStorage

@dataclass
class TimeWindow:
    """Abstract class that defines a window of time"""
    start: datetime;
    end: datetime;
    priority: Literal[1, 2, 3, 4, 5];
    
    @property
    def duration(self) -> timedelta:
        return self.end - self.start;

@dataclass
class Slot(TimeWindow):
    """A window of available time that can be filled with events"""
    id: int;
    time_used: int = 0;
    
    @property
    def capacity(self) -> timedelta:
        return self.duration - timedelta(minutes=self.time_used);
    
    @property
    def adj_start(self) -> datetime:
        return self.start + (self.duration - self.capacity);
        
@dataclass
class Event(TimeWindow):
    """A Event that has a range of length that needs to be scheduled"""
    min_time: timedelta;
    max_time: timedelta;
    
    # availibility: List[TimeWindow];
    due_date: datetime;
    id: int;
    
    # flags for state control
    is_scheduled: bool = False;
    is_failed: bool = False;
    
    def schedule_event(self, start: datetime, end: datetime) -> None:
        """Schedule the event in a specific time window."""
        
        if self.is_scheduled:
            raise ValueError("Event is already scheduled");
        
        if end - start < self.min_time or end - start > self.max_time:
            raise ValueError(f"Duration must be between {self.min_time} and {self.max_time}");
            
        self.start = start;
        self.end = end;
        self.is_scheduled = True;
    
class Scheduler:
    def __init__(self, storage: SchedulerStorage):
        self.storage = storage
        self.slots: List[Slot] = []
        self.events: List[Event] = []
        self.load_data()
    
    def load_data(self):
        current_date = datetime.now()
        conn = self.storage.get_db_connection()
        cursor = conn.cursor()

        # Load slots from today onwards
        cursor.execute("""
            SELECT start, end, priority, id FROM slots
            WHERE start >= ?
            ORDER BY priority ASC, start ASC
        """, (current_date,))
        self.slots = [Slot(datetime.fromisoformat(row['start']), datetime.fromisoformat(row['end']), row['priority'], row['id'], 0) for row in cursor.fetchall()]

        # Load all uncompleted events from today onwards, even previously scheduled
        cursor.execute("""
            SELECT id, name, start, end, due_date, min_time, max_time, priority FROM events
            WHERE due_date >= ?
            AND completed == 0
            ORDER BY priority DESC, due_date ASC
        """, (current_date,))
        self.events = [
            Event(
                None,
                None,
                row['priority'],
                timedelta(minutes=row['min_time']),
                timedelta(minutes=row['max_time']),
                datetime.fromisoformat(row['due_date']),
                row['id'],
            ) for row in cursor.fetchall()
        ]

        conn.close()

    
    def optimize_schedule(self) -> None:
        
        # pass through events in priority order
        for event in self.events:
            # try different times for event, from max to min incrementing by 15

            for duration in [timedelta(minutes=x)
                             for x in range(
                             int(event.max_time.total_seconds() / 60),
                             int(event.min_time.total_seconds() / 60) - 1,
                             -15
                            )]:
                selected_slot = None;
                for slot in self.slots:
                    if duration <= slot.capacity and (slot.start + duration <= event.due_date):
                        selected_slot = slot;
                        break;
                if selected_slot:
                    print(slot)
                    event.schedule_event(slot.adj_start, slot.adj_start + duration);
                    slot.time_used += int(duration.total_seconds() // 60);
                    break
 
            if not event.is_scheduled: event.is_failed = True;

            # could later add logic to try to recover time from previously scheduled events
        
        

    def save_scheduled_events(self) -> None:
        conn = self.storage.get_db_connection();
        cursor = conn.cursor();
        for event in self.events:
            if event.is_scheduled:
                cursor.execute("""
                    UPDATE events
                    SET start = ?, end = ?
                    WHERE id = ?
                """, (event.start.isoformat(), event.end.isoformat(), event.id));
                
        for slot in self.slots:
            if slot.time_used != 0:
                cursor.execute("""
                    UPDATE slots
                    set time_used = ?
                    WHERE id = ?
                """, (slot.time_used, slot.id));
                
        
            
        conn.commit();
        conn.close();
