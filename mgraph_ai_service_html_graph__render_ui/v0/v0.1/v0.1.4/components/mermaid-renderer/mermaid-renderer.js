/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Mermaid.js Renderer Component
   v0.1.4 - Multiple Rendering Engines

   Uses Mermaid.js for diagram visualization.
   Converts DOT output to Mermaid flowchart syntax.

   CDN: https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js
   ═══════════════════════════════════════════════════════════════════════════════ */

class MermaidRenderer extends HTMLElement {
    constructor() {
        super();
        this.targetCanvas = null;
        this.isLoaded = false;
        this.renderCount = 0;
    }

    connectedCallback() {
        this.loadMermaid();
    }

    /**
     * Load Mermaid.js from CDN
     */
    async loadMermaid() {
        if (window.mermaid) {
            this.isLoaded = true;
            //console.log('Mermaid.js already loaded');
            return;
        }

        try {
            await this.loadScript('https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js');

            // Initialize mermaid with config
            window.mermaid.initialize({
                startOnLoad: false,
                theme: 'default',
                flowchart: {
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis',
                    rankSpacing: 50,
                    nodeSpacing: 30
                },
                securityLevel: 'loose'
            });

            this.isLoaded = true;
            //console.log('Mermaid.js loaded successfully');
        } catch (error) {
            console.error('Failed to load Mermaid.js:', error);
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

    /**
     * Render DOT code using Mermaid.js
     */
    async renderDot(dotCode) {
        if (!this.isLoaded) {
            await this.loadMermaid();
        }

        if (!this.targetCanvas) {
            throw new Error('No target canvas set for Mermaid renderer');
        }

        // Convert DOT to Mermaid flowchart syntax
        const mermaidCode = this.dotToMermaid(dotCode);

        // Create unique ID for this render
        this.renderCount++;
        const containerId = `mermaid-graph-${this.renderCount}`;

        // Create container
        this.targetCanvas.innerHTML = `
            <div id="${containerId}" class="mermaid-container" style="width: 100%; height: 100%; overflow: auto; display: flex; justify-content: center; align-items: flex-start; padding: 20px;">
                <pre class="mermaid">${mermaidCode}</pre>
            </div>
        `;

        try {
            // Render mermaid diagram
            await window.mermaid.run({
                querySelector: `#${containerId} .mermaid`
            });

            // Get SVG and make it zoomable
            const svg = this.targetCanvas.querySelector('svg');
            if (svg) {
                svg.style.maxWidth = 'none';
                svg.style.cursor = 'grab';
            }

            return { success: true };
        } catch (error) {
            console.error('Mermaid render error:', error);
            // Show the mermaid code if rendering fails
            this.targetCanvas.innerHTML = `
                <div style="padding: 20px;">
                    <div style="color: #d97706; margin-bottom: 10px;">
                        ⚠️ Mermaid rendering encountered an issue. Showing generated code:
                    </div>
                    <pre style="background: #f5f5f5; padding: 15px; border-radius: 8px; font-size: 0.85em; overflow: auto; max-height: 400px;">${this.escapeHtml(mermaidCode)}</pre>
                </div>
            `;
            throw error;
        }
    }

    /**
     * Convert DOT code to Mermaid flowchart syntax
     */
    dotToMermaid(dotCode) {
        const nodes = [];
        const edges = [];
        const nodeMap = new Map();
        let nodeIdCounter = 0;

        // Generate short IDs for Mermaid (it doesn't like long hex IDs)
        const getShortId = (longId) => {
            if (!nodeMap.has(longId)) {
                nodeMap.set(longId, `n${nodeIdCounter++}`);
            }
            return nodeMap.get(longId);
        };

        // Extract node definitions
        const nodeRegex = /"([^"]+)"\s*\[([^\]]+)\]/g;
        let match;

        while ((match = nodeRegex.exec(dotCode)) !== null) {
            const nodeId = match[1];
            const attrs = match[2];

            if (attrs.includes('->')) continue;

            const label = this.extractAttr(attrs, 'label') || nodeId;
            const fillcolor = this.extractAttr(attrs, 'fillcolor') || '#f5f5f5';
            const shape = this.extractAttr(attrs, 'shape') || 'box';

            const shortId = getShortId(nodeId);
            const cleanLabel = this.cleanLabel(label).replace(/"/g, "'").replace(/\n/g, ' ');
            const nodeType = this.detectNodeType(label, fillcolor);

            // Mermaid node shapes
            let nodeShape;
            switch (nodeType) {
                case 'tag':
                    nodeShape = `${shortId}((${cleanLabel}))`;  // Circle
                    break;
                case 'attribute':
                    nodeShape = `${shortId}{{${cleanLabel}}}`;  // Hexagon
                    break;
                case 'text':
                    nodeShape = `${shortId}>"${cleanLabel}"]`;  // Flag/ribbon
                    break;
                default:
                    nodeShape = `${shortId}[${cleanLabel}]`;    // Rectangle
            }

            nodes.push({
                id: shortId,
                originalId: nodeId,
                shape: nodeShape,
                color: fillcolor,
                type: nodeType
            });
        }

        // Extract edges
        const edgeRegex = /"([^"]+)"\s*->\s*"([^"]+)"(?:\s*\[([^\]]*)\])?/g;

        while ((match = edgeRegex.exec(dotCode)) !== null) {
            const source = match[1];
            const target = match[2];
            const attrs = match[3] || '';

            if (nodeMap.has(source) && nodeMap.has(target)) {
                const sourceShort = getShortId(source);
                const targetShort = getShortId(target);
                const style = this.extractAttr(attrs, 'style');

                // Mermaid edge syntax
                const arrow = style === 'dashed' ? '-.->' : '-->';
                edges.push(`    ${sourceShort} ${arrow} ${targetShort}`);
            }
        }

        // Build Mermaid flowchart
        let mermaidCode = 'flowchart TB\n';

        // Add node definitions
        nodes.forEach(node => {
            mermaidCode += `    ${node.shape}\n`;
        });

        // Add styling
        mermaidCode += '\n';

        // Group nodes by type for styling
        const tagNodes = nodes.filter(n => n.type === 'tag').map(n => n.id);
        const attrNodes = nodes.filter(n => n.type === 'attribute').map(n => n.id);
        const textNodes = nodes.filter(n => n.type === 'text').map(n => n.id);
        const elemNodes = nodes.filter(n => n.type === 'element').map(n => n.id);

        if (tagNodes.length > 0) {
            mermaidCode += `    style ${tagNodes.join(',')} fill:#4A90D9,stroke:#2E5B8A,color:#FFFFFF\n`;
        }
        if (attrNodes.length > 0) {
            mermaidCode += `    style ${attrNodes.join(',')} fill:#B39DDB,stroke:#7E57C2,color:#333333\n`;
        }
        if (textNodes.length > 0) {
            mermaidCode += `    style ${textNodes.join(',')} fill:#FFFACD,stroke:#DAA520,color:#333333\n`;
        }
        if (elemNodes.length > 0) {
            mermaidCode += `    style ${elemNodes.join(',')} fill:#E8E8E8,stroke:#999999,color:#333333\n`;
        }

        // Add edges
        mermaidCode += '\n';
        mermaidCode += edges.join('\n');

        return mermaidCode;
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
     * Clean label text for Mermaid
     */
    cleanLabel(label) {
        return label
            .replace(/\\n/g, ' ')
            .replace(/\\"/g, "'")
            .replace(/^"(.*)"$/, '$1')
            .replace(/[<>]/g, '')  // Remove angle brackets (conflict with Mermaid syntax)
            .replace(/[\[\]{}()]/g, '')  // Remove brackets
            .substring(0, 30);  // Limit length
    }

    /**
     * Escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Fit to view
     */
    fitToView() {
        // Mermaid SVGs are auto-fitted, just scroll to top
        if (this.targetCanvas) {
            this.targetCanvas.scrollTop = 0;
        }
    }

    /**
     * Export as SVG
     */
    exportSvg() {
        const svg = this.targetCanvas?.querySelector('svg');
        if (!svg) return null;
        const serializer = new XMLSerializer();
        return serializer.serializeToString(svg);
    }
}

customElements.define('mermaid-renderer', MermaidRenderer);