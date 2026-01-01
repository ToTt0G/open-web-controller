"""
OpenController - Virtual Xbox Controller Server

A Flask-SocketIO application that serves a web-based virtual Xbox controller
and translates button presses to virtual gamepad inputs.
"""

from flask import Flask, render_template, jsonify, send_from_directory, request, send_file
from io import BytesIO
from flask_socketio import SocketIO
import vgamepad as vg
import os
import ssl
import socket
import signal
import sys
import atexit

# Lazy initialization for gamepad (handles ViGEmBus connection issues)
# Multi-controller support: up to 4 virtual gamepads
gamepads = {}  # {controller_num: VX360Gamepad} for controller 1-4
client_assignments = {}  # {session_id: controller_num}
server_running = True
connected_clients = set()  # Track connected controller clients


def get_or_create_gamepad(controller_num):
    """Get or create the virtual gamepad for a specific controller slot (1-4)."""
    global gamepads
    
    if controller_num < 1 or controller_num > 4:
        return None
    
    if controller_num not in gamepads:
        try:
            gamepads[controller_num] = vg.VX360Gamepad()
            print(f"  ✓ Virtual Xbox 360 controller {controller_num} connected")
        except Exception as e:
            print(f"  ✗ Could not connect controller {controller_num} to ViGEmBus: {e}")
            print("    Try: Restart the ViGEmBus service or reboot your PC")
            return None
    
    return gamepads[controller_num]


def disconnect_gamepad(controller_num):
    """Disconnect a specific virtual gamepad if it exists."""
    global gamepads
    
    if controller_num in gamepads:
        try:
            gamepads[controller_num].reset()
            gamepads[controller_num].update()
            del gamepads[controller_num]
            print(f"  ✓ Virtual controller {controller_num} disconnected")
        except Exception as e:
            print(f"  ✗ Error disconnecting controller {controller_num}: {e}")


def get_clients_for_controller(controller_num):
    """Get all client session IDs using a specific controller."""
    return [sid for sid, num in client_assignments.items() if num == controller_num]


def cleanup_unused_controllers():
    """Disconnect controllers that have no clients assigned."""
    for num in list(gamepads.keys()):
        if not get_clients_for_controller(num):
            disconnect_gamepad(num)


def cleanup_gamepad():
    """Safely cleanup and disconnect all virtual gamepads."""
    global gamepads
    if gamepads:
        for num in list(gamepads.keys()):
            try:
                gamepads[num].reset()
                gamepads[num].update()
            except Exception as e:
                print(f"\n  ✗ Error during controller {num} cleanup: {e}")
        gamepads.clear()
        print("\n  ✓ All virtual controllers disconnected safely")


def shutdown_server():
    """Gracefully shutdown the server and cleanup resources."""
    global server_running
    if not server_running:
        return  # Prevent double shutdown
    
    server_running = False
    print("\n  Shutting down server...")
    cleanup_gamepad()
    print("  ✓ Server shutdown complete")


def signal_handler(sig, frame):
    """Handle shutdown signals (Ctrl+C, SIGTERM)."""
    print(f"\n  Received shutdown signal ({signal.Signals(sig).name})")
    shutdown_server()
    sys.exit(0)


# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

# Register cleanup on normal exit
atexit.register(cleanup_gamepad)

# Flask app configuration
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# SSL certificate paths
CERT_DIR = os.path.join(os.path.dirname(__file__), 'certs')
CERT_FILE = os.path.join(CERT_DIR, 'cert.pem')
KEY_FILE = os.path.join(CERT_DIR, 'key.pem')

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
    'start': vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
    'back': vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
    'guide': vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE,
}


