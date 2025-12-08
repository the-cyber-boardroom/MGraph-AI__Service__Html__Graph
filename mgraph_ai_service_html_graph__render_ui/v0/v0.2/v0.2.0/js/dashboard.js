/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Dashboard
   v0.2.0 - Consolidated from v0.1.x
   ═══════════════════════════════════════════════════════════════════════════════ */

/**
 * Dashboard Controller
 * Handles dashboard initialization and API status checking
 */
class Dashboard {
    constructor() {
        this.statusDot = null;
        this.statusText = null;
        this.checkInterval = null;
    }

    /**
     * Initialize the dashboard
     */
    init() {
        this.statusDot = document.getElementById('api-status-dot');
        this.statusText = document.getElementById('api-status-text');

        // Check API status immediately
        this.checkApiStatus();

        // Check status every 30 seconds
        this.checkInterval = setInterval(() => this.checkApiStatus(), 30000);

        console.log('Dashboard v0.2.0 initialized');
    }

    /**
     * Check API health status and update UI
     */
    async checkApiStatus() {
        if (!this.statusDot || !this.statusText) return;

        // Set loading state
        this.statusDot.className = 'api-status-dot loading';
        this.statusText.textContent = 'Checking...';

        try {
            const isHealthy = await window.apiClient.checkHealth();     // todo: replace this use of window.apiClient with an event driven solution

            if (isHealthy) {
                this.statusDot.className = 'api-status-dot';
                this.statusText.textContent = 'Connected';
            } else {
                this.statusDot.className = 'api-status-dot error';
                this.statusText.textContent = 'Disconnected';
            }
        } catch (error) {
            this.statusDot.className = 'api-status-dot error';
            this.statusText.textContent = 'Error';
            console.error('API health check failed:', error);
        }
    }

    /**
     * Cleanup on page unload
     */
    destroy() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new Dashboard();
    dashboard.init();

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => dashboard.destroy());
});
