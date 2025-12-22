/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - vis.js Renderer Component
   v0.3.0 - Consolidated from v0.2.0 → v0.2.3

   Merged features:
   - Base vis.js renderer with DOT parsing (v0.2.0)
   - Native format render() method (v0.2.3)

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

    // ═══════════════════════════════════════════════════════════════════════════════
    // Native Format Rendering (from v0.2.3)
    // ═══════════════════════════════════════════════════════════════════════════════

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

        // Process nodes - ensure proper vis.js structure
        const processedNodes = nodes.map(node => ({
            ...node,
            color: node.color || { background: '#E8E8E8', border: '#CCCCCC' },
            font: node.font || { color: '#333333', size: 11 }
        }));

        // Process edges - handle 'from' key which may come as 'from_node' from Python
        const processedEdges = edges.map(edge => ({
            ...edge,
            from: edge.from || edge.from_node,
            color: edge.color || { color: '#888888', highlight: '#6366f1' }
        }));

        // Create vis.js datasets
        const nodesDataset = new vis.DataSet(processedNodes);
        const edgesDataset = new vis.DataSet(processedEdges);

        // Network options
        const options = {
            nodes: {
                shape: 'box',
                margin: 10,
                font: { size: 12, face: 'system-ui, sans-serif' },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                arrows: { to: { enabled: true, scaleFactor: 0.5 } },
                smooth: { type: 'cubicBezier', forceDirection: 'vertical', roundness: 0.4 }
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
            physics: { enabled: false },
            interaction: { dragNodes: true, dragView: true, zoomView: true, hover: true, tooltipDelay: 200 }
        };

        // Create network
        this.network = new vis.Network(container, { nodes: nodesDataset, edges: edgesDataset }, options);

        // Fit to view after stabilization
        this.network.once('stabilized', () => {
            this.network.fit({ animation: { duration: 300, easingFunction: 'easeInOutQuad' } });
        });

        return { nodes: nodes.length, edges: edges.length };
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // DOT Parsing (from v0.2.0 - deprecated but kept for backwards compatibility)
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Render DOT code using vis.js
     * @deprecated Use render() with native vis.js format instead
     */
    async renderDot(dotCode) {
        console.warn('VisRenderer.renderDot() is deprecated. Use render(graphData) with native vis.js format.');

        if (!this.isLoaded) {
            await this.loadVisJs();
        }

        if (!this.targetCanvas) {
            throw new Error('No target canvas set for vis.js renderer');
        }

        // Parse DOT to extract nodes and edges
        const { nodes, edges } = this.parseDot(dotCode);

        // Use the native render method
        return this.render({ nodes, edges });
    }

    /**
     * Parse DOT code to extract nodes and edges
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
            const shape = this.extractAttr(attrs, 'shape') || 'box';

            const visShape = this.mapShape(shape);
            const nodeType = this.detectNodeType(label, fillcolor);

            nodes.push({
                id: nodeId,
                label: this.cleanLabel(label),
                color: {
                    background: fillcolor,
                    border: this.darkenColor(fillcolor),
                    highlight: {
                        background: this.lightenColor(fillcolor),
                        border: '#6366f1'
                    }
                },
                font: {
                    color: fontcolor
                },
                shape: visShape,
                title: this.cleanLabel(label),
                nodeType: nodeType
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

    mapShape(dotShape) {
        const shapeMap = {
            'box': 'box',
            'ellipse': 'ellipse',
            'circle': 'circle',
            'diamond': 'diamond',
            'triangle': 'triangle',
            'star': 'star',
            'hexagon': 'hexagon',
            'note': 'box',
            'tab': 'box',
            'folder': 'box',
            'component': 'box'
        };
        return shapeMap[dotShape] || 'box';
    }

    detectNodeType(label, color) {
        if (label.startsWith('<') && label.endsWith('>')) return 'tag';
        if (label.includes('=')) return 'attribute';
        if (color === '#FFFACD' || color === '#fffacd') return 'text';
        return 'element';
    }

    cleanLabel(label) {
        return label
            .replace(/\\n/g, '\n')
            .replace(/\\"/g, '"')
            .replace(/^"(.*)"$/, '$1');
    }

    darkenColor(hex) {
        const color = hex.replace('#', '');
        const r = Math.max(0, parseInt(color.substr(0, 2), 16) - 30);
        const g = Math.max(0, parseInt(color.substr(2, 2), 16) - 30);
        const b = Math.max(0, parseInt(color.substr(4, 2), 16) - 30);
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }

    lightenColor(hex) {
        const color = hex.replace('#', '');
        const r = Math.min(255, parseInt(color.substr(0, 2), 16) + 30);
        const g = Math.min(255, parseInt(color.substr(2, 2), 16) + 30);
        const b = Math.min(255, parseInt(color.substr(4, 2), 16) + 30);
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // View Controls
    // ═══════════════════════════════════════════════════════════════════════════════

    fitToView() {
        if (this.network) {
            this.network.fit({ animation: { duration: 300, easingFunction: 'easeInOutQuad' } });
        }
    }

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
