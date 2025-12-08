/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - DOT Renderer Component
   v0.2.0 - Consolidated from v0.1.x
   
   Renders DOT/Graphviz strings to SVG using viz-js (WebAssembly Graphviz)
   ═══════════════════════════════════════════════════════════════════════════════ */

/**
 * DOT Renderer Component
 * Renders DOT/Graphviz strings to SVG using viz-js (WebAssembly Graphviz)
 */
class DotRenderer extends HTMLElement {
    constructor() {
        super();
        this.viz = null;
        this.vizLoading = null;
        this.graphCanvas = null;
    }

    connectedCallback() {
        // This component is invisible - it just provides rendering capability
        this.style.display = 'none';
        
        // Get reference to graph-canvas
        this.graphCanvas = document.querySelector('graph-canvas');
        
        // Load viz-js library
        this.loadVizJs();
    }

    /**
     * Load viz-js from CDN
     */
    async loadVizJs() {
        if (this.viz) return this.viz;
        if (this.vizLoading) return this.vizLoading;

        this.vizLoading = new Promise(async (resolve, reject) => {
            try {
                // Check if already loaded
                if (typeof Viz !== 'undefined') {
                    this.viz = await Viz.instance();
                    resolve(this.viz);
                    return;
                }

                // Load viz-js from CDN
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/@viz-js/viz@3.2.4/lib/viz-standalone.js';
                script.async = true;

                script.onload = async () => {
                    try {
                        this.viz = await Viz.instance();
                        //console.log('viz-js loaded successfully');
                        resolve(this.viz);
                    } catch (err) {
                        reject(new Error(`Failed to initialize viz-js: ${err.message}`));
                    }
                };

                script.onerror = () => {
                    reject(new Error('Failed to load viz-js from CDN'));
                };

                document.head.appendChild(script);
            } catch (error) {
                reject(error);
            }
        });

        return this.vizLoading;
    }

    /**
     * Render DOT string to SVG
     * @param {string} dotString - DOT language string
     * @param {object} options - Rendering options
     * @returns {Promise<string>} SVG string
     */
    async renderDot(dotString, options = {}) {
        if (!dotString || !dotString.trim()) {
            throw new Error('Empty DOT string');
        }

        try {
            // Ensure viz-js is loaded
            const viz = await this.loadVizJs();

            // Render DOT to SVG
            const svg = viz.renderSVGElement(dotString, {
                engine: options.engine || 'dot',
                format: 'svg'
            });

            // Convert SVG element to string
            const svgString = new XMLSerializer().serializeToString(svg);

            // Update graph canvas if available
            if (this.graphCanvas) {
                this.graphCanvas.renderSvg(svgString);
            }

            return svgString;
        } catch (error) {
            console.error('DOT rendering error:', error);
            
            // Show error in canvas
            if (this.graphCanvas) {
                this.graphCanvas.showError('Failed to render DOT graph', error.message);
            }

            throw error;
        }
    }

    /**
     * Render DOT to PNG (via SVG)
     * @param {string} dotString - DOT language string
     * @param {object} options - Rendering options
     * @returns {Promise<Blob>} PNG blob
     */
    async renderToPng(dotString, options = {}) {
        const svgString = await this.renderDot(dotString, options);
        
        return new Promise((resolve, reject) => {
            const img = new Image();
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');

            img.onload = () => {
                canvas.width = img.width * (options.scale || 2);
                canvas.height = img.height * (options.scale || 2);
                ctx.scale(options.scale || 2, options.scale || 2);
                ctx.drawImage(img, 0, 0);
                canvas.toBlob(resolve, 'image/png');
            };

            img.onerror = () => reject(new Error('Failed to convert SVG to PNG'));

            const svgBlob = new Blob([svgString], { type: 'image/svg+xml' });
            img.src = URL.createObjectURL(svgBlob);
        });
    }

    /**
     * Check if viz-js is ready
     * @returns {boolean}
     */
    isReady() {
        return this.viz !== null;
    }

    /**
     * Get supported engines
     * @returns {string[]}
     */
    getSupportedEngines() {
        return ['dot', 'neato', 'fdp', 'sfdp', 'twopi', 'circo'];
    }
}

customElements.define('dot-renderer', DotRenderer);
