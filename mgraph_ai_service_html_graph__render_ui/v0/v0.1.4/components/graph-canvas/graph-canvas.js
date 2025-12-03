/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Graph Canvas Component
   v0.1.4 - Multiple Rendering Engines (overrides v0.1.1)

   Enables all 5 renderers: DOT, vis.js, D3.js, Cytoscape, Mermaid
   ═══════════════════════════════════════════════════════════════════════════════ */

class GraphCanvas extends HTMLElement {
    constructor() {
        super();
        this.currentRenderer = 'dot';
        // All 5 renderers enabled
        this.renderers = {
            dot:       { name: 'DOT (Graphviz)',      available: true,  description: 'Static hierarchical layout using WebAssembly Graphviz' },
            visjs:     { name: 'vis.js (Interactive)', available: true,  description: 'Interactive network with drag & zoom' },
            d3:        { name: 'D3 (Force Layout)',    available: true,  description: 'Force-directed physics simulation' },
            cytoscape: { name: 'Cytoscape',            available: true,  description: 'Advanced network visualization with multiple layouts' },
            mermaid:   { name: 'Mermaid',              available: true,  description: 'Flowchart-style diagrams' }
        };
        this.canvasArea = null;
        this.currentScale = 1;
    }

    connectedCallback() {
        this.render();
        this.setupEventListeners();
    }

    render() {
        const rendererOptions = Object.entries(this.renderers)
            .map(([key, val]) => {
                const disabled = !val.available ? 'disabled' : '';
                const suffix = !val.available ? ' (coming soon)' : '';
                return `<option value="${key}" ${disabled} title="${val.description}">${val.name}${suffix}</option>`;
            })
            .join('');

        this.innerHTML = `
            <div class="graph-canvas-container">
                <div class="canvas-toolbar">
                    <div class="canvas-toolbar-left">
                        <div class="renderer-selector">
                            <label for="renderer-select">Renderer:</label>
                            <select id="renderer-select">
                                ${rendererOptions}
                            </select>
                        </div>
                    </div>
                    <div class="canvas-toolbar-right">
                        <button id="btn-zoom-in" class="btn btn-sm btn-secondary" title="Zoom In">+</button>
                        <button id="btn-zoom-out" class="btn btn-sm btn-secondary" title="Zoom Out">−</button>
                        <button id="btn-reset-zoom" class="btn btn-sm btn-secondary" title="Fit to View">⟲</button>
                        <button id="btn-download" class="btn btn-sm btn-secondary" title="Download">⬇</button>
                    </div>
                </div>
                <div id="canvas-area" class="canvas-area">
                    <div class="canvas-empty">
                        <div class="canvas-empty-icon">📊</div>
                        <p>Enter HTML and click "Render Graph" to visualize</p>
                        <div class="renderer-info" style="margin-top: 15px; font-size: 0.85em; color: #888; text-align: left; max-width: 400px;">
                            <strong>Available Renderers:</strong><br>
                            • <strong>DOT</strong>: Hierarchical tree layout (static)<br>
                            • <strong>vis.js</strong>: Interactive network, drag nodes<br>
                            • <strong>D3</strong>: Force-directed physics simulation<br>
                            • <strong>Cytoscape</strong>: Advanced network analysis<br>
                            • <strong>Mermaid</strong>: Flowchart-style diagrams
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.canvasArea = this.querySelector('#canvas-area');
    }

    setupEventListeners() {
        // Renderer selection
        this.querySelector('#renderer-select').addEventListener('change', (e) => {
            this.currentRenderer = e.target.value;
            this.dispatchEvent(new CustomEvent('renderer-changed', {
                detail: { renderer: this.currentRenderer },
                bubbles: true
            }));
        });

        // Zoom controls
        this.querySelector('#btn-zoom-in').addEventListener('click', () => this.zoom(1.2));
        this.querySelector('#btn-zoom-out').addEventListener('click', () => this.zoom(0.8));
        this.querySelector('#btn-reset-zoom').addEventListener('click', () => this.resetZoom());

        // Download
        this.querySelector('#btn-download').addEventListener('click', () => this.downloadGraph());
    }

    showLoading() {
        this.canvasArea.innerHTML = `
            <div class="canvas-loading">
                <div class="spinner"></div>
                <span>Rendering graph...</span>
            </div>
        `;
    }

    showError(message, details = null) {
        this.canvasArea.innerHTML = `
            <div class="canvas-error">
                <p>❌ ${message}</p>
                ${details ? `<pre>${this.escapeHtml(details)}</pre>` : ''}
            </div>
        `;
    }

    showEmpty() {
        this.render();
    }

    renderSvg(svgContent) {
        this.canvasArea.innerHTML = svgContent;
        this.currentScale = 1;

        const svg = this.canvasArea.querySelector('svg');
        if (svg) {
            svg.style.maxWidth = '100%';
            svg.style.height = 'auto';
        }
    }

    zoom(factor) {
        const svg = this.canvasArea.querySelector('svg');
        if (!svg) return;

        this.currentScale = (this.currentScale || 1) * factor;
        this.currentScale = Math.max(0.1, Math.min(5, this.currentScale));
        svg.style.transform = `scale(${this.currentScale})`;
        svg.style.transformOrigin = 'top left';
    }

    resetZoom() {
        // Call fitToView on the active renderer
        const rendererMap = {
            'visjs': 'vis-renderer',
            'd3': 'd3-renderer',
            'cytoscape': 'cytoscape-renderer',
            'mermaid': 'mermaid-renderer'
        };

        const rendererTag = rendererMap[this.currentRenderer];
        if (rendererTag) {
            const renderer = document.querySelector(rendererTag);
            if (renderer && renderer.fitToView) {
                renderer.fitToView();
                return;
            }
        }

        // For DOT/SVG
        const svg = this.canvasArea.querySelector('svg');
        if (!svg) return;

        this.currentScale = 1;
        svg.style.transform = 'scale(1)';
    }

    downloadGraph() {
        const svg = this.canvasArea.querySelector('svg');
        if (svg) {
            const svgData = new XMLSerializer().serializeToString(svg);
            const blob = new Blob([svgData], { type: 'image/svg+xml' });
            const url = URL.createObjectURL(blob);

            const link = document.createElement('a');
            link.href = url;
            link.download = 'graph.svg';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            return;
        }

        // Check for canvas (vis.js and Cytoscape use canvas)
        const canvas = this.canvasArea.querySelector('canvas');
        if (canvas) {
            const dataUrl = canvas.toDataURL('image/png');
            const link = document.createElement('a');
            link.href = dataUrl;
            link.download = 'graph.png';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            return;
        }

        // Try renderer-specific export
        const rendererMap = {
            'cytoscape': document.querySelector('cytoscape-renderer')
        };

        const renderer = rendererMap[this.currentRenderer];
        if (renderer && renderer.exportPng) {
            const dataUrl = renderer.exportPng();
            if (dataUrl) {
                const link = document.createElement('a');
                link.href = dataUrl;
                link.download = 'graph.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                return;
            }
        }

        alert('No graph to download');
    }

    getCurrentRenderer() {
        return this.currentRenderer;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

customElements.define('graph-canvas', GraphCanvas);