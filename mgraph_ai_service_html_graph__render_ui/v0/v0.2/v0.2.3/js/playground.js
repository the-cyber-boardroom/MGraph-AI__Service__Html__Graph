/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Playground Orchestrator
   v0.2.2 - Surgical Override: Route to native format API endpoints
   
   Overrides from v0.2.0:
   - renderGraph(): Call appropriate API endpoint per renderer
   - renderWithFormat(): Route to correct render method
   - renderWithVisJs(): Use native vis.js format
   - renderWithD3(): Use native D3 format
   - renderWithCytoscape(): Use native Cytoscape format
   - renderWithMermaid(): Use native Mermaid format
   ═══════════════════════════════════════════════════════════════════════════════ */


/**
 * Build the API request object
 */
Playground.prototype.buildRequest = function() {
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
};

/**
 * OVERRIDE: Render the graph using the appropriate API endpoint for the selected renderer
 */
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
    const request = this.buildRequest();

    try {
        const apiStartTime = performance.now();

        // v0.2.2: Call the appropriate native format API endpoint
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
};

/**
 * NEW: Render with the appropriate renderer using native format
 */
Playground.prototype.renderWithFormat = async function(renderer, response) {
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
};

/**
 * NEW: Render with vis.js using native format (no DOT parsing)
 */
Playground.prototype.renderWithVisJs = async function(response) {
    if (!this.visRenderer) {
        throw new Error('vis.js renderer not available');
    }

    // Response is already in native vis.js format
    await this.visRenderer.render({
        nodes: response.nodes,
        edges: response.edges
    });
};

/**
 * NEW: Render with D3.js using native format (no DOT parsing)
 */
Playground.prototype.renderWithD3 = async function(response) {
    if (!this.d3Renderer) {
        throw new Error('D3.js renderer not available');
    }

    // Response is already in native D3 format
    await this.d3Renderer.render({
        nodes: response.nodes,
        links: response.links
    });
};

/**
 * NEW: Render with Cytoscape.js using native format (no DOT parsing)
 */
Playground.prototype.renderWithCytoscape = async function(response) {
    if (!this.cytoscapeRenderer) {
        throw new Error('Cytoscape renderer not available');
    }

    // Response is already in native Cytoscape format
    await this.cytoscapeRenderer.render({
        elements: response.elements
    });
};

/**
 * NEW: Render with Mermaid.js using native format (no DOT conversion)
 */
Playground.prototype.renderWithMermaid = async function(response) {
    if (!this.mermaidRenderer) {
        throw new Error('Mermaid renderer not available');
    }

    // Response contains pre-generated Mermaid code
    await this.mermaidRenderer.render({
        mermaid: response.mermaid
    });
};

/**
 * OVERRIDE: Render with DOT/viz.js using response object
 */
Playground.prototype.renderWithDot = async function(response) {
    if (!this.dotRenderer) {
        throw new Error('DOT renderer not available');
    }

    await this.dotRenderer.renderDot(response.dot);
    this.enablePanning();
};

// Re-register renderer-changed to trigger re-render
document.addEventListener('renderer-changed', function(e) {
    // Dispatch render-requested which the base Playground listens to
    document.dispatchEvent(new CustomEvent('render-requested'));
});

console.log('Playground v0.2.2 surgical override loaded (native format routing)');
