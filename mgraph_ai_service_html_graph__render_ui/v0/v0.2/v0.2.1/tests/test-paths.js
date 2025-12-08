/* ═══════════════════════════════════════════════════════════════════════════════
   MGraph HTML Graph - Test Suite - Path Configuration
   v0.2.1 - Updated for Shadow DOM components
   
   All paths are local to v0.2.1 (self-contained, no cross-version references)
   ═══════════════════════════════════════════════════════════════════════════════ */

const TestPaths = {
    // v0.2.1: Base path
    BASE_PATH: '/console/v0/v0.2/v0.2.1',
    
    // v0.2.0: For linking back to unchanged files
    V020_BASE_PATH: '/console/v0/v0.2/v0.2.0',
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Foundation (v0.2.1 new files)
    // ═══════════════════════════════════════════════════════════════════════════
    
    get componentPaths() {
        return `${this.BASE_PATH}/config/component-paths.js`;
    },
    
    get baseComponent() {
        return `${this.BASE_PATH}/components/_base/base-component.js`;
    },
    
    get helpers() {
        return `${this.BASE_PATH}/js/utils/helpers.js`;
    },
    
    get sharedCss() {
        return `${this.BASE_PATH}/css/components-shared.css`;
    },
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Refactored Components (v0.2.1)
    // ═══════════════════════════════════════════════════════════════════════════
    
    get statsToolbar() {
        return `${this.BASE_PATH}/components/stats-toolbar/stats-toolbar.js`;
    },
    
    get urlInput() {
        return `${this.BASE_PATH}/components/url-input/url-input.js`;
    },
    
    // ═══════════════════════════════════════════════════════════════════════════
    // v0.2.0 Components (not yet refactored - link back)
    // ═══════════════════════════════════════════════════════════════════════════
    
    get configPanel() {
        return `${this.V020_BASE_PATH}/components/config-panel/config-panel.js`;
    },
    
    get graphCanvas() {
        return `${this.V020_BASE_PATH}/components/graph-canvas/graph-canvas.js`;
    },
    
    get htmlInput() {
        return `${this.V020_BASE_PATH}/components/html-input/html-input.js`;
    },
    
    get topNav() {
        return `${this.V020_BASE_PATH}/components/top-nav/top-nav.js`;
    },
    
    get dotRenderer() {
        return `${this.V020_BASE_PATH}/components/dot-renderer/dot-renderer.js`;
    },
    
    get visRenderer() {
        return `${this.V020_BASE_PATH}/components/vis-renderer/vis-renderer.js`;
    },
    
    get d3Renderer() {
        return `${this.V020_BASE_PATH}/components/d3-renderer/d3-renderer.js`;
    },
    
    get cytoscapeRenderer() {
        return `${this.V020_BASE_PATH}/components/cytoscape-renderer/cytoscape-renderer.js`;
    },
    
    get mermaidRenderer() {
        return `${this.V020_BASE_PATH}/components/mermaid-renderer/mermaid-renderer.js`;
    },
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Services (link back to v0.2.0)
    // ═══════════════════════════════════════════════════════════════════════════
    
    get apiClient() {
        return `${this.V020_BASE_PATH}/js/services/api-client.js`;
    },
    
    get playgroundJs() {
        return `${this.V020_BASE_PATH}/js/playground.js`;
    },
    
    // ═══════════════════════════════════════════════════════════════════════════
    // CSS Paths
    // ═══════════════════════════════════════════════════════════════════════════
    
    get commonCss() {
        return `${this.V020_BASE_PATH}/css/common.css`;
    },
    
    get playgroundCss() {
        return `${this.V020_BASE_PATH}/css/playground.css`;
    },
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Sample Paths
    // ═══════════════════════════════════════════════════════════════════════════
    
    getSamplePath(sampleName) {
        return `${this.V020_BASE_PATH}/samples/${sampleName}.html`;
    },
    
    // ═══════════════════════════════════════════════════════════════════════════
    // Helper to get component path by name
    // ═══════════════════════════════════════════════════════════════════════════
    
    getComponentPath(componentName) {
        const refactoredComponents = ['stats-toolbar', 'url-input'];
        const basePath = refactoredComponents.includes(componentName) 
            ? this.BASE_PATH 
            : this.V020_BASE_PATH;
        return `${basePath}/components/${componentName}/${componentName}.js`;
    }
};

// Freeze to prevent accidental modification
Object.freeze(TestPaths);

// Export for both browser and Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TestPaths;
}
if (typeof window !== 'undefined') {
    window.TestPaths = TestPaths;
}
