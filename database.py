from sqlite3 import connect, IntegrityError
from datetime import datetime, timedelta
from models import Slot, Event, Scheduler

DB_PATH = "database.db";

class SchedulerStorage:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path;
        self._initialize_db();
        
        self.scheduler = Scheduler();
        self._load_data();

    def _initialize_db(self):
        """Create tables if they don't exist."""
        with connect(self.db_path) as conn:
            cursor = conn.cursor();
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS slots (
                    start TEXT NOT NULL,
                    end TEXT NOT NULL,
                    percent_left REAL NOT NULL,
                    priority INTEGER NOT NULL,
                    PRIMARY KEY(start, end)
                );

                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start TEXT DEFAULT NULL,
                    end TEXT DEFAULT NULL,
                    min_time INTEGER NOT NULL,
                    max_time INTEGER NOT NULL,
                    priority INTEGER NOT NULL,
                    due_date TEXT DEFAULT NULL,
                    is_scheduled INTEGER NOT NULL DEFAULT 0,
                    is_failed INTEGER NOT NULL DEFAULT 0,
                    is_done INTEGER NOT NULL DEFAULT 0
                );
            """);
            conn.commit();

    def _load_data(self):
        """Fill scheduler with prexisting data"""
        self.scheduler.slots = self.get_future_slots();
        self.scheduler.events = self.get_schedulable_events();
        
    def add_slot(self, slot: Slot):
        """Insert a new slot into the database."""
        with connect(self.db_path) as conn:
            cursor = conn.cursor();
            try:
                cursor.execute("""
                    INSERT INTO slots (start, end, percent_left, priority)
                    VALUES (?, ?, ?, ?)
                """, (slot.start.isoformat(), slot.end.isoformat(), slot.percent_left, slot.priority))
                conn.commit()
                self.scheduler.add_slot(slot);
            except IntegrityError:
                print(f"Slot from {slot.start} to {slot.end} already exists. Skipping insert.")

            

    def add_event(self, event: Event):
        """Insert a new event into the database."""
        with connect(self.db_path) as conn:
            cursor = conn.cursor();
            cursor.execute("""
                INSERT INTO events (start, end, min_time, max_time, priority, due_date, is_scheduled, is_failed, is_done)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
            None, None,
            int(event.min_time.total_seconds()),
            int(event.max_time.total_seconds()),
            event.priority,
            event.due_date.isoformat() if event.due_date else None,
            0, 0, 0
        ))
            
        self.scheduler.add_event(event);

    def get_slots(self):
        """Retrieve all slots in List[Slot] form."""
        with connect(self.db_path) as conn: 
            cursor = conn.cursor();
            cursor.execute("SELECT * FROM slots");
            rows = cursor.fetchall();
            return [Slot(datetime.fromisoformat(row[0]), datetime.fromisoformat(row[1]), row[3], row[2]) for row in rows];
        
    def get_future_slots(self):
        """Retrieve all future slots in List[Slot] form."""
        now = datetime.now()
        with connect(self.db_path) as conn: 
            cursor = conn.cursor();
            cursor.execute("SELECT * FROM slots WHERE start > ?", (now.isoformat(),));
            rows = cursor.fetchall();
            return [Slot(datetime.fromisoformat(row[0]), datetime.fromisoformat(row[1]), row[3], row[2]) for row in rows];

    def get_events(self):
        """Retrieve all events in List[Event] form."""
        with connect(self.db_path) as conn:
            cursor = conn.cursor();
            cursor.execute("SELECT * FROM events");
            rows = cursor.fetchall();
            return [Event(
                    None, 
                    None, 
                    row[5], 
                    timedelta(seconds=row[3]), 
                    timedelta(seconds=row[4]), 
                    datetime.fromisoformat(row[6]), 
                    bool(row[7]), 
                    bool(row[8])) 
                for row in rows if row[9] == 0];

    def get_schedulable_events(self):
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
                    None, 
                    None, 
                    row[5], 
                    timedelta(seconds=row[3]), 
                    timedelta(seconds=row[4]), 
                    datetime.fromisoformat(row[6]), 
                    bool(row[7]), 
                    bool(row[8])) 
                for row in rows if row[9] == 0];
        
    def optimize_schedule(self):
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

    def display_schedule(self):
        """Display the schedule from the scheduler."""
        self.scheduler.display_schedule();