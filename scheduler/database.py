from sqlite3 import connect, IntegrityError
from datetime import datetime, timedelta
from model import Slot, Event, Scheduler
from typing import List

DB_PATH = "database.db";

class SchedulerStorage:
    def __init__(self, scheduler: Scheduler, db_path=DB_PATH):
        self.db_path = db_path;
        self._initialize_db();
        
        self.scheduler = scheduler;
        self._load_data();

    def _initialize_db(self) -> None:
        """Create tables if they don't exist."""
        with connect(self.db_path) as conn:
            cursor = conn.cursor();
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS slots (
                    start DATETIME NOT NULL,
                    end DATETIME NOT NULL,
                    percent_left REAL NOT NULL,
                    priority INTEGER NOT NULL,
                    PRIMARY KEY(start, end)
                );

                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start DATETIME DEFAULT NULL,
                    end DATETIME DEFAULT NULL,
                    min_time INTEGER NOT NULL,
                    max_time INTEGER NOT NULL,
                    priority INTEGER NOT NULL,
                    due_date DATETIME DEFAULT NULL,
                    is_scheduled INTEGER NOT NULL DEFAULT 0,
                    is_done INTEGER NOT NULL DEFAULT 0
                );
            """);
            conn.commit();

    def _load_data(self) -> None:
        """Fill scheduler with prexisting data"""
        self.scheduler.slots = self.get_future_slots();
        self.scheduler.events = self.get_schedulable_events();
        
    def add_slot(self, slot: Slot) -> None:
        """Insert a new slot into the database."""
        with connect(self.db_path) as conn:
            cursor = conn.cursor();
            try:
                cursor.execute("""
                    INSERT INTO slots (start, end, percent_left, priority)
                    VALUES (?, ?, ?, ?)
                """, (slot.start.isoformat(), slot.end.isoformat(), slot.percent_left, slot.priority))
                conn.commit()
            except IntegrityError:
                print(f"Slot from {slot.start} to {slot.end} already exists. Skipping insert.")

            

    def add_event(self, event: Event) -> None:
        """Insert a new event into the database."""
        with connect(self.db_path) as conn:
            cursor = conn.cursor();
            cursor.execute("""
                INSERT INTO events (start, end, min_time, max_time, priority, due_date, is_scheduled, is_done)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
            event.start, event.end,
            int(event.min_time.total_seconds()),
            int(event.max_time.total_seconds()),
            event.priority,
            event.due_date.isoformat() if event.due_date else None,
            event.is_scheduled, 0
        ))
        

    def get_slots(self) -> List[Slot]:
        """Retrieve all slots in List[Slot] form."""
        with connect(self.db_path) as conn: 
            cursor = conn.cursor();
            cursor.execute("SELECT * FROM slots");
            rows = cursor.fetchall();
            return [Slot(datetime.fromisoformat(row[0]), datetime.fromisoformat(row[1]), row[3], row[2]) for row in rows];
        
    def get_future_slots(self) -> List[Slot]:
        """Retrieve all future slots in List[Slot] form."""
        now = datetime.now()
        with connect(self.db_path) as conn: 
            cursor = conn.cursor();
            cursor.execute("SELECT * FROM slots WHERE start > ?", (now.isoformat(),));
            rows = cursor.fetchall();
            return [Slot(datetime.fromisoformat(row[0]), datetime.fromisoformat(row[1]), row[3], row[2]) for row in rows];

    def get_scheduled_events(self, year, month) -> List[int]:
        """Retrieve all events in List[Event] form."""
        with connect(self.db_path) as conn:
            cursor = conn.cursor();
            
            # First day of the month
            start_date = datetime(year, month, 1);
            
            # Last day of the month
            if month == 12:
                end_date = datetime(year + 1, 1, 1);
            else:
                end_date = datetime(year, month + 1, 1);
                
            cursor.execute("""
                SELECT DISTINCT strftime('%d', start) as day
                FROM events
                WHERE is_scheduled = 1 
                AND start >= ?
                AND start < ?
                """, (start_date, end_date));
        
        return [row[0] for row in cursor.fetchall()];

    def get_schedulable_events(self) -> List[Event]:
        """Retrieve all events in List[Event] form."""
        now = datetime.now()
        with connect(self.db_path) as conn:
            cursor = conn.cursor();
            cursor.execute("""
                SELECT * FROM events 
                WHERE (is_scheduled = 0 OR (end < ? AND is_done = 0))
            """, (now.isoformat(),));
            rows = cursor.fetchall();
            return [Event(
                    row[0],
                    None, 
                    None, 
                    row[5], 
                    timedelta(seconds=row[3]), 
                    timedelta(seconds=row[4]), 
                    datetime.fromisoformat(row[6]), 
                    bool(row[7]))
                for row in rows if row[8] == 0];
        
    def update_event_done(self, event_id: int, is_done: bool) -> None:
        """
        Update an event's `is_done` flag in the database.
        """
        with connect(self.db_path) as conn:
            cursor = conn.cursor();
            cursor.execute("""
                UPDATE events
                SET is_done = ?
                WHERE id = ?
            """, (1 if is_done else 0, event_id));
            conn.commit();
        
    def optimize_schedule(self) -> None:
        """Optimize and store scheduled events in the database."""
        self.scheduler.optimize_schedule();
        
        with connect(self.db_path) as conn:
            cursor = conn.cursor();
            for event in self.scheduler.events:
                if event.is_scheduled:
                    cursor.execute("""
                        UPDATE events
                        SET start = ?, end = ?, is_scheduled = 1
                        WHERE min_time = ? AND max_time = ? AND priority = ?
                    """, (event.start.isoformat(), event.end.isoformat(), int(event.min_time.total_seconds()), int(event.max_time.total_seconds()), event.priority));
            conn.commit();

    def display_schedule(self) -> None:
        """Display the schedule from the scheduler."""
        self.scheduler.display_schedule();