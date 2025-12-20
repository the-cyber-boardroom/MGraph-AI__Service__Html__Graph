/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - D3.js Renderer
   v0.2.7 - Surgical Override: Fix trackpad zoom + auto-fit after simulation

   Fixes:
   - Trackpad pinch-to-zoom now works correctly
   - Graph auto-fits to viewport after simulation stabilizes
   - Zoom extent is relative to fitted view, not raw simulation output

   Root cause:
   1. Browser translates trackpad pinch to wheel events with ctrlKey=true
   2. Graph wasn't being fitted after simulation, so zoom extent was wrong
   ═══════════════════════════════════════════════════════════════════════════════ */

/**
 * OVERRIDE: Render graph with fixed zoom behavior for trackpad support
 * @param {object} graphData - Native D3 format {nodes, links} from API
 */
D3Renderer.prototype.render = async function(graphData) {
    if (!this.isLoaded) {
        await this.loadD3();
    }

    if (!this.targetCanvas) {
        throw new Error('No target canvas set for D3 renderer');
    }

    const { nodes, links } = graphData;
    const self = this;

    // Clear previous content
    this.targetCanvas.innerHTML = '';

    const width = this.targetCanvas.clientWidth || 800;
    const height = this.targetCanvas.clientHeight || 600;

    // Create SVG
    const svg = d3.select(this.targetCanvas)
        .append('svg')
        .attr('width', '100%')
        .attr('height', '100%')
        .attr('viewBox', [0, 0, width, height])
        .attr('preserveAspectRatio', 'xMidYMid meet');

    // Create container group for zoom
    const g = svg.append('g');

    // ═══════════════════════════════════════════════════════════════════════════
    // v0.2.7 FIX: Improved zoom with trackpad support and proper scale extent
    // ═══════════════════════════════════════════════════════════════════════════
    const zoom = d3.zoom()
        .scaleExtent([0.01, 50])  // Much wider range: 1% to 5000%
        .filter(event => {
            // Allow all wheel events (trackpad pinch sends wheel with ctrlKey=true)
            if (event.type === 'wheel') return true;
            // Allow touch events
            if (event.type.startsWith('touch')) return true;
            // Block right-click, allow left-click drag
            return !event.button;
        })
        .on('zoom', (event) => g.attr('transform', event.transform));

    svg.call(zoom);

    // Prevent wheel events from scrolling the page
    svg.on('wheel.preventDefault', event => event.preventDefault());
    // ═══════════════════════════════════════════════════════════════════════════

    // Create arrow marker for edges
    svg.append('defs').append('marker')
        .attr('id', 'd3-arrow')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 35)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('fill', '#888888')
        .attr('d', 'M0,-5L10,0L0,5');

    // Create links
    const link = g.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('stroke', d => d.color || '#888888')
        .attr('stroke-width', d => d.width || 1.5)
        .attr('stroke-dasharray', d => d.dashed ? '5,5' : null)
        .attr('marker-end', 'url(#d3-arrow)');

    // Create node groups
    const node = g.append('g')
        .attr('class', 'nodes')
        .selectAll('g')
        .data(nodes)
        .join('g')
        .call(this.drag(d3.forceSimulation())); // Temporary, will be updated

    // Add circles to nodes
    node.append('circle')
        .attr('r', d => d.radius || 25)
        .attr('fill', d => d.color || '#E8E8E8')
        .attr('stroke', d => this.darkenColor(d.color || '#E8E8E8'))
        .attr('stroke-width', 2);

    // Add labels to nodes
    node.append('text')
        .text(d => d.label || d.id)
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .attr('fill', d => d.fontColor || '#333333')
        .style('font-size', '10px')
        .style('font-family', 'system-ui, sans-serif')
        .style('pointer-events', 'none');

    // Add tooltips
    node.append('title')
        .text(d => `${d.label || d.id}\n${d.domPath || ''}`);

    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(80))
        .force('charge', d3.forceManyBody().strength(-200))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(d => (d.radius || 25) + 5));

    // Update drag with actual simulation
    node.call(this.drag(simulation));

    // Tick function
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // ═══════════════════════════════════════════════════════════════════════════
    // v0.2.7 FIX: Auto-fit to viewport after simulation stabilizes
    // ═══════════════════════════════════════════════════════════════════════════
    let hasFitted = false;

    const doFit = () => {
        if (!hasFitted) {
            hasFitted = true;
            self.fitToViewInternal(svg, g, zoom, nodes, width, height);
        }
    };

    simulation.on('end', doFit);

    // For large graphs, fit once simulation has mostly settled (alpha < 0.1)
    // This runs much faster than waiting for full stabilization
    const checkAndFit = () => {
        if (hasFitted) return;
        if (simulation.alpha() < 0.1) {
            doFit();
        } else {
            requestAnimationFrame(checkAndFit);
        }
    };

    // Start checking after a brief delay to let simulation begin
    setTimeout(checkAndFit, 100);

    // Fallback: force fit after 5 seconds for very large graphs
    setTimeout(() => {
        if (!hasFitted) {
            simulation.stop();
            doFit();
        }
    }, 5000);
    // ═══════════════════════════════════════════════════════════════════════════

    // Store references for external access
    this.simulation = simulation;
    this.svg = svg;
    this.g = g;
    this.zoom = zoom;
    this.nodes = nodes;
    this.width = width;
    this.height = height;

    return { nodes: nodes.length, links: links.length };
};

