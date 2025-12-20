/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - D3.js Force-Directed Renderer Component (Updated)
   v0.3.0 - Uses native D3 format from API (no DOT parsing)

   Uses D3.js for force-directed graph visualization.
   Now receives pre-processed data directly from the backend API.

   CDN: https://d3js.org/d3.v7.min.js
   ═══════════════════════════════════════════════════════════════════════════════ */

class D3Renderer extends HTMLElement {
    constructor() {
        super();
        this.svg = null;
        this.simulation = null;
        this.targetCanvas = null;
        this.isLoaded = false;
    }

    connectedCallback() {
        this.loadD3();
    }

    /**
     * Load D3.js from CDN
     */
    async loadD3() {
        if (window.d3) {
            this.isLoaded = true;
            return;
        }

        try {
            await this.loadScript('https://d3js.org/d3.v7.min.js');
            this.isLoaded = true;
        } catch (error) {
            console.error('Failed to load D3.js:', error);
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
     * Render graph using native D3 data from API
     * @param {object} graphData - Native D3 format {nodes, links} from API
     */
    async render(graphData) {
        if (!this.isLoaded) {
            await this.loadD3();
        }

        if (!this.targetCanvas) {
            throw new Error('No target canvas set for D3 renderer');
        }

        // D3 uses 'links' not 'edges'
        const nodes = graphData.nodes.map(n => ({ ...n }));  // Clone to avoid mutation
        const links = graphData.links.map(l => ({ ...l }));

        // Get dimensions
        const width = this.targetCanvas.clientWidth || 800;
        const height = this.targetCanvas.clientHeight || 600;

        // Clear previous content
        this.targetCanvas.innerHTML = '';

        // Stop previous simulation
        if (this.simulation) {
            this.simulation.stop();
        }

        // Create SVG
        this.svg = d3.select(this.targetCanvas)
            .append('svg')
            .attr('width', '100%')
            .attr('height', '100%')
            .attr('viewBox', [0, 0, width, height])
            .attr('style', 'max-width: 100%; height: auto;');

        // Add zoom behavior
        const g = this.svg.append('g');

        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            });

        this.svg.call(zoom);

        // Create arrow marker for directed edges
        this.svg.append('defs').append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '-0 -5 10 10')
            .attr('refX', 20)
            .attr('refY', 0)
            .attr('orient', 'auto')
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .append('path')
            .attr('d', 'M 0,-5 L 10,0 L 0,5')
            .attr('fill', '#888');

        // Create force simulation
        this.simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(80))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(d => d.radius || 40));

        // Create links
        const link = g.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(links)
            .join('line')
            .attr('stroke', d => d.color || '#888')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', d => d.width || 1.5)
            .attr('stroke-dasharray', d => d.dashed ? '5,5' : null)
            .attr('marker-end', 'url(#arrowhead)');

        // Create node groups
        const node = g.append('g')
            .attr('class', 'nodes')
            .selectAll('g')
            .data(nodes)
            .join('g')
            .call(this.drag(this.simulation));

        // Add rectangles for nodes
        node.append('rect')
            .attr('width', d => Math.max(60, d.label.length * 7 + 20))
            .attr('height', 30)
            .attr('x', d => -Math.max(60, d.label.length * 7 + 20) / 2)
            .attr('y', -15)
            .attr('rx', 6)
            .attr('ry', 6)
            .attr('fill', d => d.color || '#f5f5f5')
            .attr('stroke', d => this.darkenColor(d.color || '#f5f5f5'))
            .attr('stroke-width', 2)
            .style('cursor', 'grab');

        // Add labels
        node.append('text')
            .attr('dy', 4)
            .attr('text-anchor', 'middle')
            .attr('font-size', '11px')
            .attr('font-family', 'system-ui, sans-serif')
            .attr('fill', d => d.fontColor || '#333')
            .text(d => this.truncateLabel(d.label, 20));

        // Add tooltips
        node.append('title')
            .text(d => d.value || d.label);

        // Update positions on tick
        this.simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node.attr('transform', d => `translate(${d.x},${d.y})`);
        });

        // Run simulation for a bit then stop
        this.simulation.alpha(1).restart();

        setTimeout(() => {
            this.simulation.stop();
        }, 3000);

        return { nodes: nodes.length, links: links.length };
    }

    /**
     * Legacy: Render DOT code (for backwards compatibility)
     * @deprecated Use render(graphData) instead
     */
    async renderDot(dotCode) {
        console.warn('D3Renderer.renderDot() is deprecated. Use render(graphData) with native D3 format.');
        const { nodes, links } = this.parseDot(dotCode);
        return this.render({ nodes, links });
    }

    /**
     * Create drag behavior
     */
    drag(simulation) {
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }

        return d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended);
    }

    /**
     * Legacy: Parse DOT code (for backwards compatibility)
     * @deprecated
     */
    parseDot(dotCode) {
        const nodes = [];
        const links = [];
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
                color: fillcolor,
                fontColor: fontcolor
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

                links.push({
                    source: source,
                    target: target,
                    dashed: style === 'dashed',
                    color: color
                });
            }
        }

        return { nodes, links };
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
        return label.replace(/\\n/g, ' ').replace(/\\"/g, '"').replace(/^"(.*)"$/, '$1');
    }

    truncateLabel(label, maxLength) {
        if (label.length <= maxLength) return label;
        return label.substring(0, maxLength - 3) + '...';
    }

    darkenColor(hex) {
        const color = hex.replace('#', '');
        const r = Math.max(0, parseInt(color.substr(0, 2), 16) - 30);
        const g = Math.max(0, parseInt(color.substr(2, 2), 16) - 30);
        const b = Math.max(0, parseInt(color.substr(4, 2), 16) - 30);
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }

    /**
     * Fit to view
     */
    fitToView() {
        if (this.svg) {
            this.svg.transition().duration(300).call(
                d3.zoom().transform,
                d3.zoomIdentity
            );
        }
    }

    /**
     * Export as SVG
     */
    exportSvg() {
        if (!this.svg) return null;
        const svgNode = this.svg.node();
        const serializer = new XMLSerializer();
        return serializer.serializeToString(svgNode);
    }
}

customElements.define('d3-renderer', D3Renderer);
