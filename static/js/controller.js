/**
 * OpenController - Cyber Series Logic
 * Features: Floating Joystick, Multi-touch, Haptics
 */

const socket = io();

// State
const state = {
    useThumbstick: true, // Default to true (Floating Joystick)
    activeTouches: new Map() // specialized map for button touches
};

// DOM Elements
const els = {
    zoneLeft: document.getElementById('zone-left'),
    thumbstickLayer: document.getElementById('thumbstick-layer'),
    thumbstickBase: document.getElementById('thumbstick-base'),
    thumbstickKnob: document.getElementById('thumbstick-knob'),
    dpadContainer: document.getElementById('dpad-container'),
    settingsModal: document.getElementById('settings-modal'),
    settingsBtn: document.getElementById('settings-btn'),
    closeSettings: document.getElementById('close-settings'),
    inputModeToggle: document.getElementById('input-mode-toggle'),
    inputModeDesc: document.getElementById('input-mode-desc'),
    status: document.getElementById('connection-status'),
    statusText: document.querySelector('#connection-status .text')
};

// ============================================
// Haptics Engine
// ============================================
const haptics = {
    tap: () => navigator.vibrate && navigator.vibrate(10), // Ultra short
    bump: () => navigator.vibrate && navigator.vibrate(15),
    limit: () => navigator.vibrate && navigator.vibrate(30), // Thud
};

// ============================================
// Settings Management
// ============================================

function toggleInputMode(useStick) {
    state.useThumbstick = useStick;
    if (useStick) {
        els.dpadContainer.style.display = 'none';
        els.thumbstickLayer.style.display = 'block';
        els.inputModeDesc.textContent = "Dynamic Stick active. Touch anywhere on left side to move.";
    } else {
        els.dpadContainer.style.display = 'block';
        els.thumbstickLayer.style.display = 'none';
        els.inputModeDesc.textContent = "Standard D-Pad active.";
    }
    localStorage.setItem('inputMode', useStick ? 'stick' : 'dpad');
}

// Load saved settings
const savedMode = localStorage.getItem('inputMode');
// Default to D-Pad (false) if no save, or if saved as 'dpad'
if (savedMode === 'stick') {
    els.inputModeToggle.checked = true;
    toggleInputMode(true);
} else {
    els.inputModeToggle.checked = false;
    toggleInputMode(false);
}

// Event Listeners
els.settingsBtn.addEventListener('click', () => els.settingsModal.classList.add('open'));
els.closeSettings.addEventListener('click', () => els.settingsModal.classList.remove('open'));
els.settingsModal.addEventListener('click', (e) => {
    if (e.target === els.settingsModal) els.settingsModal.classList.remove('open');
});

els.inputModeToggle.addEventListener('change', (e) => {
    toggleInputMode(e.target.checked);
});

// ============================================
// Floating Joystick Logic
// ============================================

let stickTouchId = null;
let stickCenter = { x: 0, y: 0 };
const MAX_RADIUS = 50; // Max visual distance in pixels

function initJoystick() {
    // We attach listeners to the entire left zone
    els.zoneLeft.addEventListener('touchstart', handleStickStart, { passive: false });
    els.zoneLeft.addEventListener('touchmove', handleStickMove, { passive: false });
    els.zoneLeft.addEventListener('touchend', handleStickEnd, { passive: false });
    els.zoneLeft.addEventListener('touchcancel', handleStickEnd, { passive: false });
}

function handleStickStart(e) {
    if (!state.useThumbstick) return; // Ignore if in D-Pad mode
    e.preventDefault();

    if (stickTouchId !== null) return; // Already active

    // Find the touch that started in this zone
    // Since we attached to zoneLeft, e.changedTouches should contain it
    const touch = e.changedTouches[0];
    if (!touch) return;

    stickTouchId = touch.identifier;

    // Set the anchor point for the joystick
    stickCenter = { x: touch.clientX, y: touch.clientY };

    // Position the visuals instantly
    updateStickVisuals(touch.clientX, touch.clientY);

    // Show visuals
    els.thumbstickLayer.classList.add('active');

    // Feedback
    haptics.tap();
}

