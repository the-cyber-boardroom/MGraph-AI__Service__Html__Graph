class PlantUMLRenderer extends HTMLElement {

    // Static: CheerpJ loader URL
    static CHEERPJ_LOADER = 'https://cjrtnc.leaningtech.com/2.3/loader.js';

    // Static: Default JAR path (remote hosted)
    //static DEFAULT_JAR_PATH = 'https://plantuml.github.io/plantuml.js/plantuml-wasm';

    // Static: Shared initialization state across all instances
    static _initPromise  = null;
    static _initialized  = false;
    static _initializing = false;

    constructor() {
        super();
        this._text      = '';
        this._theme     = 'light';
        this._svg       = '';
        //this._jarPath   = PlantUMLRenderer.DEFAULT_JAR_PATH;
        this._rendering = false;

        // Create shadow DOM for encapsulation
        this.attachShadow({ mode: 'open' });
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    width: 100%;
                    height: 100%;
                    overflow: auto;
                }
                .container {
                    width: 100%;
                    height: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .loading {
                    color: #666;
                    font-family: system-ui, sans-serif;
                    font-size: 14px;
                }
                .error {
                    color: #c00;
                    font-family: monospace;
                    font-size: 12px;
                    padding: 16px;
                    white-space: pre-wrap;
                    background: #fff0f0;
                    border-radius: 4px;
                    max-width: 100%;
                    overflow: auto;
                }
                .svg-container {
                    width: 100%;
                    height: 100%;
                }
                .svg-container svg {
                    max-width: 100%;
                    height: auto;
                }
                .powered-by {
                    position: absolute;
                    bottom: 4px;
                    right: 8px;
                    font-size: 10px;
                    color: #999;
                    font-family: system-ui, sans-serif;
                }
                .powered-by a {
                    color: #666;
                    text-decoration: none;
                }
                .powered-by a:hover {
                    text-decoration: underline;
                }
            </style>
            <div class="container">
                <div class="loading">Initializing PlantUML...</div>
            </div>
            <div class="powered-by">
                Powered by <a href="https://docs.leaningtech.com/cheerpj" target="_blank">CheerpJ</a>
            </div>
        `;

        this._container = this.shadowRoot.querySelector('.container');
    }

    // Observed attributes
    static get observedAttributes() {
        return ['theme', 'jar-path'];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (oldValue === newValue) return;

        switch (name) {
            case 'theme':
                this._theme = newValue === 'dark' ? 'dark' : 'light';
                if (this._text && PlantUMLRenderer._initialized) {
                    this.render();
                }
                break;
            // case 'jar-path':
            //     this._jarPath = newValue || PlantUMLRenderer.DEFAULT_JAR_PATH;
            //     break;
        }
    }

    async connectedCallback() {
        // Read initial attributes (use constructor defaults if not specified)
        this._theme   = this.getAttribute('theme') === 'dark' ? 'dark' : 'light';
        //this._jarPath = this.getAttribute('jar-path') || this._jarPath;  // Keep constructor default

        try {
            await this._ensureInitialized();
            this._showReady();
            this._dispatchEvent('plantuml-ready');
        } catch (error) {
            this._showError(`Initialization failed: ${error.message}`);
            this._dispatchEvent('plantuml-error', { error });
        }
    }

    /**
     * Ensure CheerpJ and PlantUML are initialized (singleton pattern)
     */
    async _ensureInitialized() {
        // Already initialized
        if (PlantUMLRenderer._initialized) {
            return;
        }

        // Initialization in progress - wait for it
        if (PlantUMLRenderer._initPromise) {
            return PlantUMLRenderer._initPromise;
        }

        // Start initialization
        PlantUMLRenderer._initPromise = this._initialize();
        return PlantUMLRenderer._initPromise;
    }

    /**
     * Initialize CheerpJ and PlantUML runtime
     */
    async _initialize() {
        PlantUMLRenderer._initializing = true;

        try {
            // Load CheerpJ loader script if not present
            if (!window.cheerpjInit) {
                await this._loadScript(PlantUMLRenderer.CHEERPJ_LOADER);
            }

            // Initialize CheerpJ
            await cheerpjInit();

            // Initialize PlantUML - ensure no trailing slash and proper path
            //const jarUrl = `${this._jarPath.replace(/\/$/, '')}/jars/plantuml-core.jar`;
            const jarUrl = `/app/jars/plantuml-core.jar`;                               //  cheerpjRunMain needs '/app'
            console.log('[PlantUML Renderer] Loading JAR from:', jarUrl);

            await cheerpjRunMain(
                "com.plantuml.api.cheerpj.v1.RunInit",
                jarUrl
            );

            PlantUMLRenderer._initialized  = true;
            PlantUMLRenderer._initializing = false;

            console.log('[PlantUML Renderer] Initialized successfully');

        } catch (error) {
            PlantUMLRenderer._initializing = false;
            PlantUMLRenderer._initPromise  = null;
            throw error;
        }
    }

    /**
     * Load external script dynamically
     */
    _loadScript(src) {
        return new Promise((resolve, reject) => {
            // Check if already loaded
            if (document.querySelector(`script[src="${src}"]`)) {
                resolve();
                return;
            }

            const script  = document.createElement('script');
            script.src    = src;
            script.async  = true;
            script.onload = resolve;
            script.onerror = () => reject(new Error(`Failed to load: ${src}`));
            document.head.appendChild(script);
        });
    }

    /**
     * Set PlantUML text and render
     */
    async setText(text) {
        this._text = text || '';

        if (!this._text) {
            this._showReady();
            return;
        }

        if (!PlantUMLRenderer._initialized) {
            this._showLoading('Waiting for initialization...');
            await this._ensureInitialized();
        }

        await this.render();
    }

    /**
     * Get current PlantUML text
     */
    getText() {
        return this._text;
    }

    /**
     * Set theme (light/dark)
     */
    setTheme(theme) {
        this._theme = theme === 'dark' ? 'dark' : 'light';
        if (this._text && PlantUMLRenderer._initialized) {
            this.render();
        }
    }

    /**
     * Get current theme
     */
    getTheme() {
        return this._theme;
    }

    /**
     * Get current SVG string
     */
    getSvg() {
        return this._svg;
    }

    /**
     * Render the diagram
     */
    async render() {
        if (!this._text) {
            this._showReady();
            return;
        }

        if (!PlantUMLRenderer._initialized) {
            this._showError('PlantUML not initialized');
            return;
        }

        if (this._rendering) {
            return; // Prevent concurrent renders
        }

        this._rendering = true;
        this._showLoading('Rendering...');

        try {
            // Call PlantUML WASM to generate SVG
            const result = await cjCall(
                "com.plantuml.api.cheerpj.v1.Svg",
                "convert",
                this._theme,
                this._text
            );

            // Check if result is SVG or error JSON
            if (result && result.startsWith('<svg') || result.startsWith('<?xml')) {
                this._svg = result;
                this._showSvg(result);
                this._dispatchEvent('plantuml-rendered', { svg: result });
            } else {
                // Try to parse as error JSON
                let errorMsg = result;
                try {
                    const errorData = JSON.parse(result);
                    errorMsg = errorData.error || errorData.message || result;
                } catch (e) {
                    // Not JSON, use as-is
                }
                throw new Error(errorMsg);
            }

        } catch (error) {
            this._svg = '';
            this._showError(`Render error: ${error.message}`);
            this._dispatchEvent('plantuml-error', { error });
        } finally {
            this._rendering = false;
        }
    }

    /**
     * Check PlantUML syntax
     */
    async checkSyntax(text) {
        if (!PlantUMLRenderer._initialized) {
            throw new Error('PlantUML not initialized');
        }

        const result = await cjCall(
            "com.plantuml.api.cheerpj.v1.Info",
            "syntaxCheck",
            text || this._text
        );

        return JSON.parse(result);
    }

    // UI helpers

    _showLoading(message) {
        this._container.innerHTML = `<div class="loading">${message}</div>`;
    }

    _showReady() {
        this._container.innerHTML = `<div class="loading">Ready - awaiting diagram</div>`;
    }

    _showError(message) {
        this._container.innerHTML = `<div class="error">${this._escapeHtml(message)}</div>`;
    }

    _showSvg(svg) {
        this._container.innerHTML = `<div class="svg-container">${svg}</div>`;
    }

    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    _dispatchEvent(name, detail = {}) {
        this.dispatchEvent(new CustomEvent(name, {
            bubbles: true,
            composed: true,
            detail
        }));
    }
}

// Register custom element
customElements.define('plantuml-renderer', PlantUMLRenderer);

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PlantUMLRenderer;
}