from flask import Flask, render_template, request
from flaskwebgui import FlaskUI

from database import SchedulerStorage
from model import Scheduler

from datetime import datetime, timedelta
from calendar import monthrange, month_abbr

app = Flask(__name__);
ui = FlaskUI(server="flask", app=app, width=800, height=800);

scheduler = Scheduler();
storage = SchedulerStorage(scheduler);

@app.route('/week_view')
def week_view():
    # Get selected date from query parameters
    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', datetime.now().month))
    day = int(request.args.get('day', datetime.now().day))
    start_hour = int(request.args.get('start_hour', 5))  # Default to 5 AM

    # Find the start of the week (Monday)
    selected_date = datetime(year, month, day)
    start_of_week = selected_date - timedelta(days=selected_date.weekday())

    # Generate week days
    week_days = [(start_of_week + timedelta(days=i)) for i in range(7)]

    return render_template(
        'week_view.html',
        week_days=week_days,
        start_hour=start_hour,
        hours_range=list(range(start_hour, start_hour + 16))  # 16-hour range
    )
    
@app.route('/save_slots', methods=['POST'])
def save_slots():
    pass

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
        start_weekday=datetime(year, month, 1).weekday(),
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

if __name__ == "__main__":
    ui.run();