from dataclasses import dataclass, field
from typing import List, Literal, Optional
from datetime import datetime, timedelta
from tabulate import tabulate

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
        return self.start + (self.duration - self.capacity)
        
@dataclass
class Event(TimeWindow):
    """A Event that has a range of length that needs to be scheduled"""
    min_time: timedelta;
    max_time: timedelta;
    
    # availibility: List[TimeWindow];
    due_date: Optional[datetime] = None;
    
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
    
@dataclass
class Scheduler:
    slots: List[Slot] = field(default_factory=list);
    events: List[Event] = field(default_factory=list);
    
    def add_slot(self, slot: Slot) -> None:
        """Add an slot to the slots list."""
        self.slots.append(slot);
        self.slots.sort(key=lambda x: (x.priority, x.start));
        
    def add_event(self, event: Event) -> None:
        """Add an event to the events list."""
        self.events.append(event);
        self.events.sort(key=lambda x: (x.priority, x.due_date or datetime.max));

    def _find_slot(self, target_duration: timedelta) -> Optional[Slot]:
        """
        Find the highest-priority available time slot that can accommodate the target duration.
        Returns the Slot if found, None otherwise.
        """
        for slot in self.slots:
            if target_duration <= slot.capacity: return slot;
        
        return None;
    
    def optimize_schedule(self) -> None:
        
        # pass through events in priority order
        for event in self.events:
            # try different times for event, from max to min incrementing by 5
            for duration in [timedelta(minutes=x)
                            for x in range(
                                int(event.max_time.total_seconds() / 60),
                                int(event.min_time.total_seconds() / 60) - 1,
                                -5
                            )]:
                
                slot = self._find_slot(duration);
                if slot and (not event.due_date or slot.start + duration <= event.due_date):
                                        
                    event.schedule_event(slot.adj_start, slot.adj_start + duration);
                    slot.percent_left -= duration / slot.capacity;
                    
                    break
            
            if not event.is_scheduled: event.is_failed = True;
            # could later add logic to try to recover time from previously scheduled events
                
    def display_schedule(self) -> None:
        # Display slots with their remaining capacit
        print("\nAvailable Slots:");
        print(tabulate([(
                slot.start.strftime("%Y-%m-%d %H:%M"),
                slot.end.strftime("%Y-%m-%d %H:%M"),
                f"{slot.percent_left*100:.1f}%",
                slot.priority)
            for slot in self.slots], 
            headers=["Start", "End", "Remaining", "Priority"],
            tablefmt="grid"
        ));
        # Display scheduled events
        print("\nScheduled Events:");
        print(tabulate([(
                event.start.strftime("%Y-%m-%d %H:%M"),
                event.end.strftime("%Y-%m-%d %H:%M"),
                f"{event.duration.total_seconds() / 60:.1f}m",
                event.priority)
            for event in self.events if event.is_scheduled],
            headers=["Start", "End", "Duration", "Priority"],
            tablefmt="grid"
        ));
        
        print("\nFailed Events:");
        print(tabulate([(
                event.start.strftime("%Y-%m-%d %H:%M"),
                event.end.strftime("%Y-%m-%d %H:%M"),
                f"{event.duration.total_seconds() / 60:.1f}m",
                event.priority)
            for event in self.events if event.is_failed],
            headers=["Start", "End", "Duration", "Priority"],
            tablefmt="grid"
        ));

        
# hardcoded example                 
if __name__ == '__main__':
    
    scheduler = Scheduler();
    
    slots = [
        Slot(
            priority=5,
            start=datetime(2025, 1, 1, 9),
            end=datetime(2025, 1, 1, 12),
        ),
        Slot(
            priority=3,
            start=datetime(2025, 1, 1, 13),
            end=datetime(2025, 1, 1, 17)
        ),
        Slot(
            priority=4,
            start=datetime(2025, 1, 2, 9),
            end=datetime(2025, 1, 2, 13)
        )
    ];
    
    for slot in slots:
        scheduler.add_slot(slot);
        
        events = [
        Event(
            priority=5,
            start=None,
            end=None,
            min_time=timedelta(minutes=30),
            max_time=timedelta(hours=2)
        ),
        Event(
            priority=4,
            start=None,
            end=None,
            min_time=timedelta(minutes=15),
            max_time=timedelta(minutes=30)
        ),
        Event(
            priority=3,
            start=None,
            end=None,
            min_time=timedelta(minutes=45),
            max_time=timedelta(hours=1)
        ),
        Event(
            priority=2,
            start=None,
            end=None,
            min_time=timedelta(minutes=60),
            max_time=timedelta(hours=2)
        )];
        
    # Add events to scheduler
    for event in events:
        scheduler.add_event(event);
        
    scheduler.display_schedule();
    scheduler.optimize_schedule();
    scheduler.display_schedule();