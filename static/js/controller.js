/**
 * OpenController - Virtual Xbox Controller JavaScript
 */

const socket = io();
const statusEl = document.getElementById('connection-status');
const statusText = statusEl.querySelector('.text');

// ============================================
// Connection Status Handlers
// ============================================

socket.on('connect', () => {
    statusEl.className = 'connected';
    statusText.textContent = 'Connected';
    // Auto-hide after 2 seconds when connected
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

// Show full indicator on hover
statusEl.addEventListener('mouseenter', () => statusEl.style.opacity = '1');
statusEl.addEventListener('mouseleave', () => {
    if (statusEl.classList.contains('connected')) {
        statusEl.style.opacity = '0.3';
    }
});

// ============================================
// Context Menu Prevention
// ============================================

window.oncontextmenu = function(event) {
    event.preventDefault();
    event.stopPropagation();
    return false;
};

// ============================================
// Button Input Handling
// ============================================

const buttons = document.querySelectorAll('.dpad-btn, .action-btn');

buttons.forEach(btn => {
    const key = btn.getAttribute('data-key');
    
    // Touch events
    btn.addEventListener('touchstart', (e) => {
        e.preventDefault(); 
        emit(key, true, btn);
    }, {passive: false});

    btn.addEventListener('touchend', (e) => {
        e.preventDefault();
        emit(key, false, btn);
    }, {passive: false});

    // Mouse events for debugging on desktop
    btn.addEventListener('mousedown', (e) => {
        emit(key, true, btn);
    });
    btn.addEventListener('mouseup', (e) => {
        emit(key, false, btn);
    });
    btn.addEventListener('mouseleave', (e) => {
        // Ensure release if mouse leaves button while pressed
    });
});

/**
 * Emit button state to server and handle visual/haptic feedback
 * @param {string} btnKey - The button identifier
 * @param {boolean} pressed - Whether button is pressed
 * @param {HTMLElement} element - The button DOM element
 */
function emit(btnKey, pressed, element) {
    if (pressed) {
        element.classList.add('active');
        
        // Haptics
        if (window.navigator && window.navigator.vibrate) {
            // Stronger vibration for actions, lighter for dpad
            if (['a', 'x'].includes(btnKey)) {
                window.navigator.vibrate(70); 
            } else {
                window.navigator.vibrate(30);
            }
        }
    } else {
        element.classList.remove('active');
    }
    
    socket.emit('input', {button: btnKey, pressed: pressed});
}

// ============================================
// Service Worker Registration (PWA)
// ============================================

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then(reg => console.log('SW registered:', reg.scope))
            .catch(err => console.log('SW registration failed:', err));
    });
}
