/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Playground
   v0.2.5 - Surgical Override: Add transformation mode support
   
   Adds:
   - Transformation dropdown in maximize toolbar
   - Load/refresh transformations from server
   - Pass transformation to API calls
   ═══════════════════════════════════════════════════════════════════════════════ */

// Store current transformation
Playground.prototype.currentTransformation = 'default';
Playground.prototype.availableTransformations = [];

/**
 * NEW: Load available transformations from server
 */
Playground.prototype.loadTransformations = async function() {
    try {
        const transformations = await window.apiClient.getTransformations();
        this.availableTransformations = transformations;
        this.updateTransformationDropdowns();
        console.log('Loaded transformations:', transformations.map(t => t.name));
    } catch (error) {
        console.error('Failed to load transformations:', error);
        // Fallback to default
        this.availableTransformations = [
            { name: 'default', label: 'Default', description: 'Standard HTML to MGraph conversion' }
        ];
        this.updateTransformationDropdowns();
    }
};

/**
 * NEW: Update all transformation dropdowns with available options
 */
Playground.prototype.updateTransformationDropdowns = function() {
    const dropdowns = document.querySelectorAll('.transformation-select');
    
    dropdowns.forEach(dropdown => {
        const currentValue = dropdown.value || 'default';
        dropdown.innerHTML = '';
        
        this.availableTransformations.forEach(t => {
            const option = document.createElement('option');
            option.value = t.name;
            option.textContent = t.label;
            option.title = t.description;
            if (t.name === currentValue) {
                option.selected = true;
            }
            dropdown.appendChild(option);
        });
    });
};

/**
 * NEW: Set current transformation
 */
Playground.prototype.setTransformation = function(transformationName) {
    this.currentTransformation = transformationName;
    
    // Sync all transformation dropdowns
    const dropdowns = document.querySelectorAll('.transformation-select');
    dropdowns.forEach(dropdown => {
        dropdown.value = transformationName;
    });
    
    console.log('Transformation set to:', transformationName);
};

/**
 * OVERRIDE: Render graph with transformation
 */
const originalRenderGraphV025 = Playground.prototype.renderGraph;
Playground.prototype.renderGraph = async function() {
    if (this.isRendering) return;

    const html = this.htmlInput ? this.htmlInput.getHtml() : this.currentHtml;

    if (!html || !html.trim()) {
        this.statsToolbar?.showError(
            'No HTML to render',
            'Please enter some HTML or fetch from a URL first.',
            ''
        );
        return;
    }

    this.isRendering = true;
    this.statsToolbar?.setRenderingState(true);
    this.statsToolbar?.hideError();
    this.statsToolbar?.clearStats();
    this.graphCanvas?.showLoading();

    const renderer = this.graphCanvas?.getCurrentRenderer() || 'dot';
    const transformation = this.currentTransformation || 'default';
    const request = this.buildRequest();

    try {
        const apiStartTime = performance.now();

        // Call API with transformation parameter
        let response;
        switch (renderer) {
            case 'dot':
                response = await window.apiClient.htmlToDot(request, transformation);
                break;
            case 'visjs':
                response = await window.apiClient.htmlToVisJs(request, transformation);
                break;
            case 'd3':
                response = await window.apiClient.htmlToD3(request, transformation);
                break;
            case 'cytoscape':
                response = await window.apiClient.htmlToCytoscape(request, transformation);
                break;
            case 'mermaid':
                response = await window.apiClient.htmlToMermaid(request, transformation);
                break;
            default:
                throw new Error(`Unknown renderer: ${renderer}`);
        }

        const apiEndTime = performance.now();
        this.currentApiMs = Math.round(apiEndTime - apiStartTime);

        // Update stats
        if (response.stats) {
            this.currentStats = response.stats;
            this.statsToolbar?.setStats(response.stats);
        }

        // Render
        const renderStartTime = performance.now();
        await this.renderWithFormat(renderer, response);
        const renderEndTime = performance.now();

        // Update timing
        this.statsToolbar?.setTiming({
            api_ms: this.currentApiMs,
            server_ms: Math.round((response.duration || 0) * 1000),
            dot_size: response.dot_size || response.mermaid_size || 0,
            render_ms: Math.round(renderEndTime - renderStartTime)
        });

        // Update max stats if in maximize mode
        this.updateMaxStats();

    } catch (error) {
        console.error('Render error:', error);
        this.statsToolbar?.showError(
            'API Error',
            error.message || 'Failed to call the API.',
            'Check that the server is running and try again.'
        );
        this.graphCanvas?.showError('API request failed', error.message);
    } finally {
        this.isRendering = false;
        this.statsToolbar?.setRenderingState(false);
    }
};

