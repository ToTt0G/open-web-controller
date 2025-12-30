"""
OpenController - Virtual Xbox Controller Server

A Flask-SocketIO application that serves a web-based virtual Xbox controller
and translates button presses to virtual gamepad inputs.
"""

from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO
import vgamepad as vg
import os
import ssl
import socket

# Initialize the Virtual Xbox 360 Controller
gamepad = vg.VX360Gamepad()

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
    import ipaddress
    
    local_ip = get_local_ip()
    
    print("=" * 50)
    print("  OpenController - Virtual Xbox Controller")
    print("=" * 50)
    print("\n  Generating SSL certificate...")
    
    use_ssl = generate_self_signed_cert()
    
    if use_ssl:
        protocol = "https"
        print(f"\n  🔒 HTTPS enabled (self-signed certificate)")
        print(f"\n  ⚠️  First time: Accept the security warning on your phone")
    else:
        protocol = "http"
    
    print(f"\n  Server running at: {protocol}://0.0.0.0:5000")
    print(f"  Access from phone: {protocol}://{local_ip}:5000")
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