def get_local_ip():
    """Get the local IP address of this machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


def generate_self_signed_cert():
    """Generate a self-signed SSL certificate if it doesn't exist."""
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        return True
    
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime
        
        # Create certs directory
        os.makedirs(CERT_DIR, exist_ok=True)
        
        # Generate private key
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Get local IP for certificate
        local_ip = get_local_ip()
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "OpenController"),
            x509.NameAttribute(NameOID.COMMON_NAME, "OpenController"),
        ])
        
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.DNSName(local_ip),
                    x509.IPAddress(ipaddress.IPv4Address(local_ip)),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]),
                critical=False,
            )
            .sign(key, hashes.SHA256(), default_backend())
        )
        
        # Write key file
        with open(KEY_FILE, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Write cert file
        with open(CERT_FILE, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        print(f"  ✓ SSL certificate generated for {local_ip}")
        return True
        
    except ImportError:
        print("  ✗ 'cryptography' package not installed.")
        print("    Install with: pip install cryptography")
        print("    Falling back to HTTP (PWA won't work as standalone app)")
        return False
    except Exception as e:
        print(f"  ✗ Failed to generate certificate: {e}")
        return False


def get_mkcert_ca_path():
    """Find mkcert's root CA certificate path."""
    import subprocess
    try:
        result = subprocess.run(['mkcert', '-CAROOT'], capture_output=True, text=True)
        if result.returncode == 0:
            ca_dir = result.stdout.strip()
            ca_path = os.path.join(ca_dir, 'rootCA.pem')
            if os.path.exists(ca_path):
                return ca_path
    except FileNotFoundError:
        pass  # mkcert not installed
    return None


# ============================================
# Routes
# ============================================

@app.route('/')
def index():
    """Serve the main controller interface."""
    return render_template('index.html')


@app.route('/manifest.json')
def manifest():
    """Serve the PWA manifest from static folder."""
    return send_from_directory('static', 'manifest.json', mimetype='application/json')


@app.route('/sw.js')
def service_worker():
    """Serve service worker from root path for proper scope."""
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')


@app.route('/status')
def status():
    """Return server status and controller state."""
    return jsonify({
        'running': server_running,
        'controller_connected': gamepad is not None
    })


@app.route('/offline')
def offline():
    """Serve the offline fallback page for PWA."""
    return render_template('offline.html')


@app.route('/shutdown', methods=['POST'])
def shutdown():
    """
    Safely shutdown the server via HTTP request.
    Only allows requests from localhost for security.
    """
    # Security: Only allow shutdown from localhost
    if request.remote_addr not in ['127.0.0.1', '::1', 'localhost']:
        return jsonify({'error': 'Shutdown only allowed from localhost'}), 403
    
    # Trigger shutdown
    shutdown_server()
    
    # Schedule the actual server stop
    def stop_server():
        import time
        time.sleep(0.5)  # Give time for response to be sent
        os._exit(0)
    
    import threading
    threading.Thread(target=stop_server, daemon=True).start()
    
    return jsonify({'message': 'Server shutting down...'})


# ============================================
# Lobby Routes (Kahoot-style dashboard)
# ============================================

@app.route('/lobby')
def lobby():
    """Serve the lobby dashboard for big screen display."""
    local_ip = get_local_ip()
    protocol = "https" if os.path.exists(CERT_FILE) else "http"
    server_url = f"{protocol}://{local_ip}:5000"
    mkcert_available = get_mkcert_ca_path() is not None
    
    return render_template('lobby.html',
        server_url=server_url,
        local_ip=local_ip,
        mkcert_available=mkcert_available,
        client_count=len(connected_clients)
    )


@app.route('/lobby/qr-join.png')
def lobby_qr_join():
    """Generate QR code for controller URL."""
    import qrcode
    
    local_ip = get_local_ip()
    protocol = "https" if os.path.exists(CERT_FILE) else "http"
    url = f"{protocol}://{local_ip}:5000"
    
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)
    
    return send_file(buffer, mimetype='image/png')


@app.route('/lobby/qr-cert.png')
def lobby_qr_cert():
    """Generate QR code for certificate setup page."""
    import qrcode
    
    local_ip = get_local_ip()
    protocol = "https" if os.path.exists(CERT_FILE) else "http"
    url = f"{protocol}://{local_ip}:5000/setup"
    
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)
    
    return send_file(buffer, mimetype='image/png')


@app.route('/setup')
def setup():
    """Serve certificate setup page with download and instructions."""
    local_ip = get_local_ip()
    protocol = "https" if os.path.exists(CERT_FILE) else "http"
    server_url = f"{protocol}://{local_ip}:5000"
    mkcert_available = get_mkcert_ca_path() is not None
    
    return render_template('setup.html',
        server_url=server_url,
        mkcert_available=mkcert_available
    )


@app.route('/setup/ca.pem')
def setup_ca():
    """Download mkcert root CA certificate."""
    ca_path = get_mkcert_ca_path()
    if ca_path:
        return send_file(ca_path, as_attachment=True, download_name='rootCA.pem')
    return jsonify({'error': 'mkcert not installed or CA not found'}), 404


# ============================================
# Socket.IO Event Handlers
# ============================================

def broadcast_controller_status():
    """Broadcast which controllers are currently in use."""
    status = {
        num: len(get_clients_for_controller(num)) 
        for num in range(1, 5)
    }
    socketio.emit('controller_status', status)


def get_next_available_controller():
    """Find the next available controller slot (1-4), preferring empty slots."""
    for num in range(1, 5):
        if not get_clients_for_controller(num):
            return num
    # All slots have at least one client, return slot 1 as default
    return 1


