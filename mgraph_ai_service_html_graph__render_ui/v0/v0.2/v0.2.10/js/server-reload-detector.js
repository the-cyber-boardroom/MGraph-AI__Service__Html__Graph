/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Server Reload Detector
   v0.2.10 - Auto-refresh on server restart (SSE-based)

   Features:
   - Connects to /events/server SSE endpoint
   - Detects server restart via timestamp change
   - Auto-triggers graph reload
   - Toggle to enable/disable
   ═══════════════════════════════════════════════════════════════════════════════ */

function ServerReloadDetector(options) {
    options = options || {};

    this.endpoint = options.endpoint || '/events/server';
    this.enabled = options.enabled || false;
    this.eventSource = null;
    this.lastServerTime = null;
    this.wasDisconnected = false;
    this.onReload = options.onReload || function() {};

    this.init();
}

ServerReloadDetector.prototype.init = function() {
    // Check localStorage for saved preference
    var saved = localStorage.getItem('serverReloadDetector.enabled');
    if (saved !== null) {
        this.enabled = saved === 'true';
    }

    if (this.enabled) {
        this.connect();
    }

    console.log('[ServerReloadDetector] Initialized, enabled:', this.enabled);
};

ServerReloadDetector.prototype.connect = function() {
    if (this.eventSource) {
        return; // Already connected
    }

    var self = this;

    try {
        this.eventSource = new EventSource(this.endpoint);

        this.eventSource.onmessage = function(event) {
            var serverTime = event.data.trim();

            if (self.lastServerTime && serverTime !== self.lastServerTime) {
                console.log('[ServerReloadDetector] Server restarted, triggering reload...');
                self.showToast('Server restarted - reloading...');

                // Small delay to let server fully initialize
                setTimeout(function() {
                    self.onReload();
                }, 500);
            }

            self.lastServerTime = serverTime;
        };

        this.eventSource.onerror = function() {
            console.log('[ServerReloadDetector] Connection lost, waiting for server...');
            self.wasDisconnected = true;
        };

        this.eventSource.onopen = function() {
            if (self.wasDisconnected) {
                console.log('[ServerReloadDetector] Reconnected to server');
                self.showToast('Reconnected to server');
                self.wasDisconnected = false;
            }
        };

        console.log('[ServerReloadDetector] Connected to', this.endpoint);

    } catch (error) {
        console.warn('[ServerReloadDetector] Failed to connect:', error);
    }
};

ServerReloadDetector.prototype.disconnect = function() {
    if (this.eventSource) {
        this.eventSource.close();
        this.eventSource = null;
        this.lastServerTime = null;
        console.log('[ServerReloadDetector] Disconnected');
    }
};

ServerReloadDetector.prototype.setEnabled = function(enabled) {
    this.enabled = enabled;
    localStorage.setItem('serverReloadDetector.enabled', enabled);

    if (enabled) {
        this.connect();
        this.showToast('Auto-reload enabled');
    } else {
        this.disconnect();
        this.showToast('Auto-reload disabled');
    }
};

ServerReloadDetector.prototype.toggle = function() {
    this.setEnabled(!this.enabled);
    return this.enabled;
};

ServerReloadDetector.prototype.isEnabled = function() {
    return this.enabled;
};

ServerReloadDetector.prototype.showToast = function(message) {
    var existing = document.getElementById('server-reload-toast');
    if (existing) existing.remove();

    var toast = document.createElement('div');
    toast.id = 'server-reload-toast';
    toast.className = 'server-reload-toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    // Trigger animation
    requestAnimationFrame(function() {
        toast.classList.add('visible');
    });

    setTimeout(function() {
        toast.classList.remove('visible');
        setTimeout(function() { toast.remove(); }, 300);
    }, 2000);
};

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ServerReloadDetector;
}