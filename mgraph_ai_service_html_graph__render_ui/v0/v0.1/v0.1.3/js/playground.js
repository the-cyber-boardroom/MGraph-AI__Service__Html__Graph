/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Playground Orchestrator
   v0.1.4 - Improved Layout & Error Handling

   Key improvements:
   - Stats shown immediately after API call (before viz.js rendering)
   - Graceful handling of viz.js memory errors
   - Timing tracking for API, server, and render
   - Stats toolbar at top-right for better visibility
   ═══════════════════════════════════════════════════════════════════════════════ */

/**
 * Playground Controller
 * v0.1.4: Improved error handling and timing display
 * v0.1.4.1: Auto-render with debounce when HTML changes
 */
class Playground {
    constructor() {
        this.htmlInput = null;
        this.configPanel = null;
        this.statsToolbar = null;
        this.graphCanvas = null;
        this.dotRenderer = null;
        this.urlInput = null;

        this.currentHtml = '';
        this.currentConfig = {};
        this.isRendering = false;

        // Debounce timer for auto-render
        this.autoRenderTimer = null;
        this.autoRenderDelay = 800;  // ms to wait after user stops typing
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
        this.dotRenderer = document.querySelector('dot-renderer');
        this.urlInput = document.querySelector('url-input');

        // Setup event listeners
        this.setupEventListeners();

        // Check for sample or URL in query params
        this.loadFromUrl();

        console.log('Playground v0.1.4 initialized (auto-render enabled, 800ms debounce)');
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

        // Config changed - trigger immediate render
        document.addEventListener('config-changed', (e) => {
            this.currentConfig = e.detail.config;
            // If we have HTML content, re-render with new config
            if (this.currentHtml && this.currentHtml.trim()) {
                this.scheduleAutoRender(300);  // Shorter delay for config changes
            }
        });

        // Renderer changed
        document.addEventListener('renderer-changed', (e) => {
            console.log('Renderer changed to:', e.detail.renderer);
        });

        // URL HTML fetched
        document.addEventListener('url-html-fetched', (e) => {
            this.handleUrlHtmlFetched(e.detail);
        });

        // Render requested (from stats-toolbar button) - NEW in v0.1.4
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

        // Auto-render fetched content after short delay
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
    }

    /**
     * Schedule auto-render with debounce
     * Waits for user to stop typing before rendering
     */
    scheduleAutoRender(delay = null) {
        // Clear any existing timer
        if (this.autoRenderTimer) {
            clearTimeout(this.autoRenderTimer);
            this.autoRenderTimer = null;
        }

        // Don't auto-render if already rendering
        if (this.isRendering) return;

        // Don't auto-render if no HTML content
        const html = this.htmlInput ? this.htmlInput.getHtml() : this.currentHtml;
        if (!html || !html.trim()) return;

        // Schedule render after delay
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
            this.statsToolbar.showError(
                'No HTML to render',
                'Please enter some HTML or fetch from a URL first.',
                ''
            );
            return;
        }

        this.isRendering = true;
        this.statsToolbar.setRenderingState(true);
        this.statsToolbar.hideError();
        this.statsToolbar.clearStats();  // Clear previous stats immediately
        this.graphCanvas.showLoading();

