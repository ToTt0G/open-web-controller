# 🎮 Open Web Controller

A web-based virtual Xbox 360 controller that runs on your PC and can be accessed from any device with a browser. Turn your phone into a gamepad!

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

## ✨ Features

- **🎯 Full Xbox Controls** - ABXY buttons in authentic Xbox diamond layout
- **🕹️ Dual Input Modes** - Switch between D-pad and floating analog thumbstick
- **👆 Multi-Touch Support** - Press multiple buttons simultaneously
- **🌐 PWA Ready** - Install as a standalone app on iOS & Android
- **🔒 HTTPS Support** - Auto-generated self-signed SSL certificates
- **🔌 Real-time Input** - Low-latency WebSocket connection via Socket.IO
- **📶 Connection Status** - Visual indicator shows connection state
- **📳 Haptic Feedback** - Vibration on button presses (mobile)
- **⚙️ Settings Menu** - Customize thumbstick/D-pad, haptics, and more
- **🛡️ Safe Shutdown** - Graceful cleanup of virtual controller on exit

## 🎯 Controls

| Control | Xbox Input |
|---------|------------|
| D-Pad ▲▼◀▶ | D-Pad directions |
| Thumbstick | Left analog stick |
| A (green) | A button |
| B (red) | B button |
| X (blue) | X button |
| Y (yellow) | Y button |

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
1. Find your PC's local IP (shown in the terminal, or run `ipconfig`)
2. Open `https://<your-ip>:5000` on your phone
3. Accept the self-signed certificate warning
4. Tap ⚙️ to access settings
5. **Add to home screen** for the best fullscreen experience!

## 📱 Install as App (PWA)

For the best experience, install the controller as a Progressive Web App:

**Android (Chrome):**
1. Open the controller URL in Chrome
2. Tap the menu (⋮) → "Add to Home Screen"
3. Launch from your home screen for fullscreen mode

**iOS (Safari):**
1. Open the controller URL in Safari
2. Tap the Share button → "Add to Home Screen"
3. Launch from your home screen

## 📁 Project Structure

```
open-web-controller/
├── app.py                  # Flask server & gamepad logic
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Controller HTML
├── static/
│   ├── css/style.css       # Controller styling
│   ├── js/controller.js    # Client-side logic
│   ├── icons/              # PWA icons
│   ├── manifest.json       # PWA manifest
│   └── sw.js               # Service worker for PWA
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

## 🔧 Configuration

The server automatically:
- Detects your local IP address
- Generates SSL certificates on first run (stored in `certs/`)
- Runs on port `5000` by default

## 🛑 Shutting Down

The server handles shutdown gracefully:
- Press `Ctrl+C` to stop the server
- Virtual controller is automatically disconnected
- All resources are cleaned up properly

## 🤝 Contributing

Contributions are welcome! Some ideas for improvements:

- [ ] Add Start/Select/Menu buttons
- [ ] Add shoulder buttons (LB, RB, LT, RT)
- [ ] Right thumbstick support
- [ ] Customizable button layout
- [ ] Multiple controller profiles
- [ ] Button mapping configuration

## 📄 License

MIT License - feel free to use this project however you'd like!

---

Made with ❤️ for couch gaming
