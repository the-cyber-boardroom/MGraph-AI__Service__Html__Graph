/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Mini Browser Component
   v0.2.11 - Iframe-based HTML preview with navigation controls
   
   Features:
   - Render HTML content in sandboxed iframe
   - URL bar showing current path/URL
   - Refresh functionality
   - Responsive scaling
   ═══════════════════════════════════════════════════════════════════════════════ */

class MiniBrowser extends BaseComponent {
    constructor() {
        super();
        this.html = '';
        this.url = '';
        this.cacheKey = '';
        this.isLoading = false;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Lifecycle
    // ═══════════════════════════════════════════════════════════════════════════

    bindElements() {
        this.urlBar = this.$('#browser-url');
        this.refreshBtn = this.$('#browser-refresh-btn');
        this.scaleSelect = this.$('#browser-scale');
        this.iframe = this.$('#browser-frame');
        this.placeholder = this.$('#browser-placeholder');
    }

    setupEventListeners() {
        this.addTrackedListener(this.refreshBtn, 'click', this.refresh);
        this.addTrackedListener(this.scaleSelect, 'change', this.handleScaleChange);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Public API
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Set HTML content to display
     */
    setHtml(html, cacheKey = '', url = '') {
        this.html = html;
        this.cacheKey = cacheKey;
        this.url = url || cacheKey;
        
        this.updateUrlBar();
        this.renderHtml();
    }

    /**
     * Refresh current content
     */
    refresh() {
        if (this.html) {
            this.renderHtml();
            this.emit('browser-refreshed', { url: this.url, cacheKey: this.cacheKey });
        }
    }

    /**
     * Clear content
     */
    clear() {
        this.html = '';
        this.url = '';
        this.cacheKey = '';
        this.urlBar.value = '';
        this.showPlaceholder();
    }

    /**
     * Get current HTML content
     */
    getHtml() {
        return this.html;
    }

    /**
     * Get current URL/path
     */
    getUrl() {
        return this.url;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Event Handlers
    // ═══════════════════════════════════════════════════════════════════════════

    handleScaleChange() {
        const scale = parseFloat(this.scaleSelect.value);
        this.applyScale(scale);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Rendering
    // ═══════════════════════════════════════════════════════════════════════════

    updateUrlBar() {
        this.urlBar.value = this.url || this.cacheKey || '';
    }

    renderHtml() {
        if (!this.html) {
            this.showPlaceholder();
            return;
        }

        // Hide placeholder, show iframe
        this.placeholder.style.display = 'none';
        this.iframe.style.display = 'block';

        // Write HTML to iframe
        try {
            const doc = this.iframe.contentDocument || this.iframe.contentWindow.document;
            doc.open();
            doc.write(this.html);
            doc.close();
        } catch (error) {
            console.error('[MiniBrowser] Render error:', error);
            this.showError('Failed to render HTML');
        }
    }

    showPlaceholder() {
        this.iframe.style.display = 'none';
        this.placeholder.style.display = 'flex';
        this.placeholder.innerHTML = `
            <div class="placeholder-icon">🌐</div>
            <p>Load an entity to preview its HTML</p>
        `;
    }

    showError(message) {
        this.iframe.style.display = 'none';
        this.placeholder.style.display = 'flex';
        this.placeholder.innerHTML = `
            <div class="placeholder-icon">❌</div>
            <p class="error-message">${this.escapeHtml(message)}</p>
        `;
    }

    applyScale(scale) {
        const container = this.$('.browser-viewport');
        if (container) {
            this.iframe.style.transform = `scale(${scale})`;
            this.iframe.style.transformOrigin = 'top left';
            this.iframe.style.width = `${100 / scale}%`;
            this.iframe.style.height = `${100 / scale}%`;
        }
    }
}

customElements.define('mini-browser', MiniBrowser);
