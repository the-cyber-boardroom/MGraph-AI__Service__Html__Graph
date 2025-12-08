/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Playground Orchestrator
   v0.2.0 - Consolidated from v0.1.x

   Supports 5 renderers: DOT (viz.js), vis.js, D3.js, Cytoscape, Mermaid
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

        this.currentHtml = '';
        this.currentConfig = {};
        this.currentDot = null;      // Cache DOT for renderer switching
        this.currentStats = null;
        this.currentApiMs = 0;
        this.currentServerMs = 0;
        this.currentDotSize = 0;
        this.isRendering = false;

        // Debounce timer for auto-render
        this.autoRenderTimer = null;
        this.autoRenderDelay = 800;
    }

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

        // Set target canvas for renderers that need it
        const canvasArea = this.graphCanvas?.canvasArea;
        if (canvasArea) {
            if (this.visRenderer) this.visRenderer.setTargetCanvas(canvasArea);
            if (this.d3Renderer) this.d3Renderer.setTargetCanvas(canvasArea);
            if (this.cytoscapeRenderer) this.cytoscapeRenderer.setTargetCanvas(canvasArea);
            if (this.mermaidRenderer) this.mermaidRenderer.setTargetCanvas(canvasArea);
        }

        // Setup event listeners
        this.setupEventListeners();

        // Check for sample or URL in query params
        this.loadFromUrl();

        console.log('Playground v0.2.0 initialized (5 renderers: DOT, vis.js, D3, Cytoscape, Mermaid)');
    }

    /**
     * Setup event listeners for component communication
     */
    setupEventListeners() {
        // HTML changed - trigger debounced auto-render
        document.addEventListener('html-changed', (e) => {
            this.currentHtml = e.detail.html;
            this.currentDot = null;  // Clear cached DOT
            this.scheduleAutoRender();
        });

        // Config changed - trigger render
        document.addEventListener('config-changed', (e) => {
            this.currentConfig = e.detail.config;
            this.currentDot = null;  // Clear cached DOT
            if (this.currentHtml && this.currentHtml.trim()) {
                this.scheduleAutoRender(300);
            }
        });

        // Renderer changed - re-render with cached DOT if available
        document.addEventListener('renderer-changed', (e) => {
            const newRenderer = e.detail.renderer;
            console.log('Renderer changed to:', newRenderer);

            // If we have cached DOT, render with new renderer immediately
            if (this.currentDot && this.currentHtml) {
                this.renderWithCurrentRenderer();
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

        // Check for renderer param
        const renderer = params.get('renderer');
        if (renderer) {
            const select = this.graphCanvas?.querySelector('#renderer-select');
            if (select) {
                select.value = renderer;
            }
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

    /**
     * Render the graph
     */
    async renderGraph() {
        if (this.isRendering) return;

        const html = this.htmlInput ? this.htmlInput.getHtml() : this.currentHtml;
        const config = this.configPanel ? this.configPanel.getConfig() : this.currentConfig;

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

        try {
            // Always call API to get DOT (needed by all renderers)
            await this.fetchDotFromApi(html, config);

            // Then render with current renderer
            await this.renderWithCurrentRenderer();

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
     * Fetch DOT from API
     */
    async fetchDotFromApi(html, config) {
        const request = {
            html: html,
            preset: config.preset || 'FULL_DETAIL',
            show_tag_nodes: config.show_tag_nodes !== false,
            show_attr_nodes: config.show_attr_nodes !== false,
            show_text_nodes: config.show_text_nodes !== false,
            color_scheme: config.color_scheme || 'DEFAULT'
        };

        const apiStartTime = performance.now();
        const response = await window.apiClient.htmlToDot(request);
        const apiEndTime = performance.now();
        const apiMs = Math.round(apiEndTime - apiStartTime);

        // Cache the response
        this.currentDot = response.dot;
        this.currentStats = response.stats;
        this.currentApiMs = apiMs;
        this.currentServerMs = response.processing_ms || 0;
        this.currentDotSize = response.dot_size_bytes || response.dot.length;

        // Update stats immediately
        if (response.stats) {
            this.statsToolbar?.setStats(response.stats);
        }

        this.statsToolbar?.setTiming({
            api_ms: apiMs,
            server_ms: response.processing_ms || 0,
            dot_size: response.dot_size_bytes || response.dot.length,
            render_ms: 0
        });

        return response;
    }

    /**
     * Render with the currently selected renderer
     */
    async renderWithCurrentRenderer() {
        if (!this.currentDot) {
            console.warn('No DOT available to render');
            return;
        }

        const renderer = this.graphCanvas?.getCurrentRenderer() || 'dot';
        const renderStartTime = performance.now();

        try {
            switch (renderer) {
                case 'dot':
                    await this.renderWithDot();
                    break;
                case 'visjs':
                    await this.renderWithVisJs();
                    break;
                case 'd3':
                    await this.renderWithD3();
                    break;
                case 'cytoscape':
                    await this.renderWithCytoscape();
                    break;
                case 'mermaid':
                    await this.renderWithMermaid();
                    break;
                default:
                    throw new Error(`Unknown renderer: ${renderer}`);
            }

            const renderEndTime = performance.now();
            const renderMs = Math.round(renderEndTime - renderStartTime);

            this.statsToolbar?.setTiming({
                api_ms: this.currentApiMs,
                server_ms: this.currentServerMs,
                dot_size: this.currentDotSize,
                render_ms: renderMs
            });

        } catch (error) {
            console.error(`${renderer} rendering error:`, error);
            this.handleRenderError(renderer, error);
        }
    }

    /**
     * Render with DOT/viz.js
     */
    async renderWithDot() {
        if (!this.dotRenderer) {
            throw new Error('DOT renderer not available');
        }

        await this.dotRenderer.renderDot(this.currentDot);

        // Handle small diagrams
        // const svg = this.graphCanvas.canvasArea.querySelector('svg');
        // if (svg && parseFloat(svg.getAttribute('height')) < 300) {
        //     this.graphCanvas.zoom(0.3);
        // }

        this.enablePanning();
    }

    /**
     * Render with vis.js
     */
    async renderWithVisJs() {
        if (!this.visRenderer) {
            throw new Error('vis.js renderer not available. Make sure <vis-renderer> is included in the page.');
        }

        await this.visRenderer.renderDot(this.currentDot);
    }

    /**
     * Render with D3.js
     */
    async renderWithD3() {
        if (!this.d3Renderer) {
            throw new Error('D3.js renderer not available. Make sure <d3-renderer> is included in the page.');
        }

        await this.d3Renderer.renderDot(this.currentDot);
    }

    /**
     * Render with Cytoscape.js
     */
    async renderWithCytoscape() {
        if (!this.cytoscapeRenderer) {
            throw new Error('Cytoscape renderer not available. Make sure <cytoscape-renderer> is included in the page.');
        }

        await this.cytoscapeRenderer.renderDot(this.currentDot);
    }

    /**
     * Render with Mermaid.js
     */
    async renderWithMermaid() {
        if (!this.mermaidRenderer) {
            throw new Error('Mermaid renderer not available. Make sure <mermaid-renderer> is included in the page.');
        }

        await this.mermaidRenderer.renderDot(this.currentDot);
    }

    /**
     * Handle render errors
     */
    handleRenderError(renderer, error) {
        const errorMsg = error.message || String(error);

        const isMemoryError = errorMsg.includes('memory') ||
                             errorMsg.includes('out of bounds') ||
                             errorMsg.includes('allocation') ||
                             errorMsg.includes('RuntimeError') ||
                             errorMsg.includes('WASM');

        if (isMemoryError) {
            this.statsToolbar?.showError(
                'Graph too large for browser rendering',
                `${this.currentStats?.total_nodes?.toLocaleString() || '?'} nodes. Try a different renderer (vis.js, D3, or Cytoscape handle large graphs better).`,
                `Error: ${errorMsg}`
            );

            this.showDotFallback(this.currentDot, this.currentStats, errorMsg);
        } else {
            this.statsToolbar?.showError(
                `${renderer} rendering failed`,
                errorMsg,
                'Try a different renderer.'
            );
            this.graphCanvas?.showError(`${renderer} error`, errorMsg);
        }
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

    /**
     * Show raw DOT code as fallback
     */
    showDotFallback(dot, stats, errorMessage = '') {
        const truncatedDot = dot.length > 5000
            ? dot.substring(0, 5000) + '\n\n... (truncated, showing first 5KB of ' + this.formatBytes(dot.length) + ')'
            : dot;

        this.graphCanvas.canvasArea.innerHTML = `
            <div style="width: 100%; height: 100%; overflow: auto; padding: 20px;">
                <div style="margin-bottom: 15px; padding: 12px; background: rgba(245, 158, 11, 0.1); border-radius: 8px; border: 1px solid rgba(245, 158, 11, 0.3);">
                    <div style="font-weight: 600; color: #d97706; margin-bottom: 5px;">
                        ⚠️ Browser rendering unavailable for this graph size
                    </div>
                    <div style="font-size: 0.9em; color: #666;">
                        Graph has ${stats?.total_nodes?.toLocaleString() || '?'} nodes. 
                        Try vis.js, D3, or Cytoscape renderers for large graphs, or copy the DOT code below.
                    </div>
                    ${errorMessage ? `
                    <div style="margin-top: 8px; padding: 8px; background: rgba(0,0,0,0.05); border-radius: 4px; font-family: monospace; font-size: 0.8em; color: #666; word-break: break-all;">
                        <strong>Error:</strong> ${this.escapeHtml(errorMessage)}
                    </div>
                    ` : ''}
                </div>
                <div style="margin-bottom: 10px;">
                    <button onclick="navigator.clipboard.writeText(document.getElementById('dot-output').textContent).then(() => this.textContent = '✓ Copied!')" 
                            style="padding: 6px 12px; background: var(--color-primary); color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85em;">
                        📋 Copy DOT Code
                    </button>
                </div>
                <pre id="dot-output" style="text-align: left; background: #f5f5f5; padding: 15px; border-radius: 8px; font-size: 0.8em; white-space: pre-wrap; word-wrap: break-word; max-height: 400px; overflow-y: auto;">${this.escapeHtml(truncatedDot)}</pre>
            </div>
        `;
    }

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
