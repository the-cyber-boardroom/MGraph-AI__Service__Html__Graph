/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Playground
   v0.2.4 - Surgical Override: Add maximize/fullscreen canvas mode
   ═══════════════════════════════════════════════════════════════════════════════ */

/**
 * NEW: Initialize maximize mode UI
 */
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

    // Add maximize button to stats-toolbar (next to Render Graph button)
    this.addMaximizeButton();

    // Bind events
    this.bindMaximizeEvents();
};

/**
 * NEW: Add maximize button to stats toolbar
 */
Playground.prototype.addMaximizeButton = function() {
    // Try to find the stats toolbar's button area
    const statsToolbar = document.querySelector('stats-toolbar');
    if (!statsToolbar) return;

    // Wait for component to render
    setTimeout(() => {
        // Look for the toolbar element inside stats-toolbar
        const toolbar = statsToolbar.querySelector('.stats-toolbar')
                     || statsToolbar.querySelector('.toolbar')
                     || statsToolbar;

        // Find the render button area
        const renderBtn = toolbar.querySelector('.render-btn')
                       || toolbar.querySelector('button');

        if (renderBtn && renderBtn.parentElement) {
            const maxBtn = document.createElement('button');
            maxBtn.className = 'maximize-btn';
            maxBtn.id = 'maximize-btn';
            maxBtn.innerHTML = '⛶';
            maxBtn.title = 'Maximize canvas (fullscreen)';

            // Insert after render button
            renderBtn.parentElement.insertBefore(maxBtn, renderBtn.nextSibling);
        }
    }, 100);
};

/**
 * NEW: Bind maximize mode events
 */
Playground.prototype.bindMaximizeEvents = function() {
    const self = this;
    const playground = document.querySelector('.playground');

    // Maximize button (use event delegation for dynamically added button)
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

    // Renderer select in maximize toolbar
    document.getElementById('max-renderer-select')?.addEventListener('change', function(e) {
        const newRenderer = e.target.value;

        // Sync with main renderer select
        const mainSelect = document.querySelector('#renderer-select');
        if (mainSelect) {
            mainSelect.value = newRenderer;
        }

        // Dispatch renderer-changed event
        document.dispatchEvent(new CustomEvent('renderer-changed', {
            detail: { renderer: newRenderer }
        }));
    });

    // Escape key to exit
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && playground.classList.contains('maximized')) {
            self.exitMaximizeMode();
        }
    });

    // Sync renderer selects
    document.addEventListener('renderer-changed', function(e) {
        const maxSelect = document.getElementById('max-renderer-select');
        if (maxSelect && e.detail?.renderer) {
            maxSelect.value = e.detail.renderer;
        }
    });
};

/**
 * NEW: Enter maximize mode
 */
Playground.prototype.enterMaximizeMode = function() {
    const playground = document.querySelector('.playground');
    playground.classList.add('maximized');

    // Sync renderer select
    const mainSelect = document.querySelector('#renderer-select');
    const maxSelect = document.getElementById('max-renderer-select');
    if (mainSelect && maxSelect) {
        maxSelect.value = mainSelect.value;
    }

    // Update stats display
    this.updateMaxStats();

    // Trigger resize for renderers
    setTimeout(() => window.dispatchEvent(new Event('resize')), 50);
};

/**
 * NEW: Exit maximize mode
 */
Playground.prototype.exitMaximizeMode = function() {
    const playground = document.querySelector('.playground');
    playground.classList.remove('maximized');

    // Trigger resize for renderers
    setTimeout(() => window.dispatchEvent(new Event('resize')), 50);
};

/**
 * NEW: Update stats in maximize toolbar
 */
Playground.prototype.updateMaxStats = function() {
    const statsEl = document.getElementById('max-stats');
    if (!statsEl || !this.currentStats) return;

    const stats = this.currentStats;
    statsEl.textContent = `${stats.total_nodes || 0} nodes · ${stats.total_edges || 0} edges · ${this.currentApiMs || 0}ms`;
};

/**
 * NEW: Zoom controls - delegate to current renderer
 */
Playground.prototype.zoomIn = function() {
    const renderer = this.graphCanvas?.getCurrentRenderer();
    if (renderer === 'visjs' && this.visRenderer?.network) {
        const scale = this.visRenderer.network.getScale();
        this.visRenderer.network.moveTo({ scale: scale * 1.2 });
    } else if (renderer === 'd3' && this.d3Renderer?.simulation) {
        // D3 zoom handled via SVG transform
        this.triggerZoom(1.2);
    } else if (renderer === 'cytoscape' && this.cytoscapeRenderer?.cy) {
        this.cytoscapeRenderer.cy.zoom(this.cytoscapeRenderer.cy.zoom() * 1.2);
    }
};

Playground.prototype.zoomOut = function() {
    const renderer = this.graphCanvas?.getCurrentRenderer();
    if (renderer === 'visjs' && this.visRenderer?.network) {
        const scale = this.visRenderer.network.getScale();
        this.visRenderer.network.moveTo({ scale: scale / 1.2 });
    } else if (renderer === 'd3' && this.d3Renderer?.simulation) {
        this.triggerZoom(1 / 1.2);
    } else if (renderer === 'cytoscape' && this.cytoscapeRenderer?.cy) {
        this.cytoscapeRenderer.cy.zoom(this.cytoscapeRenderer.cy.zoom() / 1.2);
    }
};

Playground.prototype.zoomReset = function() {
    const renderer = this.graphCanvas?.getCurrentRenderer();
    if (renderer === 'visjs' && this.visRenderer?.network) {
        this.visRenderer.network.moveTo({ scale: 1 });
    } else if (renderer === 'cytoscape' && this.cytoscapeRenderer?.cy) {
        this.cytoscapeRenderer.cy.zoom(1);
        this.cytoscapeRenderer.cy.center();
    }
};

Playground.prototype.zoomFit = function() {
    const renderer = this.graphCanvas?.getCurrentRenderer();
    if (renderer === 'visjs' && this.visRenderer?.network) {
        this.visRenderer.network.fit({ animation: true });
    } else if (renderer === 'cytoscape' && this.cytoscapeRenderer?.cy) {
        this.cytoscapeRenderer.cy.fit(undefined, 50);
    }
};

Playground.prototype.triggerZoom = function(factor) {
    // Trigger zoom on canvas - works for D3/SVG-based renderers
    const canvas = this.graphCanvas?.canvasArea;
    if (canvas) {
        const event = new WheelEvent('wheel', {
            deltaY: factor > 1 ? -100 : 100,
            ctrlKey: true
        });
        canvas.dispatchEvent(event);
    }
};

// Override renderGraph to also update max stats
const originalRenderGraph = Playground.prototype.renderGraph;
Playground.prototype.renderGraph = async function() {
    await originalRenderGraph.call(this);
    this.updateMaxStats();
};

// Initialize maximize mode after original init
const originalInit = Playground.prototype.init;
Playground.prototype.init = function() {
    originalInit.call(this);
    this.initMaximizeMode();

    // Re-register renderer-changed to trigger re-render
    const self = this;
    document.addEventListener('renderer-changed', function() {
        const html = self.htmlInput?.getHtml?.() || self.currentHtml;
        if (html && html.trim()) {
            self.renderGraph();
        }
    });
};

console.log('Playground v0.2.4 surgical override loaded (maximize mode)');