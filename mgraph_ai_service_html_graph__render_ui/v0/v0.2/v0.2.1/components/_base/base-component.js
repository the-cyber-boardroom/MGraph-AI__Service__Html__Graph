/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Base Component Class
   v0.2.1 - Foundation for Shadow DOM components with resource loading
   
   Provides:
   - Shadow DOM encapsulation
   - Async CSS/HTML template loading
   - Event listener tracking and cleanup
   - Common utility method access
   - Standardized lifecycle hooks
   ═══════════════════════════════════════════════════════════════════════════════ */

class BaseComponent extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this._eventListeners = [];
        this._isReady = false;
        this._resourcesLoaded = false;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Lifecycle Methods
    // ═══════════════════════════════════════════════════════════════════════════
    
    async connectedCallback() {
        try {
            await this.loadResources();
            this.bindElements();
            this.setupEventListeners();
            this._isReady = true;
            this.onReady();
            this.emit('component-ready', { component: this.tagName.toLowerCase() });
        } catch (error) {
            console.error(`[${this.tagName}] Failed to initialize:`, error);
            this.showError(`Failed to load component: ${error.message}`);
        }
    }

    disconnectedCallback() {
        this.cleanup();
    }

    /**
     * Override in subclass for post-ready initialization
     */
    onReady() {
        // Subclass hook
    }

    /**
     * Override in subclass to bind element references after template loads
     */
    bindElements() {
        // Subclass hook
    }

    /**
     * Override in subclass to setup event listeners
     */
    setupEventListeners() {
        // Subclass hook
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Resource Loading
    // ═══════════════════════════════════════════════════════════════════════════
    
    async loadResources() {
        if (this._resourcesLoaded) return;
        
        const componentName = this.tagName.toLowerCase();
        const paths = ComponentPaths.getComponentPaths(componentName);
        
        // Load CSS and HTML in parallel
        const [sharedCss, componentCss, templateHtml] = await Promise.all([
            this.fetchCss(ComponentPaths.sharedCss.components),
            this.fetchCss(paths.css),
            this.fetchHtml(paths.html)
        ]);
        
        // Inject into Shadow DOM
        this.shadowRoot.innerHTML = `
            <style>${sharedCss}</style>
            <style>${componentCss}</style>
            ${templateHtml}
        `;
        
        this._resourcesLoaded = true;
    }

    /**
     * Fetch CSS file content
     * @param {string} url - CSS file URL
     * @returns {Promise<string>} CSS content
     */
    async fetchCss(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                console.warn(`[${this.tagName}] CSS not found: ${url}`);
                return '';
            }
            return await response.text();
        } catch (error) {
            console.warn(`[${this.tagName}] Failed to load CSS: ${url}`, error);
            return '';
        }
    }

    /**
     * Fetch HTML template file
     * @param {string} url - HTML file URL
     * @returns {Promise<string>} HTML content
     */
    async fetchHtml(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.text();
        } catch (error) {
            console.error(`[${this.tagName}] Failed to load HTML template: ${url}`, error);
            throw error;
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Event Helpers
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Emit a custom event that crosses Shadow DOM boundary
     * @param {string} eventName - Event name
     * @param {object} detail - Event detail data
     */
    emit(eventName, detail = {}) {
        this.dispatchEvent(new CustomEvent(eventName, {
            detail,
            bubbles: true,
            composed: true  // Crosses Shadow DOM boundary
        }));
    }

    /**
     * Add event listener with tracking for cleanup
     * @param {EventTarget} target - Element to listen on
     * @param {string} eventType - Event type
     * @param {Function} handler - Event handler
     * @param {object} options - addEventListener options
     */
    addTrackedListener(target, eventType, handler, options = {}) {
        const boundHandler = handler.bind(this);
        target.addEventListener(eventType, boundHandler, options);
        this._eventListeners.push({ target, eventType, handler: boundHandler, options });
    }

    /**
     * Query element within Shadow DOM
     * @param {string} selector - CSS selector
     * @returns {Element|null}
     */
    $(selector) {
        return this.shadowRoot.querySelector(selector);
    }

    /**
     * Query all elements within Shadow DOM
     * @param {string} selector - CSS selector
     * @returns {NodeList}
     */
    $$(selector) {
        return this.shadowRoot.querySelectorAll(selector);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Utility Accessors (delegate to Helpers)
    // ═══════════════════════════════════════════════════════════════════════════
    
    escapeHtml(text) {
        return Helpers.escapeHtml(text);
    }

    formatNumber(num) {
        return Helpers.formatNumber(num);
    }

    formatBytes(bytes) {
        return Helpers.formatBytes(bytes);
    }

    isValidUrl(url) {
        return Helpers.isValidUrl(url);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Error Display
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Display error message in component
     * @param {string} message - Error message
     */
    showError(message) {
        this.shadowRoot.innerHTML = `
            <style>
                .component-error {
                    padding: 20px;
                    background: #fee2e2;
                    border: 1px solid #fecaca;
                    border-radius: 8px;
                    color: #dc2626;
                    font-family: system-ui, sans-serif;
                }
                .component-error-title {
                    font-weight: 600;
                    margin-bottom: 8px;
                }
            </style>
            <div class="component-error">
                <div class="component-error-title">⚠️ Component Error</div>
                <div>${this.escapeHtml(message)}</div>
            </div>
        `;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Cleanup
    // ═══════════════════════════════════════════════════════════════════════════
    
    cleanup() {
        // Remove all tracked event listeners
        for (const { target, eventType, handler, options } of this._eventListeners) {
            target.removeEventListener(eventType, handler, options);
        }
        this._eventListeners = [];
        this._isReady = false;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // State Helpers
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Check if component is ready
     * @returns {boolean}
     */
    get isReady() {
        return this._isReady;
    }

    /**
     * Wait for component to be ready
     * @param {number} timeout - Timeout in ms (default 5000)
     * @returns {Promise<void>}
     */
    whenReady(timeout = 5000) {
        if (this._isReady) return Promise.resolve();
        
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => {
                reject(new Error(`Component ${this.tagName} ready timeout`));
            }, timeout);
            
            this.addEventListener('component-ready', () => {
                clearTimeout(timer);
                resolve();
            }, { once: true });
        });
    }
}

// Export for both browser and Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BaseComponent;
}
if (typeof window !== 'undefined') {
    window.BaseComponent = BaseComponent;
}
