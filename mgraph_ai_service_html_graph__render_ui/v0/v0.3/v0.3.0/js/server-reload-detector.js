/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Server Reload Detector
   v0.3.0 - From v0.2.10 (unchanged)
   
   SSE-based server restart detection with auto-reload capability
   ═══════════════════════════════════════════════════════════════════════════════ */

class ServerReloadDetector {
    constructor(options = {}) {
        this.sseUrl = options.sseUrl || '/events/reload';
        this.enabled = options.enabled !== false;
        this.autoReload = options.autoReload !== false;
        this.reconnectDelay = options.reconnectDelay || 1000;
        this.maxReconnectDelay = options.maxReconnectDelay || 30000;
        
        this.eventSource = null;
        this.currentDelay = this.reconnectDelay;
        this.isConnected = false;
        this.serverStartTime = null;
        
        if (this.enabled) {
            this.connect();
        }
    }

    connect() {
        if (this.eventSource) {
            this.eventSource.close();
        }

        try {
            this.eventSource = new EventSource(this.sseUrl);

            this.eventSource.onopen = () => {
                console.log('[ServerReloadDetector] Connected to SSE');
                this.isConnected = true;
                this.currentDelay = this.reconnectDelay;
            };

            this.eventSource.onmessage = (event) => {
                this.handleMessage(event);
            };

            this.eventSource.onerror = (error) => {
                console.warn('[ServerReloadDetector] SSE error, reconnecting...', error);
                this.isConnected = false;
                this.scheduleReconnect();
            };

        } catch (error) {
            console.error('[ServerReloadDetector] Failed to connect:', error);
            this.scheduleReconnect();
        }
    }

    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'startup') {
                const newStartTime = data.server_start_time;
                
                if (this.serverStartTime && this.serverStartTime !== newStartTime) {
                    console.log('[ServerReloadDetector] Server restarted, reloading page...');
                    this.showReloadToast();
                    
                    if (this.autoReload) {
                        setTimeout(() => window.location.reload(), 500);
                    }
                }
                
                this.serverStartTime = newStartTime;
            }
            
            if (data.type === 'ping') {
                // Keepalive, do nothing
            }

        } catch (error) {
            console.warn('[ServerReloadDetector] Failed to parse message:', error);
        }
    }

    scheduleReconnect() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }

        setTimeout(() => {
            this.connect();
        }, this.currentDelay);

        // Exponential backoff
        this.currentDelay = Math.min(this.currentDelay * 2, this.maxReconnectDelay);
    }

    showReloadToast() {
        const toast = document.createElement('div');
        toast.className = 'server-reload-toast';
        toast.innerHTML = `
            <span class="reload-icon">🔄</span>
            <span class="reload-text">Server restarted, reloading...</span>
        `;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #4CAF50;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            z-index: 10001;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            animation: slideUp 0.3s ease;
        `;

        // Add animation keyframes if not exists
        if (!document.getElementById('reload-toast-styles')) {
            const style = document.createElement('style');
            style.id = 'reload-toast-styles';
            style.textContent = `
                @keyframes slideUp {
                    from { transform: translateX(-50%) translateY(20px); opacity: 0; }
                    to { transform: translateX(-50%) translateY(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(toast);
    }

    disconnect() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
        this.isConnected = false;
    }

    setAutoReload(enabled) {
        this.autoReload = enabled;
    }

    getStatus() {
        return {
            connected: this.isConnected,
            serverStartTime: this.serverStartTime,
            autoReload: this.autoReload
        };
    }
}

// DO NOT auto-initialize - this should be user-driven
// The user can enable it via a toggle button

// Make class available globally (but not started)
window.ServerReloadDetector = ServerReloadDetector;

// Helper to create and connect when user enables it
window.enableServerReloadDetector = function(options = {}) {
    if (!window.serverReloadDetector) {
        window.serverReloadDetector = new ServerReloadDetector({
            ...options,
            enabled: true
        });
    } else if (!window.serverReloadDetector.isConnected) {
        window.serverReloadDetector.connect();
    }
    return window.serverReloadDetector;
};

window.disableServerReloadDetector = function() {
    if (window.serverReloadDetector) {
        window.serverReloadDetector.disconnect();
    }
};