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
    'x': vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
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
    "theme_color": "#00ff00",
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


# ============================================
# Socket.IO Event Handlers
# ============================================

@socketio.on('input')
def handle_input(data):
    """Handle button input from web client using dictionary-based mapping."""
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
    
    gamepad.update()


# ============================================
# Entry Point
# ============================================

if __name__ == '__main__':
    # '0.0.0.0' allows external connections (your phone)
    print("Starting OpenController server...")
    print("Access the controller at: http://<your-ip>:5000")
    socketio.run(app, host='0.0.0.0', port=5000)