        try {
            const renderer = this.graphCanvas.getCurrentRenderer();

            if (renderer === 'dot') {
                await this.renderDot(html, config);
            } else {
                this.statsToolbar.showError(
                    'Renderer not available',
                    `The '${renderer}' renderer is not yet implemented.`,
                    'Try using the DOT (Graphviz) renderer.'
                );
            }
        } catch (error) {
            console.error('Render error:', error);
            this.statsToolbar.showError(
                'API Error',
                error.message || 'Failed to call the API.',
                'Check that the server is running and try again.'
            );
            this.graphCanvas.showError('API request failed', error.message);
        } finally {
            this.isRendering = false;
            this.statsToolbar.setRenderingState(false);
        }
    }

    /**
     * Render using DOT/Graphviz
     * v0.1.4: Shows stats immediately, handles viz.js errors gracefully with actual error message
     */
    async renderDot(html, config) {
        // Build request
        const request = {
            html: html,
            preset: config.preset || 'FULL_DETAIL',
            show_tag_nodes: config.show_tag_nodes !== false,
            show_attr_nodes: config.show_attr_nodes !== false,
            show_text_nodes: config.show_text_nodes !== false,
            color_scheme: config.color_scheme || 'DEFAULT'
        };

        // Call API with timing
        const apiStartTime = performance.now();
        const response = await apiClient.htmlToDot(request);
        const apiEndTime = performance.now();
        const apiMs = Math.round(apiEndTime - apiStartTime);

        // IMMEDIATELY update stats (before viz.js rendering) - v0.1.4 improvement
        if (response.stats) {
            this.statsToolbar.setStats(response.stats);
        }

        // Update timing info immediately (render_ms will be updated after)
        this.statsToolbar.setTiming({
            api_ms: apiMs,
            server_ms: response.processing_ms || 0,
            dot_size: response.dot_size_bytes || response.dot.length,
            render_ms: 0
        });

        // Now attempt viz.js rendering
        if (this.dotRenderer && response.dot) {
            const renderStartTime = performance.now();

            try {

                this.statsToolbar.setTiming({
                    api_ms: apiMs,
                    server_ms: response.processing_ms || 0,
                    dot_size: response.dot_size_bytes || response.dot.length,
                });

                await this.dotRenderer.renderDot(response.dot);

                const renderEndTime = performance.now();
                const renderMs = Math.round(renderEndTime - renderStartTime);

                // Update render timing
                this.statsToolbar.setTiming({
                    api_ms: apiMs,
                    server_ms: response.processing_ms || 0,
                    dot_size: response.dot_size_bytes || response.dot.length,
                    render_ms: renderMs
                });
                const svg = this.graphCanvas.canvasArea.querySelector('svg');
                if(parseFloat(svg.getAttribute('height')) < 300) {              // handle case of small diagrams that were not displaying ok
                    this.graphCanvas.zoom(0.3) }

                // Enable panning on the rendered SVG
                this.enablePanning();

            } catch (vizError) {
                console.error('viz.js rendering error:', vizError);

                // Get the actual error message
                const errorMsg = vizError.message || String(vizError);

                // Check if it's a memory/WASM error
                const isMemoryError = errorMsg.includes('memory') ||
                                     errorMsg.includes('out of bounds') ||
                                     errorMsg.includes('allocation') ||
                                     errorMsg.includes('RuntimeError') ||
                                     errorMsg.includes('WASM');

                // Show error with actual message
                this.statsToolbar.showError(
                    isMemoryError ? 'Graph too large for browser rendering' : 'Rendering failed',
                    `${response.stats.total_nodes.toLocaleString()} nodes, ${response.stats.total_edges.toLocaleString()} edges`,
                    `Error: ${errorMsg}`
                );

                // Show the raw DOT as fallback
                this.showDotFallback(response.dot, response.stats, errorMsg);
            }
        } else if (response.dot) {
            // No dot-renderer available, show raw DOT
            this.showDotFallback(response.dot, response.stats, 'viz.js renderer not loaded');
        }
    }

    /**
     * Enable panning (drag to move) on the graph canvas
     */
    enablePanning() {
        const canvasArea = this.graphCanvas.canvasArea;
        const svg = canvasArea.querySelector('svg');
        if (!svg) return;

        let isPanning = false;
        let startX, startY;
        let scrollLeft, scrollTop;

        // Make canvas scrollable
        canvasArea.style.overflow = 'auto';
        canvasArea.style.cursor = 'grab';

        canvasArea.addEventListener('mousedown', (e) => {
            // Only pan with left mouse button and not on interactive elements
            if (e.button !== 0) return;
            isPanning = true;
            canvasArea.style.cursor = 'grabbing';
            startX = e.pageX - canvasArea.offsetLeft;
            startY = e.pageY - canvasArea.offsetTop;
            scrollLeft = canvasArea.scrollLeft;
            scrollTop = canvasArea.scrollTop;
            e.preventDefault();
        });

        canvasArea.addEventListener('mousemove', (e) => {
            if (!isPanning) return;

            const x = e.pageX - canvasArea.offsetLeft;
            const y = e.pageY - canvasArea.offsetTop;

            const walkX = (x - startX) * 1.5;  // Scroll speed multiplier
            const walkY = (y - startY) * .5;

            canvasArea.scrollLeft = scrollLeft - walkX;
            canvasArea.scrollTop = scrollTop - walkY;
        });

        canvasArea.addEventListener('mouseup', () => {
            isPanning = false;
            canvasArea.style.cursor = 'grab';
        });

        canvasArea.addEventListener('mouseleave', () => {
            isPanning = false;
            canvasArea.style.cursor = 'grab';
        });
    }

    /**
     * Show raw DOT code as fallback when viz.js fails
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
                        Graph has ${stats.total_nodes.toLocaleString()} nodes. 
                        Showing raw DOT code below. You can copy this and use it with a local Graphviz installation.
                    </div>
                    ${errorMessage ? `
                    <div style="margin-top: 8px; padding: 8px; background: rgba(0,0,0,0.05); border-radius: 4px; font-family: monospace; font-size: 0.8em; color: #666; word-break: break-all;">
                        <strong>Error:</strong> ${this.escapeHtml(errorMessage)}
                    </div>
                    ` : ''}
                    <div style="margin-top: 8px; font-size: 0.85em; color: #888;">
                        💡 Tip: Try "Structure Only" or "Minimal" preset, or hide attribute/text nodes to reduce graph size.
                    </div>
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