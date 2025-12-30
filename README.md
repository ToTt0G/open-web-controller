# OpenController

A web-based virtual Xbox controller that runs on your PC and can be accessed from your phone or any device with a browser.

## Project Structure

```
open-web-controller/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Main controller interface
└── static/
    ├── css/
    │   └── style.css       # Controller styling
    ├── js/
    │   └── controller.js   # Client-side logic
    ├── icons/
    │   └── icon.svg        # PWA icon
    └── sw.js               # Service worker for PWA
```

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   python app.py
   ```

3. Open the controller on your phone:
   - Find your PC's IP address
   - Navigate to `http://<your-ip>:5000`
   - Add to home screen for PWA experience

## Requirements

- Windows (for vgamepad virtual controller)
- ViGEmBus driver installed
- Python 3.8+
