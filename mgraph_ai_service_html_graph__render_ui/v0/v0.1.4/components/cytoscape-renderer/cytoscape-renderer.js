/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Cytoscape.js Renderer Component
   v0.1.4 - Multiple Rendering Engines

   Uses Cytoscape.js for network visualization with multiple layout options.
   Parses DOT output and converts to Cytoscape format.

   CDN: https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js
   Layouts: https://unpkg.com/cytoscape-dagre@2.5.0/cytoscape-dagre.js
   ═══════════════════════════════════════════════════════════════════════════════ */

class CytoscapeRenderer extends HTMLElement {
    constructor() {
        super();
        this.cy = null;
        this.targetCanvas = null;
        this.isLoaded = false;
    }

    connectedCallback() {
        this.loadCytoscape();
    }

    /**
     * Load Cytoscape.js and dagre layout from CDN
     */
    async loadCytoscape() {
        if (window.cytoscape) {
            this.isLoaded = true;
            console.log('Cytoscape.js already loaded');
            return;
        }

        try {
            // Load Cytoscape core
            await this.loadScript('https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js');

            // Load dagre for hierarchical layout
            await this.loadScript('https://unpkg.com/dagre@0.8.5/dist/dagre.min.js');
            await this.loadScript('https://unpkg.com/cytoscape-dagre@2.5.0/cytoscape-dagre.js');

            // Register dagre layout
            if (window.cytoscape && window.cytoscapeDagre) {
                window.cytoscape.use(window.cytoscapeDagre);
            }

            this.isLoaded = true;
            console.log('Cytoscape.js loaded successfully');
        } catch (error) {
            console.error('Failed to load Cytoscape.js:', error);
        }
    }

    loadScript(src) {
        return new Promise((resolve, reject) => {
            // Check if already loaded
            if (document.querySelector(`script[src="${src}"]`)) {
                resolve();
                return;
            }
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
     * Render DOT code using Cytoscape.js
     */
    async renderDot(dotCode) {
        if (!this.isLoaded) {
            await this.loadCytoscape();
        }

        if (!this.targetCanvas) {
            throw new Error('No target canvas set for Cytoscape renderer');
        }

        // Parse DOT to extract nodes and edges
        const { nodes, edges } = this.parseDot(dotCode);

        // Destroy previous instance
        if (this.cy) {
            this.cy.destroy();
            this.cy = null;
        }

        // Create container
        this.targetCanvas.innerHTML = '<div id="cy-container" style="width: 100%; height: 100%; min-height: 400px;"></div>';
        const container = this.targetCanvas.querySelector('#cy-container');

        // Convert to Cytoscape format
        const elements = [
            ...nodes.map(n => ({ data: n })),
            ...edges.map(e => ({ data: e }))
        ];

        // Create Cytoscape instance
        this.cy = cytoscape({
            container: container,
            elements: elements,
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': 'data(color)',
                        'label': 'data(label)',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-size': '11px',
                        'font-family': 'system-ui, sans-serif',
                        'color': 'data(fontColor)',
                        'text-wrap': 'wrap',
                        'text-max-width': '100px',
                        'width': 'label',
                        'height': 'label',
                        'padding': '10px',
                        'shape': 'roundrectangle',
                        'border-width': 2,
                        'border-color': 'data(borderColor)'
                    }
                },
                {
                    selector: 'node[nodeType="tag"]',
                    style: {
                        'shape': 'ellipse'
                    }
                },
                {
                    selector: 'node[nodeType="text"]',
                    style: {
                        'shape': 'rectangle',
                        'border-style': 'dashed'
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 1.5,
                        'line-color': 'data(color)',
                        'target-arrow-color': 'data(color)',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'arrow-scale': 0.8
                    }
                },
                {
                    selector: 'edge[dashed]',
                    style: {
                        'line-style': 'dashed'
                    }
                },
                {
                    selector: ':selected',
                    style: {
                        'border-color': '#6366f1',
                        'border-width': 3
                    }
                }
            ],
            layout: {
                name: 'dagre',
                rankDir: 'TB',
                nodeSep: 50,
                rankSep: 80,
                padding: 30
            },
            minZoom: 0.1,
            maxZoom: 4,
            wheelSensitivity: 0.3
        });

        // Fit to view after layout
        this.cy.on('layoutstop', () => {
            this.cy.fit(undefined, 30);
        });

        return { nodes: nodes.length, edges: edges.length };
    }

