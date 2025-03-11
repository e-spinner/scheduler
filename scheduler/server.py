from flask import Flask, render_template, request
from flaskwebgui import FlaskUI

from database import SchedulerStorage
from model import Scheduler

from datetime import datetime
from calendar import monthrange

app = Flask(__name__);
ui = FlaskUI(server="flask", app=app, width=800, height=800);

scheduler = Scheduler();
storage = SchedulerStorage(scheduler);

@app.route('/')
def month_view():
    # Get selected month and year from query parameters (defaults to current date)
    year = int(request.args.get('year', datetime.now().year));
    month = int(request.args.get('month', datetime.now().month));

    return render_template(
        'month_view.html',
        year=year,
        month=month,
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
    # Define the range of years (e.g., 5 years back and 5 years forward)
    current_year = int(request.args.get('year', datetime.now().year));

    return render_template(
        'year_view.html',
        start_year=datetime.now().year,
        end_year=current_year + 5
    );

if __name__ == "__main__":
    ui.run();