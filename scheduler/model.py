from dataclasses import dataclass
from typing import Literal
from datetime import datetime, timedelta

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
    
    def calc_duration(self, percent: float) -> timedelta:
        return self.min_time + percent * (self.max_time - self.min_time);
    
    def schedule_event(self, start: datetime, end: datetime) -> None:
        """Schedule the event in a specific time window."""
        
        if self.is_scheduled:
            raise ValueError("Event is already scheduled");
        
        if end - start < self.min_time or end - start > self.max_time:
            raise ValueError(f"Duration must be between {self.min_time} and {self.max_time}");
            
        self.start = start;
        self.end = end;
        self.is_scheduled = True;
