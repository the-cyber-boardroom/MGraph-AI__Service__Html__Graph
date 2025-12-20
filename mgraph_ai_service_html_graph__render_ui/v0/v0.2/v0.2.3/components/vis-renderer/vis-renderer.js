/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - vis.js Renderer
   v0.2.2 - Surgical Override: Add native format render() method
   
   Adds to VisRenderer from v0.2.0:
   - render(): Accepts native vis.js format {nodes, edges} directly from API
   
   Deprecates:
   - renderDot(): Still works but logs deprecation warning
   ═══════════════════════════════════════════════════════════════════════════════ */

/**
 * NEW: Render graph using native vis.js data from API
 * @param {object} graphData - Native vis.js format {nodes, edges} from API
 */
VisRenderer.prototype.render = async function(graphData) {
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
};

/**
 * OVERRIDE: Mark renderDot as deprecated
 */
const originalRenderDot = VisRenderer.prototype.renderDot;
VisRenderer.prototype.renderDot = async function(dotCode) {
    console.warn('VisRenderer.renderDot() is deprecated in v0.2.2. Use render(graphData) with native vis.js format.');
    return originalRenderDot.call(this, dotCode);
};

console.log('VisRenderer v0.2.2 surgical override loaded (native format support)');
