/**
 * OpenController - Virtual Xbox Controller JavaScript
 * Features: Multi-touch, D-pad/Thumbstick toggle, ABXY buttons
 */

const socket = io();

// ============================================
// Settings Management
// ============================================

const settings = {
    useThumbstick: localStorage.getItem('useThumbstick') === 'true'
};

function saveSettings() {
    localStorage.setItem('useThumbstick', settings.useThumbstick);
}

function applySettings() {
    const dpad = document.getElementById('dpad-container');
    const thumbstick = document.getElementById('thumbstick-container');
    const toggle = document.getElementById('thumbstick-toggle');

    if (settings.useThumbstick) {
        dpad.style.display = 'none';
        thumbstick.classList.add('visible');
        toggle.classList.add('active');
    } else {
        dpad.style.display = 'block';
        thumbstick.classList.remove('visible');
        toggle.classList.remove('active');
    }
}

// ============================================
// Settings Modal
// ============================================

document.getElementById('settings-btn').addEventListener('click', () => {
    document.getElementById('settings-modal').classList.add('open');
});

document.getElementById('close-settings').addEventListener('click', () => {
    document.getElementById('settings-modal').classList.remove('open');
});

document.getElementById('thumbstick-toggle').addEventListener('click', (e) => {
    settings.useThumbstick = !settings.useThumbstick;
    saveSettings();
    applySettings();
});

// Close modal when clicking outside
document.getElementById('settings-modal').addEventListener('click', (e) => {
    if (e.target.id === 'settings-modal') {
        document.getElementById('settings-modal').classList.remove('open');
    }
});

// ============================================
// Connection Status Handlers
// ============================================

const statusEl = document.getElementById('connection-status');
const statusText = statusEl.querySelector('.text');

socket.on('connect', () => {
    statusEl.className = 'connected';
    statusText.textContent = 'Connected';
    setTimeout(() => {
        if (statusEl.classList.contains('connected')) {
            statusEl.style.opacity = '0.3';
        }
    }, 2000);
});

socket.on('disconnect', () => {
    statusEl.className = 'disconnected';
    statusText.textContent = 'Disconnected';
    statusEl.style.opacity = '1';
});

socket.on('connect_error', () => {
    statusEl.className = 'disconnected';
    statusText.textContent = 'Connection Error';
    statusEl.style.opacity = '1';
});

statusEl.addEventListener('mouseenter', () => statusEl.style.opacity = '1');
statusEl.addEventListener('mouseleave', () => {
    if (statusEl.classList.contains('connected')) {
        statusEl.style.opacity = '0.3';
    }
});

// ============================================
// Context Menu Prevention
// ============================================

window.oncontextmenu = (e) => { e.preventDefault(); return false; };

// ============================================
// Multi-touch Button Handling
// ============================================

// Track active touches per button
const activeTouches = new Map();

function setupButtonEvents() {
    const buttons = document.querySelectorAll('.dpad-btn, .action-btn');

    buttons.forEach(btn => {
        const key = btn.getAttribute('data-key');
        if (!key) return;

        // Touch events with multi-touch support
        btn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            // Track all touches on this button
            for (const touch of e.changedTouches) {
                activeTouches.set(touch.identifier, { key, element: btn });
            }
            emit(key, true, btn);
        }, { passive: false });

        btn.addEventListener('touchend', (e) => {
            e.preventDefault();
            for (const touch of e.changedTouches) {
                activeTouches.delete(touch.identifier);
            }
            // Only release if no more touches on this button
            const stillPressed = [...activeTouches.values()].some(t => t.key === key);
            if (!stillPressed) {
                emit(key, false, btn);
            }
        }, { passive: false });

        btn.addEventListener('touchcancel', (e) => {
            e.preventDefault();
            for (const touch of e.changedTouches) {
                activeTouches.delete(touch.identifier);
            }
            emit(key, false, btn);
        }, { passive: false });

        // Mouse events for desktop testing
        btn.addEventListener('mousedown', () => emit(key, true, btn));
        btn.addEventListener('mouseup', () => emit(key, false, btn));
        btn.addEventListener('mouseleave', () => {
            if (btn.classList.contains('active')) {
                emit(key, false, btn);
            }
        });
    });
}

