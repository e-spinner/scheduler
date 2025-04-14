from typing import List
from datetime import datetime, timedelta

from model import Slot, Event
from database import SchedulerStorage

import numpy as np
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.termination import get_termination
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling


# opt logic
def optimize_schedule( x:np.ndarray, slots:List[Slot], events:List[Event], debug:bool) -> tuple[float, int, float, List[Event], List[Slot]]:

    if debug: print(f'x: {x}');
    # extract x
    duration_scalars = x[:len(events)];
    ordering_values  = x[len(events):];
    
    # sort events by second half of x
    events_zip = list(zip(events, duration_scalars, ordering_values));
    events_zip.sort(key=lambda tuple: tuple[2]);
    
    events_sorted = [event for event, _, _ in events_zip];
    duration_scalars = [duration for _, duration, _ in events_zip];
    
    total_slot_priority: float = 0;
    num_late: int = 0;
    event_sooness_penalty: float = 0;
    
    slot_index: int = 0;
    out_of_space: bool = False;
    
    # walk through each event, with each x
    for x_index, event in enumerate(events_sorted):
        if debug: print(f'current event: {event.id}');
                    
        total_minutes = event.calc_duration(duration_scalars[x_index]).total_seconds() / 60;
        duration: timedelta = timedelta(minutes=round(total_minutes / 15) * 15);
        
        if debug: print(f'duration: {duration}');
        
        # loop to find a slot
        while(True):
            
            # first check to see if out of bounds
            if slot_index >= len(slots) or out_of_space: 
                if debug: print(f'checking slot: OUT_OF_SPACE');
                out_of_space = True;
                num_late += 1;
                total_slot_priority += 5.01;
                break;
                
            if debug: print(f'checking slot: {slots[slot_index].id}');
            # next check to see if current slot has room for event
            if slots[slot_index].capacity < duration:
                # move to next slot if previous too small
                slot_index += 1;
            
            # there is room, move on to schedule   
            else: break;
            
        # assign event to slot
        if not out_of_space:
            start: datetime = slots[slot_index].adj_start;
            
            end: datetime = start + duration;
            
            if debug: print(f'scheduling event: {event.id}');
            event.schedule_event(start=start, end=end);
            slots[slot_index].time_used += int(duration.total_seconds() // 60);

            # Calculate objectives
            total_slot_priority += slots[slot_index].priority;
            
            if slots[slot_index].adj_start + event.min_time > event.due_date:
                num_late += 10;
                
            days_till_due = (event.due_date - event.start).days;
            if debug: print(f'days: {days_till_due}');
                
            event_sooness_penalty += 1 - pow( np.e, 0.2 * (days_till_due));
            # if days_till_due <= 0: event_sooness_penalty += 10;
                    
    return (total_slot_priority, num_late, event_sooness_penalty, events, slots);

class SchedulerProblem(ElementwiseProblem):
    def __init__(self, slots: List[Slot], events: List[Event], debug: bool = False):
        self.slots = slots;
        self.events = events;
        self.debug = debug;
        
        # Two variables per event -> the 0 to 1 scale of event.min to event.max time
        #                         -> the order to schedule events, 0 to 1
        n_var = len(events) * 2;
        
        n_obj = 2;
        n_constr = 1;
        
        # Decision variable bounds (0 to 1)
        xl = np.zeros(n_var);
        xu = np.ones(n_var);

        super().__init__(n_var=n_var, n_obj=n_obj, n_constr=n_constr, xl=xl, xu=xu);

    # ================== ASSUMPTIONS ==================== #
    # Slots are given in the order that they should be used
    
    def _evaluate(self, x, out, *args, **kwargs):
        
        total_slot_priority, num_late, sooness, _, _ = optimize_schedule(x, self.slots, self.events, self.debug);

        out["F"] = [total_slot_priority, sooness];
        out["G"] = [num_late];
        
        # reset objects
        for slot in self.slots:
            slot.time_used = 0;
            
        for event in self.events:
            event.is_scheduled = False;
            event.start = None;
            event.end = None;
       
# MARK: NSGA2  
def schedule_with_nsga2(slots: List[Slot], events: List[Event]) -> tuple[List[Event], List[Slot]]:
    problem = SchedulerProblem(slots, events);

    algorithm = NSGA2(pop_size=100,
                sampling=FloatRandomSampling(),
                crossover=SBX(prob=1.0, eta=3.0),
                mutation=PM(prob=1.0, eta=3.0),
                eliminate_duplicates=False,
                );

    termination = get_termination("n_gen", 100);

    result = minimize(
        problem,
        algorithm,
        termination,
        verbose=False
    );
    
    _, _, _, opt_events, opt_slots = optimize_schedule(result.X[0], slots, events, False);

    return (opt_events, opt_slots);


# MARK: Greedy
def greedy_scheduler(slots: List[Slot], events: List[Event]) -> tuple[List[Event], List[Slot]]:
        # pass through events in priority order
    for event in events:
        # try different times for event, from max to min incrementing by 15

        for duration in [timedelta(minutes=x)
                            for x in range(
                            int(event.max_time.total_seconds() / 60),
                            int(event.min_time.total_seconds() / 60) - 1,
                            -15
                        )]:
            selected_slot = None;
            for slot in slots:
                if duration <= slot.capacity and (slot.start + duration <= event.due_date):
                    selected_slot = slot;
                    break;
            if selected_slot:
                event.schedule_event(slot.adj_start, slot.adj_start + duration);
                slot.time_used += int(duration.total_seconds() // 60);
                break

        if not event.is_scheduled: event.is_failed = True;

        # could later add logic to try to recover time from previously scheduled events
        
        return (events, slots);
   
# MARK: Scheduler
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

    def schedule(self, greedy:bool = False) -> None:
        if greedy:
            self.events, self.slots = greedy_scheduler(self.slots, self.events);
            
        else: 
            self.events, self.slots = schedule_with_nsga2(self.slots, self.events);

        

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