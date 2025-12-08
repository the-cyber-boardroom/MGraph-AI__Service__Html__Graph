/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Component Paths Configuration
   v0.2.1 - Configurable resource paths for components
   
   Enables:
   - Easy path overrides in v0.2.x minor versions
   - Testing with alternative resources
   - Potential CDN deployment in future
   ═══════════════════════════════════════════════════════════════════════════════ */

const ComponentPaths = {
    // Base path for all component resources
    // Override this in v0.2.x for different deployment scenarios
    basePath: '/console/v0/v0.2/v0.2.1',
    
    // v0.2.0 base path for linking back to unchanged files
    v020BasePath: '/console/v0/v0.2/v0.2.0',
    
    /**
     * Returns paths for a component's resources
     * @param {string} componentName - e.g., 'stats-toolbar'
     * @returns {object} Object with js, css, html paths
     */
    getComponentPaths(componentName) {
        const base = `${this.basePath}/components/${componentName}`;
        return {
            js: `${base}/${componentName}.js`,
            css: `${base}/${componentName}.css`,
            html: `${base}/${componentName}.html`
        };
    },
    
    /**
     * Get path for a v0.2.0 component (for components not yet refactored)
     * @param {string} componentName
     * @returns {string} Path to v0.2.0 component JS
     */
    getV020ComponentPath(componentName) {
        return `${this.v020BasePath}/components/${componentName}/${componentName}.js`;
    },
    
    // Shared CSS resources
    sharedCss: {
        get common() { return `${ComponentPaths.basePath}/css/common.css`; },
        get components() { return `${ComponentPaths.basePath}/css/components-shared.css`; }
    },
    
    // Utility scripts
    utils: {
        get helpers() { return `${ComponentPaths.basePath}/js/utils/helpers.js`; },
        get dotParser() { return `${ComponentPaths.basePath}/js/utils/dot-parser.js`; }
    },
    
    // Services
    services: {
        get apiClient() { return `${ComponentPaths.basePath}/js/services/api-client.js`; }
    },
    
    // Samples path
    getSamplePath(sampleName) {
        return `${this.basePath}/samples/${sampleName}.html`;
    }
};

// Freeze to prevent accidental modification
Object.freeze(ComponentPaths.sharedCss);
Object.freeze(ComponentPaths.utils);
Object.freeze(ComponentPaths.services);
Object.freeze(ComponentPaths);

// Export for both browser and Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ComponentPaths;
}
if (typeof window !== 'undefined') {
    window.ComponentPaths = ComponentPaths;
}