    /**
     * Parse DOT code to extract nodes and edges
     */
    parseDot(dotCode) {
        const nodes = [];
        const edges = [];
        const nodeMap = new Map();

        // Extract node definitions
        const nodeRegex = /"([^"]+)"\s*\[([^\]]+)\]/g;
        let match;

        while ((match = nodeRegex.exec(dotCode)) !== null) {
            const nodeId = match[1];
            const attrs = match[2];

            if (attrs.includes('->')) continue;

            const label = this.extractAttr(attrs, 'label') || nodeId;
            const fillcolor = this.extractAttr(attrs, 'fillcolor') || '#f5f5f5';
            const fontcolor = this.extractAttr(attrs, 'fontcolor') || '#333333';

            const nodeType = this.detectNodeType(label, fillcolor);

            nodes.push({
                id: nodeId,
                label: this.cleanLabel(label),
                color: fillcolor,
                fontColor: fontcolor,
                borderColor: this.darkenColor(fillcolor),
                nodeType: nodeType
            });

            nodeMap.set(nodeId, true);
        }

        // Extract edges
        const edgeRegex = /"([^"]+)"\s*->\s*"([^"]+)"(?:\s*\[([^\]]*)\])?/g;

        while ((match = edgeRegex.exec(dotCode)) !== null) {
            const source = match[1];
            const target = match[2];
            const attrs = match[3] || '';

            if (nodeMap.has(source) && nodeMap.has(target)) {
                const style = this.extractAttr(attrs, 'style');
                const color = this.extractAttr(attrs, 'color') || '#888888';

                edges.push({
                    id: `${source}-${target}`,
                    source: source,
                    target: target,
                    color: color,
                    dashed: style === 'dashed'
                });
            }
        }

        return { nodes, edges };
    }

    /**
     * Extract attribute value from DOT attribute string
     */
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

    /**
     * Detect node type from label and color
     */
    detectNodeType(label, color) {
        if (label.startsWith('<') && label.endsWith('>')) return 'tag';
        if (label.includes('=')) return 'attribute';
        if (color === '#FFFACD' || color === '#fffacd') return 'text';
        return 'element';
    }

    /**
     * Clean label text
     */
    cleanLabel(label) {
        return label
            .replace(/\\n/g, '\n')
            .replace(/\\"/g, '"')
            .replace(/^"(.*)"$/, '$1');
    }

    /**
     * Darken a hex color
     */
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
        if (this.cy) {
            this.cy.fit(undefined, 30);
        }
    }

    /**
     * Export as PNG
     */
    exportPng() {
        if (!this.cy) return null;
        return this.cy.png({ full: true, scale: 2 });
    }

    /**
     * Export as SVG (Cytoscape doesn't support SVG directly, return null)
     */
    exportSvg() {
        return null;
    }

    /**
     * Run a different layout
     */
    runLayout(layoutName = 'dagre') {
        if (!this.cy) return;

        const layouts = {
            dagre: { name: 'dagre', rankDir: 'TB', nodeSep: 50, rankSep: 80 },
            breadthfirst: { name: 'breadthfirst', directed: true, spacingFactor: 1.5 },
            circle: { name: 'circle', spacingFactor: 1.5 },
            grid: { name: 'grid', spacingFactor: 1.2 },
            cose: { name: 'cose', nodeRepulsion: 8000, idealEdgeLength: 80 }
        };

        const layout = this.cy.layout(layouts[layoutName] || layouts.dagre);
        layout.run();
    }
}

customElements.define('cytoscape-renderer', CytoscapeRenderer);