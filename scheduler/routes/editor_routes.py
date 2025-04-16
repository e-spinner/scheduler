from flask import Flask, render_template, request, jsonify, Response

from database import SchedulerStorage

from datetime import datetime

# ============ #
# EVENT EDITOR #
# ============ #

def event_editor(storage: SchedulerStorage) -> str:
    
    try:
        conn = storage.get_db_connection();
        cursor = conn.cursor();

        today = datetime.now().strftime('%Y-%m-%d');
        cursor.execute("""SELECT * FROM events 
                          WHERE completed = 0 
                          AND due_date >= ? 
                          AND start >= ? 
                          ORDER BY start ASC, due_date ASC""", (today, today));
        scheduled = [dict(row) for row in cursor.fetchall()];
        
        cursor.execute("""SELECT * FROM events 
                          WHERE completed = 0 
                          AND due_date >= ? 
                          AND start is NULL 
                          ORDER BY priority DESC, due_date ASC""", (today,));
        unscheduled = [dict(row) for row in cursor.fetchall()];
        
        cursor.execute("""SELECT * FROM events 
                          WHERE completed = 1 
                          ORDER BY priority DESC, due_date ASC""");
        completed = [dict(row) for row in cursor.fetchall()];
        
        for row in scheduled:
            due_date = datetime.fromisoformat(row['due_date']);
            row['due_date'] = f'{str(due_date.month).zfill(2)}/{due_date.day} @ {due_date.hour}:{str(due_date.minute).zfill(2)}';
            
            start = datetime.fromisoformat(row['start']);
            end = datetime.fromisoformat(row['end']);
            
            time = f'{start.month}/{start.day}, {start.hour}:{str(start.minute).zfill(2)} - {end.hour}:{str(end.minute).zfill(2)}';
            row['start'] = time;
                
        for row in unscheduled:
            due_date = datetime.fromisoformat(row['due_date']);
            row['due_date'] = f'{str(due_date.month).zfill(2)}/{due_date.day} @ {due_date.hour}:{str(due_date.minute).zfill(2)}';

        for row in completed:
            due_date = datetime.fromisoformat(row['due_date']);
            row['due_date'] = f'{str(due_date.month).zfill(2)}/{due_date.day} @ {due_date.hour}:{str(due_date.minute).zfill(2)}';
                
        return render_template(
            'event_editor.html', 
            scheduled=scheduled,
            unscheduled=unscheduled,
            completed=completed,
            today = datetime.today()
            );
    except Exception as e:
        return jsonify({'error': str(e)}), 500;
    finally:
        conn.close();
        
def get_event(event_id: int, storage: SchedulerStorage) -> Response:
    try:
        conn = storage.get_db_connection();
        cursor = conn.cursor();

        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,));
        event = cursor.fetchone();

        if event:
            return jsonify(dict(event));
        else:
            return jsonify({'error': 'Event not found'}), 404;
    except Exception as e:
        return jsonify({'error': str(e)}), 500;
    finally:
        conn.close();
        
def add_event(storage: SchedulerStorage) -> Response:
    data = request.json;
    try:
        conn = storage.get_db_connection();
        cursor = conn.cursor();

        cursor.execute("""
            INSERT INTO events (name, due_date, min_time, max_time, priority)
            VALUES (?, ?, ?, ?, ?)
        """, (data['name'], data['due_date'], data['min_time'], data['max_time'], data['priority']));

        conn.commit();
        return jsonify({'message': 'Event added successfully'});
    except Exception as e:
        return jsonify({'error': str(e)}), 500;
    finally:
        conn.close();
        
def update_event(event_id: int, storage: SchedulerStorage) -> Response:
    data = request.json;
    try:
        conn = storage.get_db_connection();
        cursor = conn.cursor();

        cursor.execute("""
            UPDATE events
            SET name = ?, due_date = ?, min_time = ?, max_time = ?, priority = ?
            WHERE id = ?
        """, (data['name'], data['due_date'], data['min_time'], data['max_time'], data['priority'], event_id));

        conn.commit();
        return jsonify({'message': 'Event updated successfully'});
    except Exception as e:
        return jsonify({'error': str(e)}), 500;
    finally:
        conn.close();
        
def delete_event(event_id: int, storage: SchedulerStorage) -> Response:
    try:
        conn = storage.get_db_connection();
        cursor = conn.cursor();

        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,));
        conn.commit();

        return jsonify({'message': 'Event deleted successfully'});
    except Exception as e:
        return jsonify({'error': str(e)}), 500;
    finally:
        conn.close();
        
def set_done(event_id: int, done: int, storage: SchedulerStorage) -> Response:
    try:
        conn = storage.get_db_connection();
        cursor = conn.cursor();

        cursor.execute("""
            UPDATE events
            SET completed = ?
            WHERE id = ?
        """, (done, event_id,));
        conn.commit();

        return jsonify({'success': True});
    except Exception as e:
        return jsonify({'error': str(e)});
    finally:
        conn.close();
