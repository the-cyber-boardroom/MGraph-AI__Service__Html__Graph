/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Playground Orchestrator
   v0.1.1 - Core UI Framework
   ═══════════════════════════════════════════════════════════════════════════════ */

/**
 * Playground Controller
 * Orchestrates communication between components and API
 */
class Playground {
    constructor() {
        this.htmlInput = null;
        this.configPanel = null;
        this.statsPanel = null;
        this.graphCanvas = null;
        this.renderButton = null;
        this.dotRenderer = null;

        this.currentHtml = '';
        this.currentConfig = {};
        this.isRendering = false;
    }

    /**
     * Initialize the playground
     */
    init() {
        // Get component references
        this.htmlInput = document.querySelector('html-input');
        this.configPanel = document.querySelector('config-panel');
        this.statsPanel = document.querySelector('stats-panel');
        this.graphCanvas = document.querySelector('graph-canvas');
        this.renderButton = document.getElementById('render-button');
        this.dotRenderer = document.querySelector('dot-renderer');

        // Setup event listeners
        this.setupEventListeners();

        // Check for sample in URL
        this.loadFromUrl();

        console.log('Playground initialized');
    }

    /**
     * Setup event listeners for component communication
     */
    setupEventListeners() {
        // HTML changed
        document.addEventListener('html-changed', (e) => {
            this.currentHtml = e.detail.html;
        });

        // Config changed
        document.addEventListener('config-changed', (e) => {
            this.currentConfig = e.detail.config;
        });

        // Renderer changed
        document.addEventListener('renderer-changed', (e) => {
            console.log('Renderer changed to:', e.detail.renderer);
        });

        // Render button click
        if (this.renderButton) {
            this.renderButton.addEventListener('click', () => this.renderGraph());
        }

        // Keyboard shortcut (Ctrl+Enter to render)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.renderGraph();
            }
        });
    }

    /**
     * Load sample from URL query parameter
     */
    loadFromUrl() {
        const params = new URLSearchParams(window.location.search);
        const sample = params.get('sample');
        if (sample && this.htmlInput) {
            this.htmlInput.loadSample(sample);
        }
    }

    /**
     * Render the graph
     */
    async renderGraph() {
        if (this.isRendering) return;

        const html = this.htmlInput ? this.htmlInput.getHtml() : this.currentHtml;
        const config = this.configPanel ? this.configPanel.getConfig() : this.currentConfig;

        if (!html || !html.trim()) {
            this.graphCanvas.showError('Please enter some HTML to render');
            return;
        }

        this.isRendering = true;
        this.setRenderButtonState(true);
        this.graphCanvas.showLoading();

        try {
            const renderer = this.graphCanvas.getCurrentRenderer();

            if (renderer === 'dot') {
                await this.renderDot(html, config);
            } else {
                this.graphCanvas.showError(`Renderer '${renderer}' is not yet implemented`);
            }
        } catch (error) {
            console.error('Render error:', error);
            this.graphCanvas.showError('Failed to render graph', error.message);
            this.statsPanel.clearStats();
        } finally {
            this.isRendering = false;
            this.setRenderButtonState(false);
        }
    }

    /**
     * Render using DOT/Graphviz
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

        // Call API
        const response = await apiClient.htmlToDot(request);

        // Update stats
        if (response.stats) {
            this.statsPanel.setStats(response.stats);
        }

        // Render DOT to SVG using dot-renderer component
        if (this.dotRenderer && response.dot) {
            await this.dotRenderer.renderDot(response.dot);
        } else if (response.dot) {
            // Fallback: show raw DOT
            this.graphCanvas.canvasArea.innerHTML = `
                <pre style="text-align: left; padding: 20px; overflow: auto;">${this.escapeHtml(response.dot)}</pre>
            `;
        }
    }

    /**
     * Set render button loading state
     */
    setRenderButtonState(loading) {
        if (!this.renderButton) return;

        if (loading) {
            this.renderButton.disabled = true;
            this.renderButton.innerHTML = '<span class="spinner"></span> Rendering...';
        } else {
            this.renderButton.disabled = false;
            this.renderButton.innerHTML = '🔄 Render Graph';
        }
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
