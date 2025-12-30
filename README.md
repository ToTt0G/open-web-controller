# 🎮 Open Web Controller

A web-based virtual Xbox 360 controller that runs on your PC and can be accessed from any device with a browser. Turn your phone into a gamepad!

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

## ✨ Features

- **🌐 Web-Based** - No app installation needed, works in any modern browser
- **📱 PWA Support** - Install as an app on your phone for a native experience
- **🔌 Real-time** - Low-latency WebSocket connection for responsive controls
- **📶 Connection Status** - Visual indicator shows connection state
- **📳 Haptic Feedback** - Vibration feedback on button presses (on supported devices)
- **🔄 Landscape Lock** - Optimized for landscape orientation with rotation prompt

## 🎯 Controls

| Control | Xbox Button |
|---------|-------------|
| D-Pad ▲▼◀▶ | D-Pad directions |
| A Button | A |
| X Button | X |

## 📋 Requirements

- **Windows** (uses ViGEmBus for virtual controller)
- **Python 3.8+**
- **[ViGEmBus Driver](https://github.com/ViGEm/ViGEmBus/releases)** - Required for virtual gamepad

## 🚀 Installation

1. **Install ViGEmBus Driver**
   - Download from [ViGEmBus Releases](https://github.com/ViGEm/ViGEmBus/releases)
   - Run the installer and restart if prompted

2. **Clone the repository**
   ```bash
   git clone https://github.com/ToTt0G/open-web-controller.git
   cd open-web-controller
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**
   ```bash
   python app.py
   ```

5. **Connect from your phone**
   - Find your PC's local IP (run `ipconfig` in terminal)
   - Open `http://<your-ip>:5000` on your phone
   - Add to home screen for the best experience!

## 📁 Project Structure

```
open-web-controller/
├── app.py                  # Flask server & gamepad logic
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Controller HTML
└── static/
    ├── css/style.css       # Controller styling
    ├── js/controller.js    # Client-side logic
    ├── icons/icon.svg      # PWA icon
    └── sw.js               # Service worker for PWA
```

## 🛠️ Tech Stack

- **Backend**: Flask + Flask-SocketIO
- **Frontend**: Vanilla HTML/CSS/JS
- **Virtual Gamepad**: vgamepad (ViGEmBus wrapper)
- **Real-time**: Socket.IO

## 🤝 Contributing

Contributions are welcome! Some ideas for improvements:

- [ ] Add more buttons (Y, B, Start, Select, triggers)
- [ ] Add analog joystick support
- [ ] Customizable button layout
- [ ] Multiple controller profiles
- [ ] Button mapping configuration

## 📄 License

MIT License - feel free to use this project however you'd like!

---

Made with ❤️ for couch gaming
