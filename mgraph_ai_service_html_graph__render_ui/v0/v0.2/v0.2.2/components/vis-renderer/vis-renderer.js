/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - vis.js Renderer Component (Updated)
   v0.3.0 - Uses native vis.js format from API (no DOT parsing)

   Uses vis.js Network for interactive graph visualization.
   Now receives pre-processed data directly from the backend API.

   CDN: https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js
   ═══════════════════════════════════════════════════════════════════════════════ */

class VisRenderer extends HTMLElement {
    constructor() {
        super();
        this.network = null;
        this.targetCanvas = null;
        this.isLoaded = false;
    }

    connectedCallback() {
        this.loadVisJs();
    }

    /**
     * Load vis.js from CDN
     */
    async loadVisJs() {
        if (window.vis) {
            this.isLoaded = true;
            return;
        }

        try {
            await this.loadScript('https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js');
            this.isLoaded = true;
        } catch (error) {
            console.error('Failed to load vis.js:', error);
        }
    }

    loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    /**
     * Set the target canvas element
     */
    setTargetCanvas(canvasElement) {
        this.targetCanvas = canvasElement;
    }

    /**
     * Render graph using native vis.js data from API
     * @param {object} graphData - Native vis.js format {nodes, edges} from API
     */
    async render(graphData) {
        if (!this.isLoaded) {
            await this.loadVisJs();
        }

        if (!this.targetCanvas) {
            throw new Error('No target canvas set for vis.js renderer');
        }

        const { nodes, edges } = graphData;

        // Clear previous network
        if (this.network) {
            this.network.destroy();
            this.network = null;
        }

        // Create container
        this.targetCanvas.innerHTML = '<div id="vis-container" style="width: 100%; height: 100%;"></div>';
        const container = this.targetCanvas.querySelector('#vis-container');

        // Convert nodes - remap 'from' key (Python reserves 'from')
        const processedNodes = nodes.map(node => ({
            ...node,
            // Ensure proper vis.js structure
            color: node.color || {
                background: '#E8E8E8',
                border: '#CCCCCC'
            },
            font: node.font || {
                color: '#333333',
                size: 11
            }
        }));

        // Convert edges - API uses 'from_node' to avoid Python keyword
        const processedEdges = edges.map(edge => ({
            ...edge,
            from: edge.from || edge.from_node,  // Handle both naming conventions
            color: edge.color || {
                color: '#888888',
                highlight: '#6366f1'
            }
        }));

        // Create vis.js datasets
        const nodesDataset = new vis.DataSet(processedNodes);
        const edgesDataset = new vis.DataSet(processedEdges);

        // Network options
        const options = {
            nodes: {
                shape: 'box',
                margin: 10,
                font: {
                    size: 12,
                    face: 'system-ui, sans-serif'
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                arrows: {
                    to: { enabled: true, scaleFactor: 0.5 }
                },
                smooth: {
                    type: 'cubicBezier',
                    forceDirection: 'vertical',
                    roundness: 0.4
                }
            },
            layout: {
                hierarchical: {
                    enabled: true,
                    direction: 'UD',
                    sortMethod: 'directed',
                    levelSeparation: 80,
                    nodeSpacing: 120,
                    treeSpacing: 200
                }
            },
            physics: {
                enabled: false
            },
            interaction: {
                dragNodes: true,
                dragView: true,
                zoomView: true,
                hover: true,
                tooltipDelay: 200
            }
        };

        // Create network
        this.network = new vis.Network(container, { nodes: nodesDataset, edges: edgesDataset }, options);

        // Fit to view after stabilization
        this.network.once('stabilized', () => {
            this.network.fit({ animation: { duration: 300, easingFunction: 'easeInOutQuad' } });
        });

        return { nodes: nodes.length, edges: edges.length };
    }

    /**
     * Legacy: Render DOT code (for backwards compatibility)
     * @deprecated Use render(graphData) instead
     */
    async renderDot(dotCode) {
        console.warn('VisRenderer.renderDot() is deprecated. Use render(graphData) with native vis.js format.');
        // Fall back to DOT parsing if native format not available
        const { nodes, edges } = this.parseDot(dotCode);
        return this.render({ nodes, edges });
    }

    /**
     * Legacy: Parse DOT code (for backwards compatibility only)
     * @deprecated
     */
    parseDot(dotCode) {
        const nodes = [];
        const edges = [];
        const nodeMap = new Map();

        const nodeRegex = /"([^"]+)"\s*\[([^\]]+)\]/g;
        let match;

        while ((match = nodeRegex.exec(dotCode)) !== null) {
            const nodeId = match[1];
            const attrs = match[2];

            if (attrs.includes('->')) continue;

            const label = this.extractAttr(attrs, 'label') || nodeId;
            const fillcolor = this.extractAttr(attrs, 'fillcolor') || '#f5f5f5';
            const fontcolor = this.extractAttr(attrs, 'fontcolor') || '#333333';

            nodes.push({
                id: nodeId,
                label: this.cleanLabel(label),
                color: {
                    background: fillcolor,
                    border: this.darkenColor(fillcolor)
                },
                font: { color: fontcolor },
                title: this.cleanLabel(label)
            });

            nodeMap.set(nodeId, true);
        }

        const edgeRegex = /"([^"]+)"\s*->\s*"([^"]+)"(?:\s*\[([^\]]*)\])?/g;

        while ((match = edgeRegex.exec(dotCode)) !== null) {
            const from = match[1];
            const to = match[2];
            const attrs = match[3] || '';

            if (nodeMap.has(from) && nodeMap.has(to)) {
                const style = this.extractAttr(attrs, 'style');
                const color = this.extractAttr(attrs, 'color') || '#888888';

                edges.push({
                    from: from,
                    to: to,
                    dashes: style === 'dashed',
                    color: { color: color }
                });
            }
        }

        return { nodes, edges };
    }

    extractAttr(attrString, attrName) {
        const patterns = [
            new RegExp(`${attrName}="([^"]*)"`, 'i'),
            new RegExp(`${attrName}=([^,\\]\\s]+)`, 'i')
        ];
        for (const pattern of patterns) {
            const match = attrString.match(pattern);
            if (match) {
                return match[1].replace(/\\"/g, '"').replace(/\\n/g, '\n');
            }
        }
        return null;
    }

    cleanLabel(label) {
        return label.replace(/\\n/g, '\n').replace(/\\"/g, '"').replace(/^"(.*)"$/, '$1');
    }

    darkenColor(hex) {
        const color = hex.replace('#', '');
        const r = Math.max(0, parseInt(color.substr(0, 2), 16) - 30);
        const g = Math.max(0, parseInt(color.substr(2, 2), 16) - 30);
        const b = Math.max(0, parseInt(color.substr(4, 2), 16) - 30);
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }

    /**
     * Fit graph to view
     */
    fitToView() {
        if (this.network) {
            this.network.fit({ animation: { duration: 300, easingFunction: 'easeInOutQuad' } });
        }
    }

    /**
     * Export as PNG
     */
    async exportPng() {
        if (!this.network) return null;
        const canvas = this.targetCanvas.querySelector('canvas');
        if (canvas) {
            return canvas.toDataURL('image/png');
        }
        return null;
    }
}

customElements.define('vis-renderer', VisRenderer);
