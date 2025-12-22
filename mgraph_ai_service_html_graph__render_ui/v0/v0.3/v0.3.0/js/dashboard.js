/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Dashboard Controller
   v0.3.0 - From v0.2.0 (unchanged)
   ═══════════════════════════════════════════════════════════════════════════════ */

class Dashboard {
    constructor() {
        this.statusDot = null;
        this.statusText = null;
    }

    init() {
        this.statusDot = document.getElementById('api-status-dot');
        this.statusText = document.getElementById('api-status-text');
        
        this.checkApiStatus();
    }

    async checkApiStatus() {
        try {
            const isHealthy = await window.apiClient.checkHealth();
            
            if (isHealthy) {
                this.setStatus('online', 'API Online');
            } else {
                this.setStatus('offline', 'API Offline');
            }
        } catch (error) {
            this.setStatus('offline', 'API Unreachable');
        }
    }

    setStatus(status, text) {
        if (this.statusDot) {
            this.statusDot.className = `api-status-dot ${status}`;
        }
        if (this.statusText) {
            this.statusText.textContent = text;
        }
    }
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new Dashboard();
    dashboard.init();
});
