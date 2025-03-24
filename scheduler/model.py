from dataclasses import dataclass, field
from typing import List, Literal, Optional
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
    percent_left: float = 1.0;
    
    @property
    def capacity(self) -> timedelta:
        return self.duration * self.percent_left;
    
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
            SELECT start, end, percent_left, priority FROM slots
            WHERE start >= ?
            ORDER BY priority ASC, start ASC
        """, (current_date,))
        self.slots = [Slot(datetime.fromisoformat(row['start']), datetime.fromisoformat(row['end']), row['priority'], row['percent_left']) for row in cursor.fetchall()]

        # Load all events from today onwards, even previously scheduled
        cursor.execute("""
            SELECT id, name, start, end, due_date, min_time, max_time, priority FROM events
            WHERE due_date >= ?
            ORDER BY priority ASC, due_date ASC
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
        
        # scheduling logic goes here
        
        pass
        

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
        conn.commit();
        conn.close();
