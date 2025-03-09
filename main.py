import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from backend.database import SchedulerStorage
from backend.datamodel import Scheduler, Event, Slot
from backend.databinding import DataBinding
from datetime import datetime, timedelta

if __name__ == "__main__":
    
    
    scheduler = Scheduler();
    storage = SchedulerStorage(scheduler);
    binding = DataBinding(storage);
    
    
    # events = [
    #     Event(
    #         datetime(2025, 3, 10, 8, 00),
    #         datetime(2025, 3, 10, 9, 00),
    #         3,
    #         timedelta(minutes=30),
    #         timedelta(minutes=60),
    #         datetime(2025, 3, 15),
    #         True, False, None
    #     ),
    #     Event(
    #         datetime(2025, 3, 8, 12, 30),
    #         datetime(2025, 3, 8, 14, 00),
    #         2,
    #         timedelta(minutes=45),
    #         timedelta(minutes=90),
    #         datetime(2025, 3, 15),
    #         True, False, None
    #     ),
    #     Event(
    #         datetime(2025, 3, 12, 14, 00),
    #         datetime(2025, 3, 12, 16, 00),
    #         4,
    #         timedelta(minutes=30),
    #         timedelta(minutes=120),
    #         datetime(2025, 3, 15),
    #         True, False, None
    #     ),
    # ]
    
    # for event in events:
    #     storage.add_event(event)
    
    print(storage.get_scheduled_events(2025,3));
    
    app = QGuiApplication(sys.argv);
    engine = QQmlApplicationEngine();
    engine.addImportPath("/home/dev/Documents/qt/6.8.2/gcc_64/qml");
    
    
    engine.rootContext().setContextProperty("databinding", binding);
    
    qml_file = "./main.qml";
    engine.load(qml_file);
    
    
    if not engine.rootObjects():
        sys.exit(-1);
        
    sys.exit(app.exec());