/**
 * Emit button state to server with visual/haptic feedback
 */
function emit(btnKey, pressed, element) {
    if (pressed) {
        element.classList.add('active');
        if (navigator.vibrate) {
            navigator.vibrate(['a', 'b', 'x', 'y'].includes(btnKey) ? 50 : 25);
        }
    } else {
        element.classList.remove('active');
    }
    socket.emit('input', { type: 'button', button: btnKey, pressed });
}

// ============================================
// Thumbstick Handling
// ============================================

const thumbstickBase = document.getElementById('thumbstick-base');
const thumbstickKnob = document.getElementById('thumbstick-knob');
let thumbstickTouch = null;
let thumbstickCenter = { x: 0, y: 0 };
let thumbstickRadius = 0;

function initThumbstick() {
    const container = document.getElementById('thumbstick-container');

    container.addEventListener('touchstart', (e) => {
        e.preventDefault();
        if (thumbstickTouch !== null) return;

        const touch = e.changedTouches[0];
        thumbstickTouch = touch.identifier;

        const rect = thumbstickBase.getBoundingClientRect();
        thumbstickCenter = {
            x: rect.left + rect.width / 2,
            y: rect.top + rect.height / 2
        };
        thumbstickRadius = rect.width / 2;

        thumbstickKnob.classList.add('active');
        updateThumbstick(touch.clientX, touch.clientY);
    }, { passive: false });

    container.addEventListener('touchmove', (e) => {
        e.preventDefault();
        for (const touch of e.changedTouches) {
            if (touch.identifier === thumbstickTouch) {
                updateThumbstick(touch.clientX, touch.clientY);
                break;
            }
        }
    }, { passive: false });

    container.addEventListener('touchend', (e) => {
        for (const touch of e.changedTouches) {
            if (touch.identifier === thumbstickTouch) {
                resetThumbstick();
                break;
            }
        }
    }, { passive: false });

    container.addEventListener('touchcancel', resetThumbstick, { passive: false });

    // Mouse support for desktop
    let mouseDown = false;
    container.addEventListener('mousedown', (e) => {
        mouseDown = true;
        const rect = thumbstickBase.getBoundingClientRect();
        thumbstickCenter = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
        thumbstickRadius = rect.width / 2;
        thumbstickKnob.classList.add('active');
        updateThumbstick(e.clientX, e.clientY);
    });

    window.addEventListener('mousemove', (e) => {
        if (mouseDown) updateThumbstick(e.clientX, e.clientY);
    });

    window.addEventListener('mouseup', () => {
        if (mouseDown) {
            mouseDown = false;
            resetThumbstick();
        }
    });
}

function updateThumbstick(clientX, clientY) {
    let dx = clientX - thumbstickCenter.x;
    let dy = clientY - thumbstickCenter.y;

    // Clamp to circle
    const distance = Math.sqrt(dx * dx + dy * dy);
    const maxDistance = thumbstickRadius * 0.8;

    if (distance > maxDistance) {
        dx = (dx / distance) * maxDistance;
        dy = (dy / distance) * maxDistance;
    }

    // Update knob position
    const knobSize = thumbstickKnob.offsetWidth;
    thumbstickKnob.style.left = `calc(50% + ${dx}px)`;
    thumbstickKnob.style.top = `calc(50% + ${dy}px)`;

    // Normalize to -1 to 1
    const normX = dx / maxDistance;
    const normY = dy / maxDistance;

    // Send to server
    socket.emit('input', { type: 'stick', x: normX, y: normY });
}

function resetThumbstick() {
    thumbstickTouch = null;
    thumbstickKnob.classList.remove('active');
    thumbstickKnob.style.left = '50%';
    thumbstickKnob.style.top = '50%';
    thumbstickKnob.style.transform = 'translate(-50%, -50%)';
    socket.emit('input', { type: 'stick', x: 0, y: 0 });
}

// ============================================
// Service Worker Registration (PWA)
// ============================================

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(reg => console.log('SW registered:', reg.scope))
            .catch(err => console.log('SW registration failed:', err));
    });
}

// ============================================
// Initialize
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    applySettings();
    setupButtonEvents();
    initThumbstick();
});
