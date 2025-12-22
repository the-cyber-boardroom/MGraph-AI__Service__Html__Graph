/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Cytoscape.js Renderer Component
   v0.3.0 - Consolidated from v0.2.0 → v0.2.3

   Merged features:
   - Base Cytoscape.js renderer with DOT parsing (v0.2.0)
   - Native format render() method (v0.2.3)

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
            return;
        }

        try {
            await this.loadScript('https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js');
            await this.loadScript('https://unpkg.com/dagre@0.8.5/dist/dagre.min.js');
            await this.loadScript('https://unpkg.com/cytoscape-dagre@2.5.0/cytoscape-dagre.js');

            if (window.cytoscape && window.cytoscapeDagre) {
                window.cytoscape.use(window.cytoscapeDagre);
            }

            this.isLoaded = true;
        } catch (error) {
            console.error('Failed to load Cytoscape.js:', error);
        }
    }

    loadScript(src) {
        return new Promise((resolve, reject) => {
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

    // ═══════════════════════════════════════════════════════════════════════════════
    // Native Format Rendering (from v0.2.3)
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Render graph using native Cytoscape data from API
     * @param {object} graphData - Native Cytoscape format {elements} from API
     */
    async render(graphData) {
        if (!this.isLoaded) {
            await this.loadCytoscape();
        }

        if (!this.targetCanvas) {
            throw new Error('No target canvas set for Cytoscape renderer');
        }

        const { elements } = graphData;

        // Destroy previous instance
        if (this.cy) {
            this.cy.destroy();
            this.cy = null;
        }

        // Clear and create container
        this.targetCanvas.innerHTML = '';
        const container = document.createElement('div');
        container.style.width = '100%';
        container.style.height = '100%';
        this.targetCanvas.appendChild(container);

        // Process elements - ensure proper Cytoscape structure
        const processedElements = {
            nodes: elements.nodes.map(node => ({
                ...node,
                data: {
                    ...node.data,
                    label: node.data.label || node.data.id
                }
            })),
            edges: elements.edges.map(edge => ({
                ...edge,
                data: {
                    ...edge.data,
                    source: edge.data.source,
                    target: edge.data.target
                }
            }))
        };

        // Create Cytoscape instance
        this.cy = cytoscape({
            container: container,
            elements: [...processedElements.nodes, ...processedElements.edges],
            style: [
                {
                    selector: 'node',
                    style: {
                        'label': 'data(label)',
                        'background-color': 'data(color)',
                        'color': 'data(fontColor)',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-size': '10px',
                        'font-family': 'system-ui, sans-serif',
                        'border-width': 2,
                        'border-color': 'data(borderColor)',
                        'width': 80,
                        'height': 40,
                        'shape': 'round-rectangle',
                        'text-wrap': 'wrap',
                        'text-max-width': 70
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': 'data(color)',
                        'target-arrow-color': 'data(color)',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'line-style': function(ele) {
                            return ele.data('dashed') ? 'dashed' : 'solid';
                        }
                    }
                },
                {
                    selector: ':selected',
                    style: {
                        'border-color': '#6366f1',
                        'border-width': 3,
                        'line-color': '#6366f1',
                        'target-arrow-color': '#6366f1'
                    }
                }
            ],
            layout: {
                name: 'dagre',
                rankDir: 'TB',
                nodeSep: 50,
                rankSep: 80,
                padding: 30
            }
        });

        // Fit to view
        this.cy.fit(undefined, 50);

        return { 
            nodes: elements.nodes.length, 
            edges: elements.edges.length 
        };
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // DOT Parsing (from v0.2.0 - deprecated but kept for backwards compatibility)
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Render DOT code using Cytoscape.js
     * @deprecated Use render() with native Cytoscape format instead
     */
    async renderDot(dotCode) {
        console.warn('CytoscapeRenderer.renderDot() is deprecated. Use render(graphData) with native Cytoscape format.');

        if (!this.isLoaded) {
            await this.loadCytoscape();
        }

        if (!this.targetCanvas) {
            throw new Error('No target canvas set for Cytoscape renderer');
        }

        const { nodes, edges } = this.parseDot(dotCode);

        // Destroy previous instance
        if (this.cy) {
            this.cy.destroy();
            this.cy = null;
        }

        this.targetCanvas.innerHTML = '<div id="cy-container" style="width: 100%; height: 100%; min-height: 400px;"></div>';
        const container = this.targetCanvas.querySelector('#cy-container');

        const elements = [
            ...nodes.map(n => ({ data: n })),
            ...edges.map(e => ({ data: e }))
        ];

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
                    style: { 'shape': 'ellipse' }
                },
                {
                    selector: 'node[nodeType="text"]',
                    style: { 'shape': 'rectangle', 'border-style': 'dashed' }
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
                    style: { 'line-style': 'dashed' }
                },
                {
                    selector: ':selected',
                    style: { 'border-color': '#6366f1', 'border-width': 3 }
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

        this.cy.on('layoutstop', () => {
            this.cy.fit(undefined, 30);
        });

        return { nodes: nodes.length, edges: edges.length };
    }

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

    // ═══════════════════════════════════════════════════════════════════════════════
    // View Controls
    // ═══════════════════════════════════════════════════════════════════════════════

    fitToView() {
        if (this.cy) {
            this.cy.fit(undefined, 30);
        }
    }

    exportPng() {
        if (!this.cy) return null;
        return this.cy.png({ full: true, scale: 2 });
    }

    exportSvg() {
        return null;
    }

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
