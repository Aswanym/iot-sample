from flask import Flask, render_template, request, jsonify
from datetime import datetime
import psutil
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Dictionary to store the latest data and timestamp from each script
data_sources = {}

# Map of script identifiers to the script file names
script_map = {
    'Room 1': 'sensor.py',
    'Room 2': 'sensor_script2.py',
    'Room 3': 'sensor_script3.py',
    # Add more scripts as needed
}

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    source = data.get('source', 'Unknown')  # Identify the source script by a unique ID
    data_sources[source] = {
        'data': data,
        'last_update': datetime.now(),
        'status': 'Active'  # Mark as active when data is received
    }
    # Emit the updated status and data to all connected clients
    socketio.emit('update', {'source': source, 'status': 'Active', 'data': data})
    return jsonify({'message': 'Data received'}), 200

def check_script_status():
    """Check if the scripts are currently running and update their status."""
    for source, script_name in script_map.items():
        is_running = check_script_status_single(script_name)
        current_status = 'Active' if is_running else 'Stopped'

        # If the status has changed, update and emit the change
        if data_sources.get(source, {}).get('status') != current_status:
            data_sources[source]['status'] = current_status
            # Emit the status update to all connected clients
            socketio.emit('update', {'source': source, 'status': current_status, 'data': data_sources[source].get('data', {})})

def check_script_status_single(script_name):
    """Check if a single script is currently running."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        cmdline = proc.info['cmdline']
        if cmdline and script_name in cmdline:
            return True
    return False

@app.route('/dashboard')
def dashboard():
    # Check all script statuses before rendering the dashboard
    check_script_status()
    return render_template('dashboard.html', data_sources=data_sources)

@socketio.on('connect')
def handle_connect():
    # Send initial data when a new client connects
    for source, details in data_sources.items():
        emit('update', {'source': source, 'status': details['status'], 'data': details['data']})

if __name__ == '__main__':
    # You can use a background thread to periodically check the script statuses
    socketio.start_background_task(check_script_status)
    socketio.run(app, debug=True)
