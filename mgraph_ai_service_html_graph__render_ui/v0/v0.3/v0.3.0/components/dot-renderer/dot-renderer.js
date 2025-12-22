/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Render UI - DOT Renderer Component
   v0.3.0 - From v0.2.0 (unchanged)
   
   Renders DOT/Graphviz strings to SVG using viz-js (WebAssembly Graphviz)
   ═══════════════════════════════════════════════════════════════════════════════ */

class DotRenderer extends HTMLElement {
    constructor() {
        super();
        this.viz = null;
        this.vizLoading = null;
        this.graphCanvas = null;
    }

    connectedCallback() {
        this.style.display = 'none';
        this.graphCanvas = document.querySelector('graph-canvas');
        this.loadVizJs();
    }

    async loadVizJs() {
        if (this.viz) return this.viz;
        if (this.vizLoading) return this.vizLoading;

        this.vizLoading = new Promise(async (resolve, reject) => {
            try {
                if (typeof Viz !== 'undefined') {
                    this.viz = await Viz.instance();
                    resolve(this.viz);
                    return;
                }

                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/@viz-js/viz/lib/viz-standalone.js';
                script.async = true;

                script.onload = async () => {
                    try {
                        this.viz = await Viz.instance();
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

    async renderDot(dotString, options = {}) {
        if (!dotString || !dotString.trim()) {
            throw new Error('Empty DOT string');
        }

        try {
            const viz = await this.loadVizJs();

            const svg = viz.renderSVGElement(dotString, {
                engine: options.engine || 'dot',
                format: 'svg'
            });

            const svgString = new XMLSerializer().serializeToString(svg);

            if (this.graphCanvas) {
                this.graphCanvas.renderSvg(svgString);
            }

            return svgString;
        } catch (error) {
            console.error('DOT rendering error:', error);
            
            if (this.graphCanvas) {
                this.graphCanvas.showError('Failed to render DOT graph', error.message);
            }

            throw error;
        }
    }

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

    isReady() {
        return this.viz !== null;
    }

    getSupportedEngines() {
        return ['dot', 'neato', 'fdp', 'sfdp', 'twopi', 'circo'];
    }
}

customElements.define('dot-renderer', DotRenderer);