/**
 * NEW: Internal fit-to-view that calculates proper transform
 */
D3Renderer.prototype.fitToViewInternal = function(svg, g, zoom, nodes, width, height) {
    if (!nodes || nodes.length === 0) return;

    // Calculate bounding box of all nodes
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;
    let validNodes = 0;

    nodes.forEach(node => {
        // Skip nodes without valid positions
        if (node.x == null || node.y == null || isNaN(node.x) || isNaN(node.y)) return;

        validNodes++;
        const r = node.radius || 25;
        if (node.x - r < minX) minX = node.x - r;
        if (node.x + r > maxX) maxX = node.x + r;
        if (node.y - r < minY) minY = node.y - r;
        if (node.y + r > maxY) maxY = node.y + r;
    });

    // Need at least some valid nodes
    if (validNodes === 0) return;

    // Add padding
    const padding = 50;
    minX -= padding;
    minY -= padding;
    maxX += padding;
    maxY += padding;

    const graphWidth = maxX - minX;
    const graphHeight = maxY - minY;

    // Calculate scale to fit - NO upper limit, let it zoom out as much as needed
    const scale = Math.min(
        width / graphWidth,
        height / graphHeight
    );

    // Calculate translation to center
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;
    const translateX = width / 2 - centerX * scale;
    const translateY = height / 2 - centerY * scale;

    // Apply transform
    const transform = d3.zoomIdentity
        .translate(translateX, translateY)
        .scale(scale);

    svg.transition()
        .duration(500)
        .call(zoom.transform, transform);
};

/**
 * Programmatic zoom controls
 */
D3Renderer.prototype.zoomIn = function() {
    if (this.svg && this.zoom) {
        this.svg.transition().duration(300).call(this.zoom.scaleBy, 1.5);
    }
};

D3Renderer.prototype.zoomOut = function() {
    if (this.svg && this.zoom) {
        this.svg.transition().duration(300).call(this.zoom.scaleBy, 0.67);
    }
};

D3Renderer.prototype.zoomReset = function() {
    if (this.svg && this.zoom) {
        this.svg.transition().duration(300).call(this.zoom.transform, d3.zoomIdentity);
    }
};

D3Renderer.prototype.fitToView = function() {
    if (this.svg && this.g && this.zoom && this.nodes) {
        this.fitToViewInternal(this.svg, this.g, this.zoom, this.nodes, this.width, this.height);
    }
};

console.log('D3Renderer v0.2.7 surgical override loaded (trackpad zoom + auto-fit)');