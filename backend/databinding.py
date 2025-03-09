from PySide6.QtCore import QObject, Signal, Slot, Property
from backend.database import SchedulerStorage

class DataBinding(QObject):
    updated = Signal()  # Signal for refreshing the UI when data changes

    def __init__(self, storage: SchedulerStorage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.current_year = 2025
        self.current_month = 3
        self.scheduled_events = []

        self.load_data()

    @Slot()
    def load_data(self):
        """Load data from the database and notify the UI."""
        self.scheduled_events = self.storage.get_scheduled_events(self.current_year, self.current_month)
        self.updated.emit()

    @Slot(int, int)
    def set_date(self, year, month):
        """Change the active month/year and refresh data."""
        self.current_year = year
        self.current_month = month
        self.load_data()

    @Slot(result='QVariantList')
    def get_event_days(self):
        """Return scheduled event days for QML use."""
        return self.scheduled_events

    @Slot(result=int)
    def get_year(self):
        return self.current_year

    @Slot(result=int)
    def get_month(self):
        return self.current_month
