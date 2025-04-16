from flask import render_template, request, jsonify, Response

from database import SchedulerStorage

from datetime import datetime, timedelta
from calendar import monthrange, month_abbr

def_start_hour = 8;

# ======== #
# CALENDAR #                             
# ======== #

# == WEEK == #                          MARK: Week
def week_view() -> str:
    # Get selected date from query parameters
    year = int(request.args.get('year', datetime.now().year));
    month = int(request.args.get('month', datetime.now().month));
    day = int(request.args.get('day', datetime.now().day));
    start_hour = int(request.args.get('start_hour', def_start_hour));  # Default to 5 AM

    # Find the start of the week (Monday)
    selected_date = datetime(year, month, day);
    start_of_week = get_week_start(selected_date);
    prev_week_start = start_of_week - timedelta(days=7);
    next_week_start = start_of_week + timedelta(days=7);

    # Generate week days
    week_days = [(start_of_week + timedelta(days=i)) for i in range(7)];


    return render_template(
        'calendar/week_view.html',
        week_days=week_days,
        start_hour=start_hour,
        hours_range=list(range(start_hour, start_hour + 16)),  # 16-hour range
        year=year,
        month=month,
        day=day,
        prev_day=prev_week_start.day,
        prev_month=prev_week_start.month,
        prev_year=prev_week_start.year,
        next_day=next_week_start.day,
        next_month=next_week_start.month,
        next_year=next_week_start.year,
        today = datetime.today()
    );

def save_slots(storage: SchedulerStorage) -> Response:
    data = request.json.get('slots', []);
    date = request.json.get('date', []);
    
    try:
        conn = storage.get_db_connection();
        cursor = conn.cursor();

        # Determine the week start from the first slot
        date = datetime(date[0], date[1], date[2]);
        week_start = get_week_start(date);
        week_end = week_start + timedelta(days=7);

        # Delete existing slots for the week
        cursor.execute("""
            DELETE FROM slots
            WHERE start >= ? AND start < ?
        """, (week_start, week_end));

        # Insert new slots
        if data:
            for slot in data:
                start = datetime(slot['slot_year'], slot['slot_month'], slot['slot_day'], int(slot['start'] / 60), int(slot['start']) % 60);
                end = start + timedelta(minutes=slot['duration']);
                cursor.execute("""
                    INSERT INTO slots (start, end, time_used, priority)
                    VALUES (?, ?, 0, ?)
                """, (start, end, slot['priority']));

        conn.commit();
        return jsonify({'message': 'Slots saved successfully'});

    except Exception as e:
        return jsonify({'message': str(e)}), 500;

    finally:
        conn.close();

def get_slots(storage: SchedulerStorage) -> Response:
    year = int(request.args.get('year'));
    month = int(request.args.get('month'));
    day = int(request.args.get('day'));

    date = datetime(year, month, day);
    week_start = get_week_start(date);
    week_end = week_start + timedelta(days=7);

    try:
        conn = storage.get_db_connection();
        cursor = conn.cursor();
        cursor.execute("""
            SELECT start, end, priority FROM slots
            WHERE start >= ? AND start < ?
        """, (week_start, week_end));

        slots = [];
        
        for row in cursor.fetchall():
            start_time = datetime.fromisoformat(row['start']);
            end_time = datetime.fromisoformat(row['end']);
            start = start_time.hour * 60 + start_time.minute - def_start_hour * 60;
            end = end_time.hour * 60 + end_time.minute - def_start_hour * 60;
            slots.append({
                'start': start,
                'duration': end - start,
                'day': start_time.day,
                'priority': row['priority']
            });


        return jsonify({'slots': slots});

    except Exception as e:
        return jsonify({'error': str(e)}), 500;

    finally:
        conn.close();

# == MONTH == #                         MARK: Month
def month_view(storage: SchedulerStorage) -> str:
    year = int(request.args.get('year', datetime.now().year));
    month = int(request.args.get('month', datetime.now().month));

    try:
        conn = storage.get_db_connection();
        cursor = conn.cursor();

        # Fetch events that are scheduled in the selected month and are scheduled
        cursor.execute("""
            SELECT start, priority, completed
            FROM events 
            WHERE strftime('%Y', start) = ? 
            AND strftime('%m', start) = ? 
            AND start is not NULL
        """, (str(year), str(month).zfill(2)));

        events = cursor.fetchall();
        num_per_priority = {};

        for event in events:
            day = datetime.fromisoformat(event['start']).day;
            if day not in num_per_priority:
                num_per_priority[day] = [0,0,0,0,0,0];
            
            if event['completed'] == 0:
                num_per_priority[day][event['priority']-1] += 1;
            else:
                num_per_priority[day][5] += 1;
                
        start_weekday = datetime(year, month, 1).weekday()+1;

        return render_template(
            'calendar/month_view.html',
            year=year,
            month=month,
            month_name=month_abbr[month],
            start_weekday=start_weekday if start_weekday < 7 else 0,
            num_days=monthrange(year, month)[1],
            prev_month=(month - 1) if month > 1 else 12,
            prev_year=year if month > 1 else year - 1,
            next_month=(month + 1) if month < 12 else 1,
            next_year=year if month < 12 else year + 1,
            num_per_priority=num_per_priority,
            today = datetime.today()
        );
        
    finally:
        conn.close();

def events_on_day(storage: SchedulerStorage) -> Response:
    year = int(request.args.get('year', datetime.now().year));
    month = int(request.args.get('month', datetime.now().month));
    day = int(request.args.get('day', datetime.now().day));
    
    try:
        conn = storage.get_db_connection();
        cursor = conn.cursor();
        
        cursor.execute("""
            SELECT * FROM events
            WHERE strftime('%Y', start) = ? 
            AND strftime('%m', start) = ? 
            AND strftime('%d', start) = ? 
            AND start is not NULL
            ORDER BY start ASC, priority DESC
        """, (str(year), str(month).zfill(2), str(day).zfill(2))),
        
        events = [dict(row) for row in cursor.fetchall()];
        
        for event in events:
            event['start'] = datetime.fromisoformat(event['start']).strftime('%I:%M %p');
            event['end'] = datetime.fromisoformat(event['end']).strftime('%I:%M %p');
        
        return jsonify(events);
    
    finally:
        conn.close();


# == YEAR == #                          MARK: Year
def year_view() -> str:
    year = int(request.args.get('year', datetime.now().year));

    return render_template(
        'calendar/year_view.html',
        year=year,
        month_names=[month_abbr[m] for m in range(1, 13)],
        today = datetime.today()
    );

# == YEARS == #                         MARK: Years
def years_view() -> str:
    current_year = int(request.args.get('year', datetime.now().year));

    return render_template(
        'calendar/years_view.html',
        start_year=datetime.now().year,
        end_year=current_year + 5,
        today = datetime.today()
    );

# ================ #
# HELPER FUNCTIONS #                    MARK: Helper
# ================ #    

def get_week_start(date: datetime) -> datetime:
    weekday = date.weekday();
    weekday = 0 if weekday == 6 else weekday + 1;
    
    return date - timedelta(days=weekday);