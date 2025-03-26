from sqlite3 import connect, Row

DB_PATH = "database.db";

class SchedulerStorage:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Create tables if they don't exist."""
        with connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS slots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start DATETIME NOT NULL,
                    end DATETIME NOT NULL,
                    time_used INTERGER NOT NULL DEFAULT 0,
                    priority INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(28) NOT NULL,
                    start DATETIME DEFAULT NULL,
                    end DATETIME DEFAULT NULL,
                    due_date DATETIME NOT NULL,
                    min_time INTEGER NOT NULL,
                    max_time INTEGER NOT NULL,
                    priority INTEGER NOT NULL,
                    completed BOOLEAN DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS event_availability (
                    event_id INTEGER,
                    start DATETIME NOT NULL,
                    end DATETIME NOT NULL,
                    priority INTEGER NOT NULL,
                    FOREIGN KEY (event_id) REFERENCES events(id),
                    PRIMARY KEY (event_id, start, end)
                );
            """);
            conn.commit()

    def get_db_connection(self):
        conn = connect(self.db_path)
        conn.row_factory = Row
        return conn
