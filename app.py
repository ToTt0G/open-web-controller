"""
OpenController - Virtual Xbox Controller Server

A Flask-SocketIO application that serves a web-based virtual Xbox controller
and translates button presses to virtual gamepad inputs.
"""

from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO
import vgamepad as vg
import os

# Initialize the Virtual Xbox 360 Controller
gamepad = vg.VX360Gamepad()

# Flask app configuration
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Button mapping dictionary for cleaner input handling
BUTTON_MAP = {
    'a': vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    'b': vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    'x': vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    'y': vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    'up': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
    'down': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
    'left': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
    'right': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
}

# Web App Manifest for PWA
MANIFEST = {
    "name": "OpenController",
    "short_name": "OController",
    "description": "Virtual Xbox Controller for your PC",
    "start_url": "/",
    "display": "fullscreen",
    "orientation": "landscape",
    "background_color": "#1a1a1a",
    "theme_color": "#1a1a1a",
    "icons": [
        {"src": "/static/icons/icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}
    ]
}


# ============================================
# Routes
# ============================================

@app.route('/')
def index():
    """Serve the main controller interface."""
    return render_template('index.html')


@app.route('/manifest.json')
def manifest():
    """Serve the PWA manifest."""
    return jsonify(MANIFEST)


@app.route('/sw.js')
def service_worker():
    """Serve service worker from root path for proper scope."""
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')


# ============================================
# Socket.IO Event Handlers
# ============================================

@socketio.on('input')
def handle_input(data):
    """Handle input from web client (buttons and thumbstick)."""
    input_type = data.get('type', 'button')
    
    if input_type == 'button':
        btn = data.get('button')
        pressed = data.get('pressed', False)
        
        # Look up button in mapping dictionary
        xbox_button = BUTTON_MAP.get(btn)
        if xbox_button is None:
            return  # Unknown button, ignore
        
        # Press or release the mapped button
        if pressed:
            gamepad.press_button(button=xbox_button)
        else:
            gamepad.release_button(button=xbox_button)
    
    elif input_type == 'stick':
        # Handle thumbstick input (-1.0 to 1.0)
        x = data.get('x', 0)
        y = data.get('y', 0)
        
        # Convert to int16 range (-32768 to 32767)
        stick_x = int(x * 32767)
        stick_y = int(-y * 32767)  # Invert Y axis (up is negative in web)
        
        # Clamp values
        stick_x = max(-32768, min(32767, stick_x))
        stick_y = max(-32768, min(32767, stick_y))
        
        gamepad.left_joystick(x_value=stick_x, y_value=stick_y)
    
    gamepad.update()


# ============================================
# Entry Point
# ============================================

if __name__ == '__main__':
    print("=" * 50)
    print("  OpenController - Virtual Xbox Controller")
    print("=" * 50)
    print(f"\n  Server running at: http://0.0.0.0:5000")
    print(f"  Access from phone: http://<your-pc-ip>:5000")
    print("\n  Press Ctrl+C to stop\n")
    socketio.run(app, host='0.0.0.0', port=5000)
