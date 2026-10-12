from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO, emit
import os
import threading
import time
import random
import json
from datetime import datetime
# Add to main.py
import paho.mqtt.client as mqtt

# MQTT client setup
mqtt_client = mqtt.Client()

def on_mqtt_message(client, userdata, message):
    try:
        data = json.loads(message.payload.decode())
        socketio.emit('update_data', data)
        print(f"Forwarded MQTT data to WebSocket: {data}")
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def setup_mqtt_client():
    mqtt_client.on_message = on_mqtt_message
    mqtt_client.connect("127.0.0.1", 1883, 60)
    mqtt_client.subscribe("dashboard/data")
    mqtt_client.loop_start()

# Call this before starting Flask
setup_mqtt_client()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Keep the dashboard local to this computer.
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000
SERVER_URL = f"http://localhost:{SERVER_PORT}"

# Path to your HTML file
HTML_FILE_PATH = r"indexlocal.html"

# Global variables for simulation
is_running = False
simulation_thread = None

def read_html_file():
    """Read the HTML file and return its content"""
    try:
        with open(HTML_FILE_PATH, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return f"""
        <html>
        <body>
            <h1>Error: HTML file not found</h1>
            <p>Could not find file at: {HTML_FILE_PATH}</p>
            <p>Please check the file path and make sure the file exists.</p>
        </body>
        </html>
        """

@app.route('/')
def dashboard():
    """Serve the dashboard HTML page"""
    html_content = read_html_file()
    return render_template_string(html_content)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid if "request" in globals() else "Unknown"}')
    emit('connected', {'data': 'Connected to Flask-SocketIO server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

def generate_sample_data():
    """Generate sample data for testing"""
    # Simulate realistic data
    base_temp = 35 + random.uniform(-5, 15)  # Temperature between 30-50°C
    
    # Simulate GPS coordinates (example: around Ho Chi Minh City)
    base_lat = 10.731976073258629
    base_lng = 106.69932603584631
    lat_offset = random.uniform(-0.01, 0.01)  # Small movement
    lng_offset = random.uniform(-0.01, 0.01)
    
    # Storage usage simulation
    base_usage = random.uniform(20, 80)  # 20-80% usage
    total_gb = 500
    used_gb = (base_usage / 100) * total_gb
    free_gb = total_gb - used_gb
    
    # People counter simulation
    down_up = random.randint(0, 50)  # People IN
    up_down = random.randint(0, 50)   # People OUT
    
    # Speed simulation
    speed = random.uniform(0, 120)  # 0-120 km/h
    
    return {
        'down_up_count': down_up,
        'up_down_count': up_down,
        'usage_percent': base_usage,
        'used_gb': used_gb,
        'free_gb': free_gb,
        'total_gb': total_gb,
        'temperature': round(base_temp, 1),
        'latitude': base_lat + lat_offset,
        'longitude': base_lng + lng_offset,
        'speed': round(speed, 1),
        'timestamp': datetime.now().isoformat()
    }

def data_simulation_worker():
    """Background thread to send sample data periodically"""
    global is_running
    
    while is_running:
        try:
            sample_data = generate_sample_data()
            socketio.emit('update_data', sample_data)
            print(f"Sent data: People IN:{sample_data['down_up_count']}, OUT:{sample_data['up_down_count']}, "
                  f"Temp:{sample_data['temperature']}°C, Speed:{sample_data['speed']}km/h")
            time.sleep(2)  # Send updates every 2 seconds
        except Exception as e:
            print(f"Error in simulation worker: {e}")
            time.sleep(1)

@app.route('/start_simulation')
def start_simulation():
    """Start the data simulation"""
    global is_running, simulation_thread
    
    if not is_running:
        is_running = True
        simulation_thread = threading.Thread(target=data_simulation_worker, daemon=True)
        simulation_thread.start()
        return jsonify({'status': 'started', 'message': 'Data simulation started'})
    else:
        return jsonify({'status': 'already_running', 'message': 'Simulation is already running'})

@app.route('/stop_simulation')
def stop_simulation():
    """Stop the data simulation"""
    global is_running
    
    is_running = False
    return jsonify({'status': 'stopped', 'message': 'Data simulation stopped'})

@app.route('/send_data', methods=['POST'])
def send_custom_data():
    """Endpoint to send custom data to the dashboard"""
    try:
        from flask import request
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['down_up_count', 'up_down_count', 'usage_percent', 
                         'used_gb', 'free_gb', 'total_gb', 'temperature', 'speed']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Optional fields
        if 'latitude' not in data:
            data['latitude'] = 10.731976073258629
        if 'longitude' not in data:
            data['longitude'] = 106.69932603584631
        
        socketio.emit('update_data', data)
        return jsonify({'status': 'success', 'message': 'Data sent to dashboard'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def get_status():
    """Get server status"""
    return jsonify({
        'status': 'running',
        'simulation_active': is_running,
        'html_file_path': HTML_FILE_PATH,
        'html_file_exists': os.path.exists(HTML_FILE_PATH),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 INTEL MONITOR DASHBOARD SERVER")
    print("=" * 60)
    print(f"📁 HTML File: {HTML_FILE_PATH}")
    print(f"📊 Dashboard URL: {SERVER_URL}")
    print("🔧 Control URLs:")
    print(f"   • Start Simulation: {SERVER_URL}/start_simulation")
    print(f"   • Stop Simulation: {SERVER_URL}/stop_simulation")
    print(f"   • Server Status: {SERVER_URL}/api/status")
    print("=" * 60)
    
    # Check if HTML file exists
    if os.path.exists(HTML_FILE_PATH):
        print("✅ HTML file found successfully!")
    else:
        print("❌ WARNING: HTML file not found at specified path!")
        print("   Please check the file path and ensure the file exists.")
    
    print("\n🌐 Starting Flask-SocketIO server...")
    print("   Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start the server
        socketio.run(app, 
                    host=SERVER_HOST,
                    port=SERVER_PORT,
                    debug=True, 
                    use_reloader=False)  # Disable reloader to prevent thread issues
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        is_running = False
    except Exception as e:
        print(f"❌ Error starting server: {e}")