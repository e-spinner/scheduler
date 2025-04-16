from flask import Flask, render_template, request, jsonify, Response
from flaskwebgui import FlaskUI

from database import SchedulerStorage
from optimize import Scheduler
import routes.cal_routes as cal
import routes.editor_routes as edit

from datetime import datetime

app = Flask(__name__);
ui = FlaskUI(server="flask", app=app, width=1000, height=800);

storage = SchedulerStorage(db_path='./scheduler/database.db');

# ======== #
# CALENDAR #
# ======== #

# == WEEK == #
@app.route('/week_view')
def week_view(): return cal.week_view();
      
@app.route('/save_slots', methods=['POST'])
def save_slots(): return cal.save_slots(storage);

@app.route('/get_slots', methods=['GET'])
def get_slots(): return cal.get_slots(storage);

# == MONTH == #
@app.route('/')
def month_view(): return cal.month_view(storage);

@app.route('/events_on_day')
def events_on_day(): return cal.events_on_day(storage);

# == YEAR == #
@app.route('/year_view')
def year_view(): return cal.year_view();

# == YEARS == #
@app.route('/years_view')
def years_view(): return cal.years_view();

# ======== #
# SETTINGS #
# ======== #

@app.route('/settings')
def settings() -> str:
    return render_template(
        'base.html',
        today = datetime.today()
    );

# ============ #
# EVENT EDITOR #
# ============ #

@app.route('/event_editor')
def event_editor(): return edit.event_editor(storage);

@app.route('/get_event/<int:event_id>')
def get_event(event_id): return edit.get_event(event_id, storage);

@app.route('/add_event', methods=['POST'])
def add_event(): return edit.add_event(storage);

@app.route('/update_event/<int:event_id>', methods=['POST'])
def update_event(event_id): return edit.update_event(event_id, storage);

@app.route('/delete_event/<int:event_id>', methods=['DELETE'])
def delete_event(event_id): return edit.delete_event(event_id, storage);

@app.route('/set_done/<int:event_id>/<int:done>', methods=['POST'])
def set_done(event_id, done): return edit.set_done(event_id, done, storage);

# ================ #
# HELPER FUNCTIONS #
# ================ #

@app.route('/optimize/<method>')
def optimize(method: str):
    
    scheduler = Scheduler(storage);
    
    scheduler.schedule(method);
    scheduler.save_scheduled_events();
    
    print(method)
    
    return jsonify({'success': True});

# =========== #
# DRIVER CODE #
# =========== #

if __name__ == "__main__":
    ui.run();
    