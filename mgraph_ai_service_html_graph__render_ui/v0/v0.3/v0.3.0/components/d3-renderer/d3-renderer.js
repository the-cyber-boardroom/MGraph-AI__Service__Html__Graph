/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - D3.js Force-Directed Renderer Component
   v0.3.0 - Consolidated from v0.2.0 → v0.2.3 → v0.2.8

   Merged features:
   - Base D3.js renderer with DOT parsing (v0.2.0)
   - Native format render() method (v0.2.3)
   - Fixed trackpad zoom + auto-fit after simulation (v0.2.8)

   CDN: https://d3js.org/d3.v7.min.js
   ═══════════════════════════════════════════════════════════════════════════════ */

class D3Renderer extends HTMLElement {
    constructor() {
        super();
        this.svg = null;
        this.g = null;
        this.zoom = null;
        this.simulation = null;
        this.nodes = null;
        this.width = 800;
        this.height = 600;
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

    // ═══════════════════════════════════════════════════════════════════════════════
    // Native Format Rendering (from v0.2.3 + v0.2.8 fixes)
    // ═══════════════════════════════════════════════════════════════════════════════

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

        const { nodes, links } = graphData;
        const self = this;

        // Clear previous content
        this.targetCanvas.innerHTML = '';

        this.width = this.targetCanvas.clientWidth || 800;
        this.height = this.targetCanvas.clientHeight || 600;

        // Create SVG
        this.svg = d3.select(this.targetCanvas)
            .append('svg')
            .attr('width', '100%')
            .attr('height', '100%')
            .attr('viewBox', [0, 0, this.width, this.height])
            .attr('preserveAspectRatio', 'xMidYMid meet');

        // Create container group for zoom
        this.g = this.svg.append('g');

        // v0.2.8: Improved zoom with trackpad support and proper scale extent
        this.zoom = d3.zoom()
            .scaleExtent([0.01, 50])
            .filter(event => {
                if (event.type === 'wheel') return true;
                if (event.type.startsWith('touch')) return true;
                return !event.button;
            })
            .on('zoom', (event) => this.g.attr('transform', event.transform));

        this.svg.call(this.zoom);
        this.svg.on('wheel.preventDefault', event => event.preventDefault());

        // Create arrow marker for edges
        this.svg.append('defs').append('marker')
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
        const link = this.g.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(links)
            .join('line')
            .attr('stroke', d => d.color || '#888888')
            .attr('stroke-width', d => d.width || 1.5)
            .attr('stroke-dasharray', d => d.dashed ? '5,5' : null)
            .attr('marker-end', 'url(#d3-arrow)');

        // Create node groups
        const node = this.g.append('g')
            .attr('class', 'nodes')
            .selectAll('g')
            .data(nodes)
            .join('g')
            .call(this.drag(d3.forceSimulation()));

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
        this.simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(80))
            .force('charge', d3.forceManyBody().strength(-200))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2))
            .force('collision', d3.forceCollide().radius(d => (d.radius || 25) + 5));

        // Update drag with actual simulation
        node.call(this.drag(this.simulation));

        // Store nodes reference
        this.nodes = nodes;

        // Tick function
        this.simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node.attr('transform', d => `translate(${d.x},${d.y})`);
        });

        // v0.2.8: Auto-fit to viewport after simulation stabilizes
        let hasFitted = false;

        const doFit = () => {
            if (!hasFitted) {
                hasFitted = true;
                this.fitToViewInternal();
            }
        };

        this.simulation.on('end', doFit);

        const checkAndFit = () => {
            if (hasFitted) return;
            if (this.simulation.alpha() < 0.1) {
                doFit();
            } else {
                requestAnimationFrame(checkAndFit);
            }
        };

        setTimeout(checkAndFit, 100);

        // Fallback: force fit after 5 seconds for very large graphs
        setTimeout(() => {
            if (!hasFitted) {
                this.simulation.stop();
                doFit();
            }
        }, 5000);

        return { nodes: nodes.length, links: links.length };
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

    // ═══════════════════════════════════════════════════════════════════════════════
    // DOT Parsing (from v0.2.0 - deprecated but kept for backwards compatibility)
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Render DOT code using D3.js force-directed layout
     * @deprecated Use render() with native D3 format instead
     */
    async renderDot(dotCode) {
        console.warn('D3Renderer.renderDot() is deprecated. Use render(graphData) with native D3 format.');
        
        if (!this.isLoaded) {
            await this.loadD3();
        }

        if (!this.targetCanvas) {
            throw new Error('No target canvas set for D3 renderer');
        }

        // Parse DOT to extract nodes and links
        const { nodes, links } = this.parseDot(dotCode);

        // Use the native render method
        return this.render({ nodes, links });
    }

    /**
     * Parse DOT code to extract nodes and links
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
        return label
            .replace(/\\n/g, ' ')
            .replace(/\\"/g, '"')
            .replace(/^"(.*)"$/, '$1');
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Zoom Controls (from v0.2.8)
    // ═══════════════════════════════════════════════════════════════════════════════

    /**
     * Internal fit-to-view that calculates proper transform
     */
    fitToViewInternal() {
        if (!this.nodes || this.nodes.length === 0) return;

        let minX = Infinity, maxX = -Infinity;
        let minY = Infinity, maxY = -Infinity;
        let validNodes = 0;

        this.nodes.forEach(node => {
            if (node.x == null || node.y == null || isNaN(node.x) || isNaN(node.y)) return;

            validNodes++;
            const r = node.radius || 25;
            if (node.x - r < minX) minX = node.x - r;
            if (node.x + r > maxX) maxX = node.x + r;
            if (node.y - r < minY) minY = node.y - r;
            if (node.y + r > maxY) maxY = node.y + r;
        });

        if (validNodes === 0) return;

        const padding = 50;
        minX -= padding;
        minY -= padding;
        maxX += padding;
        maxY += padding;

        const graphWidth = maxX - minX;
        const graphHeight = maxY - minY;

        const scale = Math.min(
            this.width / graphWidth,
            this.height / graphHeight
        );

        const centerX = (minX + maxX) / 2;
        const centerY = (minY + maxY) / 2;
        const translateX = this.width / 2 - centerX * scale;
        const translateY = this.height / 2 - centerY * scale;

        const transform = d3.zoomIdentity
            .translate(translateX, translateY)
            .scale(scale);

        this.svg.transition()
            .duration(500)
            .call(this.zoom.transform, transform);
    }

    zoomIn() {
        if (this.svg && this.zoom) {
            this.svg.transition().duration(300).call(this.zoom.scaleBy, 1.5);
        }
    }

    zoomOut() {
        if (this.svg && this.zoom) {
            this.svg.transition().duration(300).call(this.zoom.scaleBy, 0.67);
        }
    }

    zoomReset() {
        if (this.svg && this.zoom) {
            this.svg.transition().duration(300).call(this.zoom.transform, d3.zoomIdentity);
        }
    }

    fitToView() {
        this.fitToViewInternal();
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Utility Methods
    // ═══════════════════════════════════════════════════════════════════════════════

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

    exportSvg() {
        if (!this.svg) return null;
        const svgNode = this.svg.node();
        const serializer = new XMLSerializer();
        return serializer.serializeToString(svgNode);
    }
}

customElements.define('d3-renderer', D3Renderer);
