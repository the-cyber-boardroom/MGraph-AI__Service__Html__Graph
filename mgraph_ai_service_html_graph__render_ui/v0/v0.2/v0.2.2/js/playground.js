/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Playground Orchestrator (Updated)
   v0.3.0 - Native format support for all renderers

   Supports 5 renderers with native API formats:
   - DOT: Uses /graph/from/html/to/dot → viz.js WASM rendering
   - vis.js: Uses /graph/from/html/to/visjs → native vis.js format
   - D3: Uses /graph/from/html/to/d3 → native D3 format  
   - Cytoscape: Uses /graph/from/html/to/cytoscape → native Cytoscape format
   - Mermaid: Uses /graph/from/html/to/mermaid → native Mermaid code
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
        this.currentStats = null;
        this.currentApiMs = 0;
        this.currentServerMs = 0;
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

        console.log('Playground v0.3.0 initialized (native format support for all renderers)');
    }

    /**
     * Setup event listeners for component communication
     */
    setupEventListeners() {
        // HTML changed - trigger debounced auto-render
        document.addEventListener('html-changed', (e) => {
            this.currentHtml = e.detail.html;
            this.scheduleAutoRender();
        });

        // Config changed - trigger render
        document.addEventListener('config-changed', (e) => {
            this.currentConfig = e.detail.config;
            if (this.currentHtml && this.currentHtml.trim()) {
                this.scheduleAutoRender(300);
            }
        });

        // Renderer changed - re-render with new renderer's native format
        document.addEventListener('renderer-changed', (e) => {
            const newRenderer = e.detail.renderer;
            console.log('Renderer changed to:', newRenderer);

            // Re-render with the new renderer's native format
            if (this.currentHtml && this.currentHtml.trim()) {
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

    /**
     * Handle HTML fetched from URL
     */
    handleUrlHtmlFetched(detail) {
        const { html, url, contentType } = detail;

        if (this.htmlInput) {
            this.htmlInput.setHtml(html);
        }

        this.currentHtml = html;
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
        const request = this.buildRequest();

        try {
            const apiStartTime = performance.now();

            // Call the appropriate API endpoint based on renderer
            let response;
            switch (renderer) {
                case 'dot':
                    response = await window.apiClient.htmlToDot(request);
                    break;
                case 'visjs':
                    response = await window.apiClient.htmlToVisJs(request);
                    break;
                case 'd3':
                    response = await window.apiClient.htmlToD3(request);
                    break;
                case 'cytoscape':
                    response = await window.apiClient.htmlToCytoscape(request);
                    break;
                case 'mermaid':
                    response = await window.apiClient.htmlToMermaid(request);
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
                dot_size: response.dot_size || response.mermaid_size || 0,
                render_ms: Math.round(renderEndTime - renderStartTime)
            });

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

        // Response is already in native vis.js format
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

        // Response is already in native D3 format
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

        // Response is already in native Cytoscape format
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

        // Response contains pre-generated Mermaid code
        await this.mermaidRenderer.render({
            mermaid: response.mermaid
        });
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
