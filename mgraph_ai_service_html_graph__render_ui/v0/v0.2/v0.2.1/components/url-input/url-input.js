/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - URL Input Component
   v0.2.1 - Refactored to use Shadow DOM + BaseComponent
   
   Fetches HTML content from a URL via the API.
   
   Original v0.2.0: ~150 lines (inline CSS + HTML)
   This version: ~100 lines (slim, template-based)
   ═══════════════════════════════════════════════════════════════════════════════ */

class UrlInput extends BaseComponent {
    constructor() {
        super();
        this.isFetching = false;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Lifecycle Hooks
    // ═══════════════════════════════════════════════════════════════════════════
    
    bindElements() {
        this.urlInput = this.$('#url-input');
        this.fetchButton = this.$('#url-fetch-btn');
        this.statusText = this.$('#url-status');
    }

    setupEventListeners() {
        this.addTrackedListener(this.fetchButton, 'click', this.fetchUrl);
        this.addTrackedListener(this.urlInput, 'keydown', this.onKeyDown);
        
        // Example buttons
        this.$$('.url-example-btn').forEach(btn => {
            this.addTrackedListener(btn, 'click', () => {
                this.urlInput.value = btn.dataset.url;
                this.fetchUrl();
            });
        });
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Event Handlers
    // ═══════════════════════════════════════════════════════════════════════════
    
    onKeyDown(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            this.fetchUrl();
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Core Functionality
    // ═══════════════════════════════════════════════════════════════════════════
    
    async fetchUrl() {
        const url = this.urlInput.value.trim();

        if (!url) {
            this.setStatus('Please enter a URL', 'error');
            return;
        }

        if (!this.isValidUrl(url)) {
            this.setStatus('Please enter a valid URL (including https://)', 'error');
            return;
        }

        if (this.isFetching) return;

        this.isFetching = true;
        this.setFetchingState(true);
        this.setStatus('Fetching HTML...', '');

        try {
            const response = await window.apiClient.post('/html/from/url', { url: url, timeout: 30 });

            this.setStatus(`✓ Fetched ${this.formatBytes(response.html.length)} from ${response.url}`, 'success');

            this.emit('url-html-fetched', {
                html: response.html,
                url: response.url,
                contentType: response.content_type
            });

        } catch (error) {
            console.error('URL fetch error:', error);
            this.setStatus(`✗ ${error.message || 'Failed to fetch URL'}`, 'error');
        } finally {
            this.isFetching = false;
            this.setFetchingState(false);
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // UI State Management
    // ═══════════════════════════════════════════════════════════════════════════
    
    setFetchingState(fetching) {
        this.fetchButton.disabled = fetching;
        this.fetchButton.innerHTML = fetching
            ? '<span class="spinner"></span> Fetching...'
            : '🔗 Fetch';
    }

    setStatus(message, type = '') {
        this.statusText.textContent = message;
        this.statusText.className = 'url-status ' + type;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Public API
    // ═══════════════════════════════════════════════════════════════════════════
    
    getUrl() {
        return this.urlInput.value.trim();
    }

    setUrl(url) {
        this.urlInput.value = url;
    }
}

customElements.define('url-input', UrlInput);
