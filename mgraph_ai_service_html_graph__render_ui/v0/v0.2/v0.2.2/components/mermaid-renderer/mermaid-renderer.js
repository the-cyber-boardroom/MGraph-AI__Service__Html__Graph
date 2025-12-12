/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Mermaid.js Renderer Component (Updated)
   v0.3.0 - Uses native Mermaid format from API (no DOT-to-Mermaid conversion)

   Uses Mermaid.js for diagram visualization.
   Now receives pre-generated Mermaid code directly from the backend API.

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
     * Render graph using native Mermaid code from API
     * @param {object} graphData - Native Mermaid format {mermaid: string} from API
     */
    async render(graphData) {
        if (!this.isLoaded) {
            await this.loadMermaid();
        }

        if (!this.targetCanvas) {
            throw new Error('No target canvas set for Mermaid renderer');
        }

        // Extract mermaid code from API response
        const mermaidCode = graphData.mermaid || graphData;

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
     * Legacy: Render DOT code (for backwards compatibility)
     * @deprecated Use render(graphData) instead
     */
    async renderDot(dotCode) {
        console.warn('MermaidRenderer.renderDot() is deprecated. Use render(graphData) with native Mermaid format.');
        // Convert DOT to Mermaid (legacy fallback)
        const mermaidCode = this.dotToMermaid(dotCode);
        return this.render({ mermaid: mermaidCode });
    }

    /**
     * Legacy: Convert DOT code to Mermaid flowchart syntax
     * @deprecated - Server now generates Mermaid code directly
     */
    dotToMermaid(dotCode) {
        const nodeMap = new Map();
        let nodeIdCounter = 0;

        const getShortId = (longId) => {
            if (!nodeMap.has(longId)) {
                nodeMap.set(longId, `n${nodeIdCounter++}`);
            }
            return nodeMap.get(longId);
        };

        const nodes = [];
        const edges = [];

        // Extract nodes
        const nodeRegex = /"([^"]+)"\s*\[([^\]]+)\]/g;
        let match;

        while ((match = nodeRegex.exec(dotCode)) !== null) {
            const nodeId = match[1];
            const attrs = match[2];
            if (attrs.includes('->')) continue;

            const label = this.extractAttr(attrs, 'label') || nodeId;
            const fillcolor = this.extractAttr(attrs, 'fillcolor') || '#f5f5f5';
            const shortId = getShortId(nodeId);
            const cleanLabel = this.cleanLabel(label);
            const nodeType = this.detectNodeType(label, fillcolor);

            let nodeShape;
            switch (nodeType) {
                case 'tag':
                    nodeShape = `${shortId}((${cleanLabel}))`;
                    break;
                case 'attribute':
                    nodeShape = `${shortId}{{${cleanLabel}}}`;
                    break;
                case 'text':
                    nodeShape = `${shortId}>"${cleanLabel}"]`;
                    break;
                default:
                    nodeShape = `${shortId}[${cleanLabel}]`;
            }

            nodes.push({ id: shortId, shape: nodeShape, type: nodeType });
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
                const arrow = style === 'dashed' ? '-.->' : '-->';
                edges.push(`    ${sourceShort} ${arrow} ${targetShort}`);
            }
        }

        // Build Mermaid code
        let mermaidCode = 'flowchart TB\n';
        nodes.forEach(node => {
            mermaidCode += `    ${node.shape}\n`;
        });

        mermaidCode += '\n';

        // Add styling
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

        mermaidCode += '\n';
        mermaidCode += edges.join('\n');

        return mermaidCode;
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
            .replace(/\\n/g, ' ')
            .replace(/\\"/g, "'")
            .replace(/^"(.*)"$/, '$1')
            .replace(/[<>]/g, '')
            .replace(/[\[\]{}()]/g, '')
            .substring(0, 30);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Fit to view
     */
    fitToView() {
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
