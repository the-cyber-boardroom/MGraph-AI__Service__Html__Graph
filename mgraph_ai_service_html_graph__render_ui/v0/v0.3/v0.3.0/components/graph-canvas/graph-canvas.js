/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Graph Canvas Component
   v0.3.0 - Consolidated from v0.2.0 → v0.2.9 → v0.2.10

   Merged features:
   - Base canvas with 5 renderers (v0.2.0)
   - Tree and tree_text renderers added (v0.2.9)
   - DOT SVG rendering fix for canvas fit (v0.2.9)
   - Copy to clipboard functionality (v0.2.10)
   ═══════════════════════════════════════════════════════════════════════════════ */

class GraphCanvas extends HTMLElement {
    constructor() {
        super();
        this.currentRenderer = 'dot';
        // All 7 renderers enabled (including tree renderers from v0.2.9)
        this.renderers = {
            dot:       { name: 'DOT (Graphviz)',      available: true,  description: 'Static hierarchical layout using WebAssembly Graphviz' },
            visjs:     { name: 'vis.js (Interactive)', available: true,  description: 'Interactive network with drag & zoom' },
            d3:        { name: 'D3 (Force Layout)',    available: true,  description: 'Force-directed physics simulation' },
            cytoscape: { name: 'Cytoscape',            available: true,  description: 'Advanced network visualization with multiple layouts' },
            mermaid:   { name: 'Mermaid',              available: true,  description: 'Flowchart-style diagrams' },
            tree:      { name: 'Tree (JSON)',          available: true,  description: 'Collapsible hierarchical tree view' },
            tree_text: { name: 'Tree (Text)',          available: true,  description: 'Formatted text representation' }
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
                        <button id="btn-copy" class="btn btn-sm btn-secondary" title="Copy to Clipboard">📋</button>
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
                            • <strong>Mermaid</strong>: Flowchart-style diagrams<br>
                            • <strong>Tree (JSON)</strong>: Collapsible tree view<br>
                            • <strong>Tree (Text)</strong>: Formatted text output
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

        // Copy to clipboard (from v0.2.10)
        this.querySelector('#btn-copy').addEventListener('click', () => this.copyToClipboard());

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

    /**
     * Render SVG content with proper fit (fixed in v0.2.9)
     */
    renderSvg(svgContent) {
        this.canvasArea.innerHTML = svgContent;
        this.currentScale = 1;
        this.canvasArea.style.background = 'white';

        const svg = this.canvasArea.querySelector('svg');
        if (svg) {
            // Remove pt-based dimensions that cause overflow
            svg.removeAttribute('width');
            svg.removeAttribute('height');

            // Fit to container while preserving aspect ratio
            svg.style.width = '100%';
            svg.style.height = '100%';
            svg.style.maxWidth = '100%';
            svg.style.maxHeight = '100%';
            svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
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
        const rendererMap = {
            'visjs': 'vis-renderer',
            'd3': 'd3-renderer',
            'cytoscape': 'cytoscape-renderer',
            'mermaid': 'mermaid-renderer',
            'tree': 'tree-renderer',
            'tree_text': 'tree-text-renderer'
        };

        const rendererTag = rendererMap[this.currentRenderer];
        if (rendererTag) {
            const renderer = document.querySelector(rendererTag);
            if (renderer && renderer.fitToView) {
                renderer.fitToView();
                return;
            }
        }

        const svg = this.canvasArea.querySelector('svg');
        if (!svg) return;

        this.currentScale = 1;
        svg.style.transform = 'scale(1)';
    }

    /**
     * Copy graph to clipboard (from v0.2.10)
     */
    async copyToClipboard() {
        const svg = this.canvasArea.querySelector('svg');
        if (svg) {
            try {
                const svgData = new XMLSerializer().serializeToString(svg);
                await navigator.clipboard.writeText(svgData);
                this.showToast('SVG copied to clipboard');
            } catch (err) {
                console.error('Failed to copy:', err);
                this.showToast('Failed to copy to clipboard');
            }
            return;
        }

        // For tree text, copy the text content
        const treeText = this.canvasArea.querySelector('.tree-text-content');
        if (treeText) {
            try {
                const text = treeText.textContent;
                await navigator.clipboard.writeText(text);
                this.showToast('Text copied to clipboard');
            } catch (err) {
                console.error('Failed to copy:', err);
                this.showToast('Failed to copy to clipboard');
            }
            return;
        }

        this.showToast('Nothing to copy');
    }

    showToast(message) {
        const existing = document.getElementById('graph-canvas-toast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.id = 'graph-canvas-toast';
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 14px;
            z-index: 10000;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => toast.remove(), 2000);
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
