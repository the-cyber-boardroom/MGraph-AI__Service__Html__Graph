/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - D3.js Renderer
   v0.2.2 - Surgical Override: Add native format render() method
   
   Adds to D3Renderer from v0.2.0:
   - render(): Accepts native D3 format {nodes, links} directly from API
   
   Deprecates:
   - renderDot(): Still works but logs deprecation warning
   ═══════════════════════════════════════════════════════════════════════════════ */

/**
 * NEW: Render graph using native D3 data from API
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

    // Clear previous content
    this.targetCanvas.innerHTML = '';

    const width = this.targetCanvas.clientWidth || 800;
    const height = this.targetCanvas.clientHeight || 600;

    // Create SVG
    const svg = d3.select(this.targetCanvas)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('viewBox', [0, 0, width, height]);

    // Create container group for zoom
    const g = svg.append('g');

    // Add zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => g.attr('transform', event.transform));
    svg.call(zoom);

    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(d => (d.radius || 25) + 10));

    // Create links
    const link = g.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('stroke', d => d.color || '#888888')
        .attr('stroke-width', d => d.width || 1)
        .attr('stroke-dasharray', d => d.dashed ? '5,5' : null);

    // Create node groups
    const node = g.append('g')
        .attr('class', 'nodes')
        .selectAll('g')
        .data(nodes)
        .join('g')
        .call(this.drag(simulation));

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

    // Tick function
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Store simulation reference
    this.simulation = simulation;

    return { nodes: nodes.length, links: links.length };
};

/**
 * OVERRIDE: Mark renderDot as deprecated
 */
const originalD3RenderDot = D3Renderer.prototype.renderDot;
D3Renderer.prototype.renderDot = async function(dotCode) {
    console.warn('D3Renderer.renderDot() is deprecated in v0.2.2. Use render(graphData) with native D3 format.');
    return originalD3RenderDot.call(this, dotCode);
};

console.log('D3Renderer v0.2.2 surgical override loaded (native format support)');
