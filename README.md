# 🎮 Open Web Controller

A web-based virtual Xbox 360 controller that runs on your PC and can be accessed from any device with a browser. Turn your phone into a gamepad!

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![PWA](https://img.shields.io/badge/PWA-ready-blueviolet)

## ✨ Features

- **🎯 Full Xbox Controls** - ABXY buttons in authentic Xbox diamond layout
- **🕹️ Dual Input Modes** - Switch between D-pad and floating analog thumbstick
- **👆 Multi-Touch Support** - Press multiple buttons simultaneously
- **🌐 PWA Ready** - Install as a standalone app on iOS & Android
- **🔒 HTTPS Support** - Auto-generated SSL certificates (or mkcert for full trust)
- **🔌 Real-time Input** - Low-latency WebSocket connection via Socket.IO
- **📶 Connection Status** - Visual indicator shows connection state
- **📳 Haptic Feedback** - Vibration on button presses (mobile)
- **⚙️ Settings Menu** - Customize thumbstick/D-pad, haptics, and more
- **🛡️ Safe Shutdown** - Graceful cleanup of virtual controller on exit
- **🖥️ Lobby Dashboard** - Kahoot-style screen with QR codes for easy phone setup

### 🆕 PWA Enhancements

- **📱 Custom Install Prompt** - Beautiful "Add to Home Screen" UI
- **📴 Offline Support** - Custom offline page when disconnected
- **🔄 Auto-Updates** - Get notified when a new version is available
- **💡 Wake Lock** - Screen stays on during gameplay (no dimming!)
- **⚡ Instant Load** - Assets cached for lightning-fast startup


## 🎯 Controls

| Control | Xbox Input |
|---------|------------|
| D-Pad ▲▼◀▶ | D-Pad directions |
| Thumbstick | Left analog stick |
| A (green) | A button |
| B (red) | B button |
| X (blue) | X button |
| Y (yellow) | Y button |
| SELECT | Back button |
| START | Start button |
| Guide (center) | Xbox Guide button |


## 📋 Requirements

- **Windows** (uses ViGEmBus for virtual controller)
- **Python 3.8+**
- **[ViGEmBus Driver](https://github.com/ViGEm/ViGEmBus/releases)** - Required for virtual gamepad

## 🚀 Quick Start

### 1. Install ViGEmBus Driver
Download from [ViGEmBus Releases](https://github.com/ViGEm/ViGEmBus/releases) and run the installer.

### 2. Clone & Install
```bash
git clone https://github.com/ToTt0G/open-web-controller.git
cd open-web-controller
pip install -r requirements.txt
```

### 3. Run the Server
```bash
python app.py
```

### 4. Connect from Your Phone
1. Open `https://<your-ip>:5000/lobby` on your PC (display on big screen)
2. Scan the **Join Game** QR code with your phone
3. Accept the self-signed certificate warning (or set up mkcert below)
4. **Add to home screen** for the best fullscreen experience!

## 🖥️ Lobby Dashboard

The lobby (`/lobby`) is designed for display on a TV or monitor:

- **📱 Join Game QR** - Scan to open the controller
- **🔐 Certificate QR** - Scan for mkcert CA setup (optional)
- **👥 Live Counter** - Shows connected controllers in real-time

## 🔐 Full PWA Support (mkcert)

For a true "native app" experience without browser security warnings:

### 1. Install mkcert
```powershell
winget install --id FiloSottile.mkcert
# Restart your terminal after installing
mkcert -install
```

### 2. Generate Trusted Certificates
```powershell
cd certs
# Delete old self-signed certs
Remove-Item cert.pem, key.pem -ErrorAction SilentlyContinue

# Generate new certs (replace IP with yours)
mkcert 192.168.x.x localhost 127.0.0.1

# Rename to expected filenames
Rename-Item "192.168.x.x+2.pem" "cert.pem"
Rename-Item "192.168.x.x+2-key.pem" "key.pem"
cd ..
```

### 3. Install CA on Phone
Scan the **Certificate QR** from the lobby, or manually:

**Android:** Settings → Security → Install certificate → CA certificate  
**iOS:** Settings → General → VPN & Device Mgmt → Install, then enable in Certificate Trust Settings

## 📱 Install as App (PWA)

For the best experience, install the controller as a Progressive Web App:

**Android (Chrome):**
1. Open the controller URL in Chrome
2. Look for the **"Install OpenController"** prompt at the bottom
3. Tap **INSTALL** or use menu (⋮) → "Add to Home Screen"
4. Launch from your home screen for fullscreen mode

**iOS (Safari):**
1. Open the controller URL in Safari
2. Tap the Share button → "Add to Home Screen"
3. Launch from your home screen

> 💡 **Tip:** The app works offline! If you lose connection, you'll see a friendly offline page with a retry button.

## 📁 Project Structure

```
open-web-controller/
├── app.py                  # Flask server & gamepad logic
├── requirements.txt        # Python dependencies
├── templates/
│   ├── index.html          # Controller HTML
│   └── offline.html        # Offline fallback page
├── static/
│   ├── css/style.css       # Controller styling
│   ├── js/controller.js    # Client-side logic
│   ├── images/             # PWA icons
│   ├── manifest.json       # PWA manifest
│   └── sw.js               # Service worker
└── certs/                  # Auto-generated SSL certificates (git-ignored)
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Flask + Flask-SocketIO |
| Frontend | Vanilla HTML/CSS/JS |
| Virtual Gamepad | vgamepad (ViGEmBus wrapper) |
| Real-time | Socket.IO (WebSocket) |
| SSL | Self-signed certificates (auto-generated) |
| PWA | Service Worker + Web App Manifest |

## 🔧 Configuration

The server automatically:
- Detects your local IP address
- Generates SSL certificates on first run (stored in `certs/`)
- Runs on port `5000` by default

### Settings (in-app)
- **Input Mode** - Toggle between floating thumbstick and D-pad
- **Wake Lock** - Prevent screen from sleeping during use

## 🛑 Shutting Down

The server handles shutdown gracefully:
- Press `Ctrl+C` to stop the server
- Virtual controller is automatically disconnected
- All resources are cleaned up properly

## 🤝 Contributing

Contributions are welcome! Some ideas for improvements:

- [x] Add Start/Select/Menu buttons
- [ ] Add shoulder buttons (LB, RB, LT, RT)
- [ ] Right thumbstick support
- [ ] Customizable button layout
- [ ] Multiple controller profiles
- [ ] Button mapping configuration

## 📄 License

MIT License - feel free to use this project however you'd like!

---

Made with ❤️ for couch gaming
