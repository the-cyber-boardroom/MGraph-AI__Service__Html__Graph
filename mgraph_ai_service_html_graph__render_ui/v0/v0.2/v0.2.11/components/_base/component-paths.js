/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Component Paths Configuration
   v0.2.11 - Path resolution for Shadow DOM components
   ═══════════════════════════════════════════════════════════════════════════════ */

const ComponentPaths = {
    // Base path for this version
    base: '../v0.2.11',
    
    // Shared CSS files
    sharedCss: {
        components: '../v0.2.1/css/components-shared.css',
        common: '../v0.2.0/css/common.css'
    },
    
    // Component path patterns
    components: {
        'cache-browser': {
            js: '../v0.2.11/components/cache-browser/cache-browser.js',
            css: '../v0.2.11/components/cache-browser/cache-browser.css',
            html: '../v0.2.11/components/cache-browser/cache-browser.html'
        },
        'cache-metadata': {
            js: '../v0.2.11/components/cache-metadata/cache-metadata.js',
            css: '../v0.2.11/components/cache-metadata/cache-metadata.css',
            html: '../v0.2.11/components/cache-metadata/cache-metadata.html'
        },
        'html-viewer': {
            js: '../v0.2.11/components/html-viewer/html-viewer.js',
            css: '../v0.2.11/components/html-viewer/html-viewer.css',
            html: '../v0.2.11/components/html-viewer/html-viewer.html'
        },
        'flow-timeline': {
            js: '../v0.2.11/components/flow-timeline/flow-timeline.js',
            css: '../v0.2.11/components/flow-timeline/flow-timeline.css',
            html: '../v0.2.11/components/flow-timeline/flow-timeline.html'
        },
        'mini-browser': {
            js: '../v0.2.11/components/mini-browser/mini-browser.js',
            css: '../v0.2.11/components/mini-browser/mini-browser.css',
            html: '../v0.2.11/components/mini-browser/mini-browser.html'
        }
    },
    
    /**
     * Get paths for a component
     * @param {string} componentName - Component tag name
     * @returns {object} Paths object with js, css, html
     */
    getComponentPaths(componentName) {
        const paths = this.components[componentName];
        if (!paths) {
            console.warn(`[ComponentPaths] Unknown component: ${componentName}`);
            return {
                js: `${this.base}/components/${componentName}/${componentName}.js`,
                css: `${this.base}/components/${componentName}/${componentName}.css`,
                html: `${this.base}/components/${componentName}/${componentName}.html`
            };
        }
        return paths;
    }
};

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ComponentPaths;
}
if (typeof window !== 'undefined') {
    window.ComponentPaths = ComponentPaths;
}