/**
 * OVERRIDE: Initialize maximize mode with transformation dropdown
 */
const originalInitMaximizeMode = Playground.prototype.initMaximizeMode;
Playground.prototype.initMaximizeMode = function() {
    // Add maximize toolbar to DOM
    const toolbar = document.createElement('div');
    toolbar.className = 'maximize-toolbar';
    toolbar.innerHTML = `
        <div class="maximize-toolbar-left">
            <button class="max-toolbar-btn" id="minimize-btn" title="Exit fullscreen (Esc)">
                ✕ Exit
            </button>
            <div class="max-toolbar-separator"></div>
            <select class="max-renderer-select" id="max-renderer-select">
                <option value="dot">DOT / Graphviz</option>
                <option value="visjs">vis.js Network</option>
                <option value="d3">D3 (Force Layout)</option>
                <option value="cytoscape">Cytoscape.js</option>
                <option value="mermaid">Mermaid</option>
            </select>
            <div class="max-toolbar-separator"></div>
            <select class="max-renderer-select transformation-select" id="max-transformation-select">
                <option value="default">Default</option>
            </select>
            <button class="max-toolbar-btn" id="max-refresh-transforms" title="Refresh transformations from server">
                🔄
            </button>
            <div class="max-toolbar-separator"></div>
            <button class="max-toolbar-btn primary" id="max-reload-btn" title="Re-render (Ctrl+Enter)">
                ↻ Reload
            </button>
        </div>
        <div class="maximize-toolbar-center">
            <span class="max-stats" id="max-stats"></span>
        </div>
        <div class="maximize-toolbar-right">
            <button class="max-toolbar-btn icon-only" id="max-zoom-in" title="Zoom in">+</button>
            <button class="max-toolbar-btn icon-only" id="max-zoom-out" title="Zoom out">−</button>
            <button class="max-toolbar-btn icon-only" id="max-zoom-reset" title="Reset zoom">↺</button>
            <button class="max-toolbar-btn icon-only" id="max-zoom-fit" title="Fit to view">⤢</button>
        </div>
    `;
    document.querySelector('.playground').prepend(toolbar);

    // Add maximize button
    this.addMaximizeButton();

    // Add transformation dropdown to main UI
    this.addMainTransformationDropdown();

    // Bind events
    this.bindMaximizeEvents();
    
    // Bind transformation events
    this.bindTransformationEvents();
    
    // Load transformations from server
    this.loadTransformations();
};

/**
 * NEW: Bind transformation-related events
 */
Playground.prototype.bindTransformationEvents = function() {
    const self = this;
    
    // Transformation select change
    document.getElementById('max-transformation-select')?.addEventListener('change', function(e) {
        self.setTransformation(e.target.value);
        self.renderGraph();
    });
    
    // Refresh transformations button
    document.getElementById('max-refresh-transforms')?.addEventListener('click', function() {
        self.loadTransformations();
    });
};

/**
 * OVERRIDE: Update max stats to include transformation
 */
const originalUpdateMaxStats = Playground.prototype.updateMaxStats;
Playground.prototype.updateMaxStats = function() {
    const statsEl = document.getElementById('max-stats');
    if (!statsEl) return;
    
    if (!this.currentStats) {
        statsEl.textContent = '';
        return;
    }
    
    const stats = this.currentStats;
    const transformation = this.currentTransformation !== 'default' 
        ? ` · ${this.currentTransformation}` 
        : '';
    
    statsEl.textContent = `${stats.total_nodes || 0} nodes · ${stats.total_edges || 0} edges · ${this.currentApiMs || 0}ms${transformation}`;
};

/**
 * OVERRIDE: Enter maximize mode - sync transformation dropdown
 */
const originalEnterMaximizeMode = Playground.prototype.enterMaximizeMode;
Playground.prototype.enterMaximizeMode = function() {
    const playground = document.querySelector('.playground');
    playground.classList.add('maximized');
    
    // Sync renderer select
    const mainSelect = document.querySelector('#renderer-select');
    const maxSelect = document.getElementById('max-renderer-select');
    if (mainSelect && maxSelect) {
        maxSelect.value = mainSelect.value;
    }
    
    // Sync transformation select
    const maxTransformSelect = document.getElementById('max-transformation-select');
    if (maxTransformSelect) {
        maxTransformSelect.value = this.currentTransformation;
    }
    
    // Update stats display
    this.updateMaxStats();
    
    // Trigger resize
    setTimeout(() => window.dispatchEvent(new Event('resize')), 50);
};

/**
 * OVERRIDE: Fix renderer selection in maximize mode
 */
