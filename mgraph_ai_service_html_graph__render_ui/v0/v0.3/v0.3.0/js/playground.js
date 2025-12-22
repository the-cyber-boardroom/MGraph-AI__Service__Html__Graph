/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Playground Orchestrator
   v0.3.0 - Consolidated from v0.2.0 → v0.2.3 → v0.2.4 → v0.2.5 → v0.2.6 → v0.2.9 → v0.2.10

   Merged features:
   - Base playground with 5 renderers (v0.2.0)
   - Native format API routing per renderer (v0.2.3)
   - Maximize/fullscreen canvas mode (v0.2.4)
   - Transformation mode support (v0.2.5)
   - Keyboard shortcuts integration (v0.2.6)
   - Tree and tree_text engine support (v0.2.9)
   - Server reload detection integration (v0.2.10)
   ═══════════════════════════════════════════════════════════════════════════════ */

/**
 * Playground Controller
 * Orchestrates communication between components and API
 */
class Playground {
    constructor() {
        this.htmlInput = null;
        this.configPanel = null;
        this.statsToolbar = null;
        this.graphCanvas = null;
        this.urlInput = null;

        // All renderers
        this.dotRenderer = null;
        this.visRenderer = null;
        this.d3Renderer = null;
        this.cytoscapeRenderer = null;
        this.mermaidRenderer = null;
        this.treeRenderer = null;
        this.treeTextRenderer = null;

        this.currentHtml = '';
        this.currentConfig = {};
        this.currentDot = null;
        this.currentStats = null;
        this.currentApiMs = 0;
        this.currentServerMs = 0;
        this.currentDotSize = 0;
        this.isRendering = false;

        // Transformation support (from v0.2.5)
        this.currentTransformation = 'default';
        this.availableTransformations = [];
        this.transformations = ['default'];

        // Keyboard shortcuts (from v0.2.6)
        this.keyboardShortcuts = null;

        // Debounce timer for auto-render
        this.autoRenderTimer = null;
        this.autoRenderDelay = 800;
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Initialization
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Initialize the playground
     */
    init() {
        // Get component references
        this.htmlInput = document.querySelector('html-input');
        this.configPanel = document.querySelector('config-panel');
        this.statsToolbar = document.querySelector('stats-toolbar');
        this.graphCanvas = document.querySelector('graph-canvas');
        this.urlInput = document.querySelector('url-input');

        // Get all renderer references
        this.dotRenderer = document.querySelector('dot-renderer');
        this.visRenderer = document.querySelector('vis-renderer');
        this.d3Renderer = document.querySelector('d3-renderer');
        this.cytoscapeRenderer = document.querySelector('cytoscape-renderer');
        this.mermaidRenderer = document.querySelector('mermaid-renderer');
        this.treeRenderer = document.querySelector('tree-renderer');
        this.treeTextRenderer = document.querySelector('tree-text-renderer');

        // Set target canvas for renderers that need it
        const canvasArea = this.graphCanvas?.canvasArea;
        if (canvasArea) {
            if (this.visRenderer) this.visRenderer.setTargetCanvas(canvasArea);
            if (this.d3Renderer) this.d3Renderer.setTargetCanvas(canvasArea);
            if (this.cytoscapeRenderer) this.cytoscapeRenderer.setTargetCanvas(canvasArea);
            if (this.mermaidRenderer) this.mermaidRenderer.setTargetCanvas(canvasArea);
            if (this.treeRenderer) this.treeRenderer.setTargetCanvas(canvasArea);
            if (this.treeTextRenderer) this.treeTextRenderer.setTargetCanvas(canvasArea);
        }

        // Setup event listeners
        this.setupEventListeners();

        // Initialize maximize mode (from v0.2.4)
        this.initMaximizeMode();

        // Initialize keyboard shortcuts (from v0.2.6)
        this.initKeyboardShortcuts();

        // Load transformations (from v0.2.5)
        this.loadTransformations();

        // Check for sample or URL in query params
        this.loadFromUrl();

        console.log('Playground v0.3.0 initialized (7 renderers: DOT, vis.js, D3, Cytoscape, Mermaid, Tree, Tree Text)');
    }

    /**
     * Setup event listeners for component communication
     */
    setupEventListeners() {
        // HTML changed - trigger debounced auto-render
        document.addEventListener('html-changed', (e) => {
            this.currentHtml = e.detail.html;
            this.currentDot = null;
            this.scheduleAutoRender();
        });

        // Config changed - trigger render
        document.addEventListener('config-changed', (e) => {
            this.currentConfig = e.detail.config;
            this.currentDot = null;
            if (this.currentHtml && this.currentHtml.trim()) {
                this.scheduleAutoRender(300);
            }
        });

        // Renderer changed - re-render
        document.addEventListener('renderer-changed', (e) => {
            const newRenderer = e.detail.renderer;
            console.log('Renderer changed to:', newRenderer);

            const html = this.htmlInput?.getHtml?.() || this.currentHtml;
            if (html && html.trim()) {
                this.renderGraph();
            }
        });

        // URL HTML fetched
        document.addEventListener('url-html-fetched', (e) => {
            this.handleUrlHtmlFetched(e.detail);
        });

        // Render requested (from stats-toolbar button)
        document.addEventListener('render-requested', () => {
            this.renderGraph();
        });

        // Keyboard shortcut (Ctrl+Enter to render)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.renderGraph();
            }
        });
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Transformation Support (from v0.2.5)
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Load available transformations from server
     */
    async loadTransformations() {
        try {
            const transformations = await window.apiClient.getTransformations();
            this.availableTransformations = transformations;
            this.transformations = transformations.map(t => t.name || t);
            this.updateTransformationDropdowns();
            console.log('Loaded transformations:', this.transformations);
        } catch (error) {
            console.error('Failed to load transformations:', error);
            this.availableTransformations = [
                { name: 'default', label: 'Default', description: 'Standard HTML to MGraph conversion' }
            ];
            this.transformations = ['default'];
            this.updateTransformationDropdowns();
        }
    }

    /**
     * Update all transformation dropdowns with available options
     */
    updateTransformationDropdowns() {
        const dropdowns = document.querySelectorAll('.transformation-select');
        
        dropdowns.forEach(dropdown => {
            const currentValue = dropdown.value || this.currentTransformation || 'default';
            dropdown.innerHTML = '';
            
            this.availableTransformations.forEach(t => {
                const option = document.createElement('option');
                option.value = t.name || t;
                option.textContent = t.label || t.name || t;
                option.title = t.description || '';
                if ((t.name || t) === currentValue) {
                    option.selected = true;
                }
                dropdown.appendChild(option);
            });
        });
    }

    /**
     * Set current transformation
     */
    setTransformation(transformationName) {
        this.currentTransformation = transformationName;
        
        const dropdowns = document.querySelectorAll('.transformation-select');
        dropdowns.forEach(dropdown => {
            dropdown.value = transformationName;
        });
        
        console.log('Transformation set to:', transformationName);
    }

    /**
     * Add transformation dropdown to main UI
     */
    addMainTransformationDropdown() {
        if (document.getElementById('main-transformation-select')) return;

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

            const rendererSelector = toolbarLeft.querySelector('.renderer-selector');
            if (rendererSelector) {
                rendererSelector.insertAdjacentElement('afterend', container);
            } else {
                toolbarLeft.appendChild(container);
            }

            document.getElementById('main-transformation-select')?.addEventListener('change', (e) => {
                this.setTransformation(e.target.value);
                this.renderGraph();
            });
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Maximize Mode (from v0.2.4 + v0.2.5 fixes)
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Initialize maximize mode UI
     */
    initMaximizeMode() {
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
                    <option value="tree">Tree (JSON)</option>
                    <option value="tree_text">Tree (Text)</option>
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
        document.querySelector('.playground')?.prepend(toolbar);

        this.addMaximizeButton();
        this.addMainTransformationDropdown();
        this.bindMaximizeEvents();
    }

    /**
     * Add maximize button to stats toolbar
     */
    addMaximizeButton() {
        const statsToolbar = document.querySelector('stats-toolbar');
        if (!statsToolbar) return;

        setTimeout(() => {
            const toolbar = statsToolbar.querySelector('.stats-toolbar') || statsToolbar;
            const renderBtn = toolbar.querySelector('.render-btn') || toolbar.querySelector('button');

            if (renderBtn && renderBtn.parentElement) {
                const maxBtn = document.createElement('button');
                maxBtn.className = 'maximize-btn';
                maxBtn.id = 'maximize-btn';
                maxBtn.innerHTML = '⛶';
                maxBtn.title = 'Maximize canvas (fullscreen)';
                renderBtn.parentElement.insertBefore(maxBtn, renderBtn.nextSibling);
            }
        }, 100);
    }

    /**
     * Bind maximize mode events
     */
    bindMaximizeEvents() {
        const self = this;
        const playground = document.querySelector('.playground');

        document.addEventListener('click', function(e) {
            if (e.target.id === 'maximize-btn' || e.target.closest('#maximize-btn')) {
                self.enterMaximizeMode();
            }
        });

        document.getElementById('minimize-btn')?.addEventListener('click', function() {
            self.exitMaximizeMode();
        });

        document.getElementById('max-reload-btn')?.addEventListener('click', function() {
            self.renderGraph();
        });

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

        document.getElementById('max-renderer-select')?.addEventListener('change', function(e) {
            const newRenderer = e.target.value;
            const mainSelect = document.querySelector('#renderer-select');
            if (mainSelect) {
                mainSelect.value = newRenderer;
                mainSelect.dispatchEvent(new Event('change', { bubbles: true }));
            }
            self.renderGraph();
        });

        document.getElementById('max-transformation-select')?.addEventListener('change', function(e) {
            self.setTransformation(e.target.value);
            self.renderGraph();
        });

        document.getElementById('max-refresh-transforms')?.addEventListener('click', function() {
            self.loadTransformations();
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && playground?.classList.contains('maximized')) {
                self.exitMaximizeMode();
            }
        });

        document.addEventListener('renderer-changed', function(e) {
            const maxSelect = document.getElementById('max-renderer-select');
            if (maxSelect && e.detail?.renderer) {
                maxSelect.value = e.detail.renderer;
            }
        });
    }

    /**
     * Enter maximize mode
     */
    enterMaximizeMode() {
        const playground = document.querySelector('.playground');
        playground?.classList.add('maximized');

        const mainSelect = document.querySelector('#renderer-select');
        const maxSelect = document.getElementById('max-renderer-select');
        if (mainSelect && maxSelect) {
            maxSelect.value = mainSelect.value;
        }

        const maxTransformSelect = document.getElementById('max-transformation-select');
        if (maxTransformSelect) {
            maxTransformSelect.value = this.currentTransformation;
        }

        this.updateMaxStats();
        setTimeout(() => window.dispatchEvent(new Event('resize')), 50);
    }

    /**
     * Exit maximize mode
     */
    exitMaximizeMode() {
        const playground = document.querySelector('.playground');
        playground?.classList.remove('maximized');
        setTimeout(() => window.dispatchEvent(new Event('resize')), 50);
    }

    /**
     * Toggle maximize mode
     */
    toggleMaximizeMode() {
        const playground = document.querySelector('.playground');
        if (playground?.classList.contains('maximized')) {
            this.exitMaximizeMode();
        } else {
            this.enterMaximizeMode();
        }
    }

    /**
     * Update stats in maximize toolbar
     */
    updateMaxStats() {
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
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Keyboard Shortcuts (from v0.2.6)
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Initialize keyboard shortcuts system
     */
    initKeyboardShortcuts() {
        if (typeof KeyboardShortcuts === 'undefined') {
            console.warn('KeyboardShortcuts not loaded');
            return;
        }

        this.keyboardShortcuts = new KeyboardShortcuts({
            configUrl: this.getShortcutsConfigUrl()
        });
        this.bindShortcutEvents();
        this.addShortcutsLinks();
        console.log('Keyboard shortcuts initialized');
    }

    /**
     * Get shortcuts config URL
     */
    getShortcutsConfigUrl() {
        return './js/keyboard-shortcuts.json';
    }

    /**
     * Bind all shortcut event listeners
     */
    bindShortcutEvents() {
        const self = this;

        document.addEventListener('shortcut:reload', function() {
            self.renderGraph();
        });

        document.addEventListener('shortcut:maximize-toggle', function() {
            self.toggleMaximizeMode();
        });

        document.addEventListener('shortcut:zoom-in', function() {
            self.zoomIn();
        });

        document.addEventListener('shortcut:zoom-out', function() {
            self.zoomOut();
        });

        document.addEventListener('shortcut:zoom-reset', function() {
            self.zoomReset();
        });

        document.addEventListener('shortcut:zoom-fit', function() {
            self.zoomFit();
        });

        document.addEventListener('shortcut:transformation-next', function() {
            self.cycleTransformation(1);
        });

        document.addEventListener('shortcut:transformation-prev', function() {
            self.cycleTransformation(-1);
        });

        document.addEventListener('shortcut:transformation-select', function(e) {
            var index = e.detail?.index;
            if (typeof index === 'number') {
                self.selectTransformationByIndex(index);
            }
        });

        document.addEventListener('shortcut:engine-next', function() {
            self.cycleEngine(1);
        });

        document.addEventListener('shortcut:engine-prev', function() {
            self.cycleEngine(-1);
        });

        document.addEventListener('shortcut:help-toggle', function() {
            self.toggleShortcutsHelp();
        });

        document.addEventListener('shortcut:escape', function() {
            self.handleEscape();
        });
    }

    /**
     * Add shortcuts links to UI
     */
    addShortcutsLinks() {
        const self = this;

        const toolbarRight = document.querySelector('.canvas-toolbar-right');
        if (toolbarRight) {
            const link = document.createElement('button');
            link.className = 'shortcuts-link';
            link.innerHTML = '⌨️ <span>Shortcuts</span>';
            link.title = 'Keyboard Shortcuts (H)';
            link.addEventListener('click', function() {
                self.toggleShortcutsHelp();
            });
            toolbarRight.insertBefore(link, toolbarRight.firstChild);
        }

        this.addShortcutsLinkStyles();
    }

    /**
     * Add styles for shortcuts link
     */
    addShortcutsLinkStyles() {
        if (document.getElementById('shortcuts-link-styles')) return;

        const style = document.createElement('style');
        style.id = 'shortcuts-link-styles';
        style.textContent = `
            .shortcuts-link {
                display: inline-flex;
                align-items: center;
                gap: 4px;
                background: transparent;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 13px;
                color: #666;
                cursor: pointer;
                transition: all 0.2s;
            }
            .shortcuts-link:hover {
                background: #f5f5f5;
                border-color: #ccc;
                color: #333;
            }
            .shortcuts-link span {
                font-size: 12px;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Cycle through transformations
     */
    cycleTransformation(direction) {
        if (!this.transformations || this.transformations.length <= 1) {
            const select = document.querySelector('#main-transformation-select, #max-transformation-select');
            if (select && select.options.length > 1) {
                this.transformations = Array.from(select.options).map(opt => opt.value);
                this.currentTransformation = select.value;
            }
        }

        if (!this.transformations || this.transformations.length === 0) {
            this.showToast('Transformations not loaded');
            return;
        }

        const currentIndex = this.transformations.indexOf(this.currentTransformation);
        const newIndex = (currentIndex + direction + this.transformations.length) % this.transformations.length;
        const newTransformation = this.transformations[newIndex];

        this.setTransformation(newTransformation);
        this.renderGraph();
        this.showToast('Transform: ' + this.formatTransformationName(newTransformation));
    }

    /**
     * Select transformation by index
     */
    selectTransformationByIndex(index) {
        if (!this.transformations || this.transformations.length === 0) {
            this.showToast('Transformations not loaded');
            return;
        }

        if (index >= 0 && index < this.transformations.length) {
            const newTransformation = this.transformations[index];
            this.setTransformation(newTransformation);
            this.renderGraph();
            this.showToast('Transform: ' + this.formatTransformationName(newTransformation));
        }
    }

    /**
     * Format transformation name for display
     */
    formatTransformationName(name) {
        if (!name) return 'Unknown';
        return name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }

    /**
     * Cycle through engines
     */
    cycleEngine(direction) {
        const engines = ['dot', 'visjs', 'd3', 'cytoscape', 'mermaid', 'tree', 'tree_text'];
        const currentEngine = this.getCurrentEngine();
        let currentIndex = engines.indexOf(currentEngine);
        if (currentIndex === -1) currentIndex = 0;

        const newIndex = (currentIndex + direction + engines.length) % engines.length;
        const newEngine = engines[newIndex];

        this.setEngine(newEngine);
        this.renderGraph();
        this.showToast('Engine: ' + this.formatEngineName(newEngine));
    }

    /**
     * Get current engine from select
     */
    getCurrentEngine() {
        const select = document.querySelector('#renderer-select');
        return select ? select.value : 'dot';
    }

    /**
     * Set engine and sync selects
     */
    setEngine(engine) {
        const mainSelect = document.querySelector('#renderer-select');
        if (mainSelect) {
            mainSelect.value = engine;
            mainSelect.dispatchEvent(new Event('change', { bubbles: true }));
        }

        const maxSelect = document.getElementById('max-renderer-select');
        if (maxSelect) {
            maxSelect.value = engine;
        }
    }

    /**
     * Format engine name for display
     */
    formatEngineName(engine) {
        const names = {
            'dot': 'DOT (Graphviz)',
            'visjs': 'VisJS',
            'd3': 'D3 Force',
            'cytoscape': 'Cytoscape',
            'mermaid': 'Mermaid',
            'tree': 'Tree (JSON)',
            'tree_text': 'Tree (Text)'
        };
        return names[engine] || engine;
    }

    /**
     * Toggle shortcuts help panel
     */
    toggleShortcutsHelp() {
        if (this.keyboardShortcuts) {
            this.keyboardShortcuts.toggleHelp();
        }
    }

    /**
     * Handle escape key
     */
    handleEscape() {
        if (this.keyboardShortcuts && this.keyboardShortcuts.helpVisible) {
            this.keyboardShortcuts.hideHelp();
            return;
        }

        const playground = document.querySelector('.playground');
        if (playground?.classList.contains('maximized')) {
            this.exitMaximizeMode();
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Zoom Controls (from v0.2.4 + v0.2.6)
    // ═══════════════════════════════════════════════════════════════════════════════

    zoomIn() {
        const renderer = this.graphCanvas?.getCurrentRenderer();
        if (renderer === 'visjs' && this.visRenderer?.network) {
            const scale = this.visRenderer.network.getScale();
            this.visRenderer.network.moveTo({ scale: scale * 1.2 });
        } else if (renderer === 'd3' && this.d3Renderer?.zoomIn) {
            this.d3Renderer.zoomIn();
        } else if (renderer === 'cytoscape' && this.cytoscapeRenderer?.cy) {
            this.cytoscapeRenderer.cy.zoom(this.cytoscapeRenderer.cy.zoom() * 1.2);
        }
        this.showToast('Zoom In');
    }

    zoomOut() {
        const renderer = this.graphCanvas?.getCurrentRenderer();
        if (renderer === 'visjs' && this.visRenderer?.network) {
            const scale = this.visRenderer.network.getScale();
            this.visRenderer.network.moveTo({ scale: scale / 1.2 });
        } else if (renderer === 'd3' && this.d3Renderer?.zoomOut) {
            this.d3Renderer.zoomOut();
        } else if (renderer === 'cytoscape' && this.cytoscapeRenderer?.cy) {
            this.cytoscapeRenderer.cy.zoom(this.cytoscapeRenderer.cy.zoom() / 1.2);
        }
        this.showToast('Zoom Out');
    }

    zoomReset() {
        const renderer = this.graphCanvas?.getCurrentRenderer();
        if (renderer === 'visjs' && this.visRenderer?.network) {
            this.visRenderer.network.moveTo({ scale: 1 });
        } else if (renderer === 'd3' && this.d3Renderer?.zoomReset) {
            this.d3Renderer.zoomReset();
        } else if (renderer === 'cytoscape' && this.cytoscapeRenderer?.cy) {
            this.cytoscapeRenderer.cy.zoom(1);
            this.cytoscapeRenderer.cy.center();
        }
        this.showToast('Zoom Reset');
    }

    zoomFit() {
        const renderer = this.graphCanvas?.getCurrentRenderer();
        if (renderer === 'visjs' && this.visRenderer?.network) {
            this.visRenderer.network.fit({ animation: true });
        } else if (renderer === 'd3' && this.d3Renderer?.fitToView) {
            this.d3Renderer.fitToView();
        } else if (renderer === 'cytoscape' && this.cytoscapeRenderer?.cy) {
            this.cytoscapeRenderer.cy.fit(undefined, 50);
        }
        this.showToast('Fit to View');
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Toast Notifications (from v0.2.6)
    // ═══════════════════════════════════════════════════════════════════════════════

    showToast(message, duration = 1500) {
        const existing = document.getElementById('playground-toast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.id = 'playground-toast';
        toast.className = 'playground-toast';
        toast.textContent = message;

        this.addToastStyles();
        document.body.appendChild(toast);

        requestAnimationFrame(function() {
            toast.classList.add('visible');
        });

        setTimeout(function() {
            toast.classList.remove('visible');
            setTimeout(function() { toast.remove(); }, 300);
        }, duration);
    }

    addToastStyles() {
        if (document.getElementById('playground-toast-styles')) return;

        const style = document.createElement('style');
        style.id = 'playground-toast-styles';
        style.textContent = `
            .playground-toast {
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%) translateY(20px);
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                z-index: 10001;
                opacity: 0;
                transition: opacity 0.3s, transform 0.3s;
                pointer-events: none;
            }
            .playground-toast.visible {
                opacity: 1;
                transform: translateX(-50%) translateY(0);
            }
        `;
        document.head.appendChild(style);
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // URL and Sample Loading
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Handle HTML fetched from URL
     */
    handleUrlHtmlFetched(detail) {
        const { html, url, contentType } = detail;

        if (this.htmlInput) {
            this.htmlInput.setHtml(html);
        }

        this.currentHtml = html;
        this.currentDot = null;
        console.log(`Fetched HTML from ${url} (${contentType})`);

        this.scheduleAutoRender(500);
    }

    /**
     * Load from URL query parameters
     */
    loadFromUrl() {
        const params = new URLSearchParams(window.location.search);

        const sample = params.get('sample');
        if (sample && this.htmlInput) {
            this.htmlInput.loadSample(sample);
            return;
        }

        const fetchUrl = params.get('url');
        if (fetchUrl && this.urlInput) {
            this.urlInput.setUrl(fetchUrl);
            setTimeout(() => this.urlInput.fetchUrl(), 100);
        }

        const renderer = params.get('renderer');
        if (renderer) {
            const select = this.graphCanvas?.querySelector('#renderer-select');
            if (select) {
                select.value = renderer;
            }
        }

        const transformation = params.get('transformation');
        if (transformation) {
            this.currentTransformation = transformation;
        }
    }

    /**
     * Schedule auto-render with debounce
     */
    scheduleAutoRender(delay = null) {
        if (this.autoRenderTimer) {
            clearTimeout(this.autoRenderTimer);
            this.autoRenderTimer = null;
        }

        if (this.isRendering) return;

        const html = this.htmlInput ? this.htmlInput.getHtml() : this.currentHtml;
        if (!html || !html.trim()) return;

        const renderDelay = delay !== null ? delay : this.autoRenderDelay;
        this.autoRenderTimer = setTimeout(() => {
            this.autoRenderTimer = null;
            this.renderGraph();
        }, renderDelay);
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Request Building
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Build the API request object
     */
    buildRequest() {
        const html = this.htmlInput ? this.htmlInput.getHtml() : this.currentHtml;
        const config = this.configPanel ? this.configPanel.getConfig() : this.currentConfig;

        return {
            html: html,
            preset: config.preset || 'FULL_DETAIL',
            show_tag_nodes: config.show_tag_nodes !== false,
            show_attr_nodes: config.show_attr_nodes !== false,
            show_text_nodes: config.show_text_nodes !== false,
            color_scheme: config.color_scheme || 'DEFAULT'
        };
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Main Render Logic (from v0.2.3 + v0.2.9)
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Render the graph using the appropriate API endpoint for the selected renderer
     */
    async renderGraph() {
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

            // Route to appropriate API endpoint based on renderer
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
                case 'tree':
                    response = await window.apiClient.htmlToTree(request, transformation);
                    break;
                case 'tree_text':
                    response = await window.apiClient.htmlToTreeText(request, transformation);
                    break;
                default:
                    throw new Error(`Unknown renderer: ${renderer}`);
            }

            const apiEndTime = performance.now();
            this.currentApiMs = Math.round(apiEndTime - apiStartTime);

            // Update stats from response
            if (response.stats) {
                this.currentStats = response.stats;
                this.statsToolbar?.setStats(response.stats);
            }

            // Render with the appropriate renderer
            const renderStartTime = performance.now();
            await this.renderWithFormat(renderer, response);
            const renderEndTime = performance.now();

            // Update timing
            this.statsToolbar?.setTiming({
                api_ms: this.currentApiMs,
                server_ms: Math.round((response.duration || 0) * 1000),
                dot_size: response.dot_size || response.mermaid_size || response.tree_text_size || 0,
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
    }

    /**
     * Render with the appropriate renderer using native format
     */
    async renderWithFormat(renderer, response) {
        switch (renderer) {
            case 'dot':
                await this.renderWithDot(response);
                break;
            case 'visjs':
                await this.renderWithVisJs(response);
                break;
            case 'd3':
                await this.renderWithD3(response);
                break;
            case 'cytoscape':
                await this.renderWithCytoscape(response);
                break;
            case 'mermaid':
                await this.renderWithMermaid(response);
                break;
            case 'tree':
            case 'tree_text':
                await this.renderTreeFormat(renderer, response);
                break;
        }
    }

    /**
     * Render with DOT/viz.js
     */
    async renderWithDot(response) {
        if (!this.dotRenderer) {
            throw new Error('DOT renderer not available');
        }
        await this.dotRenderer.renderDot(response.dot);
        this.enablePanning();
    }

    /**
     * Render with vis.js using native format
     */
    async renderWithVisJs(response) {
        if (!this.visRenderer) {
            throw new Error('vis.js renderer not available');
        }
        await this.visRenderer.render({
            nodes: response.nodes,
            edges: response.edges
        });
    }

    /**
     * Render with D3.js using native format
     */
    async renderWithD3(response) {
        if (!this.d3Renderer) {
            throw new Error('D3.js renderer not available');
        }
        await this.d3Renderer.render({
            nodes: response.nodes,
            links: response.links
        });
    }

    /**
     * Render with Cytoscape.js using native format
     */
    async renderWithCytoscape(response) {
        if (!this.cytoscapeRenderer) {
            throw new Error('Cytoscape renderer not available');
        }
        await this.cytoscapeRenderer.render({
            elements: response.elements
        });
    }

    /**
     * Render with Mermaid.js using native format
     */
    async renderWithMermaid(response) {
        if (!this.mermaidRenderer) {
            throw new Error('Mermaid renderer not available');
        }
        await this.mermaidRenderer.render({
            mermaid: response.mermaid
        });
    }

    /**
     * Render tree format to canvas (from v0.2.9)
     */
    async renderTreeFormat(renderer, response) {
        const canvasArea = this.graphCanvas?.canvasArea
                        || this.graphCanvas?.querySelector('.canvas-area');

        if (!canvasArea) {
            throw new Error('No canvas area available');
        }

        let rendererEl;
        if (renderer === 'tree') {
            rendererEl = this.treeRenderer;
        } else {
            rendererEl = this.treeTextRenderer;
        }

        if (!rendererEl) {
            throw new Error(`Renderer element not found: ${renderer}`);
        }

        rendererEl.setTargetCanvas(canvasArea);
        await rendererEl.render(response);
    }

    /**
     * Enable panning on the graph canvas (for DOT renderer)
     */
    enablePanning() {
        const canvasArea = this.graphCanvas?.canvasArea;
        const svg = canvasArea?.querySelector('svg');
        if (!svg) return;

        let isPanning = false;
        let startX, startY;
        let scrollLeft, scrollTop;

        canvasArea.style.overflow = 'auto';
        canvasArea.style.cursor = 'grab';

        canvasArea.onmousedown = (e) => {
            if (e.button !== 0) return;
            isPanning = true;
            canvasArea.style.cursor = 'grabbing';
            startX = e.pageX - canvasArea.offsetLeft;
            startY = e.pageY - canvasArea.offsetTop;
            scrollLeft = canvasArea.scrollLeft;
            scrollTop = canvasArea.scrollTop;
            e.preventDefault();
        };

        canvasArea.onmousemove = (e) => {
            if (!isPanning) return;
            const x = e.pageX - canvasArea.offsetLeft;
            const y = e.pageY - canvasArea.offsetTop;
            const walkX = (x - startX) * 1.5;
            const walkY = (y - startY) * 0.5;
            canvasArea.scrollLeft = scrollLeft - walkX;
            canvasArea.scrollTop = scrollTop - walkY;
        };

        canvasArea.onmouseup = () => {
            isPanning = false;
            canvasArea.style.cursor = 'grab';
        };

        canvasArea.onmouseleave = () => {
            isPanning = false;
            canvasArea.style.cursor = 'grab';
        };
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Utility Methods
    // ═══════════════════════════════════════════════════════════════════════════════

    formatBytes(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const playground = new Playground();
    playground.init();
});
