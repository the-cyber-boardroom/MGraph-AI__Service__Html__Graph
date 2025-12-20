/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Cytoscape.js Renderer
   v0.2.2 - Surgical Override: Add native format render() method
   
   Adds to CytoscapeRenderer from v0.2.0:
   - render(): Accepts native Cytoscape format {elements} directly from API
   
   Deprecates:
   - renderDot(): Still works but logs deprecation warning
   ═══════════════════════════════════════════════════════════════════════════════ */

/**
 * NEW: Render graph using native Cytoscape data from API
 * @param {object} graphData - Native Cytoscape format {elements} from API
 */
CytoscapeRenderer.prototype.render = async function(graphData) {
    if (!this.isLoaded) {
        await this.loadCytoscape();
    }

    if (!this.targetCanvas) {
        throw new Error('No target canvas set for Cytoscape renderer');
    }

    const { elements } = graphData;

    // Clear previous content
    this.targetCanvas.innerHTML = '';

    // Create container
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
                // Ensure label exists
                label: node.data.label || node.data.id
            }
        })),
        edges: elements.edges.map(edge => ({
            ...edge,
            data: {
                ...edge.data,
                // Handle source/target
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
};

/**
 * OVERRIDE: Mark renderDot as deprecated
 */
const originalCyRenderDot = CytoscapeRenderer.prototype.renderDot;
CytoscapeRenderer.prototype.renderDot = async function(dotCode) {
    console.warn('CytoscapeRenderer.renderDot() is deprecated in v0.2.2. Use render(graphData) with native Cytoscape format.');
    return originalCyRenderDot.call(this, dotCode);
};

console.log('CytoscapeRenderer v0.2.2 surgical override loaded (native format support)');