Playground.prototype.bindMaximizeEvents = function() {
    const self = this;
    const playground = document.querySelector('.playground');

    // Maximize button
    document.addEventListener('click', function(e) {
        if (e.target.id === 'maximize-btn' || e.target.closest('#maximize-btn')) {
            self.enterMaximizeMode();
        }
    });

    // Minimize button
    document.getElementById('minimize-btn')?.addEventListener('click', function() {
        self.exitMaximizeMode();
    });

    // Reload button
    document.getElementById('max-reload-btn')?.addEventListener('click', function() {
        self.renderGraph();
    });

    // Zoom buttons
    document.getElementById('max-zoom-in')?.addEventListener('click', function() {
        self.zoomIn();
    });
    document.getElementById('max-zoom-out')?.addEventListener('click', function() {
        self.zoomOut();
    });
    document.getElementById('max-zoom-reset')?.addEventListener('click', function() {
        self.zoomReset();
    });
    document.getElementById('max-zoom-fit')?.addEventListener('click', function() {
        self.zoomFit();
    });

    // Renderer select in maximize toolbar - FIX: update graphCanvas directly
    document.getElementById('max-renderer-select')?.addEventListener('change', function(e) {
        const newRenderer = e.target.value;

        // Sync with main renderer select
        const mainSelect = document.querySelector('#renderer-select');
        if (mainSelect) {
            mainSelect.value = newRenderer;
            // Trigger change event on main select to update graphCanvas
            mainSelect.dispatchEvent(new Event('change', { bubbles: true }));
        }

        // Re-render with new renderer
        self.renderGraph();
    });

    // Escape key to exit
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && playground.classList.contains('maximized')) {
            self.exitMaximizeMode();
        }
    });

    // Sync renderer selects when changed elsewhere
    document.addEventListener('renderer-changed', function(e) {
        const maxSelect = document.getElementById('max-renderer-select');
        if (maxSelect && e.detail?.renderer) {
            maxSelect.value = e.detail.renderer;
        }
    });
};

/**
 * OVERRIDE: Update transformation dropdowns to include main UI dropdown
 */
const originalUpdateTransformationDropdowns = Playground.prototype.updateTransformationDropdowns;
Playground.prototype.updateTransformationDropdowns = function() {
    const dropdowns = document.querySelectorAll('.transformation-select');

    dropdowns.forEach(dropdown => {
        const currentValue = dropdown.value || this.currentTransformation || 'default';
        dropdown.innerHTML = '';

        this.availableTransformations.forEach(t => {
            const option = document.createElement('option');
            option.value = t.name;
            option.textContent = t.label;
            option.title = t.description;
            if (t.name === currentValue) {
                option.selected = true;
            }
            dropdown.appendChild(option);
        });
    });
};

/**
 * OVERRIDE: setTransformation to sync all dropdowns including main
 */
const originalSetTransformation = Playground.prototype.setTransformation;
Playground.prototype.setTransformation = function(transformationName) {
    this.currentTransformation = transformationName;

    // Sync ALL transformation dropdowns (main + maximize)
    const dropdowns = document.querySelectorAll('.transformation-select');
    dropdowns.forEach(dropdown => {
        dropdown.value = transformationName;
    });

    console.log('Transformation set to:', transformationName);
};

/**
 * NEW: Add transformation dropdown to main UI (next to Renderer dropdown)
 */
Playground.prototype.addMainTransformationDropdown = function() {
    // Check if already added
    if (document.getElementById('main-transformation-select')) return;

    // Find the canvas-toolbar-left where the renderer selector lives
    const toolbarLeft = document.querySelector('.canvas-toolbar-left');

    if (toolbarLeft) {
        const container = document.createElement('div');
        container.className = 'renderer-selector transformation-select-container';
        container.innerHTML = `
            <label for="main-transformation-select">Transform:</label>
            <select class="transformation-select" id="main-transformation-select">
                <option value="default">Default</option>
            </select>
        `;

        // Insert after renderer-selector
        const rendererSelector = toolbarLeft.querySelector('.renderer-selector');
        if (rendererSelector) {
            rendererSelector.insertAdjacentElement('afterend', container);
        } else {
            toolbarLeft.appendChild(container);
        }

        // Bind change event
        document.getElementById('main-transformation-select')?.addEventListener('change', (e) => {
            this.setTransformation(e.target.value);
            this.renderGraph();
        });

        console.log('Main transformation dropdown added to canvas toolbar');
    } else {
        console.warn('Could not find .canvas-toolbar-left');
    }
};

console.log('Playground v0.2.5 surgical override loaded (transformation support)');