function handleStickMove(e) {
    if (!state.useThumbstick || stickTouchId === null) return;
    e.preventDefault();

    for (let i = 0; i < e.changedTouches.length; i++) {
        const touch = e.changedTouches[i];
        if (touch.identifier === stickTouchId) {
            updateStickLogic(touch.clientX, touch.clientY);
            break;
        }
    }
}

function handleStickEnd(e) {
    if (!state.useThumbstick || stickTouchId === null) return;

    for (let i = 0; i < e.changedTouches.length; i++) {
        if (e.changedTouches[i].identifier === stickTouchId) {
            resetStick();
            break;
        }
    }
}

function updateStickLogic(clientX, clientY) {
    const dx = clientX - stickCenter.x;
    const dy = clientY - stickCenter.y;

    // Calculate distance
    const dist = Math.sqrt(dx * dx + dy * dy);

    // Normalize logic (0.0 to 1.0)
    // We implicitly define a "full input" radius. Let's say 50px is full speed.
    // But physically the knob can move up to MAX_RADIUS.
    let normX = dx / MAX_RADIUS;
    let normY = dy / MAX_RADIUS;

    // Clamp magnitude to 1.0 for output
    const mag = Math.sqrt(normX * normX + normY * normY);
    if (mag > 1.0) {
        normX /= mag;
        normY /= mag;
    }

    // Visual update (capped at MAX_RADIUS)
    let visX = dx;
    let visY = dy;
    if (dist > MAX_RADIUS) {
        visX = (dx / dist) * MAX_RADIUS;
        visY = (dy / dist) * MAX_RADIUS;
        // Optional: haptic bump when hitting edge
        // (Implementation note: needs state tracking to avoid spamming)
    }

    updateStickVisuals(stickCenter.x + visX, stickCenter.y + visY);

    // Emit
    socket.emit('input', { type: 'stick', x: normX, y: normY });
}

function updateStickVisuals(knobX, knobY) {
    // Base is always at stickCenter
    els.thumbstickBase.style.left = stickCenter.x + 'px';
    els.thumbstickBase.style.top = stickCenter.y + 'px';

    // Knob moves
    els.thumbstickKnob.style.left = knobX + 'px';
    els.thumbstickKnob.style.top = knobY + 'px';

    // Directional highlight on knob?
    // els.thumbstickKnob.classList.add('active'); // It's already active via parent class
}

function resetStick() {
    stickTouchId = null;
    els.thumbstickLayer.classList.remove('active');
    socket.emit('input', { type: 'stick', x: 0, y: 0 });
    haptics.tap(); // Release click
}

// ============================================
// Button Handling (Multi-touch)
// ============================================

function initButtons() {
    const buttons = document.querySelectorAll('.action-btn, .dpad-btn');

    buttons.forEach(btn => {
        const key = btn.dataset.key;

        btn.addEventListener('touchstart', (e) => {
            e.preventDefault(); // Prevent scroll/zoom
            haptics.tap();
            emitBtn(key, true);
            btn.classList.add('active');

            // Track touches if needed (for complex gestures), 
            // but CSS :active + class toggle is usually enough for simple buttons
        }, { passive: false });

        btn.addEventListener('touchend', (e) => {
            e.preventDefault();
            emitBtn(key, false);
            btn.classList.remove('active');
        }, { passive: false });

        // Handle "slide off" cancellation
        // Use touchmove to check if finger left the element? 
        // For now, touchend is robust enough for tap buttons.
    });
}

function emitBtn(key, pressed) {
    socket.emit('input', { type: 'button', button: key, pressed });
}

// ============================================
// Connection & Init
// ============================================

socket.on('connect', () => {
    els.status.className = 'connected';
    els.statusText.textContent = 'LINKED';
});

socket.on('disconnect', () => {
    els.status.className = 'disconnected';
    els.statusText.textContent = 'OFFLINE';
});

// Prevent context menu
window.oncontextmenu = (e) => { e.preventDefault(); return false; };

// Initialize
initJoystick();
initButtons();
console.log('OpenController Cyber v2.0 Initialized');
