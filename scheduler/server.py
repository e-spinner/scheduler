from flask import Flask, render_template, request, jsonify
from flaskwebgui import FlaskUI

import sqlite3
from database import SchedulerStorage
from model import Scheduler

from datetime import datetime, timedelta
from calendar import monthrange, month_abbr

def_start_hour = 5;

app = Flask(__name__);
ui = FlaskUI(server="flask", app=app, width=800, height=800);

scheduler = Scheduler();
storage = SchedulerStorage(scheduler);

@app.route('/week_view')
def week_view():
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
        'week_view.html',
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
        next_year=next_week_start.year
    )
    
@app.route('/')
def month_view():
    year = int(request.args.get('year', datetime.now().year));
    month = int(request.args.get('month', datetime.now().month));

    return render_template(
        'month_view.html',
        year=year,
        month=month,
        month_name=month_abbr[month],
        events_by_day=storage.get_scheduled_events(year, month),
        start_weekday=datetime(year, month, 1).weekday()+1,
        num_days=monthrange(year, month)[1],
        prev_month=(month - 1) if month > 1 else 12,
        prev_year=year if month > 1 else year - 1,
        next_month=(month + 1) if month < 12 else 1,
        next_year=year if month < 12 else year + 1
    );

@app.route('/year_view')
def year_view():
    year = int(request.args.get('year', datetime.now().year));

    return render_template(
        'year_view.html',
        year=year,
        month_names=[month_abbr[m] for m in range(1, 13)]
    );

@app.route('/years_view')
def years_view():
    current_year = int(request.args.get('year', datetime.now().year));

    return render_template(
        'years_view.html',
        start_year=datetime.now().year,
        end_year=current_year + 5
    );

def get_week_start(date: datetime) -> datetime:
    weekday = date.weekday();
    weekday = 0 if weekday == 6 else weekday + 1;
    
    return date - timedelta(days=weekday);

@app.route('/save_slots', methods=['POST'])
def save_slots():
    data = request.json.get('slots', []);
    date = request.json.get('date', []);

    print(date);
    
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
            print("data found")
            for slot in data:
                start = datetime(slot['slot_year'], slot['slot_month'], slot['slot_day'], int(slot['start'] / 60), int(slot['start']) % 60);
                end = start + timedelta(minutes=slot['duration']);
                cursor.execute("""
                    INSERT INTO slots (start, end, percent_left, priority)
                    VALUES (?, ?, 1.0, ?)
                """, (start, end, 1));

        conn.commit();
        return jsonify({'message': 'Slots saved successfully'});

    except Exception as e:
        return jsonify({'message': str(e)}), 500;

    finally:
        conn.close();

@app.route('/get_slots', methods=['GET'])
def get_slots():
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
            SELECT start, end FROM slots
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
                'day': start_time.day
            });


        return jsonify({'slots': slots});

    except Exception as e:
        return jsonify({'error': str(e)}), 500;

    finally:
        conn.close();


if __name__ == "__main__":
    ui.run();