@socketio.on('connect')
def handle_connect():
    """Track client connections and auto-assign to next available controller."""
    sid = request.sid
    connected_clients.add(sid)
    socketio.emit('client_count', len(connected_clients))
    
    # Auto-assign to next available controller slot
    next_controller = get_next_available_controller()
    client_assignments[sid] = next_controller
    
    # Create the gamepad for this controller if it doesn't exist
    gp = get_or_create_gamepad(next_controller)
    success = gp is not None
    
    # Notify client of their auto-assigned controller
    socketio.emit('controller_assigned', {
        'controller': next_controller,
        'success': success,
        'auto_assigned': True
    }, to=sid)
    
    # Broadcast updated controller status to all clients
    broadcast_controller_status()
    
    if success:
        print(f"  Client {sid[:8]}... auto-assigned to controller {next_controller}")


@socketio.on('disconnect')
def handle_disconnect():
    """Track client disconnections and cleanup controller assignments."""
    connected_clients.discard(request.sid)
    
    # Get the controller this client was using
    old_controller = client_assignments.pop(request.sid, None)
    
    # Cleanup unused controller if no other clients are using it
    if old_controller is not None:
        if not get_clients_for_controller(old_controller):
            disconnect_gamepad(old_controller)
    
    socketio.emit('client_count', len(connected_clients))
    broadcast_controller_status()


@socketio.on('select_controller')
def handle_select_controller(data):
    """Handle client request to select a specific controller (1-4)."""
    sid = request.sid
    controller_num = data.get('controller', 1)
    
    # Validate controller number
    if controller_num < 1 or controller_num > 4:
        controller_num = 1
    
    # Get old assignment
    old_controller = client_assignments.get(sid)
    
    # If already assigned to the requested controller, do nothing
    if old_controller == controller_num:
        socketio.emit('controller_assigned', {
            'controller': controller_num,
            'success': True
        }, to=sid)
        return
    
    # Remove old assignment
    if old_controller is not None:
        del client_assignments[sid]
        # Cleanup old controller if no one else is using it
        if not get_clients_for_controller(old_controller):
            disconnect_gamepad(old_controller)
    
    # Assign new controller
    client_assignments[sid] = controller_num
    
    # Create the gamepad for this controller if it doesn't exist
    gp = get_or_create_gamepad(controller_num)
    success = gp is not None
    
    # Notify client of assignment result
    socketio.emit('controller_assigned', {
        'controller': controller_num,
        'success': success
    }, to=sid)
    
    # Broadcast updated controller status to all clients
    broadcast_controller_status()
    
    if success:
        print(f"  Client {sid[:8]}... assigned to controller {controller_num}")


@socketio.on('input')
def handle_input(data):
    """Handle input from web client (buttons and thumbstick)."""
    sid = request.sid
    
    # Get this client's assigned controller
    controller_num = client_assignments.get(sid)
    if controller_num is None:
        return  # Client hasn't selected a controller yet
    
    # Get the gamepad for this controller
    gp = gamepads.get(controller_num)
    if gp is None:
        return  # Gamepad not available
    
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
            gp.press_button(button=xbox_button)
        else:
            gp.release_button(button=xbox_button)
    
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
        
        gp.left_joystick(x_value=stick_x, y_value=stick_y)
    
    gp.update()


# ============================================
# Entry Point
# ============================================

if __name__ == '__main__':
    import ipaddress
    
    local_ip = get_local_ip()
    
    print("=" * 50)
    print("  OpenController - Virtual Xbox Controller")
    print("=" * 50)
    print("\n  Generating SSL certificate...")
    
    use_ssl = generate_self_signed_cert()
    mkcert_available = get_mkcert_ca_path() is not None
    
    if use_ssl:
        protocol = "https"
        print(f"\n  🔒 HTTPS enabled (self-signed certificate)")
        print(f"\n  ⚠️  First time: Accept the security warning on your phone")
    else:
        protocol = "http"
    
    print(f"\n  ─────────────────────────────────────────────")
    print(f"  📱 Controller:  {protocol}://{local_ip}:5000")
    print(f"  🖥️  Lobby:       {protocol}://{local_ip}:5000/lobby")
    print(f"  ─────────────────────────────────────────────")
    
    if mkcert_available:
        print(f"\n  ✅ mkcert detected - Full PWA support available")
    else:
        print(f"\n  ℹ️  mkcert not found - Install for full PWA support:")
        print(f"      choco install mkcert  OR  scoop install mkcert")
        print(f"      Then run: mkcert -install")
    
    print("\n  Press Ctrl+C to stop\n")
    
    if use_ssl:
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=5000,
            certfile=CERT_FILE,
            keyfile=KEY_FILE
        )
    else:
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=5000
        )

