/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Graph Canvas Component
   v0.1.1 - Core UI Framework
   ═══════════════════════════════════════════════════════════════════════════════ */

class GraphCanvas extends HTMLElement {
    constructor() {
        super();
        this.currentRenderer = 'dot';
        this.renderers = {
            dot: { name: 'DOT (Graphviz)', available: true },
            visjs: { name: 'vis.js (Interactive)', available: false },
            d3: { name: 'D3 (Force Layout)', available: false },
            cytoscape: { name: 'Cytoscape', available: false },
            mermaid: { name: 'Mermaid', available: false }
        };
        this.canvasArea = null;
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
                return `<option value="${key}" ${disabled}>${val.name}${suffix}</option>`;
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
                        <button id="btn-reset-zoom" class="btn btn-sm btn-secondary" title="Reset">⟲</button>
                        <button id="btn-download" class="btn btn-sm btn-secondary" title="Download">⬇</button>
                    </div>
                </div>
                <div id="canvas-area" class="canvas-area">
                    <div class="canvas-empty">
                        <div class="canvas-empty-icon">📊</div>
                        <p>Enter HTML and click "Render Graph" to visualize</p>
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
        this.canvasArea.innerHTML = `
            <div class="canvas-empty">
                <div class="canvas-empty-icon">📊</div>
                <p>Enter HTML and click "Render Graph" to visualize</p>
            </div>
        `;
    }

    renderSvg(svgContent) {
        this.canvasArea.innerHTML = svgContent;
        this.currentScale = 1;

        // Make SVG responsive
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
        svg.style.transform = `scale(${this.currentScale})`;
        svg.style.transformOrigin = 'center center';
    }

    resetZoom() {
        const svg = this.canvasArea.querySelector('svg');
        if (!svg) return;

        this.currentScale = 1;
        svg.style.transform = 'scale(1)';
    }

    downloadGraph() {
        const svg = this.canvasArea.querySelector('svg');
        if (!svg) {
            alert('No graph to download');
            return;
        }

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
