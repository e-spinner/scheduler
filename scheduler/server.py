from flask import Flask, render_template
from flaskwebgui import FlaskUI

from database import SchedulerStorage
from model import Scheduler

from datetime import datetime

app = Flask(__name__);
ui = FlaskUI(server="flask", app=app, width=500, height=500);

scheduler = Scheduler();
storage = SchedulerStorage(scheduler);

@app.route('/')
def month_view():
    # Get scheduled events
    current_year = datetime.now().year;
    current_month = datetime.now().month;
    events = storage.get_scheduled_events(2025, 3);

    return render_template('month_view.html', 
                           year=current_year, 
                           month=current_month, 
                           events=events);

if __name__ == "__main__":
    ui.run();