/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - Mermaid Renderer
   v0.2.2 - Surgical Override: Add native format render() method
   
   Adds to MermaidRenderer from v0.2.0:
   - render(): Accepts native Mermaid format {mermaid} directly from API
   
   Deprecates:
   - renderDot(): Still works but logs deprecation warning
   ═══════════════════════════════════════════════════════════════════════════════ */

/**
 * NEW: Render graph using native Mermaid data from API
 * @param {object} graphData - Native Mermaid format {mermaid} from API
 */
MermaidRenderer.prototype.render = async function(graphData) {
    if (!this.isLoaded) {
        await this.loadMermaid();
    }

    if (!this.targetCanvas) {
        throw new Error('No target canvas set for Mermaid renderer');
    }

    const { mermaid: mermaidCode } = graphData;

    // Clear previous content
    this.targetCanvas.innerHTML = '';

    // Create container for Mermaid
    const container = document.createElement('div');
    container.className = 'mermaid';
    container.style.width = '100%';
    container.style.display = 'flex';
    container.style.justifyContent = 'center';
    container.style.alignItems = 'flex-start';
    container.style.padding = '20px';
    container.style.overflow = 'auto';
    
    // Set the pre-generated Mermaid code
    container.textContent = mermaidCode;
    this.targetCanvas.appendChild(container);

    // Initialize Mermaid if needed
    if (!this.mermaidInitialized) {
        mermaid.initialize({
            startOnLoad: false,
            theme: 'default',
            securityLevel: 'loose',
            flowchart: {
                htmlLabels: true,
                curve: 'basis',
                rankSpacing: 50,
                nodeSpacing: 30
            }
        });
        this.mermaidInitialized = true;
    }

    // Render the diagram
    try {
        const { svg } = await mermaid.render('mermaid-diagram', mermaidCode);
        container.innerHTML = svg;
        
        // Style the SVG for better display
        const svgElement = container.querySelector('svg');
        if (svgElement) {
            svgElement.style.maxWidth = '100%';
            svgElement.style.height = 'auto';
        }
    } catch (error) {
        console.error('Mermaid render error:', error);
        container.innerHTML = `
            <div style="color: #dc3545; padding: 20px;">
                <strong>Mermaid Render Error:</strong><br>
                ${error.message || 'Failed to render diagram'}
            </div>
        `;
    }

    return { mermaid_size: mermaidCode.length };
};

/**
 * OVERRIDE: Mark renderDot as deprecated
 */
const originalMermaidRenderDot = MermaidRenderer.prototype.renderDot;
MermaidRenderer.prototype.renderDot = async function(dotCode) {
    console.warn('MermaidRenderer.renderDot() is deprecated in v0.2.2. Use render(graphData) with native Mermaid format.');
    return originalMermaidRenderDot.call(this, dotCode);
};

console.log('MermaidRenderer v0.2.2 surgical override loaded (native format support)');
